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

# Earlier staging patches can still leave ColorPreset on these roots (notably
# Apply-034's Orin dress). Remove explicit palettes after all of those patches.
$rootsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/RootTemplates/_merged.lsx'
[xml]$roots = Get-Content -Raw -LiteralPath $rootsPath
foreach ($uuid in @(
    'def74bcd-48a7-55c2-99d6-9b72e66c2fe0',
    '334a92c4-f2b6-5dd8-9eb5-6606b424253e',
    '33bcf8bc-50ff-507b-aadf-53de85fb396d',
    'aef31c6f-07a7-5b20-9007-e910ca009ea1'
)) {
    $root = $roots.SelectSingleNode("//node[@id='GameObjects'][attribute[@id='MapKey' and @value='$uuid']]")
    if ($null -eq $root) { throw "Missing runtime-dyed root: $uuid" }
    $color = $root.SelectSingleNode("attribute[@id='ColorPreset']")
    if ($null -ne $color) { [void]$root.RemoveChild($color) }
}
$settings = New-Object System.Xml.XmlWriterSettings
$settings.Encoding = $utf8
$settings.Indent = $true
$writer = [System.Xml.XmlWriter]::Create($rootsPath, $settings)
try { $roots.PSBase.Save($writer) } finally { $writer.Dispose() }

Write-Host "Applied 0.3.13 system cleanup for $Mode."
