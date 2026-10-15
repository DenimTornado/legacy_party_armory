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

function Attr($Node, [string]$Id) { return $Node.SelectSingleNode("attribute[@id='$Id']") }

function Set-Attr([xml]$Doc, $Node, [string]$Id, [string]$Type, [string]$Value) {
    $a = Attr $Node $Id
    if ($null -eq $a) {
        $a = $Doc.CreateElement('attribute')
        $a.SetAttribute('id',$Id)
        [void]$Node.AppendChild($a)
    }
    $a.SetAttribute('type',$Type)
    $a.SetAttribute('value',$Value)
}

function Find-Param($Resource, [string]$Name) {
    foreach ($p in $Resource.SelectNodes('children/node')) {
        $n = Attr $p 'ParameterName'
        if ($null -ne $n -and $n.GetAttribute('value') -eq $Name) { return $p }
    }
    return $null
}

function Ensure-Vector3([xml]$Doc, $Resource, [string]$Name, [string]$Value) {
    $children = $Resource.SelectSingleNode('children')
    if ($null -eq $children) {
        $children = $Doc.CreateElement('children')
        [void]$Resource.AppendChild($children)
    }
    $p = Find-Param $Resource $Name
    if ($null -eq $p) {
        $p = $Doc.CreateElement('node')
        $p.SetAttribute('id','Vector3Parameters')
        [void]$children.AppendChild($p)
        Set-Attr $Doc $p 'Enabled' 'bool' 'True'
        Set-Attr $Doc $p 'ExportAsPreset' 'bool' 'True'
        Set-Attr $Doc $p 'GroupName' 'FixedString' ''
        Set-Attr $Doc $p 'ParameterName' 'FixedString' $Name
        Set-Attr $Doc $p 'IsColor' 'bool' 'True'
    }
    Set-Attr $Doc $p 'Value' 'fvec3' $Value
    Set-Attr $Doc $p 'BaseValue' 'fvec3' $Value
}

$assetsPath = Join-Path $StageRoot 'Public/DenimDragonArmor/Content/Assets/[PAK]_LegacyPartyArmory/_merged.lsx'
[xml]$assets = Get-Content -Raw -LiteralPath $assetsPath
$materials = $assets.SelectNodes("/save/region[@id='MaterialBank']/node[@id='MaterialBank']/children/node[@id='Resource']")

foreach ($m in $materials) {
    $nameAttr = Attr $m 'Name'
    if ($null -eq $nameAttr) { continue }
    $name = $nameAttr.GetAttribute('value')
    if (-not ($name.StartsWith('LPA_SharSpear_') -or $name.StartsWith('LPA_WalkingFortress_'))) { continue }

    # Reproduce the successful accidental blue test: primary candidate was
    # linear RGB 0 0.3 1 on Custom_2; pure 0 0 1 was also present in the test.
    Ensure-Vector3 $assets $m 'Custom_2' '0 0.3 1'
    Ensure-Vector3 $assets $m 'Color' '0 0.3 1'
    Ensure-Vector3 $assets $m 'VariationColor' '0 0 1'
}

Save-XmlUtf8 $assets $assetsPath
Write-Host "Applied Shadowheart electric-blue material pass for $Mode."
