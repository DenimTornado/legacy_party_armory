from pathlib import Path
import re, json, xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent
def attributes(n): return {a.get('id'):a.get('value',a.get('handle','')) for a in n.findall('attribute')}
stats={}
for module in ['Shared','SharedDev','Gustav','GustavDev','GustavX']:
 for p in (ROOT/'data/Public'/module/'Stats/Generated/Data').glob('*.txt'):
  for block in p.read_text(encoding='utf-8-sig').split('new entry ')[1:]:
   m=re.match(r'"([^"]+)"',block)
   if not m:continue
   d=dict(re.findall(r'data "([^"]+)" "([^"]*)"',block));d['_type']=re.search(r'type "([^"]+)"',block)[1]
   parent=re.search(r'^using "([^"]+)"',block,re.M); d['_parent']=parent[1] if parent else '';d['_file']=str(p.relative_to(ROOT))
   if d['_parent']==m[1] and m[1] in stats:
    d['_parent']=stats[m[1]]['_parent']; d=stats[m[1]]|d
   stats[m[1]]=d
templates={}
for directory in [PARENT/'xml',PARENT/'xml_gustav',ROOT/'extra_xml']:
 for p in directory.rglob('*.lsx'):
  for n in E.parse(p).findall('.//node[@id="GameObjects"]'):
   d=attributes(n)
   if d.get('MapKey'):templates[d['MapKey']]={'attributes':d,'file':str(p),'xml':E.tostring(n,encoding='unicode')}
def resolved(key,seen=None):
 seen=set() if seen is None else seen
 if key not in stats or key in seen:return {}
 seen.add(key);d=stats[key];return resolved(d['_parent'],seen)|d
if __name__=='__main__':
 (ROOT/'index.json').write_text(json.dumps({'stats':stats,'templates':templates},ensure_ascii=False),encoding='utf-8')
 needles=['Chaos','Hellfire','Bloodthirst','Penumbral','Bonespike','Cinder','Displacement','Marksmanship','Belm','Sylvan','Viconia','Moon','Justiciar','Harper','Infernal_Rapier','Corpsegrinder']
 for key,d in stats.items():
  if d['_type'] in ['Weapon','Armor'] and any(s.lower() in key.lower() for s in needles):
   print(key, resolved(key).get('RootTemplate',''))
 for key,t in templates.items():
  name=t['attributes'].get('Name','')
  if any(s.lower() in name.lower() for s in ['Backpack','Harper','Cindermoth','Bonespike','Penumbral','Corpsegrinder']):print('ROOT',key,name,t['attributes'].get('Stats',''))
