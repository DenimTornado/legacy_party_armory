"""Build both configurations, verify, document and produce the preview handoff."""
from pathlib import Path
import sys,subprocess,zipfile,hashlib,json
from armory_spec import VERSION
ROOT=Path(__file__).resolve().parent
def run(script,*args,log=None):
 if log:
  with (ROOT/log).open('w',encoding='utf-8') as output:subprocess.run([sys.executable,str(ROOT/script),*args],stdout=output,stderr=subprocess.STDOUT,check=True)
 else:subprocess.run([sys.executable,str(ROOT/script),*args],check=True)
for mode in ['preview','final']:run('build_armory.py','--mode',mode,log=f'build_{mode}.log')
run('test_armory.py',log='test_results.txt')
run('verify_package.py',log='verification.log')
run('write_docs.py')
checks={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob(f'LegacyPartyArmory_{VERSION}_*.pak')}
(ROOT/'SHA256.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
archive=ROOT.parents[1]/f'LegacyPartyArmory_{VERSION}_PREVIEW.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for name in [f'LegacyPartyArmory_{VERSION}_PREVIEW.pak','README.md','manifest_preview.json','SHA256.json','test_results.txt']:
  z.write(ROOT/name,name)
 for file in sorted((ROOT/'docs').glob('*.md')):z.write(file,'docs/'+file.name)
print('Verified preview archive:',archive)
for name,hash_ in checks.items():print(name,hash_)
