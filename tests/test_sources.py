from pathlib import Path
import json
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'


class SourceSnapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configs = {mode: json.loads((ROOT / 'config' / f'{mode}.json').read_text(encoding='utf-8')) for mode in ['preview', 'final']}
        cls.stats = {}
        for file in (SRC / 'Public/DenimDragonArmor/Stats/Generated/Data').glob('*.txt'):
            for block in file.read_text(encoding='utf-8').split('new entry ')[1:]:
                key = re.match(r'"([^"]+)"', block)[1]
                if key in cls.stats:
                    raise AssertionError('Duplicate stats definition: ' + key)
                cls.stats[key] = dict(re.findall(r'data "([^"]+)" "([^"]*)"', block))
        template = ET.parse(SRC / 'Public/DenimDragonArmor/RootTemplates/_merged.lsx')
        cls.templates = {n.find('attribute[@id="MapKey"]').get('value'): n for n in template.findall('.//node[@id="GameObjects"]')}

    def test_bag_structure_and_counts(self):
        for mode, count in [('preview', 30), ('final', 25)]:
            bags = self.configs[mode]['bags']
            self.assertEqual(7, len(bags))
            self.assertEqual(count, sum(1 + len(v['items']) for v in bags.values()))
            self.assertEqual(['paladin', 'wyll', 'karlach', 'minthara', 'jaheira', 'shadowheart'], bags['outer']['children'])
            self.assertEqual([], bags['shadowheart']['children'])
            self.assertNotIn('shar', bags)
            for bag in bags.values():
                self.assertIn(bag['uuid'], self.templates)
                self.assertTrue(all(child in bags for child in bag['children']))

    def test_all_custom_equipment_is_legendary(self):
        equipment = [v for v in self.stats.values() if v.get('RootTemplate') and v.get('Rarity')]
        self.assertEqual(16, len(equipment))
        self.assertTrue(all(v['Rarity'] == 'Legendary' for v in equipment))
        self.assertFalse(any(k.startswith(('MAG_', 'WPN_', 'ARM_', 'OBJ_')) for k in self.stats))

    def test_stable_dragon_ids_and_armour_balance(self):
        self.assertEqual('a22abf50-a0a1-47ad-9bd0-5866e72d9d95', self.stats['DENIM_RedDragon_Armor']['RootTemplate'])
        self.assertEqual('16', self.stats['DENIM_RedDragon_Armor']['ArmorClass'])
        self.assertEqual('None', self.stats['DENIM_RedDragon_Helmet']['ArmorType'])

    def test_current_model_choices(self):
        evidence = json.loads((ROOT / 'verification/manifest_preview.json').read_text(encoding='utf-8'))
        items = {i['key']: i for i in evidence['custom']}
        self.assertEqual('f01c3f5d-c542-420f-86c5-bdddf7819e29', items['Carsomyr']['base_uuid'])
        self.assertEqual('WPN_Halberd_2', items['DragonsBreath']['parent'])
        self.assertEqual('c0c0534c-b7fc-4d0b-a335-b8f4c548852d', items['HarperFinery']['base_uuid'])
        self.assertEqual('13', self.stats['LPA_HarperFinery']['ArmorClass'])

    def test_localization_handles(self):
        for language in ['English', 'Russian']:
            strings = {n.get('contentuid'): n.text for n in ET.parse(SRC / f'Localization/{language}/DenimDragonArmor.xml').findall('content')}
            for definition in self.stats.values():
                for field in ['DisplayName', 'Description']:
                    if definition.get(field):
                        self.assertIn(definition[field].split(';')[0], strings)

    def test_resource_compilation_manifest(self):
        files = json.loads((ROOT / 'config/resource-files.json').read_text(encoding='utf-8'))
        self.assertEqual(5, len(files))
        for file in files:
            self.assertTrue((SRC / file).is_file())
            self.assertNotIn('..', Path(file).parts)
        self.assertFalse(list(SRC.rglob('*.lsf')))
        self.assertFalse(list(SRC.rglob('*.loca')))

    def test_native_glow_materials(self):
        file = SRC / 'Public/DenimDragonArmor/Content/Assets/[PAK]_LegacyPartyArmory/_merged.lsx'
        materials = ET.parse(file).findall('./region[@id="MaterialBank"]/node/children/node')
        for key in ['Twinkle', 'Icingdeath', 'CharonsClaw']:
            material = next(n for n in materials if n.find('attribute[@id="Name"]').get('value').startswith('LPA_' + key + '_'))
            self.assertTrue(material.find('attribute[@id="SourceFile"]').get('value').endswith('/Base_GM_VT.lsf'))
            parameters = {n.find('attribute[@id="ParameterName"]').get('value'): n for n in material.findall('children/node') if n.find('attribute[@id="ParameterName"]') is not None}
            self.assertGreaterEqual(float(parameters['GlowMultiplier'].find('attribute[@id="Value"]').get('value')), 3)
            self.assertIsNotNone(parameters['Glowmap'].find('attribute[@id="ID"]'))

    def test_manual_only_runtime_present(self):
        lua = (SRC / 'Mods/DenimDragonArmor/ScriptExtender/Lua/BootstrapServer.lua').read_text(encoding='utf-8')
        self.assertIn('function API.Give(character)', lua)
        self.assertIn('Shout_LPA_Armory', lua)
        self.assertIn('pcall(Osi.IsInInventoryOf,uuid,parent)', lua)
        self.assertIn('pcall(Osi.TemplateAddTo,entry.template,parent,1,0)', lua)
        self.assertNotIn('Osi.CreateAt', lua)
        self.assertNotIn('Osi.ToInventory', lua)
        self.assertNotIn('DeliveredReleaseItems', lua)
        self.assertFalse(list(SRC.glob('Mods/*/Story/**/*')))


if __name__ == '__main__':
    unittest.main()
