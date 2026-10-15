param(
    [Parameter(Mandatory=$true)][string]$StageRoot,
    [Parameter(Mandatory=$true)][ValidateSet('preview','final')][string]$Mode
)
$ErrorActionPreference = 'Stop'
$utf8 = New-Object System.Text.UTF8Encoding($false)

function Save-XmlUtf8([xml]$Doc, [string]$Path) {
    $settings = New-Object System.Xml.XmlWriterSettings
    $settings.Encoding = $utf8
    $settings.Indent = $true
    $settings.IndentChars = "`t"
    $settings.NewLineChars = "`n"
    $settings.NewLineHandling = [System.Xml.NewLineHandling]::Replace
    $writer = [System.Xml.XmlWriter]::Create($Path, $settings)
    try { $Doc.PSBase.Save($writer) } finally { $writer.Dispose() }
}

$rootsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/RootTemplates/_merged.lsx'
[xml]$roots = Get-Content -Raw -LiteralPath $rootsPath
$root = $roots.SelectSingleNode("//node[@id='GameObjects'][attribute[@id='MapKey' and @value='33bcf8bc-50ff-507b-aadf-53de85fb396d']]")
if ($null -eq $root) { throw 'Missing Veil of Menzoberranzan root' }
$color = $root.SelectSingleNode("attribute[@id='ColorPreset']")
if ($null -eq $color) {
    $color = $roots.CreateElement('attribute')
    $color.SetAttribute('id','ColorPreset')
    [void]$root.AppendChild($color)
}
$color.SetAttribute('type','31')
$color.SetAttribute('value','9602f5d1-827b-f508-7dd4-c4b3ff068eec')
Save-XmlUtf8 $roots $rootsPath
Write-Host "Applied Veil of Menzoberranzan black/white monochrome preset for $Mode."
