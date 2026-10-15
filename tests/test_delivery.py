"""Exercise actual server Lua against asynchronous Osiris event boundaries.

Requires lupa. This verifies delivery bookkeeping, not engine rendering.
"""
import json
from pathlib import Path
import unittest

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
LUA = ROOT / 'src/Mods/DenimDragonArmor/ScriptExtender/Lua/BootstrapServer.lua'

MOCK = r'''
listeners, timers, entities, requests, deleted, logs = {}, {}, {}, {}, {}, {}
host = "Host_00000000-0000-0000-0000-000000000001"
combat, synchronous, loseEvent, failAt, wrongOwner = 0, false, false, 0, false
now, sequence, serial = 0, 0, 0
function wait(ms, fn)
    serial = serial + 1
    timers[#timers+1] = {at=now+ms, fn=fn, serial=serial}
end
function tick()
    table.sort(timers,function(a,b) return a.at==b.at and a.serial<b.serial or a.at<b.at end)
    local t=table.remove(timers,1)
    if not t then return false end
    now=t.at; t.fn(); return true
end
function drain()
    local n=0
    while tick() do n=n+1; assert(n<20000,"timer loop") end
end
function _P(_) end
Ext = {
    Require=function(_) return testData end,
    IO={SaveFile=function(_,content) logs[#logs+1]=content end},
    Osiris={RegisterListener=function(name,arity,phase,fn)
        assert(phase=="after")
        assert((name=="TemplateAddedTo" and arity==4) or (name=="UsingSpell" and arity==5))
        listeners[name]=fn
    end},
    Timer={WaitFor=wait},
    Entity={Get=function(id) return entities[id] end},
    Events={SessionLoaded={Subscribe=function(self,fn) loaded=fn end}}
}
Osi = {
    GetHostCharacter=function() return host end,
    IsInCombat=function(_) return combat end,
    AddSpell=function(...) end,
    TemplateAddTo=function(template,parent,count,notification)
        assert(count==1 and notification==0)
        assert(parent==host or entities[parent],"parent not ready")
        requests[#requests+1]={template=template,parent=parent}
        if #requests==failAt then error("injected native failure") end
        sequence=sequence+1
        local id=string.format("Item_%08d-0000-0000-0000-%012d",sequence,sequence)
        -- Noise from unrelated mods must never be mistaken for our new item.
        listeners.TemplateAddedTo("00000000-0000-0000-0000-000000000099",id,host,"Regular")
        local function emit()
            if loseEvent then return end
            entities[id]={template=template,parent=wrongOwner and host or parent}
            listeners.TemplateAddedTo("Root_"..template,id,parent,"Regular")
            listeners.TemplateAddedTo(template,id,parent,"Regular") -- duplicate
        end
        if synchronous then emit() else wait(250,emit) end
    end,
    IsInInventoryOf=function(id,parent)
        return entities[id] and entities[id].parent==parent and 1 or 0
    end,
    RequestDelete=function(id) deleted[#deleted+1]=id; entities[id]=nil end
}
'''


def lua_table(lua, value):
    if isinstance(value, dict):
        return lua.table_from({k: lua_table(lua, v) for k, v in value.items()})
    if isinstance(value, list):
        return lua.table_from([lua_table(lua, v) for v in value])
    return value


class Delivery(unittest.TestCase):
    def runtime(self, mode='preview'):
        lua = LuaRuntime(unpack_returned_tuples=True)
        data = json.loads((ROOT / f'config/{mode}.json').read_text())
        lua.globals().testData = lua_table(lua, data)
        lua.execute(MOCK)
        lua.execute(LUA.read_text())
        return lua, data

    def test_complete_nested_delivery_both_event_timings(self):
        for mode, count in [('preview', 43), ('final', 26)]:
            for synchronous in [False, True]:
                with self.subTest(mode=mode, synchronous=synchronous):
                    lua, data = self.runtime(mode)
                    lua.globals().synchronous = synchronous
                    lua.execute('loaded(); drain()')
                    self.assertEqual(0, len(lua.globals().requests))
                    self.assertTrue(lua.eval('LegacyPartyArmory.Give()')[0])
                    self.assertFalse(lua.eval('LegacyPartyArmory.Give()')[0])
                    lua.execute('drain()')
                    g = lua.globals()
                    self.assertEqual(count, len(g.requests))
                    self.assertEqual(0, len(g.deleted))
                    self.assertIsNone(g.LegacyPartyArmory.LastError)
                    by_template = {v['template']: (k, v) for k, v in g.entities.items()}
                    bags = data['bags']
                    self.assertEqual(g.host, by_template[bags['outer']['uuid']][1]['parent'])
                    for key, bag in bags.items():
                        bag_id = by_template[bag['uuid']][0]
                        # Keep duplicates in different bags; inspect actual instances.
                        actual = [v['template'] for v in g.entities.values() if v['parent'] == bag_id]
                        expected = bag['items'] + [bags[c]['uuid'] for c in bag['children']]
                        self.assertCountEqual(expected, actual, key)

    def test_native_error_rolls_back_only_this_call(self):
        lua, _ = self.runtime()
        lua.execute('entities["existing"]={}; failAt=5; LegacyPartyArmory.Give(); drain()')
        self.assertEqual(4, len(lua.globals().deleted))
        self.assertIsNotNone(lua.globals().entities['existing'])
        self.assertIn('injected native failure', lua.globals().LegacyPartyArmory.LastError)
        self.assertTrue(lua.eval('LegacyPartyArmory.Give()')[0])

    def test_missing_event_does_not_spawn_repeatedly(self):
        lua, _ = self.runtime()
        lua.execute('loseEvent=true; LegacyPartyArmory.Give(); drain()')
        self.assertEqual(1, len(lua.globals().requests))
        self.assertIn('timed out', lua.globals().LegacyPartyArmory.LastError)

    def test_wrong_inventory_stops_before_filling_bag(self):
        lua, _ = self.runtime()
        lua.execute('wrongOwner=true; LegacyPartyArmory.Give(); drain()')
        self.assertEqual(2, len(lua.globals().requests))
        self.assertEqual(2, len(lua.globals().deleted))

    def test_loading_another_session_cancels_queued_delivery(self):
        lua, _ = self.runtime()
        lua.execute('LegacyPartyArmory.Give(); loaded(); drain()')
        self.assertEqual(1, len(lua.globals().requests))
        self.assertIsNone(lua.globals().LegacyPartyArmory.LastCreated)

    def test_combat_blocks_creation(self):
        lua, _ = self.runtime()
        lua.execute('combat=1')
        self.assertFalse(lua.eval('LegacyPartyArmory.Give()')[0])
        self.assertEqual(0, len(lua.globals().requests))


if __name__ == '__main__':
    unittest.main()
