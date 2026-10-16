"""Compile approved PNG masters into BG3 icons, without editing item mechanics.

Requires Pillow. All output is confined to the supplied build staging directory.
"""
from pathlib import Path
import argparse
import copy
import json
import uuid
import xml.etree.ElementTree as ET

from PIL import Image

MODULE = uuid.UUID('5d96794a-b84b-4bf7-afaa-74063318d3a6')
ATLAS_ID = str(uuid.uuid5(MODULE, 'armory:icons:atlas:v1'))
MOD = 'DenimDragonArmor'


def attribute(node, key, value, kind='FixedString'):
    old = node.find(f'attribute[@id="{key}"]')
    if old is None:
        old = ET.SubElement(node, 'attribute', id=key, type=kind)
    old.set('value', str(value))
    return old


def write_xml(root, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space='\t')
    ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)


def fit_icon(master, size, margin):
    bbox = master.getchannel('A').getbbox()
    if bbox is None:
        raise ValueError('Empty icon master')
    subject = master.crop(bbox)
    subject.thumbnail((size - margin * 2, size - margin * 2), Image.Resampling.LANCZOS)
    result = Image.new('RGBA', (size, size))
    result.alpha_composite(subject, ((size - subject.width) // 2, (size - subject.height) // 2))
    return result


def build(project, stage):
    rows = json.loads((project / 'assets/icons/catalog.json').read_text(encoding='utf-8'))
    active = {uid for bag in json.loads((project / 'config/final.json').read_text())['bags'].values()
              for uid in bag['items']}
    if active != {row['uuid'] for row in rows}:
        raise ValueError('Icon catalog must cover exactly the active custom equipment')
    if len(rows) != len({row['key'] for row in rows}):
        raise ValueError('Duplicate icon key')

    template_path = stage / f'Public/{MOD}/RootTemplates/_merged.lsx'
    templates = ET.parse(template_path)
    roots = {n.find('attribute[@id="MapKey"]').get('value'): n
             for n in templates.findall('.//node[@id="GameObjects"]')}
    atlas = Image.new('RGBA', (512, 256))
    gui = ET.Element('save')
    ET.SubElement(gui, 'version', major='4', minor='0', revision='9', build='310')
    info = ET.SubElement(ET.SubElement(ET.SubElement(gui, 'region', id='TextureAtlasInfo'),
                                     'node', id='root'), 'children')
    for name, values in [
        ('TextureAtlasIconSize', {'Height': ('64', 'int32'), 'Width': ('64', 'int32')}),
        ('TextureAtlasPath', {'Path': ('Assets/Textures/Icons/LegacyPartyArmory_Icons.dds', 'string'),
                              'UUID': (ATLAS_ID, 'FixedString')}),
        ('TextureAtlasTextureSize', {'Height': ('256', 'int32'), 'Width': ('512', 'int32')})
    ]:
        n = ET.SubElement(info, 'node', id=name)
        for key, (value, kind) in values.items():
            attribute(n, key, value, kind)
    uv_list = ET.SubElement(ET.SubElement(ET.SubElement(gui, 'region', id='IconUVList'),
                                        'node', id='root'), 'children')
    compiled = []
    for index, row in enumerate(rows):
        icon_id = 'LPA_ICON_' + row['key']
        master = Image.open(project / 'assets/icons/masters' / (row['key'] + '.png')).convert('RGBA')
        alpha = master.getchannel('A')
        # Generated cutouts can peak at 254 after alpha encoding. Preserve that
        # alpha instead of repainting the master just to force an exact 255.
        alpha_min, alpha_max = alpha.getextrema()
        if alpha_min != 0 or alpha_max < 250:
            raise ValueError('Master requires transparent background and opaque subject: ' + row['key'])
        tile = fit_icon(master, 64, 2)
        x, y = (index % 8) * 64, (index // 8) * 64
        atlas.alpha_composite(tile, (x, y))
        uv = ET.SubElement(uv_list, 'node', id='IconUV')
        attribute(uv, 'MapKey', icon_id)
        for key, value in [('U1', (x + .5) / 512), ('U2', (x + 63.5) / 512),
                           ('V1', (y + .5) / 256), ('V2', (y + 63.5) / 256)]:
            attribute(uv, key, value, 'float')
        attribute(roots[row['uuid']], 'Icon', icon_id)
        for size, folder in [(380, 'Tooltips/ItemIcons'), (144, 'ControllerUIIcons/items_png')]:
            image = fit_icon(master, size, max(4, round(size * .035)))
            if size == 380:
                # BG3 tooltip presentation fades only the lowermost edge.
                channel = image.getchannel('A')
                fade = Image.new('L', (size, size), 255)
                pixels = fade.load()
                for yy in range(size - 24, size):
                    for xx in range(size):
                        pixels[xx, yy] = round(255 * (size - 1 - yy) / 23)
                from PIL import ImageChops
                image.putalpha(ImageChops.multiply(channel, fade))
            path = stage / f'Public/Game/GUI/Assets/{folder}/{icon_id}.DDS'
            path.parent.mkdir(parents=True, exist_ok=True)
            image.save(path, format='DDS')
        compiled.append(dict(row, icon_id=icon_id, cell=[x, y, 64, 64]))

    atlas_path = stage / f'Public/{MOD}/Assets/Textures/Icons/LegacyPartyArmory_Icons.dds'
    atlas_path.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(atlas_path, format='DDS')
    write_xml(gui, stage / f'Public/{MOD}/GUI/Icons_LegacyPartyArmory.lsx')
    write_xml(templates.getroot(), template_path)

    bank_path = stage / f'Public/{MOD}/Content/UI/[PAK]_UI/_merged.lsx'
    bank = ET.parse(bank_path)
    children = bank.find('.//region[@id="TextureBank"]/node/children')
    resource = copy.deepcopy(children.find('node'))
    for key, value in {'Height': 256, 'Width': 512, 'ID': ATLAS_ID,
                       'Name': 'LegacyPartyArmory_Icons',
                       'SourceFile': f'Public/{MOD}/Assets/Textures/Icons/LegacyPartyArmory_Icons.dds'}.items():
        attribute(resource, key, value)
    for old in list(children):
        aid = old.find('attribute[@id="ID"]')
        if aid is not None and aid.get('value') == ATLAS_ID:
            children.remove(old)
    children.append(resource)
    write_xml(bank.getroot(), bank_path)
    (stage / 'icon-build-report.json').write_text(json.dumps(compiled, indent=2), encoding='utf-8')
    print(f'Built {len(compiled)} private equipment icons, 512x256 atlas, 380px/144px DDS variants.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--stage-root', type=Path, required=True)
    args = parser.parse_args()
    build(args.project_root.resolve(), args.stage_root.resolve())
