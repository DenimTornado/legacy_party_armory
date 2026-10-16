"""Private visual fixes. Region masks are numerical UV selections, not repainted art.

Region JSONs can be regenerated from Divine's native GR2 -> Collada exports.
Only UV triangles and source hashes are retained; no native mesh is distributed.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import uuid
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFilter
from build_icons import attribute, write_xml

MODULE = uuid.UUID('5d96794a-b84b-4bf7-afaa-74063318d3a6')
ASSETS = 'Public/DenimDragonArmor/Content/Assets/[PAK]_LegacyPartyArmory/_merged.lsx'
ROOTS = 'Public/DenimDragonArmor/RootTemplates/_merged.lsx'
CARSOMYR = 'ba046cd2-af79-5587-92af-9376a2692975'
HALBERD = '6cb890e6-b682-50cf-b143-7ebe051822b7'
ROBE = '2cdc4e25-fea0-55fd-b430-e133558addf2'


def attr(node, key):
    value = node.find(f'attribute[@id="{key}"]')
    return value.get('value') if value is not None else None


def export_regions(mesh_path, key, destination):
    ns = {'c': 'http://www.collada.org/2005/11/COLLADASchema'}
    mesh = ET.parse(mesh_path).find('.//c:geometry/c:mesh', ns)
    sources = {}
    for source in mesh.findall('c:source', ns):
        numbers = list(map(float, source.find('c:float_array', ns).text.split()))
        stride = int(source.find('c:technique_common/c:accessor', ns).get('stride'))
        sources[source.get('id')] = [numbers[i:i+stride] for i in range(0, len(numbers), stride)]
    triangles = mesh.find('c:triangles', ns)
    inputs = {n.get('semantic'): (int(n.get('offset')), n.get('source')[1:])
              for n in triangles.findall('c:input', ns)}
    # Divine exports VERTEX directly against its position source.
    vertex = inputs['VERTEX']
    uv = inputs['TEXCOORD']
    stride = max(i[0] for i in inputs.values())+1
    indices = list(map(int, triangles.find('c:p', ns).text.split()))
    regions = {'R': [], 'G': []}
    for offset in range(0, len(indices), stride*3):
        rows = [indices[offset+i*stride:offset+(i+1)*stride] for i in range(3)]
        positions = [sources[vertex[1]][row[vertex[0]]] for row in rows]
        center = [sum(p[k] for p in positions)/3 for k in range(3)]
        x, _, z = center
        channel = None
        if key == 'Carsomyr':
            # Red grip; gold crossguard, langets/blade protection and pommel.
            if -.058 < z < .24 and abs(x) < .035:
                channel = 'G'
            elif z > -.48:
                channel = 'R'
        elif key == 'DragonsBreath' and (z < -1.03 or z > .40):
            channel = 'R'
        if channel:
            regions[channel].append([[round(v, 7) for v in sources[uv[1]][row[uv[0]]][:2]]
                                     for row in rows])
    data = {'key': key, 'source_sha256': hashlib.sha256(mesh_path.read_bytes()).hexdigest(),
            'description': ('R=gold guard, langets and pommel; G=red grip; black=original steel'
                            if key == 'Carsomyr' else
                            'R=reddish metal head/spike and butt cap; black=original shaft'),
            'triangles': len(indices)//(stride*3), 'regions': regions}
    assert len(regions['R']) > 50
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(data, separators=(',', ':'))+'\n')
    print(key, {k: len(v) for k, v in regions.items()})


def region_mask(data):
    channels = []
    for name in ('R', 'G', 'B'):
        mask = Image.new('L', (1024, 1024))
        draw = ImageDraw.Draw(mask)
        for coords in data['regions'].get(name, []):
            draw.polygon([(u*1023, (1-v)*1023) for u, v in coords], fill=255)
        channels.append(mask.filter(ImageFilter.MaxFilter(5)))
    return Image.merge('RGBA', (*channels, Image.new('L', (1024, 1024), 255)))


def parameter(children, node_type, name, value, kind='float'):
    node = ET.SubElement(children, 'node', id=node_type)
    for key, val, typ in [('Enabled', 'True', 'bool'), ('ExportAsPreset', 'True', 'bool'),
                          ('GroupName', '', 'FixedString'), ('ParameterName', name, 'FixedString')]:
        attribute(node, key, val, typ)
    if node_type in ('Texture2DParameters', 'VirtualTextureParameters'):
        attribute(node, 'ID', value)
        if node_type == 'VirtualTextureParameters':
            attribute(node, 'Index', 0, 'int32')
    else:
        attribute(node, 'Value', value, kind)
        attribute(node, 'BaseValue', value, kind)
        if node_type == 'Vector3Parameters':
            attribute(node, 'IsColor', 'True', 'bool')


def patch(project, stage):
    tree = ET.parse(stage / ASSETS)
    resources = {attr(n, 'ID'): n for n in tree.findall('.//node[@id="Resource"]')}
    texture_bank = tree.find('./region[@id="TextureBank"]/node/children')
    report = {'version': '0.3.17', 'weapons': {}, 'dragons_breath': 'restored to pre-0.3.16 material'}
    for key, material_id, colors, vt in [
        ('Carsomyr', CARSOMYR, ('1 0.58 0.12', '0.8 0.018 0.008', '1 1 1'),
         '527a405b-810a-3890-2a05-944597d5bff6')
    ]:
        data = json.loads((project / f'assets/model-patches/{key}-regions.json').read_text())
        mask_id = str(uuid.uuid5(MODULE, f'armory:visual0316:{key}:mask'))
        relative = f'Public/DenimDragonArmor/Assets/Textures/{key}_regions_0316.dds'
        path = stage / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        region_mask(data).save(path, format='DDS')
        resource = copy.deepcopy(resources['bf36d010-4bfa-5758-939b-369eb95dbb55'])
        attribute(resource, 'ID', mask_id)
        attribute(resource, 'Name', 'LPA_'+key+'_regions_0316', 'LSString')
        attribute(resource, 'Template', 'LPA_'+key+'_regions_0316')
        attribute(resource, 'SourceFile', relative, 'LSString')
        texture_bank.append(resource)
        material = resources[material_id]
        # RGB masks select independently tintable regions. Native virtual textures
        # still provide albedo, normals, roughness and metallic response.
        attribute(material, 'SourceFile',
                  'Public/Shared/Assets/Materials/Base/Base_MSK_AlphaTest_VT.lsf', 'LSString')
        material.remove(material.find('children'))
        children = ET.SubElement(material, 'children')
        parameter(children, 'ScalarParameters', 'SeeThroughEnabled', '0')
        parameter(children, 'ScalarParameters', 'Reflectance', '0.6')
        for index, color in enumerate(colors, 1):
            parameter(children, 'Vector3Parameters', f'Color_0{index}', color, 'fvec3')
        parameter(children, 'Texture2DParameters', 'MSKcloth', mask_id)
        parameter(children, 'VirtualTextureParameters', 'virtualtexture', vt)
        report['weapons'][key] = {'material': material_id, 'mask': mask_id, 'texture': relative,
                                 'colors': colors, 'selected_triangles':
                                 {k: len(v) for k, v in data['regions'].items()}}
    pants = {uid for uid, n in resources.items()
             if attr(n, 'Name') and attr(n, 'Name').startswith('LPA_ViconiaRobe_')
             and '_Pants' in attr(n, 'Name') and attr(n, 'SourceFile').endswith('.GR2')}
    roots = ET.parse(stage / ROOTS)
    robe = next(n for n in roots.findall('.//node[@id="GameObjects"]') if attr(n, 'MapKey') == ROBE)
    races = robe.findall('.//node[@id="Visuals"]/children/node[@id="Object"]')
    removed = []
    for race in races:
        children = race.find('children')
        for visual in list(children):
            if attr(visual, 'Object') in pants:
                removed.append({'race': attr(race, 'MapKey'), 'visual': attr(visual, 'Object')})
                children.remove(visual)
        assert len(children) >= 2, 'Body/skirt must remain on every supported race'
    assert len(removed) == len(races) > 8, 'Exactly one trouser visual per race must be removed'
    report['viconia_removed_pants'] = removed
    write_xml(tree.getroot(), stage / ASSETS)
    write_xml(roots.getroot(), stage / ROOTS)
    (stage / 'visual-patch-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Visual fixes: Carsomyr; halberd unchanged; Viconia trousers removed:', len(removed))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--stage-root', type=Path)
    parser.add_argument('--carsomyr-dae', type=Path)
    parser.add_argument('--halberd-dae', type=Path)
    args = parser.parse_args()
    for key, mesh in [('Carsomyr', args.carsomyr_dae), ('DragonsBreath', args.halberd_dae)]:
        if mesh:
            export_regions(mesh, key, args.project_root / f'assets/model-patches/{key}-regions.json')
    if args.stage_root:
        patch(args.project_root, args.stage_root)
