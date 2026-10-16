"""Select Carsomyr's lateral guard quillons without gilding its blade/langets."""
from pathlib import Path
import argparse
import hashlib
import json
from weapon_regions_0318 import clip, read_mesh
from patch_visuals_0316 import region_mask


def export(mesh, previous, output):
    triangles = read_mesh(mesh)
    old = json.loads(previous.read_text())
    gold = []
    def save(polygon):
        if len(polygon) >= 3:
            gold.append([[round(p[3], 7), round(p[4], 7)] for p in polygon])
    for tri in triangles:
        # Keep the long central blade protection steel. Lateral quillons start
        # outside the central 11cm and are confined to the crossguard's depth.
        near_guard = clip(tri, 2, -.20, 1)
        save(clip(near_guard, 0, .055, 1))
        save(clip(near_guard, 0, -.055, -1))
        # The central cylindrical ferrule between quillons is part of the gold
        # guard assembly. End this band before the longitudinal blade protection.
        collar = clip(clip(tri, 2, -.16, 1), 2, -.058, -1)
        save(clip(clip(collar, 0, -.055, 1), 0, .055, -1))
        # Preserve the previously approved golden pommel, independently of blade.
        save(clip(tri, 2, .245, 1))
    data = {'key': 'Carsomyr', 'revision': '0.3.19',
            'source_sha256': hashlib.sha256(mesh.read_bytes()).hexdigest(),
            'description': 'R=gold quillons, central ferrule and pommel; G=unchanged red grip; black=original steel blade/langets',
            'triangles': len(triangles), 'regions': {'R': gold, 'G': old['regions']['G']}}
    image = region_mask(data)
    probes = {'blade': [], 'langet': [], 'quillon': [], 'collar': []}
    for tri in triangles:
        x, y, z, u, v = [sum(p[k] for p in tri)/3 for k in range(5)]
        role = ('langet' if -.45 < z < -.20 and abs(x) < .025 else
                'blade' if z < -.55 else
                'quillon' if z > -.20 and abs(x) > .09 else
                'collar' if -.135 < z < -.068 and abs(x) < .035 else None)
        if role:
            probes[role].append([round(u, 7), round(v, 7)])
    validation = {}
    for role, coords in probes.items():
        samples = [image.getpixel((max(0, min(1023, round(u*1023))),
                                  max(0, min(1023, round((1-v)*1023)))))[0] > 127
                   for u, v in coords]
        validation[role] = {'samples': len(samples), 'gold': sum(samples)}
        assert samples
        if role in ('blade', 'langet'):
            assert sum(samples) == 0, (role, validation[role])
        else:
            assert sum(samples)/len(samples) > .98, validation[role]
    data['uv_probes'] = probes
    data['validation'] = validation
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, separators=(',', ':'))+'\n')
    print(json.dumps(validation, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mesh', type=Path, required=True)
    parser.add_argument('--previous', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    export(args.mesh, args.previous, args.output)
