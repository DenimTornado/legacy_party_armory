param(
    [Parameter(Mandatory=$true)][string]$StageRoot,
    [Parameter(Mandatory=$true)][ValidateSet('preview','final')][string]$Mode
)
$ErrorActionPreference = 'Stop'
$utf8 = New-Object System.Text.UTF8Encoding($false)

# Keep runtime instance-dye logic, but make Karlach visibly distinct.
# Boreal Blue dye root template:
#   LOOT_Dye_RoyalBlue_01 / OBJ_Dye_RoyalBlue
#   17f6e66e-1c23-41d2-9370-3bd9a5a90b4a
$luaPath = Join-Path $StageRoot 'Mods/DenimDragonArmor/ScriptExtender/Lua/BootstrapServer.lua'
$lua = [IO.File]::ReadAllText($luaPath)
$lua = $lua.Replace('API.Version = "0.3.12"', 'API.Version = "0.3.13"')
$lua = $lua.Replace(
    '-- Karlach: Black and Teal. Stronger cool contrast against her red skin than' + "`n" +
    '    -- the previous Black and Azure pass, while keeping the outfit infernal-dark.' + "`n" +
    '    ["aef31c6f-07a7-5b20-9007-e910ca009ea1"] = "94ef7170-1c1d-489a-9c18-55209d864e3a"',
    '-- Karlach: Boreal Blue. Intentionally brighter/cooler so the dye reads clearly' + "`n" +
    '    -- against her red skin and does not disappear into the native dark leather.' + "`n" +
    '    ["aef31c6f-07a7-5b20-9007-e910ca009ea1"] = "17f6e66e-1c23-41d2-9370-3bd9a5a90b4a"'
)
[IO.File]::WriteAllText($luaPath, $lua, $utf8)

Write-Host "Applied 0.3.13 system cleanup for $Mode."
