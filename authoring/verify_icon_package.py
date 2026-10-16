"""Verify icon wiring in an extracted, round-tripped release PAK."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

from PIL import Image
from build_icons import ATLAS_ID, fit_icon

ROOT = Path(__file__).resolve().parents[1]


def attr(node, key):
    item = node.find(f'attribute[@id="{key}"]')
    return item.get('value') if item is not None else None


def structure(element):
    return (element.tag, tuple(sorted(element.attrib.items())),
            tuple(structure(child) for child in element))


def verify(divine, mode):
    pak = ROOT / f'dist/LegacyPartyArmory_0.3.19_{mode.upper()}.pak'
    output = ROOT / f'build/verify-0319-{mode}'

    def run(*args):
        subprocess.run([str(divine), '-g', 'bg3', *map(str, args)], check=True,
                       stdout=subprocess.DEVNULL)

    run('-a', 'extract-package', '-s', pak, '-d', output)
    decoded = {}
    for label, relative in [
        ('roots', 'Public/DenimDragonArmor/RootTemplates/_merged.lsf'),
        ('ui', 'Public/DenimDragonArmor/Content/UI/[PAK]_UI/_merged.lsf'),
        ('assets', 'Public/DenimDragonArmor/Content/Assets/[PAK]_LegacyPartyArmory/_merged.lsf')
    ]:
        dest = ROOT / f'build/verify-0319-{mode}-{label}.lsx'
        run('-a', 'convert-resource', '-s', output / relative, '-d', dest)
        decoded[label] = ET.parse(dest)
    rows = json.loads((ROOT / 'assets/icons/catalog.json').read_text(encoding='utf-8'))
    roots = {attr(n, 'MapKey'): n for n in decoded['roots'].findall('.//node[@id="GameObjects"]')}
    descriptor = ET.parse(output / 'Public/DenimDragonArmor/GUI/Icons_LegacyPartyArmory.lsx')
    uv = {attr(n, 'MapKey'): n for n in descriptor.findall('.//node[@id="IconUV"]')}
    assert len(uv) == len(rows) == 18
    assert attr(descriptor.find('.//node[@id="TextureAtlasPath"]'), 'UUID') == ATLAS_ID
    resources = decoded['ui'].findall('.//node[@id="Resource"]')
    assert len({attr(n, 'ID') for n in resources}) == len(resources)
    resource = next(n for n in resources if attr(n, 'ID') == ATLAS_ID)
    atlas_path = output / attr(resource, 'SourceFile')
    atlas = Image.open(atlas_path).convert('RGBA')
    assert atlas.size == (512, 256)
    assert attr(resource, 'Width') == '512' and attr(resource, 'Height') == '256'
    config = json.loads((output / 'Mods/DenimDragonArmor/ScriptExtender/Lua/ArmoryData.json').read_text())
    assert config == json.loads((ROOT / f'config/{mode}.json').read_text())
    assert {r['uuid'] for r in rows}.issubset({uid for b in config['bags'].values() for uid in b['items']})
    for index, row in enumerate(rows):
        icon_id = row['icon_id']
        assert attr(roots[row['uuid']], 'Icon') == icon_id
        node = uv[icon_id]
        x, y = (index % 8) * 64, (index // 8) * 64
        for key, value in [('U1', (x+.5)/512), ('U2', (x+63.5)/512),
                           ('V1', (y+.5)/256), ('V2', (y+63.5)/256)]:
            assert abs(float(attr(node, key)) - value) < 1e-8
        master = Image.open(ROOT / 'assets/icons/masters' / (row['key']+'.png')).convert('RGBA')
        expected = fit_icon(master, 64, 2)
        assert atlas.crop((x, y, x+64, y+64)).tobytes() == expected.tobytes(), row['key']
        for size, folder in [(380, 'Tooltips/ItemIcons'), (144, 'ControllerUIIcons/items_png')]:
            image = Image.open(output / f'Public/Game/GUI/Assets/{folder}/{icon_id}.DDS')
            assert image.size == (size, size) and image.getchannel('A').getextrema() == (0, 255)
    lua_path = output / 'Mods/DenimDragonArmor/ScriptExtender/Lua/BootstrapServer.lua'
    assert 'API.Version = "0.3.19"' in lua_path.read_text()
    assert 'Osi.CreateAt' not in lua_path.read_text()
    # Check the compiled model resources, not just the patch's source report.
    from patch_visuals_0316 import CARSOMYR, HALBERD, ROBE, region_mask
    assets = {attr(n, 'ID'): n for n in decoded['assets'].findall('.//node[@id="Resource"]')}
    visual_report = json.loads((output / 'visual-patch-report.json').read_text())
    for key, material_id in [('Carsomyr', CARSOMYR)]:
        material = assets[material_id]
        assert attr(material, 'SourceFile').endswith('/Base_MSK_AlphaTest_VT.lsf')
        parameters = {attr(n, 'ParameterName'): n for n in material.findall('./children/node')}
        assert {f'Color_0{i}' for i in (1, 2, 3)}.issubset(parameters)
        assert not any('Glow' in name for name in parameters)
        mask_id = attr(parameters['MSKcloth'], 'ID')
        assert mask_id == visual_report['weapons'][key]['mask']
        texture = assets[mask_id]
        assert attr(texture, 'SRGB') == 'False'
        actual = Image.open(output / attr(texture, 'SourceFile')).convert('RGBA')
        regions = json.loads((ROOT / f'assets/model-patches/{key}-regions.json').read_text())
        assert actual.tobytes() == region_mask(regions).tobytes()
        assert actual.getchannel('R').getbbox()
        if key == 'Carsomyr':
            assert actual.getchannel('G').getbbox()
            assert regions['revision'] == '0.3.19'
            # Check selection on the actual compiled DDS at saved native UV probes.
            for role, points in regions['uv_probes'].items():
                gold = [actual.getpixel((max(0, min(1023, round(u*1023))),
                                         max(0, min(1023, round((1-v)*1023)))))[0] > 127
                        for u, v in points]
                assert gold
                if role in ('blade', 'langet'):
                    assert not any(gold), f'Gold leaked onto {role}'
                else:
                    assert sum(gold)/len(gold) > .98
            old_regions = json.loads((ROOT / 'assets/model-patches/history/0.3.18/Carsomyr-regions.json').read_text())
            assert regions['regions']['G'] == old_regions['regions']['G'], 'Grip selection changed'
    pants_ids = {uid for uid, n in assets.items() if (attr(n, 'Name') or '').startswith('LPA_ViconiaRobe_')
                 and '_Pants' in attr(n, 'Name') and (attr(n, 'SourceFile') or '').endswith('.GR2')}
    races = roots[ROBE].findall('.//node[@id="Visuals"]/children/node[@id="Object"]')
    assert len(races) == len(visual_report['viconia_removed_pants']) > 8
    for race in races:
        remaining = {attr(n, 'Object') for n in race.findall('./children/node[@id="MapValue"]')}
        assert remaining.isdisjoint(pants_ids)
        names = [attr(assets[uid], 'Name') for uid in remaining]
        assert any('_Body_' in name for name in names), names
        assert any('_Skirt' in name for name in names), names
    from weapon_regions_0318 import CLAW, HALBERD, PALETTES, mask as weapon_mask
    from PIL import ImageChops
    weapon_report = json.loads((output / 'weapon-patch-0318-report.json').read_text())
    for key, material_id in [('CharonsClaw', CLAW), ('DragonsBreath', HALBERD)]:
        material = assets[material_id]
        assert attr(material, 'SourceFile').endswith('/Base_MSK_AlphaTest_VT.lsf')
        parameters = {attr(n, 'ParameterName'): n for n in material.findall('./children/node')}
        for index, color in enumerate(PALETTES[key], 1):
            assert attr(parameters[f'Color_0{index}'], 'Value') == color
        assert attr(parameters['MSKcloth'], 'ID') == weapon_report['weapons'][key]['mask']
        assert attr(parameters['virtualtexture'], 'ID') == weapon_report['weapons'][key]['virtualtexture']
        texture = assets[attr(parameters['MSKcloth'], 'ID')]
        assert attr(texture, 'SRGB') == 'False'
        actual = Image.open(output / attr(texture, 'SourceFile')).convert('RGBA')
        data = json.loads((ROOT / f'assets/model-patches/{key}-regions-0318.json').read_text())
        assert actual.tobytes() == weapon_mask(data).tobytes()
        assert actual.size == (2048, 2048)
        red, green, blue, alpha = actual.split()
        for channel in (red, green, blue):
            assert channel.getbbox()
        assert alpha.getextrema() == (255, 255)
        assert ImageChops.add(ImageChops.add(red, green), blue).getextrema() == (255, 255)
        assert ImageChops.multiply(green, blue).getbbox() is None
        assert not any('Glow' in name for name in parameters)
    # Compare gameplay data against the previous release when available locally.
    baseline = ROOT / f'build/verify-0315-{mode}'
    if baseline.exists():
        for file in (output / 'Public/DenimDragonArmor/Stats/Generated/Data').glob('*.txt'):
            assert file.read_bytes() == (baseline / file.relative_to(output)).read_bytes(), file.name
        old_lua = (baseline / lua_path.relative_to(output)).read_text()
        assert lua_path.read_text().replace('0.3.19', '0.3.15') == old_lua
        old_assets_xml = ROOT / f'build/verify-0315-{mode}-assets.lsx'
        if not old_assets_xml.exists():
            run('-a', 'convert-resource', '-s', baseline /
                'Public/DenimDragonArmor/Content/Assets/[PAK]_LegacyPartyArmory/_merged.lsf',
                '-d', old_assets_xml)
        old_assets = {attr(n, 'ID'): n for n in ET.parse(old_assets_xml).findall('.//node[@id="Resource"]')}
        expected_new_masks = {w['mask'] for w in visual_report['weapons'].values()}
        expected_new_masks.update(w['mask'] for w in weapon_report['weapons'].values())
        assert set(assets)-set(old_assets) == expected_new_masks
        assert not set(old_assets)-set(assets)
        for uid in set(old_assets)-{CARSOMYR, CLAW, HALBERD}:
            assert structure(assets[uid]) == structure(old_assets[uid]), attr(assets[uid], 'Name')
        old_roots_xml = ROOT / f'build/verify-0315-{mode}-roots.lsx'
        if not old_roots_xml.exists():
            run('-a', 'convert-resource', '-s', baseline /
                'Public/DenimDragonArmor/RootTemplates/_merged.lsf', '-d', old_roots_xml)
        old_roots = {attr(n, 'MapKey'): n for n in ET.parse(old_roots_xml).findall('.//node[@id="GameObjects"]')}
        assert roots.keys() == old_roots.keys()
        old_robe = old_roots[ROBE]
        for container in old_robe.findall('.//node[@id="Visuals"]/children/node/children'):
            for visual in list(container):
                if attr(visual, 'Object') in pants_ids:
                    container.remove(visual)
        for uid in roots:
            assert structure(roots[uid]) == structure(old_roots[uid]), attr(roots[uid], 'Name')
    report = {'version': '0.3.19', 'mode': mode, 'icons': 18, 'tooltip_dds': 18,
              'controller_dds': 18, 'atlas': [512, 256], 'stats_match_previous_release': baseline.exists(),
              'weapon_materials_verified': 3, 'weapon_uv_masks_verified': True, 'robe_variants_without_trousers': len(races),
              'sha256': hashlib.sha256(pak.read_bytes()).hexdigest(), 'game_test': False}
    previous_assets_xml = ROOT / f'build/verify-0318-{mode}-assets.lsx'
    if previous_assets_xml.exists():
        previous_assets = {attr(n, 'ID'): n for n in ET.parse(previous_assets_xml).findall('.//node[@id="Resource"]')}
        assert previous_assets.keys() == assets.keys()
        for uid in assets:
            assert structure(assets[uid]) == structure(previous_assets[uid]), attr(assets[uid], 'Name')
        previous_output = ROOT / f'build/verify-0318-{mode}'
        carsomyr_mask = visual_report['weapons']['Carsomyr']['texture']
        previous_atlas = Image.open(previous_output / attr(resource, 'SourceFile')).convert('RGBA')
        for index, row in enumerate(rows):
            if row['key'] == 'Carsomyr':
                continue
            x, y = (index % 8)*64, (index // 8)*64
            assert atlas.crop((x, y, x+64, y+64)).tobytes() == previous_atlas.crop((x, y, x+64, y+64)).tobytes()
        # All equipment textures except Carsomyr's selection mask stay byte-identical.
        for file in (output / 'Public/DenimDragonArmor/Assets/Textures').glob('*.dds'):
            if file.relative_to(output).as_posix() != carsomyr_mask:
                assert file.read_bytes() == (previous_output / file.relative_to(output)).read_bytes(), file.name
        report['other_items_match_0318'] = True
    report['carsomyr_no_gold_on_blade'] = True
    (ROOT / f'build/verify-0319-{mode}-report.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    # Run the runtime tests using the actual server script inside the new PAK.
    import unittest
    sys.path.insert(0, str(ROOT / 'tests'))
    import test_delivery
    test_delivery.LUA = lua_path
    assert unittest.TextTestRunner(verbosity=0).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(test_delivery.Delivery)).wasSuccessful()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--divine', type=Path, required=True)
    parser.add_argument('--mode', choices=['preview', 'final'], required=True)
    args = parser.parse_args()
    verify(args.divine.resolve(), args.mode)
