-- All item creation is behind an explicit player action or Give(). No Story goals.
local data = Ext.Require("ArmoryData.lua")
LegacyPartyArmory = LegacyPartyArmory or {}
local API = LegacyPartyArmory
API.Mode = data.mode
local action = "Shout_LPA_Armory"
API.Version = "0.3.3"
local generation, busy, pending = 0, false, nil
local logLines = {}
local function valid(uuid)
    return type(uuid) == "string" and uuid ~= "" and uuid ~= "00000000-0000-0000-0000-000000000000"
end
local function log(msg)
    local line = "[Legacy Party Armory " .. API.Version .. "] " .. msg
    _P(line)
    logLines[#logLines+1] = line
    if #logLines > 500 then table.remove(logLines, 1) end
    pcall(function() Ext.IO.SaveFile("LegacyPartyArmory.log", table.concat(logLines, "\n") .. "\n") end)
end
local function guid(value)
    return type(value) == "string" and value:sub(-36):lower() or ""
end

-- Native inventory creation reports the actual instance UUID here. Register
-- before calling TemplateAddTo: the event can arrive during the call itself.
Ext.Osiris.RegisterListener("TemplateAddedTo",4,"after",function(template,object,holder)
    local p = pending
    if p and p.session == generation and not p.uuid and valid(object)
        and guid(template) == guid(p.template) and guid(holder) == guid(p.parent) then
        p.uuid = object
        p.created[#p.created+1] = object
        log("Added " .. p.template .. " as " .. object .. " into " .. holder)
    end
end)

function API.Give(character)
    if busy then return false, "Armory creation is already running" end
    local host = character or Osi.GetHostCharacter()
    if not valid(host) then return false, "Load a game before requesting the Armory" end
    if Osi.IsInCombat(host) == 1 then return false, "Use the Armory outside combat" end
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
        pending=nil
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
        local parent=entry.parent and bags[entry.parent] or host
        if not valid(parent) then fail("Missing destination: " .. tostring(entry.parent)); return end
        local request={template=entry.template,parent=parent,session=session,created=created}
        pending=request
        log("Request " .. index .. "/" .. #queue .. ": " .. entry.template .. " into " .. parent)
        local ok,err=pcall(Osi.TemplateAddTo,entry.template,parent,1,0)
        if not ok then fail("TemplateAddTo " .. entry.template .. ": " .. tostring(err)); return end
        local attempts=0
        local function confirm()
            if session ~= generation then return end
            attempts=attempts+1
            local uuid=request.uuid
            if uuid and Ext.Entity.Get(uuid) then
                local checked,inside=pcall(Osi.IsInInventoryOf,uuid,parent)
                if checked and (inside==true or inside==1) then
                    if entry.bag then bags[entry.bag]=uuid end
                    pending=nil
                    index=index+1
                    Ext.Timer.WaitFor(100,step)
                    return
                end
            end
            if attempts<100 then Ext.Timer.WaitFor(100,confirm)
            else fail("Inventory creation timed out: "..entry.template) end
        end
        Ext.Timer.WaitFor(100,confirm)
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
    generation=generation+1;busy=false;pending=nil
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
