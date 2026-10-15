from pathlib import Path
import sys,subprocess,hashlib,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
import build as dragon
from armory_spec import *
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normalized(n):
 return (n.tag,tuple(sorted(n.attrib.items())),(n.text or '').strip(),tuple(normalized(c) for c in n))
def roots(path):
 return {n.find('attribute[@id="MapKey"]').get('value'):n for n in E.parse(path).findall('.//node[@id="GameObjects"]')}
baseline=ROOT/'verify_baseline.lsx'
dragon.run('-a','convert-resource','-s',ROOT/'baseline_0.2.2/Public/DenimDragonArmor/RootTemplates/_merged.lsf','-d',baseline)
approved=roots(baseline)
for mode in ['preview','final']:
 src=ROOT/('src_'+mode);unpacked=ROOT/('verified_'+mode)
 dragon.run('-a','extract-package','-s',ROOT/f'LegacyPartyArmory_{VERSION}_{mode.upper()}.pak','-d',unpacked)
 files=list(src.rglob('*'));files=[p for p in files if p.is_file()]
 actual=[p for p in unpacked.rglob('*') if p.is_file()]
 assert {p.relative_to(src) for p in files}=={p.relative_to(unpacked) for p in actual}
 for p in files:assert digest(p)==digest(unpacked/p.relative_to(src)),p
 rt=ROOT/f'verify_{mode}_roots.lsx';dragon.run('-a','convert-resource','-s',unpacked/'Public/DenimDragonArmor/RootTemplates/_merged.lsf','-d',rt)
 items=roots(rt);assert len(items)==25
 for key,_ in DRAGONS:assert normalized(items[key])==normalized(approved[key]),'Approved dragon visuals changed'
 assets=ROOT/f'verify_{mode}_assets.lsx';dragon.run('-a','convert-resource','-s',unpacked/'Public/DenimDragonArmor/Content/Assets/[PAK]_LegacyPartyArmory/_merged.lsf','-d',assets)
 resources={n.find('attribute[@id="ID"]').get('value') for n in E.parse(assets).findall('./region/node/children/node')}
 # New bank must not overwrite a vanilla resource ID.
 import json
 index=json.loads((ROOT/'index.json').read_text(encoding='utf-8'))
 assert not resources.intersection(index['templates'])
 for i in ITEMS:
  n=items[i['uuid']]
  for ref in n.findall('.//node[@id="Visuals"]//node[@id="MapValue"]/attribute[@id="Object"]'):
   assert ref.get('value') in resources,(i['key'],ref.attrib)
 for lang in ['English','Russian']:
  target=ROOT/f'verify_{mode}_{lang}.xml'
  dragon.run('-a','convert-loca','-s',unpacked/f'Localization/{lang}/DenimDragonArmor.loca','-d',target)
  expected={n.get('contentuid'):n.text for n in E.parse(ROOT/(lang+'.xml')).findall('content')}
  decoded={n.get('contentuid'):n.text for n in E.parse(target).findall('content')}
  assert expected==decoded,(mode,lang)
 print(f'PASS packaged {mode}: {len(files)} files SHA256 identical; 25 decoded roots; approved dragon nodes unchanged; {len(resources)} private resources; EN/RU loca round-trip')
