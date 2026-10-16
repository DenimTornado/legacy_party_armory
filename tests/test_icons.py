from pathlib import Path
import json
import tempfile
import unittest
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'authoring'))
from build_icons import fit_icon


class EquipmentIcons(unittest.TestCase):
    def test_every_active_custom_item_has_one_master(self):
        rows = json.loads((ROOT / 'assets/icons/catalog.json').read_text())
        active = {uid for bag in json.loads((ROOT / 'config/final.json').read_text())['bags'].values()
                  for uid in bag['items']}
        self.assertEqual(active, {row['uuid'] for row in rows})
        self.assertEqual(18, len(rows))
        self.assertEqual(18, len({row['key'] for row in rows}))
        for row in rows:
            with self.subTest(item=row['key']):
                image = Image.open(ROOT / 'assets/icons/masters' / (row['key'] + '.png'))
                self.assertEqual('RGBA', image.mode)
                self.assertGreaterEqual(min(image.size), 512)
                alpha_min, alpha_max = image.getchannel('A').getextrema()
                self.assertEqual(0, alpha_min)
                self.assertGreaterEqual(alpha_max, 250)

    def test_tiles_have_transparent_gutter_and_no_clipping(self):
        rows = json.loads((ROOT / 'assets/icons/catalog.json').read_text())
        for row in rows:
            with self.subTest(item=row['key']):
                master = Image.open(ROOT / 'assets/icons/masters' / (row['key'] + '.png')).convert('RGBA')
                tile = fit_icon(master, 64, 2)
                box = tile.getchannel('A').getbbox()
                self.assertTrue(box)
                self.assertGreaterEqual(box[0], 2)
                self.assertGreaterEqual(box[1], 2)
                self.assertLessEqual(box[2], 62)
                self.assertLessEqual(box[3], 62)
                # DDS round-trip preserves the alpha and tiny icon dimensions.
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / 'icon.dds'
                    tile.save(path, format='DDS')
                    decoded = Image.open(path)
                    self.assertEqual((64, 64), decoded.size)
                    self.assertEqual(tile.tobytes(), decoded.tobytes())


if __name__ == '__main__':
    unittest.main()
