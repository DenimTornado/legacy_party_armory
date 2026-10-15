"""Behavioural Lua tests and compiled-package invariants; no game/render claims."""
from pathlib import Path
import sys,json,re,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'research_deps'))
from lupa import LuaRuntime
from armory_spec import *

MOCK=r'''
queue={};objects={};spells={};listeners={};logs={};created=0;deleted=0;combat=0;host="host";failAt=0;failMoves=false
Osi={}
function Osi.GetHostCharacter() return host end
function Osi.IsInCombat() return combat end
function Osi.GetPosition() return 1,2,3 end
function Osi.AddSpell(who,spell,a,b) spells[who..spell]=true end
function Osi.CreateAt(template,x,y,z,temp,spawn,event)
 assert(x==1 and y==2 and z==3 and temp==0 and spawn==0 and event=="")
 created=created+1
 if created==failAt then error("injected spawn failure") end
 local id="item-"..created
 objects[id]={template=template,owner=nil};return id
end
function Osi.ToInventory(uuid,parent,a,b,c)
 assert(objects[uuid] and (parent=="host" or objects[parent]))
 assert(a==1 and b==0 and c==1)
 if not failMoves then objects[uuid].owner=parent end
end
function Osi.IsInInventoryOf(...) assert(select('#',...)==2);local uuid,parent=...;return objects[uuid].owner==parent and 1 or 0 end
function Osi.RequestDelete(uuid) if objects[uuid] then objects[uuid]=nil;deleted=deleted+1 end end
Ext={Timer={},Entity={},Osiris={},Events={SessionLoaded={}}}
function Ext.Require() return ARMORY_DATA end
function Ext.Entity.Get(uuid) return objects[uuid] end
function Ext.Timer.WaitFor(ms,fn) queue[#queue+1]=fn end
function Ext.Osiris.RegisterListener(name,n,when,fn) listeners[name]=fn end
function Ext.Events.SessionLoaded:Subscribe(fn) sessionLoaded=fn end
function _P(s) logs[#logs+1]=s end
function drain()
 local n=0
 while #queue>0 do n=n+1;assert(n<10000);local f=table.remove(queue,1);f() end
end
function count() local n=0;for _,v in pairs(objects) do n=n+1 end;return n end
'''
def lua_value(lua,value):
 if isinstance(value,dict):return lua.table_from({k:lua_value(lua,v) for k,v in value.items()})
 if isinstance(value,list):return lua.table_from([lua_value(lua,v) for v in value])
 return value
def environment(mode):
 data=json.loads((ROOT/f'manifest_{mode}.json').read_text(encoding='utf-8'))
 l=LuaRuntime(unpack_returned_tuples=True);l.execute(MOCK);g=l.globals();g.ARMORY_DATA=lua_value(l,data)
 l.execute((ROOT/'runtime.lua').read_text(encoding='utf-8'));return l,g,data
def run_lua(mode):
 l,g,data=environment(mode)
 g.sessionLoaded();g.drain();assert g.count()==0,'session load granted items'
 assert g.spells['hostShout_LPA_Armory']
 ok,msg=g.LegacyPartyArmory.Give();assert ok,msg
 assert g.LegacyPartyArmory.Give()[0] is False,'overlapping request accepted'
 g.drain();assert g.LegacyPartyArmory.LastError is None
 expected=sum(1+len(b['items']) for b in data['bags'].values())
 assert g.count()==expected,(g.count(),expected)
 # Every bag and item must have precisely the intended immediate owner.
 instances={}
 for uuid_,obj in g.objects.items():instances.setdefault(obj.template,[]).append((uuid_,obj.owner))
 bag_entities={k:instances[v['uuid']][0][0] for k,v in data['bags'].items()}
 assert instances[data['bags']['outer']['uuid']][0][1]=='host'
 for key,bag in data['bags'].items():
  for child in bag['children']:assert instances[data['bags'][child]['uuid']][0][1]==bag_entities[key]
  for template in bag['items']:assert any(owner==bag_entities[key] for _,owner in instances[template])
 g.listeners.UsingSpell('host','Shout_LPA_Armory');g.drain();assert g.count()==2*expected
 g.combat=1;assert g.LegacyPartyArmory.Give()[0] is False;g.drain();assert g.count()==2*expected
 for failure in ['spawn','move']:
  l,g,_=environment(mode)
  if failure=='spawn':g.failAt=4
  else:g.failMoves=True
  g.LegacyPartyArmory.Give();g.drain();assert g.count()==0;assert g.LegacyPartyArmory.LastError
 # Loading another save cancels pending callbacks without creating further items.
 l,g,_=environment(mode);g.LegacyPartyArmory.Give();before=g.created;g.sessionLoaded();g.drain();assert g.created==before
 print(f'PASS Lua {mode}: {expected} objects; exact nesting, manual-only, repeat, combat, overlap, rollback, stale callbacks')

def files(mode):
 src=ROOT/('src_'+mode);stats={}
 for p in (src/'Public/DenimDragonArmor/Stats/Generated/Data').glob('*.txt'):
  for b in p.read_text(encoding='utf-8').split('new entry ')[1:]:
   key=re.match('"([^"]+)"',b)[1];assert key not in stats,key
   stats[key]=dict(re.findall('data "([^"]+)" "([^"]*)"',b))
 assert stats['DENIM_RedDragon_Armor']['ArmorClass']=='16'
 assert stats['DENIM_RedDragon_Helmet']['ArmorType']=='None'
 for item in ITEMS:
  assert item['stats'] in stats
  assert stats[item['stats']]['Rarity']=='Legendary',item['stats']
 custom={i['key']:i for i in ITEMS}
 assert custom['Carsomyr']['base']=='f01c3f5d-c542-420f-86c5-bdddf7819e29'
 assert custom['DragonsBreath']['parent']=='WPN_Halberd_2'
 assert custom['HarperFinery']['base']=='c0c0534c-b7fc-4d0b-a335-b8f4c548852d'
 assert custom['HarperFinery']['parent']=='ARM_StuddedLeather_Body'
 assets=E.parse(ROOT/'armory_assets.lsx')
 for item in ['Twinkle','Icingdeath','CharonsClaw']:
  material=next(n for n in assets.findall('./region[@id="MaterialBank"]/node/children/node') if n.find('attribute[@id="Name"]').get('value').startswith('LPA_'+item+'_'))
  assert material.find('attribute[@id="SourceFile"]').get('value').endswith('/Base_GM_VT.lsf')
  params={n.find('attribute[@id="ParameterName"]').get('value'):n for n in material.findall('children/node') if n.find('attribute[@id="ParameterName"]') is not None}
  assert params['Glowmap'].find('attribute[@id="ID"]').get('value')
  assert float(params['GlowMultiplier'].find('attribute[@id="Value"]').get('value'))>=3
 carso=next(n for n in assets.findall('./region[@id="MaterialBank"]/node/children/node') if n.find('attribute[@id="Name"]').get('value').startswith('LPA_Carsomyr_'))
 mask=carso.find('children/node/attribute[@id="ParameterName"][@value="MSK1"]')
 assert mask is not None
 assert (src/'Public/DenimDragonArmor/Assets/Textures/carsomyr_grip_mask.dds').exists()
 assert all(not key.startswith(('MAG_','WPN_','ARM_','OBJ_')) for key in stats),'vanilla stats replaced'
 assert stats['LPA_LifeDrink']['Properties']=='Highlighted;OncePerTurn'
 assert stats['Shout_LPA_Armory']['UseCosts']==''
 for e in ['Fire','Cold','Lightning','Acid','Poison']:assert stats['Shout_LPA_'+e]['SpellFlags']==''
 for lang in ['English','Russian']:
  tree=E.parse(ROOT/(lang+'.xml'));texts={n.get('contentuid'):n.text for n in tree.findall('content')}
  for d in stats.values():
   for k in ['DisplayName','Description']:
    if d.get(k):assert d[k].split(';')[0] in texts,(lang,k,d[k])
 template=E.parse(ROOT/'working_templates.lsx')
 harper=next(n for n in template.findall('.//node[@id="GameObjects"]') if n.find('attribute[@id="MapKey"]').get('value')==uid('HarperFinery'))
 assert harper.find('children/node[@id="Equipment"]/children/node[@id="Slot"]/attribute[@id="Object"]').get('value')=='Body'
 roots=template.findall('.//node[@id="GameObjects"]');ids=[n.find('attribute[@id="MapKey"]').get('value') for n in roots];assert len(set(ids))==len(ids)==25,len(ids)
 for n in roots:
  key=n.find('attribute[@id="MapKey"]').get('value')
  if key not in dict(DRAGONS):
   assert n.find('attribute[@id="ParentTemplateId"]') is None
   for banned in ['Scripts','StatusList','OnUsePeaceActions']:
    if key not in {uid('bag:'+k) for k in BAGS}:
     if banned=='StatusList' and key==uid('SeluneSpear'):
      assert {a.get('value') for a in n.findall('children/node[@id="StatusList"]//attribute')}=={'MAG_SELUNE_SPEAR_MOONBEAM_MAGIC_ITEM','MAG_SELUNE_SPEAR_MOONFIRE_MAGIC_ITEM'}
     else:assert n.find(f'children/node[@id="{banned}"]') is None
 assert not list(src.glob('Mods/*/Story/**/*')),'Story assets introduced'
 print(f'PASS files {mode}: {len(stats)} definitions, 25 private/stable roots, EN/RU handles, Rage-compatible selectors, no vanilla stats replacement')

if __name__=='__main__':
 for mode in ['preview','final']:run_lua(mode);files(mode)
 preview=json.loads((ROOT/'manifest_preview.json').read_text(encoding='utf-8'));final=json.loads((ROOT/'manifest_final.json').read_text(encoding='utf-8'))
 assert sum(len(b['items']) for b in preview['bags'].values())==sum(len(b['items']) for b in final['bags'].values())+sum(len(v) for v in PREVIEW.values())-sum(len(v) for v in FINAL_DYES.values())
 print('PASS preview/final content separation')
