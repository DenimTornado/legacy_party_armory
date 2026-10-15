-- All item creation is behind an explicit player action or Give(). No Story goals.
local data = Ext.Require("ArmoryData.lua")
LegacyPartyArmory = LegacyPartyArmory or {}
local API = LegacyPartyArmory
API.Mode = data.mode
local action = "Shout_LPA_Armory"
local generation, busy = 0, false
local function valid(uuid)
    return type(uuid) == "string" and uuid ~= "" and uuid ~= "00000000-0000-0000-0000-000000000000"
end
local function log(msg) _P("[Legacy Party Armory] " .. msg) end

function API.Give(character)
    if busy then return false, "Armory creation is already running" end
    local host = character or Osi.GetHostCharacter()
    if not valid(host) then return false, "Load a game before requesting the Armory" end
    if Osi.IsInCombat(host) == 1 then return false, "Use the Armory outside combat" end
    local x,y,z = Osi.GetPosition(host)
    if not x or not y or not z then return false, "Player position is unavailable" end
    busy = true
    local session = generation
    local created, bags, queue = {}, {}, {}
    local function enqueue(key,parent)
        queue[#queue+1] = {bag=key,template=data.bags[key].uuid,parent=parent}
        for _,child in ipairs(data.bags[key].children) do enqueue(child,key) end
        for _,item in ipairs(data.bags[key].items) do queue[#queue+1] = {template=item,parent=key} end
    end
    enqueue("outer",nil)
    local index = 1
    local function fail(message)
        -- Only entities created by this invocation are touched by rollback.
        for i=#created,1,-1 do pcall(Osi.RequestDelete,created[i]) end
        busy=false; API.LastError=tostring(message); log("Creation failed and rolled back: " .. API.LastError)
    end
    local function step()
        if session ~= generation then return end
        local entry=queue[index]
        if not entry then
            busy=false; API.LastError=nil; API.LastCreated=bags.outer
            log("Created " .. data.mode .. " Armory: " .. bags.outer .. " (" .. #created .. " objects)")
            return
        end
        local ok,uuid=pcall(Osi.CreateAt,entry.template,x,y,z,0,0,"")
        if not ok or not valid(uuid) then fail("CreateAt " .. entry.template .. ": " .. tostring(uuid)); return end
        created[#created+1]=uuid
        if entry.bag then bags[entry.bag]=uuid end
        local attempts=0
        local function move()
            if session ~= generation then return end
            attempts=attempts+1
            local parent=entry.parent and bags[entry.parent] or host
            local ready=Ext.Entity.Get(uuid)
            if not ready then
                if attempts<40 then Ext.Timer.WaitFor(50,move) else fail("Spawn timed out: "..entry.template) end
                return
            end
            local moved,err=pcall(Osi.ToInventory,uuid,parent,1,0,1)
            if not moved then fail("ToInventory: "..tostring(err));return end
            Ext.Timer.WaitFor(75,function()
                if session ~= generation then return end
                local checked,inside=pcall(Osi.IsInInventoryOf,uuid,parent)
                if not checked or not (inside==true or inside==1) then
                    if attempts<40 then Ext.Timer.WaitFor(50,move) else fail("Inventory placement failed: "..entry.template) end
                    return
                end
                index=index+1;step()
            end)
        end
        Ext.Timer.WaitFor(50,move)
    end
    step()
    return true, "Armory creation started"
end

Ext.Osiris.RegisterListener("UsingSpell",5,"after",function(caster,spell)
    if spell==action then
        local ok,err=API.Give(caster)
        if not ok then log(tostring(err)) end
    end
end)
Ext.Events.SessionLoaded:Subscribe(function()
    generation=generation+1;busy=false
    local session,attempts=generation,0
    local function addAction()
        if session~=generation then return end
        attempts=attempts+1
        local ok,host=pcall(Osi.GetHostCharacter)
        if ok and valid(host) then
            local added,err=pcall(Osi.AddSpell,host,action,0,1)
            if added then log("Manual Armory action ready ("..data.mode.."). No items were granted.");return end
            log("AddSpell: "..tostring(err))
        end
        if attempts<30 then Ext.Timer.WaitFor(1000,addAction) end
    end
    Ext.Timer.WaitFor(1500,addAction)
end)
