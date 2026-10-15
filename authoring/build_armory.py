"""Extend the approved Dragon mod using its LSLib build/conversion pipeline."""
from pathlib import Path
import sys, copy, json, shutil, argparse, subprocess, xml.etree.ElementTree as E
from armory_spec import *
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
import build as dragon
from item_content import TEXT as DRAGON_TEXT, handle as dragon_handle, FALLBACK_LANGUAGES
INDEX=json.loads((ROOT/'index.json').read_text(encoding='utf-8'))
S,T=INDEX['stats'],INDEX['templates']
LOC={'English':{},'Russian':{}}
DEFS=[];REPORT=[]
def tr(key,en,ru):
 for lang,value in [('English',en),('Russian',ru)]:LOC[lang][textid(key)]=value
 return textid(key)+';1'
def definition(key,typ,parent='',**data):
 DEFS.append('\n'.join([f'new entry "{key}"',f'type "{typ}"']+([f'using "{parent}"'] if parent else [])+[f'data "{k}" "{v}"' for k,v in data.items()])+'\n')
def a(n,k):return n.find(f'attribute[@id="{k}"]')
def setv(n,k,v,typ='FixedString'):
 node=a(n,k)
 if node is None:node=E.SubElement(n,'attribute',id=k,type=typ)
 node.set('value',str(v));return node
def translated(n,k,h):
 old=a(n,k)
 if old is not None:n.remove(old)
 E.SubElement(n,'attribute',id=k,type='TranslatedString',handle=h.split(';')[0],version='1')
def resolve(key,seen=None):
 seen=set() if seen is None else seen
 if key not in S or key in seen:return {}
 seen.add(key);d=S[key];return resolve(d['_parent'],seen)|d
def baseuuid(base):return base if base in T else resolve(base)['RootTemplate']
def flatten(key,seen=None):
 seen=set() if seen is None else seen
 assert key not in seen,key
 seen.add(key);n=E.fromstring(T[key]['xml']);p=a(n,'ParentTemplateId')
 if p is not None and p.get('value') in T:
  parent=flatten(p.get('value'),seen)
  for child in n.findall('attribute'):
   old=a(parent,child.get('id'))
   if old is not None:parent.remove(old)
   parent.append(copy.deepcopy(child))
  dst=parent.find('children')
  if dst is None:dst=E.SubElement(parent,'children')
  for child in n.findall('children/node'):
   for old in dst.findall(f'node[@id="{child.get("id")}"]'):dst.remove(old)
   dst.append(copy.deepcopy(child))
  n=parent
 return n
def clean(n,bag=False):
 # Material/Equipment/animation data survive; no inherited quest/use/status scripts.
 for attr in list(n.findall('attribute')):
  k=attr.get('id')
  if k in ['ParentTemplateId','StoryItem','QuestItem','Treasure','InventoryList','TreasureList','Script','GameMasterSpawnSubSection']:
   n.remove(attr)
 for k in ['StoryItem','IsStoryItem','QuestItem','IsQuestItem']:setv(n,k,'False','bool') if a(n,k) is not None else None
 children=n.find('children')
 if children is not None:
  for ch in list(children):
   k=ch.get('id','')
   if k in ['Scripts','ScriptOverrides','StatusList','Tags','InventoryList','TreasureList','OnDestroyActions','OnDeathActions','OnUsePeaceActions','OnUseActions']:
    # Ordinary bag interaction is inherited as UseAction from generic container,
    # retain its open-container OnUse actions; equipment is never consumable.
    if bag and k in ['OnUsePeaceActions','OnUseActions']:continue
    children.remove(ch)
 return n
def save_tree(root,path):dragon.write_xml(E.ElementTree(root),path)
def new_save(bank):
 root=E.Element('save');E.SubElement(root,'version',major='4',minor='0',revision='9',build='331')
 nodes=E.SubElement(E.SubElement(E.SubElement(root,'region',id=bank),'node',id=bank),'children')
 return root,nodes

PALETTES={
 'holy':('0.78 0.88 1','0.25 0.025 0.035','0.92 0.95 1','0.34 0.55 0.8'),
 'oxblood':('0.075 0.085 0.10','0.018 0.014 0.017','0.19 0.024 0.033','0.16 0.008 0.012'),
 'emerald':('0.14 0.18 0.19','0.016 0.025 0.02','0.018 0.4 0.17','0.22 0.38 0.31'),
 'infernal':('0.10 0.065 0.055','0.065 0.018 0.012','0.65 0.075 0.015','0.7 0.12 0.018'),
 'dragon_red':('1 0.07 0.025','0.7 0.025 0.009','0.9 0.14 0.025','1 0.1 0.015'),
 'ice':('0.7 0.82 0.9','0.018 0.025 0.035','0.37 0.62 0.83','0.25 0.5 0.7'),
 'blue':('0.72 0.8 0.9','0.025 0.035 0.06','0 0.3 1','0 0.3 1'),
 'harper':('0.24 0.30 0.13','0.09 0.045 0.025','0.42 0.25 0.065','0 0 0'),
 'shar':('0.032 0.037 0.05','0.014 0.012 0.022','0.38 0.41 0.48','0.07 0.018 0.12'),
 'moon':('0.46 0.58 0.7','0.15 0.23 0.32','0.72 0.79 0.88','0.24 0.4 0.65')}
def colours(p):
 metal,leather,accent,glow=PALETTES[p]
 return {**{f'Cloth_{k}':v for k,v in zip(['Primary','Secondary','Tertiary'],[metal,leather,accent])},
 **{f'Leather_{k}':v for k,v in zip(['Primary','Secondary','Tertiary'],[leather,leather,accent])},
 **{f'Metal_{k}':v for k,v in zip(['Primary','Secondary','Tertiary'],[metal,accent,metal])},
 'Accent_Color':accent,'Custom_1':metal,'Custom_2':accent,
 'Color_01':metal,'Color_02':accent,'Color_03':leather}

class Assets:
 def __init__(self):
  self.resources={};self.root=E.Element('save');E.SubElement(self.root,'version',major='4',minor='0',revision='9',build='331');self.banks={};self.mapped={};self.changes=[]
  for directory in [ROOT.parent/'armor_xml',ROOT/'weapon_xml',ROOT.parent/'presets_xml',ROOT/'engine_xml']:
   for path in sorted(directory.rglob('*.lsx')):
    for region in E.parse(path).findall('region'):
     for node in region.findall('node/children/node'):
      if a(node,'ID') is not None:self.resources[a(node,'ID').get('value')]=(region.get('id'),node)
 def append(self,bank,n):
  if bank not in self.banks:self.banks[bank]=E.SubElement(E.SubElement(E.SubElement(self.root,'region',id=bank),'node',id=bank),'children')
  self.banks[bank].append(n)
 def install_masks(self,src):
  for key,name,size,srgb in [('grip','carsomyr_grip_mask',1024,False),('red_gradient','dragon_red_gradient',256,True)]:
   resource=copy.deepcopy(self.resources['a90992f1-5dbf-9893-dba2-35386614d20d'][1])
   for attr,value in {'ID':uid('texture:'+key),'Name':'LPA_'+name,'Width':size,'Height':size,'SRGB':str(srgb),'Streaming':'False','Template':'LPA_'+name,'SourceFile':f'Public/DenimDragonArmor/Assets/Textures/{name}.dds'}.items():setv(resource,attr,value)
   self.append('TextureBank',resource)
   dest=src/f'Public/DenimDragonArmor/Assets/Textures/{name}.dds';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/(name+'.dds'),dest)
 def clone(self,key,item):
  cache=(key,item['key'])
  if cache in self.mapped:return self.mapped[cache]
  if key not in self.resources:
   found=subprocess.run(['rg','-l','--fixed-strings',key,str(ROOT/'all_content_xml'),'-g','*.lsx'],capture_output=True,text=True,check=False)
   for file in found.stdout.splitlines():
    for region in E.parse(file).findall('region'):
     for resource in region.findall('node/children/node'):
      if a(resource,'ID') is not None:self.resources[a(resource,'ID').get('value')]=(region.get('id'),resource)
  assert key in self.resources,('Missing visual/material',key,item['key'])
  bank,original=self.resources[key];node=copy.deepcopy(original);newid=uid(item['key']+':asset:'+key);self.mapped[cache]=newid
  setv(node,'ID',newid);setv(node,'Name','LPA_'+item['key']+'_'+a(node,'Name').get('value'),'LSString')
  if bank=='VisualBank':
   for ref in node.findall('.//attribute[@id="MaterialID"]'):ref.set('value',self.clone(ref.get('value'),item))
  elif bank=='MaterialBank':
   retain_native=item['key'] in ['Carsomyr','Twinkle','Icingdeath','CharonsClaw','DragonsBreath','EntreriDagger']
   if (resolve(item['parent']).get('_type')=='Weapon' or item['key']=='WalkingFortress') and not retain_native:
    # Ordinary weapon Base_VT has no tint uniforms. Use an installed, precompiled
    # VT shader that supports BOTH surface tint and restrained glow. Preserve UVs
    # and native virtual texture (normal/metal/roughness remain the original).
    shadername='Base_GM_Pulse_Color_AlphaTest_VT'
    shader=E.parse(ROOT/f'shader_xml/Public/Shared/Assets/Materials/Base/{shadername}.lsx')
    oldparams={a(p,'ParameterName').get('value'):copy.deepcopy(p) for p in node.findall('children/node') if a(p,'ParameterName') is not None}
    newchildren=E.Element('children')
    allowed={'Enabled','ParameterName','GroupName','ExportAsPreset','Value','BaseValue','IsColor','ID','Index','IgnoreTexelDensity'}
    for p in shader.findall('./region/node/children/node'):
     pname=a(p,'ParameterName')
     if pname is None or p.get('id') not in ['ScalarParameters','Vector3Parameters','Texture2DParameters','VirtualTextureParameters']:continue
     name=pname.get('value')
     if not name:continue
     par=copy.deepcopy(oldparams.get(name,oldparams.get('glowmap',p) if name=='Glowmap' else p))
     for child in list(par):
      if child.tag!='attribute' or child.get('id') not in allowed:par.remove(child)
     setv(par,'ParameterName',name)
     values={'Color':PALETTES[item['colour']][0],'GlowColour':PALETTES[item['colour']][3],'GlowMultiplier':'0.10','PulseSpeed':'0','MinGlow':'1','MaxGlow':'1'}
     if name in values:
      for attr in ['Value','BaseValue']:setv(par,attr,values[name],'fvec3' if par.get('id')=='Vector3Parameters' else 'float')
     setv(par,'Enabled','True','bool');newchildren.append(par)
    old=node.find('children')
    if old is not None:node.remove(old)
    node.append(newchildren);setv(node,'SourceFile',f'Public/Shared/Assets/Materials/Base/{shadername}.lsf','LSString')
   if item['key']=='Carsomyr':
    shadername='BASE_AlphaTest_ColorVar_VT'
    shader=E.parse(ROOT/f'shader_xml/Public/Shared/Assets/Materials/Base/{shadername}.lsx')
    dest=node.find('children')
    allowed={'Enabled','ParameterName','GroupName','ExportAsPreset','Value','BaseValue','IsColor','ID','Index','IgnoreTexelDensity'}
    for pname in ['VariationColor','MSK1']:
     par=copy.deepcopy(next(p for p in shader.findall('./region/node/children/node') if a(p,'ParameterName') is not None and a(p,'ParameterName').get('value')==pname))
     for child in list(par):
      if child.tag!='attribute' or child.get('id') not in allowed:par.remove(child)
     setv(par,'Enabled','True','bool')
     if pname=='VariationColor':
      setv(par,'Value','0.8 0.018 0.008','fvec3');setv(par,'BaseValue','0.8 0.018 0.008','fvec3')
     else:setv(par,'ID',uid('texture:grip'))
     dest.append(par)
    setv(node,'SourceFile',f'Public/Shared/Assets/Materials/Base/{shadername}.lsf','LSString')
   if item['key']=='DragonsBreath':
    for par in node.findall('children/node'):
     if a(par,'ParameterName') is not None and a(par,'ParameterName').get('value')=='Gradients':setv(par,'ID',uid('texture:red_gradient'))
   palette=colours(item['colour']);edits=0
   for par in node.findall('.//node'):
    pname=a(par,'ParameterName')
    if pname is None:continue
    name=pname.get('value');value=palette.get(name)
    if item['key']=='EntreriDagger' and name in ['BaseColor','InnerColor']:value={'BaseColor':'0.008 0.18 0.035','InnerColor':'0.025 0.65 0.14'}[name]
    if 'glow' in name.lower() and par.get('id')=='Vector3Parameters':value=PALETTES[item['colour']][3]
    if name in ['GlowMultiplier','GlowIntensity']:value=str({'Twinkle':6,'Icingdeath':4,'CharonsClaw':3,'DragonsBreath':3,'EntreriDagger':3}.get(item['key'],0.10)) if item['colour']!='harper' else '0'
    if item['key']=='EntreriDagger' and name in ['EdgeGlowMultiplier','DetailGlowMultiplier']:value={'EdgeGlowMultiplier':'0.75','DetailGlowMultiplier':'4'}[name]
    if name=='UseGMColor' and item['key'] in ['Twinkle','Icingdeath','CharonsClaw']:value='0'
    # Chaos uses a gradient overlay. Disable it on Carsomyr; keep the same mesh.
    if item['key']=='Carsomyr' and name=='GradientIndex':value='0'
    if value is not None:
     for attr in ['Value','BaseValue']:
      if a(par,attr) is not None:a(par,attr).set('value',value)
     if a(par,'Enabled') is not None:a(par,'Enabled').set('value','True')
     edits+=1
   self.changes.append({'item':item['key'],'material':key,'changed_parameters':edits})
  self.append(bank,node);return newid
 def paint(self,n,item):
  refs=n.findall('.//node[@id="Visuals"]//node[@id="MapValue"]/attribute[@id="Object"]')
  rootvisual=a(n,'VisualTemplate')
  if rootvisual is not None and rootvisual.get('value') in self.resources:refs.append(rootvisual)
  for ref in refs:ref.set('value',self.clone(ref.get('value'),item))
  # Equip defaults remain ordinary material overrides so subsequent dyes can replace them.
  for overrides in n.findall('.//node[@id="MaterialOverrides"]'):
   for children in overrides.findall('children'):
    for old in list(children):
     if old.get('id') in ['MaterialPresets','Vector3Parameters']:children.remove(old)
    for name,value in colours(item['colour']).items():
     ch=E.SubElement(children,'node',id='Vector3Parameters')
     for key,typ,val in [('Color','bool','True'),('Custom','bool','False'),('Enabled','bool','True'),('Parameter','FixedString',name),('Value','fvec3',value)]:E.SubElement(ch,'attribute',id=key,type=typ,value=val)

def passives():
 def passive(k,en,ru,de,dr,boost='',**data):
  definition('LPA_'+k,'PassiveData',DisplayName=tr(k+'.name',en,ru),Description=tr(k+'.desc',de,dr),Icon='PassiveFeature_MagicResistance',Properties='Highlighted',**({'Boosts':boost} if boost else {}),**data)
 passive('HolyWard','Holy Avenger','Святой мститель','Advantage on saving throws against spells.','Преимущество при спасбросках против заклинаний.','IF(IsSpell()):Advantage(AllSavingThrows)')
 passive('ClawTraining','Will of the Claw','Воля Когтя','You are proficient with longswords. This light blade uses your spellcasting ability for attack and damage rolls.','Вы владеете длинными мечами. Этот лёгкий клинок использует заклинательную характеристику для бросков атаки и урона.','Proficiency(Longswords)')
 passive('GauntletWard','Spellcatcher','Ловец чар','Advantage on saving throws against spells. Counterspell (level 3) once per Long Rest, using a reaction.','Преимущество при спасбросках против заклинаний. Контрзаклинание 3-го круга один раз до долгого отдыха за реакцию.','IF(IsSpell()):Advantage(AllSavingThrows)')
 passive('ClawBond','Claw and Gauntlet','Коготь и перчатка','While Charon’s Claw is equipped, gain +1 Armour Class.','Пока Коготь Харона надет, вы получаете +1 к классу брони.',"IF(HasPassive('LPA_ClawTraining',context.Source)):AC(1)")
 # Native OncePerTurn applies to the passive, so off-hand/extra attacks cannot spam heals.
 definition('LPA_LifeDrink','PassiveData',DisplayName=tr('life.name','Stolen Warmth','Похищенное тепло'),Description=tr('life.desc','Once per turn, damaging a living enemy with this dagger restores 1d4 hit points.','Раз в ход, нанеся этим кинжалом урон живому противнику, вы восстанавливаете 1d4 ОЗ.'),Icon='Spell_Necromancy_VampiricTouch',Properties='Highlighted;OncePerTurn',StatsFunctorContext='OnDamage',Conditions="AttackedWithPassiveSourceWeapon() and Enemy() and not Item() and not Dead() and not Tagged('UNDEAD') and not Tagged('CONSTRUCT')",StatsFunctors='RegainHitPoints(SELF,1d4)')
 passive('Frostbrand','Frostbrand','Морозный клинок','Resistance to Fire damage. Quench flames once per Short Rest.','Сопротивление урону огнём. Погасить пламя можно раз до короткого отдыха.','Resistance(Fire,Resistant)')
 passive('Defender','Elven Defender','Эльфийский защитник','Gain +1 Armour Class while this weapon is equipped, including in the off-hand.','Вы получаете +1 к классу брони, пока клинок надет, в том числе во второй руке.','AC(1)')
 definition('LPA_InfernalImpact','PassiveData',DisplayName=tr('impact.name','Infernal Impact','Инфернальный удар'),Description=tr('impact.desc','Once per turn, a critical hit with this maul sets the target Burning for 2 turns.','Раз в ход критическое попадание этим молотом поджигает цель на 2 хода.'),Icon='Spell_Evocation_FireBolt',Properties='Highlighted;OncePerTurn',StatsFunctorContext='OnDamage',Conditions='AttackedWithPassiveSourceWeapon() and IsCritical() and not Item()',StatsFunctors='ApplyStatus(BURNING,100,2)')
 passive('DragonElements','Five Draconic Tempers','Пять драконьих стихий','This halberd deals 1d4 extra damage of one selected type: Fire, Cold, Lightning, Acid or Poison. Fire is the default. Choose a type with a Bonus Action, including while Raging.','Эта алебарда наносит дополнительно 1d4 урона выбранной стихией: огнём, холодом, молнией, кислотой или ядом. По умолчанию — огнём. Выбор за бонусное действие доступен и в ярости.')

def spells():
 def spell(k,parent,en,ru,de,dr,**data):
  d=dict(SpellType='Target',DisplayName=tr(k+'.name',en,ru),Description=tr(k+'.desc',de,dr),RootSpellID='',TooltipUpcastDescription='',TooltipDamageList='',TooltipStatusApply='',DescriptionParams='',ExtraDescription='',ExtraDescriptionParams='')|data
  definition(k,'SpellData',parent,**d)
 spell('Shout_LPA_Armory','Shout_ActionSurge','Open Legacy Party Armory','Получить Legacy Party Armory','Create a full set of organised equipment backpacks. Usable outside combat. Each use creates a new Armory.','Создать полный комплект рюкзаков со снаряжением. Доступно вне боя. Каждое применение создаёт новую оружейную.',SpellType='Shout',Cooldown='',SpellProperties='',TargetConditions='Self()',UseCosts='',Requirements='!Combat',RequirementConditions='',AIFlags='',RechargeValues='',Icon='Item_LOOT_GEN_Backpack_A_Posed_A',PrepareEffect='',CastEffect='')
 whitelist=['HASTE','BLUR','MIRROR_IMAGE_1','MIRROR_IMAGE_2','MIRROR_IMAGE_3','SHIELD','MAGE_ARMOR','INVISIBILITY','GREATER_INVISIBILITY','BLADE_WARD','SHIELD_OF_FAITH','PROTECTION_FROM_EVIL_AND_GOOD']
 assert all(k in S and S[k]['_type']=='StatusData' for k in whitelist)
 spell('Target_LPA_Unweave','Target_TrueStrike','Unweave','Рассечь чары','Remove Haste, Blur, Mirror Image, Shield, Mage Armour, Invisibility, Greater Invisibility, Blade Ward, Shield of Faith and Protection from Evil and Good from one creature within 9m. Action; once per Short Rest.','Снять с существа в пределах 9 м: ускорение, размытый образ, зеркальное отражение, щит, доспехи мага, невидимость, высшую невидимость, защиту от оружия, щит веры, защиту от добра и зла. Действие; раз до короткого отдыха.',SpellProperties=';'.join('RemoveStatus('+s+')' for s in whitelist),SpellRoll='',SpellSuccess='',SpellFail='',TargetRadius='9',TargetConditions='Character() and not Dead()',UseCosts='ActionPoint:1',Cooldown='OncePerShortRest',SpellFlags='IsSpell;HasSomaticComponent',Icon='Spell_Abjuration_Counterspell')
 spell('Target_LPA_AshVeil','Target_FogCloud','Ashen Veil','Пепельная завеса','Create a 3m cloud of ash that heavily obscures an area for 3 turns. Action; once per Short Rest. No concentration.','Создать пепельное облако радиусом 3 м, сильно заслоняющее область на 3 хода. Действие; раз до короткого отдыха. Без концентрации.',SpellProperties='GROUND:CreateSurface(3,3,FogCloud,true)',AreaRadius='3',UseCosts='ActionPoint:1',Cooldown='OncePerShortRest',SpellFlags='RangeIgnoreVerticalThreshold')
 spell('Target_LPA_Quench','Target_CreateWater','Quench','Погасить пламя','Create water in a 2m area to extinguish ordinary flames. Action; once per Short Rest.','Создать воду в области радиусом 2 м и погасить обычное пламя. Действие; раз до короткого отдыха.',SpellProperties='GROUND:CreateSurface(2,3,Water,false)',AreaRadius='2',UseCosts='ActionPoint:1',Cooldown='OncePerShortRest',SpellFlags='RangeIgnoreVerticalThreshold')
 spell('Target_LPA_Counterspell','Target_MAG_CounterSpell','Claw’s Counterspell','Контрзаклинание Когтя','Counter a spell as a level 3 Counterspell. Reaction; once per Long Rest.','Прервать заклинание контрзаклинанием 3-го круга. Реакция; раз до долгого отдыха.',Level='3',InterruptPrototype='Interrupt_LPA_Counterspell',UseCosts='ReactionActionPoint:1',Cooldown='OncePerRestPerItem')
 definition('Interrupt_LPA_Counterspell','InterruptData','Interrupt_MAG_Counterspell',DisplayName=textid('Target_LPA_Counterspell.name')+';1',Roll='TryCounterspellHigherLevel(3)',Cost='ReactionActionPoint:1;Interrupt_MAG_Counterspell:1')
 for element,ru in [('Fire','Огонь'),('Cold','Холод'),('Lightning','Молния'),('Acid','Кислота'),('Poison','Яд')]:
  definition('LPA_DRAGON_'+element.upper(),'StatusData',StatusType='BOOST',DisplayName=tr('element.'+element,element,ru),Icon='Spell_Evocation_ChromaticOrb_'+element,StackId='LPA_DRAGON_ELEMENT',StackType='Overwrite',StackPriority='1',StatusPropertyFlags='DisableOverhead;DisableCombatlog')
  spell('Shout_LPA_'+element,'Shout_ActionSurge',"Dragon’s Breath: "+element,'Дыхание Дракона: '+ru,'Select this halberd’s damage type. Bonus Action; no spellcasting required.','Выбрать стихию алебарды. Бонусное действие; применение заклинаний не требуется.',SpellType='Shout',SpellProperties=';'.join('RemoveStatus(LPA_DRAGON_'+e.upper()+')' for e in ['Fire','Cold','Lightning','Acid','Poison'])+';ApplyStatus(LPA_DRAGON_'+element.upper()+',100,-1)',UseCosts='BonusActionPoint:1',Cooldown='',Requirements='',SpellFlags='',TargetConditions='Self()',AIFlags='',PrepareEffect='',CastEffect='')

def build(mode):
 src=ROOT/('src_'+mode);shutil.copytree(ROOT/'baseline_0.2.2',src,dirs_exist_ok=True)
 statsdir=src/'Public/DenimDragonArmor/Stats/Generated/Data'
 # Preserve the dragon passive definitions and approved resources, rebalance only numbers.
 p=statsdir/'Armor_DragonSet.txt'
 if not p.exists():p=next(q for q in statsdir.glob('*.txt') if 'new entry "DENIM_RedDragon_Armor"' in q.read_text(encoding='utf-8'))
 txt=p.read_text(encoding='utf-8').replace('data "ArmorClass" "20"','data "ArmorClass" "16"')
 # Keep the user's approved golden Legendary presentation; AC and effects use
 # the power budget of strong Very Rare gear, independently of frame colour.
 p.write_text(txt,encoding='utf-8')
 rootfile=src/'Public/DenimDragonArmor/RootTemplates/_merged.lsf'
 xml=ROOT/'working_templates.lsx';dragon.run('-a','convert-resource','-s',rootfile,'-d',xml)
 tree=E.parse(xml);nodes=tree.find('.//region[@id="Templates"]/node/children');assert nodes is not None
 assets=Assets();assets.install_masks(src);manifest={k:dict(uuid=uid('bag:'+k),children=[],items=[]) for k in BAGS}
 for bag,names in BAGS.items():
  n=clean(flatten('47805d79-88f1-4933-86eb-f78f67cbc33f'),bag=True)
  setv(n,'MapKey',uid('bag:'+bag));setv(n,'Name','LPA_Bag_'+bag,'LSString');setv(n,'Stats','LPA_Bag_'+bag)
  translated(n,'DisplayName',tr('bag.'+bag,*names));translated(n,'Description',tr('bag.'+bag+'.desc','Equipment prepared for your party.','Снаряжение, подготовленное для вашего отряда.'))
  # Empty on spawn; only the manual Lua action populates it.
  setv(n,'TreasureOnDestroy','False','bool');nodes.append(n)
  definition('LPA_Bag_'+bag,'Object','OBJ_Backpack',RootTemplate=uid('bag:'+bag),Weight='0.5')
 manifest['outer']['children']=['paladin','wyll','karlach','minthara','jaheira','shadowheart'];manifest['shadowheart']['children']=['shar','selune']
 for uuid_,stat in DRAGONS:manifest['paladin']['items'].append(uuid_)
 for item in ITEMS:
  base=baseuuid(item['base']);n=clean(flatten(base));original=copy.deepcopy(n)
  if item['key']=='SeluneSpear':
   # These are combat bookkeeping, not plot hooks: required for native recharge.
   children=n.find('children')
   if children is None:children=E.SubElement(n,'children')
   statuses=E.SubElement(E.SubElement(children,'node',id='StatusList'),'children')
   for status in ['MAG_SELUNE_SPEAR_MOONBEAM_MAGIC_ITEM','MAG_SELUNE_SPEAR_MOONFIRE_MAGIC_ITEM']:
    E.SubElement(E.SubElement(statuses,'node',id='Status'),'attribute',id='Object',type='FixedString',value=status)
  setv(n,'MapKey',item['uuid']);setv(n,'Name',item['stats'],'LSString');setv(n,'Stats',item['stats'])
  translated(n,'DisplayName',tr(item['key']+'.name',item['en'],item['ru']));translated(n,'Description',tr(item['key']+'.lore',item['lore_en'],item['lore_ru']))
  # Camp-only Jaheira clothes become a proper body-slot item retaining their race visuals.
  if item['key']=='HarperFinery':
   equipment=n.find('children/node[@id="Equipment"]');assert equipment is not None
   children=equipment.find('children')
   slot=equipment.find('children/node[@id="Slot"]')
   if slot is None:slot=E.SubElement(children,'node',id='Slot')
   setv(slot,'Object','Body')
   equiptype=a(n,'EquipmentTypeID')
   if equiptype is not None:n.remove(equiptype)
   setv(n,'HasGameplayValue','True','bool')
  assets.paint(n,item);nodes.append(n)
  d=item['data'].copy()
  if item['key']=='CharonsClaw':d['DefaultBoosts']+=';WeaponAttackRollAbilityOverride(SpellCastingAbility)'
  if item['key']=='CharonsGauntlet':d['PassivesOnEquip']+=';MAG_LC_Counterspell_Quarterstaff_Resource_Passive'
  if item['key']=='DragonsBreath':
   d['DefaultBoosts']+=';IF(not HasAnyStatus({'+','.join("'LPA_DRAGON_"+e+"'" for e in ['COLD','LIGHTNING','ACID','POISON'])+'},context.Source)):WeaponDamage(1d4,Fire)'
   for e in ['Cold','Lightning','Acid','Poison']:d['DefaultBoosts']+=f";IF(HasStatus('LPA_DRAGON_{e.upper()}',context.Source)):WeaponDamage(1d4,{e})"
  typ=resolve(item['parent'])['_type'];definition(item['stats'],typ,item['parent'],RootTemplate=item['uuid'],Unique='0',**d)
  manifest[item['bag']]['items'].append(item['uuid'])
  attrs={x.get('id'):x.get('value') for x in original.findall('attribute')}
  REPORT.append(item|dict(base_uuid=base,base_attributes=attrs,base_source=T[base]['file'],base_stats=attrs.get('Stats',''),final_status='CUSTOM COPY REQUIRED' if item['key'] in ['SharSpear','SeluneSpear','ViconiaRobe','WalkingFortress','MoonRobe','HarperFinery'] else 'KEEP IN MOD'))
 preview_report=[]
 for bag,keys in PREVIEW.items():
  for key in keys:
   uuid_=baseuuid(key);flat=flatten(uuid_);attrs={x.get('id'):x.get('value') for x in flat.findall('attribute')}
   preview_report.append(dict(bag=bag,stats=key,uuid=uuid_,attributes=attrs,source=T[uuid_]['file']))
   if mode=='preview' or key in FINAL_DYES.get(bag,[]):manifest[bag]['items'].append(uuid_)
 passives();spells()
 (statsdir/'LegacyPartyArmory.txt').write_text('\n'.join(DEFS),encoding='utf-8')
 dragon.write_xml(tree,xml);dragon.run('-a','convert-resource','-s',xml,'-d',rootfile)
 assetxml=ROOT/'armory_assets.lsx';save_tree(assets.root,assetxml)
 assetfile=src/'Public/DenimDragonArmor/Content/Assets/[PAK]_LegacyPartyArmory/_merged.lsf';assetfile.parent.mkdir(parents=True,exist_ok=True)
 dragon.run('-a','convert-resource','-s',assetxml,'-d',assetfile)
 # Existing dragon handles must stay stable, including its legacy item names.
 for lang,strings in DRAGON_TEXT.items():
  LOC[lang][dragon.NAME]=strings['armor_name'];LOC[lang][dragon.HELMET_NAME]=strings['helmet_name']
  for k,v in strings.items():
   if k not in ['armor_name','helmet_name']:LOC[lang][dragon_handle(k)]=v
 for lang in ['English','Russian']+FALLBACK_LANGUAGES:
  content=E.Element('contentList')
  for h,value in LOC.get(lang,LOC['English']).items():E.SubElement(content,'content',contentuid=h,version='1').text=value
  locxml=ROOT/(lang+'.xml');save_tree(content,locxml);target=src/f'Localization/{lang}/DenimDragonArmor.loca';target.parent.mkdir(parents=True,exist_ok=True)
  dragon.run('-a','convert-loca','-s',locxml,'-d',target)
 lua=src/'Mods/DenimDragonArmor/ScriptExtender/Lua'
 (lua/'BootstrapServer.lua').write_text((ROOT/'runtime.lua').read_text(encoding='utf-8'),encoding='utf-8')
 (lua/'ArmoryData.json').write_text(json.dumps(dict(mode=mode,bags=manifest),ensure_ascii=False,indent=2),encoding='utf-8')
 (lua/'ArmoryData.lua').write_text('return Ext.Json.Parse([==['+json.dumps(dict(mode=mode,bags=manifest),ensure_ascii=False)+']==])\n',encoding='utf-8')
 meta=E.parse(src/'Mods/DenimDragonArmor/meta.lsx')
 for k,v in {'Name':'Legacy Party Armory','Description':'Legacy Party Armory '+VERSION+' '+mode+' — manual nested backpack delivery.','Version64':'36028797019013121'}.items():
  for node in meta.findall(f'.//attribute[@id="{k}"]'):node.set('value',v)
 dragon.write_xml(meta,src/'Mods/DenimDragonArmor/meta.lsx')
 pak=ROOT/f'LegacyPartyArmory_{VERSION}_{mode.upper()}.pak';dragon.run('-a','create-package','-s',src,'-d',pak,'-c','lz4','--package-priority','30')
 (ROOT/f'manifest_{mode}.json').write_text(json.dumps(dict(mode=mode,bags=manifest,custom=REPORT,preview=preview_report,material_changes=assets.changes),ensure_ascii=False,indent=2),encoding='utf-8')
 print('BUILT',pak)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['preview','final'],default='preview');build(p.parse_args().mode)
