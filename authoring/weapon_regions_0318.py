"""Model-derived UV regions for Charon's Claw and Dragon's Breath.

Keep native GR2 and virtual textures; override only the private material bank.
Selections include wrapped UV islands and explicitly cover the whole surface.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import math
import uuid
import xml.etree.ElementTree as ET
from collections import defaultdict
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from build_icons import attribute, write_xml
from patch_visuals_0316 import ASSETS, MODULE, attr, parameter

CLAW = '342d382f-39f5-56b5-9ad6-d196d81f5944'
HALBERD = '6cb890e6-b682-50cf-b143-7ebe051822b7'
NS = {'c': 'http://www.collada.org/2005/11/COLLADASchema'}
PALETTES = {
    'CharonsClaw': ('0.19 0.22 0.27', '0.65 0.014 0.009', '0.43 0.51 0.62'),
    'DragonsBreath': ('0.48 0.018 0.025', '0.78 0.73 0.66', '0.62 0.39 0.19'),
}
MATERIALS = {'CharonsClaw': CLAW, 'DragonsBreath': HALBERD}


def read_mesh(path):
    mesh = ET.parse(path).find('.//c:geometry/c:mesh', NS)
    sources = {}
    for source in mesh.findall('c:source', NS):
        numbers = list(map(float, source.find('c:float_array', NS).text.split()))
        stride = int(source.find('c:technique_common/c:accessor', NS).get('stride'))
        sources[source.get('id')] = [numbers[i:i+stride] for i in range(0, len(numbers), stride)]
    tris = mesh.find('c:triangles', NS)
    inputs = {n.get('semantic'): (int(n.get('offset')), n.get('source')[1:])
              for n in tris.findall('c:input', NS)}
    stride = max(i[0] for i in inputs.values())+1
    values = list(map(int, tris.find('c:p', NS).text.split()))
    result = []
    for offset in range(0, len(values), stride*3):
        rows = [values[offset+i*stride:offset+(i+1)*stride] for i in range(3)]
        # Each vertex stores x/y/z/u/v so clipping interpolates UV exactly.
        result.append([sources[inputs['VERTEX'][1]][r[inputs['VERTEX'][0]]][:3] +
                       sources[inputs['TEXCOORD'][1]][r[inputs['TEXCOORD'][0]]][:2]
                       for r in rows])
    return result


def clip(poly, axis, limit, sign):
    """Sutherland-Hodgman clipping in model space, interpolating UV coordinates."""
    result = []
    for index, end in enumerate(poly):
        start = poly[index-1]
        da, db = sign*(start[axis]-limit), sign*(end[axis]-limit)
        if (da >= 0) != (db >= 0):
            t = da/(da-db)
            result.append([a+(b-a)*t for a, b in zip(start, end)])
        if db >= 0:
            result.append(end)
    return result


def components(triangles):
    parent = list(range(len(triangles)))
    owners = {}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for index, triangle in enumerate(triangles):
        for vertex in triangle:
            position = tuple(round(v, 5) for v in vertex[:3])
            if position in owners:
                parent[find(index)] = find(owners[position])
            else:
                owners[position] = index
    groups = defaultdict(list)
    for index in range(len(triangles)):
        groups[find(index)].append(index)
    return list(groups.values())


def export(path, key, destination):
    triangles = read_mesh(path)
    regions = {'G': [], 'B': []}  # R is the explicit remainder, never implicit shader fallback.
    def save(channel, polygon):
        if len(polygon) >= 3:
            regions[channel].append([[round(p[3], 7), round(p[4], 7)] for p in polygon])
    if key == 'CharonsClaw':
        for group in components(triangles):
            verts = [v for i in group for v in triangles[i]]
            zmin, zmax = min(v[2] for v in verts), max(v[2] for v in verts)
            is_blade = zmin < -1.3
            # Whole native guard/collar/pommel components; the long grip stays dark.
            if zmax-zmin < .1:
                for i in group:
                    save('B', triangles[i])
            if is_blade:
                for i in group:
                    # Clip wide blade polygons into a narrow 7mm central red vein.
                    stripe = clip(clip(triangles[i], 0, -.0035, 1), 0, .0035, -1)
                    save('G', stripe)
    else:
        groups = components(triangles)
        pole = max(groups, key=len)
        pole_set = set(pole)
        steel = set()
        for group in groups:
            verts = [v for i in group for v in triangles[i]]
            xmin, xmax = min(v[0] for v in verts), max(v[0] for v in verts)
            zmin, zmax = min(v[2] for v in verts), max(v[2] for v in verts)
            # Large axe plate, top spear and rear hook. Small relief details bronze.
            if group != pole and (zmin < -1.9 or (xmin < -.3 and zmax > -1.1) or xmax > .3):
                steel.update(group)
        assert len(steel) > 400
        for i, tri in enumerate(triangles):
            _, _, z = [sum(p[k] for p in tri)/3 for k in range(3)]
            if i in steel:
                save('G', tri)
            elif i not in pole_set:
                save('B', tri)
            else:
                # Long shaft triangles cross the cap boundary: clip instead of
                # coloring the entire triangle from its midpoint.
                save('G', clip(tri, 2, .465, 1))
                save('B', clip(tri, 2, -1.0, -1))
                save('B', clip(clip(tri, 2, .39, 1), 2, .465, -1))
                if max(abs(p[0]) for p in tri) > .025:
                    save('B', tri)
    assert regions['G'] and regions['B']
    data = {'key': key, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'triangles': len(triangles), 'uv_addressing': 'wrap', 'colors': PALETTES[key],
            'regions': regions}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(data, separators=(',', ':'))+'\n')
    print(key, {k: len(v) for k, v in regions.items()})


def mask(data):
    layers = []
    for name in ('G', 'B'):
        image = Image.new('L', (2048, 2048))
        draw = ImageDraw.Draw(image)
        for polygon in data['regions'][name]:
            # Never modulo vertices separately: that stretches seam-crossing triangles.
            for u_tile in range(math.floor(min(p[0] for p in polygon)),
                                math.floor(max(p[0] for p in polygon))+1):
                for v_tile in range(math.floor(min(p[1] for p in polygon)),
                                    math.floor(max(p[1] for p in polygon))+1):
                    draw.polygon([((u-u_tile)*2047, (1-(v-v_tile))*2047)
                                  for u, v in polygon], fill=255)
        layers.append(image.filter(ImageFilter.MaxFilter(3)))
    green, blue = layers
    # Preserve discrete regions at padded UV-island edges. G vein/blade has priority.
    blue = ImageChops.subtract(blue, green)
    red = ImageChops.invert(ImageChops.lighter(green, blue))
    return Image.merge('RGBA', (red, green, blue, Image.new('L', red.size, 255)))


def patch(project, stage):
    tree = ET.parse(stage / ASSETS)
    resources = {attr(n, 'ID'): n for n in tree.findall('.//node[@id="Resource"]')}
    textures = tree.find('./region[@id="TextureBank"]/node/children')
    report = {'version': '0.3.18', 'weapons': {}}
    for key, material_id in MATERIALS.items():
        material = resources[material_id]
        old_vt = material.find('./children/node[@id="VirtualTextureParameters"]')
        vt = attr(old_vt, 'ID')
        data = json.loads((project / f'assets/model-patches/{key}-regions-0318.json').read_text())
        image = mask(data)
        mask_id = str(uuid.uuid5(MODULE, f'armory:visual0318:{key}:mask'))
        relative = f'Public/DenimDragonArmor/Assets/Textures/{key}_regions_0318.dds'
        image.save(stage / relative, format='DDS')
        texture = copy.deepcopy(resources['bf36d010-4bfa-5758-939b-369eb95dbb55'])
        for name, value, kind in [('ID', mask_id, 'FixedString'), ('Name', f'LPA_{key}_regions_0318', 'LSString'),
                                  ('Template', f'LPA_{key}_regions_0318', 'FixedString'),
                                  ('SourceFile', relative, 'LSString'), ('Width', 2048, 'int32'),
                                  ('Height', 2048, 'int32')]:
            attribute(texture, name, value, kind)
        textures.append(texture)
        attribute(material, 'SourceFile', 'Public/Shared/Assets/Materials/Base/Base_MSK_AlphaTest_VT.lsf', 'LSString')
        material.remove(material.find('children'))
        children = ET.SubElement(material, 'children')
        parameter(children, 'ScalarParameters', 'SeeThroughEnabled', '0')
        parameter(children, 'ScalarParameters', 'Reflectance', '0.6')
        for index, color in enumerate(PALETTES[key], 1):
            parameter(children, 'Vector3Parameters', f'Color_0{index}', color, 'fvec3')
        parameter(children, 'Texture2DParameters', 'MSKcloth', mask_id)
        parameter(children, 'VirtualTextureParameters', 'virtualtexture', vt)
        report['weapons'][key] = {'material': material_id, 'mask': mask_id, 'texture': relative,
                                 'virtualtexture': vt, 'colors': PALETTES[key], 'mask_size': list(image.size)}
    write_xml(tree.getroot(), stage / ASSETS)
    (stage / 'weapon-patch-0318-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Applied 0.3.18 weapon region materials: Claw and Halberd')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--stage-root', type=Path)
    parser.add_argument('--claw-dae', type=Path)
    parser.add_argument('--halberd-dae', type=Path)
    args = parser.parse_args()
    for key, path in [('CharonsClaw', args.claw_dae), ('DragonsBreath', args.halberd_dae)]:
        if path:
            export(path, key, args.project_root / f'assets/model-patches/{key}-regions-0318.json')
    if args.stage_root:
        patch(args.project_root, args.stage_root)
