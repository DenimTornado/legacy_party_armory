param(
    [ValidateSet('preview','final')][string]$Mode = 'preview',
    [string]$Divine = $env:BG3_DIVINE,
    [string]$Python = $env:BG3_PYTHON
)
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath($PSScriptRoot)
if (-not $Divine) {
    $candidates = @(
        (Join-Path $projectRoot 'tools/Divine.exe'),
        (Join-Path (Split-Path $projectRoot) 'tools/ExportTool/Packed/Tools/Divine.exe')
    )
    $Divine = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $Divine -or -not (Test-Path -LiteralPath $Divine)) {
    throw 'Provide LSLib Divine.exe: ./Build.ps1 -Divine C:/Tools/ExportTool/Tools/Divine.exe'
}
$Divine = (Resolve-Path -LiteralPath $Divine).Path
$stageRoot = Join-Path $projectRoot ('build/' + $Mode + '-' + [guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $stageRoot -Force
$sourceRoot = Join-Path $projectRoot 'src'
Get-ChildItem -LiteralPath $sourceRoot | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $stageRoot -Recurse
}

# Preserve 0.3.1 as a known-good source snapshot. Later revisions are small,
# reviewable patches applied only to the staging copy.
& (Join-Path $projectRoot 'Apply-032.ps1') -StageRoot $stageRoot -Mode $Mode
& (Join-Path $projectRoot 'Apply-034.ps1') -StageRoot $stageRoot -Mode $Mode
& (Join-Path $projectRoot 'Apply-035-Minthara.ps1') -StageRoot $stageRoot -Mode $Mode
& (Join-Path $projectRoot 'Apply-035-Wyll.ps1') -StageRoot $stageRoot -Mode $Mode
& (Join-Path $projectRoot 'Apply-035-Shadowheart.ps1') -StageRoot $stageRoot -Mode $Mode
& (Join-Path $projectRoot 'Apply-039-WyllArmor.ps1') -StageRoot $stageRoot -Mode $Mode
& (Join-Path $projectRoot 'Apply-041-WyllGear.ps1') -StageRoot $stageRoot -Mode $Mode
& (Join-Path $projectRoot 'Apply-041-SystemCleanup.ps1') -StageRoot $stageRoot -Mode $Mode
& (Join-Path $projectRoot 'Apply-042-ShadowheartIdentity.ps1') -StageRoot $stageRoot -Mode $Mode
& (Join-Path $projectRoot 'Apply-042-JaheiraIdentity.ps1') -StageRoot $stageRoot -Mode $Mode
& (Join-Path $projectRoot 'Apply-042-WyllNames.ps1') -StageRoot $stageRoot -Mode $Mode

if (-not $Python) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) { $Python = $pythonCommand.Source }
}
if (-not $Python) { throw 'Provide Python with Pillow: -Python C:/Python/python.exe (or BG3_PYTHON).' }
& $Python (Join-Path $projectRoot 'authoring/patch_visuals_0316.py') --project-root $projectRoot --stage-root $stageRoot
if ($LASTEXITCODE -ne 0) { throw 'Equipment visual patch failed.' }
& $Python (Join-Path $projectRoot 'authoring/weapon_regions_0318.py') --project-root $projectRoot --stage-root $stageRoot
if ($LASTEXITCODE -ne 0) { throw 'Weapon region material patch failed.' }
& $Python (Join-Path $projectRoot 'authoring/build_icons.py') --project-root $projectRoot --stage-root $stageRoot
if ($LASTEXITCODE -ne 0) { throw 'Equipment icon compilation failed.' }

# Runtime version follows the staged patch set.
$runtimePath = Join-Path $stageRoot 'Mods/DenimDragonArmor/ScriptExtender/Lua/BootstrapServer.lua'
$runtime = [IO.File]::ReadAllText($runtimePath).Replace('API.Version = "0.3.13"', 'API.Version = "0.3.19"')
[IO.File]::WriteAllText($runtimePath, $runtime, (New-Object System.Text.UTF8Encoding($false)))

$metaPath = Join-Path $stageRoot 'Mods/DenimDragonArmor/meta.lsx'
$meta = [IO.File]::ReadAllText($metaPath).Replace('0.3.2 ', '0.3.19 ').Replace('36028797019013121', '36028797019013138')
[IO.File]::WriteAllText($metaPath, $meta, (New-Object System.Text.UTF8Encoding($false)))

function Assert-StagePath([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    $prefix = [IO.Path]::GetFullPath($stageRoot) + [IO.Path]::DirectorySeparatorChar
    if (-not $full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Build path escapes staging directory: $Path"
    }
}
function Invoke-Divine([string[]]$Arguments) {
    & $Divine @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Divine failed ($LASTEXITCODE): $Arguments" }
}
$resourceFiles = Get-Content -Raw -LiteralPath (Join-Path $projectRoot 'config/resource-files.json') | ConvertFrom-Json
foreach ($relative in $resourceFiles) {
    $inputFile = Join-Path $stageRoot $relative
    Assert-StagePath $inputFile
    $outputFile = [IO.Path]::ChangeExtension($inputFile, '.lsf')
    Invoke-Divine @('-g','bg3','-a','convert-resource','-s',$inputFile,'-d',$outputFile)
    if (-not (Test-Path -LiteralPath $outputFile)) { throw "No compiled resource: $outputFile" }
    Remove-Item -LiteralPath $inputFile
}
foreach ($inputFile in Get-ChildItem -LiteralPath (Join-Path $stageRoot 'Localization') -Recurse -Filter '*.xml' -File) {
    Assert-StagePath $inputFile.FullName
    $outputFile = [IO.Path]::ChangeExtension($inputFile.FullName, '.loca')
    Invoke-Divine @('-g','bg3','-a','convert-loca','-s',$inputFile.FullName,'-d',$outputFile)
    if (-not (Test-Path -LiteralPath $outputFile)) { throw "No compiled localization: $outputFile" }
    Remove-Item -LiteralPath $inputFile.FullName
}
$utf8 = New-Object System.Text.UTF8Encoding($false)
$data = [IO.File]::ReadAllText((Join-Path $projectRoot "config/$Mode.json"))
$null = $data | ConvertFrom-Json
$luaRoot = Join-Path $stageRoot 'Mods/DenimDragonArmor/ScriptExtender/Lua'
[IO.File]::WriteAllText((Join-Path $luaRoot 'ArmoryData.json'), $data, $utf8)
[IO.File]::WriteAllText((Join-Path $luaRoot 'ArmoryData.lua'), ('return Ext.Json.Parse([==[' + $data + ']==])' + "`n"), $utf8)
$outputRoot = Join-Path $projectRoot 'dist'
$null = New-Item -ItemType Directory -Path $outputRoot -Force
$pak = Join-Path $outputRoot ('LegacyPartyArmory_0.3.19_' + $Mode.ToUpperInvariant() + '.pak')
Invoke-Divine @('-g','bg3','-a','create-package','-s',$stageRoot,'-d',$pak,'-c','lz4','--package-priority','30')
Write-Host "Built $pak"
