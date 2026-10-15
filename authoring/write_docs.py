from pathlib import Path
import json,xml.etree.ElementTree as E
from armory_spec import *
ROOT=Path(__file__).resolve().parent
p=json.loads((ROOT/'manifest_preview.json').read_text(encoding='utf-8'))
names={n.get('contentuid'):n.text for n in E.parse(ROOT/'vanilla_english.xml').findall('content')}
def write(name,text):(ROOT/name).write_text(text,encoding='utf-8')
write('README.md','''# Legacy Party Armory — 0.3.1 PREVIEW

Расширение рабочего Denim Dragon Armor: BG3 + Script Extender 16+, без новых Story goals.
Существующие UUID модуля и драконьих вещей сохранены. Поддерживаются сохранения с прежней версией; уже созданные вещи могут потребовать снять/надеть заново или получить свежий комплект.

## Установка и получение

1. Импортировать `LegacyPartyArmory_0.3.1_PREVIEW.pak` в Vortex/BG3 Mod Manager, заменив прежний DenimDragonArmor. Два пакета с UUID `5d96794a-b84b-4bf7-afaa-74063318d3a6` одновременно не включать.
2. Экспортировать/развернуть порядок загрузки и полностью перезапустить игру. Нужен установленный BG3 Script Extender.
3. После загрузки сохранения у главного персонажа появится действие **«Получить Legacy Party Armory»** (значок рюкзака). Найти его среди общих действий/в книге способностей и нажать вне боя.
4. В инвентаре появится **один рюкзак**, содержащий рюкзаки наборов. Применение можно повторять; каждый раз выдаётся новый полный комплект.

Предметы при загрузке сохранения, начале игры и переходе уровня не выдаются. Автоматически добавляется только действие. Консольная альтернатива в серверном Lua-контексте мода: `LegacyPartyArmory.Give()`; из общей SE-консоли — `Mods.DenimDragonArmor.LegacyPartyArmory.Give()`.

```text
Legacy Party Armory
├─ Paladin: Dragon Armour, Dragon Helm, Carsomyr
├─ Wyll — Artemis Entreri
├─ Karlach — Infernal Viking
├─ Minthara — Drizzt Do’Urden
├─ Jaheira — Legacy
└─ Shadowheart
   ├─ Shadowheart — Shar
   └─ Shadowheart — Selûne
```

## Режимы

**PREVIEW**: 16 custom вещей (включая две прежние), 9 ванильных вещей для примерки и 8 флаконов красителей, разложенные по 9 рюкзакам. Итого 42 создаваемых объекта. Оригинальные ванильные вещи выдаются без перекраски: применить лежащие рядом красители вручную, как предусмотрено ТЗ. Несколько вариантов цвета позволяют сравнить результат.

**FINAL**: предварительная конфигурация для последующей финализации: 16 custom вещей + 4 основных красителя + 9 рюкзаков, всего 29 объектов. Ванильные вещи и дополнительные варианты красителей из примерки исключены. Решения о поздних ванильных вещах остаются открытыми до теста; FINAL сейчас не является утверждённым релизом.

## Сборка и файлы

`./Build.ps1 -Mode preview` или `./Build.ps1 -Mode final`.
Используются существующие функции `../build.py`, LSLib/Divine и сохранённая рабочая база `baseline_0.2.2`. Генератор не требует установленного BG3 Toolkit. Индекс и извлечённые данные должны находиться рядом, как в текущем проекте.

- `armory_spec.py` — перечень предметов, UUID, статы и палитры.
- `build_armory.py` — генерация Stats/RootTemplates/локализации/частных материалов, упаковка.
- `runtime.lua` — ручное действие, транзакционная выдача и откат при ошибке.
- `src_preview`, `src_final` — полные исходники пакетов.
- `manifest_preview.json`, `manifest_final.json` — машинная таблица содержимого и источников.
- `test_armory.py`, `verify_package.py` — Lua-поведение и проверка собранных файлов.
- `docs/ITEMS.md`, `docs/SOURCES.md`, `docs/TESTING.md` — баланс, UUID, источники, проверка.

## Локализация и визуал

Полные EN/RU названия, авторские lore-описания и описания новых механик. Для прочих локалей — английский fallback. Родные эффекты безопасных копий сохраняют игровые локализованные подсказки.

Утверждённые модели, иконки и цвета драконьего комплекта сохранены. Любимый синий сохранён в `../saved_blue_0.1.8` и в палитре Twinkle (`0 0.3 1`). Новые предметы используют частные VisualBank/MaterialBank; shared vanilla resources не перезаписываются. Палитры новых вещей применены уже в PREVIEW.

Карсомир использует Silver Sword of the Astral Plane (f01c3f5d-c542-420f-86c5-bdddf7819e29). Для красного хвата добавлена отдельная UV-маска из 240 треугольников родной модели; клинок, гарда и навершие остаются серебряными. Twinkle, Icingdeath и Charon’s Claw используют родные glowmap и Base_GM_VT с заметной яркостью, а камень кинжала — родной кристаллический шейдер с изумрудными цветами. Dragon’s Breath теперь алебарда с частной красной gradient-палитрой. Джахейра носит лёгкий доспех на базе Spidersilk Armour в древесной гамме. Все 16 custom-вещей Legendary: жёлтая рамка и названия; числовой баланс не повышен из-за цвета редкости. Огромные постоянные частицы не добавлялись. Обычная покраска одежды предусмотрена; работу dyes поверх новых material overrides проверять в игре.

Сборки не устанавливаются автоматически в Vortex и не меняют пользовательский modsettings.lsx.
''')
effects={
 'Carsomyr':'+3; +1d4 Radiant; преимущество против заклинаний; Рассечь чары: действие, раз/короткий отдых, явный список 10 баффов.',
 'CharonsClaw':'+2; +1d4 Necrotic; лёгкий длинный меч; заклинательная характеристика (CHA у Уилла); владение длинными мечами; пепельная завеса 3 м/3 хода раз/короткий отдых.',
 'CharonsGauntlet':'Преимущество против заклинаний; контрзаклинание 3-го круга за реакцию раз/долгий отдых; +1 КБ при надетом Когте.',
 'EntreriDagger':'+2; +1d4 Necrotic; восстановление 1d4 ОЗ раз/ход от урона этим кинжалом живому врагу; работает во второй руке.',
 'DragonsBreath':'+3; один выбранный тип урона +1d4: Fire/Cold/Lightning/Acid/Poison. Выбор за бонусное действие, не заклинание; по умолчанию Fire.',
 'InfernalMaul':'+2; +1d4 Fire; критическое попадание поджигает на 2 хода раз/ход. Без заклинаний, совместим с яростью.',
 'Icingdeath':'+2; +1d4 Cold; сопротивление Fire; вода 2 м для тушения пламени раз/короткий отдых.',
 'Twinkle':'+2; +1 КБ, в том числе во второй руке; без дополнительного урона.',
 'HarperFinery':'Лёгкая броня Spidersilk в древесной палитре, КБ 13 + ловкость; +1 ко всем спасброскам; преимущество Nature/Survival.',
 'SharSpear':'Родная механика Shar spear (+3), без сюжетных tags/scripts/оригинального экземпляра.',
 'ViconiaRobe':'Родная механика Viconia robe (одежда); частный тёмный материал.',
 'WalkingFortress':'Родная механика настоящей Walking Fortress, КБ +3, spellguard/rebuke/активные способности.',
 'SeluneSpear':'Родная механика Selûne spear (+3); сохранены только два технических combat-status для Moonbeam/Moonmote.',
 'MoonRobe':'Родная механика Moon Devotion Robe; одежда, спасброски и лунная защита. Наследует и ограничения родной Lunar Bulwark.'}
lines=['# ITEMS — состав и баланс','', 'Все custom-предметы Legendary (жёлтые названия); ванильные вещи и красители не изменены. Статусы FINAL предварительные до примерки. Авторские варианты не претендуют на буквальное воспроизведение старых AD&D чисел.','', '| Character | Item | Base Visual | Custom Root UUID | Stats ID | Default Colour | Canonical / Original | Final Status | Notes |','|---|---|---|---|---|---|---|---|---|']
for id_,stat in DRAGONS:
 lines.append(f'| Paladin | {"Чешуя красного дракона" if "Armor" in stat else "Шлем дракона"} | Existing approved | `{id_}` | `{stat}` | Existing red/gold | BG2 adaptation | KEEP IN MOD | '+('Legendary (gold frame retained), medium: КБ 16 + Dex до 2, Fire resistance, помеха скрытности (кроме Medium Armour Master).' if 'Armor' in stat else 'Legendary (gold frame retained); без категории брони; Cold + Lightning resistance; защита от критических ударов.')+' |')
for i in p['custom']:
 lines.append(f"| {i['bag']} | {i['en']} / {i['ru']} | {i['base']} | `{i['uuid']}` | `{i['stats']}` | {i['colour']} | "+('Original' if i['key'] in ['InfernalMaul','HarperFinery'] else 'FR/BG2 adaptation' if i['key'] not in ['SharSpear','ViconiaRobe','WalkingFortress','SeluneSpear','MoonRobe'] else 'BG3 custom copy')+f" | {i['final_status']} | {effects[i['key']]} |")
lines+=['','## Ванильные предметы и красители для примерки','', '| Bag | Display name | Stats | Root UUID | Предварительный FINAL status |','|---|---|---|---|---|']
for v in p['preview']:
 name=names.get(v['attributes'].get('DisplayName'),v['stats'])
 status='KEEP DYE ONLY' if v['stats'] in FINAL_DYES.get(v['bag'],[]) else 'REMOVE FROM FINAL (extra dye)' if v['stats'].startswith('OBJ_Dye') else 'VANILLA — OBTAIN NATURALLY (provisional; late-game items may stay after preview)'
 lines.append(f"| {v['bag']} | {name} | `{v['stats']}` | `{v['uuid']}` | {status} |")
lines+=['','## Адаптации','',
 '- Carsomyr не ограничен классом/тегом: доступен Devotion, Ancients, Vengeance, Crown и Oathbreaker. Нет буквальных +5/+6 и 50% магического сопротивления.',
 '- Рассечение чар удаляет только перечисленные баффы; не обещает универсального dispel всех модовых/сюжетных эффектов.',
 '- Charon’s Claw: сравнивались Longsword +2 (узкий клинок, выбран), Infernal Rapier (отклонён по силуэту) и Duellist’s Prerogative (рапира, не выбрана). Полный longsword mesh и анимации сохранены; Light добавлен в stats, Versatile убран ради пары с кинжалом.',
 '- Gauntlet использует родной ресурс item-counterspell. Его один заряд не складывается с другими вещами, использующими тот же Interrupt_MAG_Counterspell. Тестировать восстановление после отдыха и повторного надевания.',
 '- Dragon’s Breath снова алебарда (Halberd +2 visual); красная gradient-палитра и родная карта свечения. 1d10 base, Reach и штатные анимации алебарды; выбор стихий остаётся доступным в ярости.',
 '- Icingdeath тушит обычное пламя водой, не гарантирует рассеивания любого магического огня. Twinkle защищает владельца вместо второй большой прибавки к DPS.',
 '- Harper’s Woodland Armour использует Spidersilk Armour, древесную палитру и лёгкую категорию; UUID прежней вещи Джахейры сохранён.',
 '- Копии Shar/Selûne не выдают оригинальные сюжетные экземпляры, не ставят flags и не требуют менять путь Shadowheart. Native spell/passive IDs сохранены для совместимости.',
 '- На новом оружии базовые текстуры запечены: точное распределение серебра/кожи/камня требует визуальной проверки; все стартовые tint/glow настройки уже включены.','']
write('docs/ITEMS.md','\n'.join(lines))

sources='''# SOURCES

## Canon and mechanics

Lore written anew in EN/RU. Sources determine identity and history; numeric BG3 balance is authored here.

- [Carsomyr](https://baldursgate.fandom.com/wiki/Carsomyr): holy avenger, anti-magic and dispel identity. BG3 adaptation uses +3, saving-throw advantage and a limited buff whitelist.
- [Dragon’s Breath](https://baldursgate.fandom.com/wiki/Dragon%27s_Breath_%28item%29): original BG2 halberd and five elemental associations. Version 0.3.1 restores the halberd weapon class.
- [Artemis Entreri](https://forgottenrealms.fandom.com/wiki/Artemis_Entreri), [Charon’s Claw](https://forgottenrealms.fandom.com/wiki/Charon%27s_Claw_%28sword%29), [Vampiric dagger](https://forgottenrealms.fandom.com/wiki/Vampiric_dagger): sword/gauntlet partnership, ash, magic defence, life theft. Direct Fandom pages sometimes reject retrieval; indexed results and cited sourcebooks support identity. No full wiki text copied.
- [Icingdeath](https://forgottenrealms.fandom.com/wiki/Icingdeath): cold, silver blade/dark hilt, fire protection. [Twinkle](https://forgottenrealms.fandom.com/wiki/Twinkle): elven defensive left-hand blade. [Drizzt Do’Urden](https://forgottenrealms.fandom.com/wiki/Drizzt_Do%27Urden): paired scimitars.
- [BG3 modding](https://bg3.wiki/wiki/Modding), [items](https://bg3.wiki/wiki/Modding:Creating_Equipment), [dyes](https://bg3.wiki/wiki/Dyes), [Sinful Red on Bone White](https://bg3.wiki/wiki/Sinful_Red_on_Bone_White): cross-reference; actual schema/identifiers come from installed data. The equipment tutorial URL did not return content during this run; no claims depend on it.
- [CreateAt — Larian official docs](https://docs.baldursgate3.game/index.php?title=CreateAt): spawning a real backpack and moving it to inventory. Delivery remains Lua + existing Osi API calls, without new Story goals.
- [IsInInventoryOf](https://docs.baldursgate3.game/index.php?title=IsInInventoryOf), [ToInventory](https://docs.baldursgate3.game/index.php?title=ToInventory): Lua supplies only query inputs (two for inventory membership); returned integer confirms placement. Transfers clear original ownership so generated gear is not stolen.
- [BG3 Script Extender](https://github.com/Norbyte/bg3se): local API source under `../../research_v1_00/api_source/bg3se-main`; native callbacks, timers, module environment and Lua loading.

## Installed game data as authority

Game: `D:/SteamLibrary/steamapps/common/Baldurs Gate 3/Data`. Extracted Shared, Gustav, GustavX and Patch8 HotFix9/10. Index module order: Shared, SharedDev, Gustav, GustavDev, GustavX; same-key patch extensions merge with their earlier definition.

`index.json` stores source template XML/attributes and stat provenance. `manifest_preview.json` lists base IDs and original flattened attributes. `armory_assets.lsx` and compiled private bank contain only new resource IDs. Base shader `Public/Shared/Assets/Materials/Base/Base_GM_Pulse_Color_AlphaTest_VT.lsf` is read from installed Materials.pak; custom meshes/animations use installed native files.

For armour/body material overrides the installed default presets and approved dragon setup were used. The real Sinful Red on Bone White preset is `33f7e7b9-7e66-7893-b18f-e080f39fe3e3`, confirmed in vanilla ItemCombos; custom weapons deliberately use dark metal/ember materials instead of turning the entire weapon bone-white. Vanilla clothing is left untouched and supplied with dye.

## Base template registry

| Display name | Stats ID | RootTemplate UUID | VisualResource ID (base) | Extracted source |
|---|---|---|---|---|
'''
entries={i['base_uuid']:(i['base_stats'],i['base_attributes'],i['base_source']) for i in p['custom']}
entries.update({v['uuid']:(v['stats'],v['attributes'],v['source']) for v in p['preview']})
for uuid_,(stat,attrs,source) in entries.items():
 name=names.get(attrs.get('DisplayName'),attrs.get('Name',stat))
 source=source.replace(str(ROOT.parent)+'\\','../').replace('\\','/')
 sources+=f"| {name} | `{stat}` | `{uuid_}` | `{attrs.get('VisualTemplate','see Equipment.Visuals')}` | `{source}` |\n"
sources+='''
For wearable items, one root VisualTemplate is the inventory/world mesh. Equipped visual maps are kept in `Equipment.Visuals` for each body/race; the clone pass remaps these to private VisualBank IDs. All map entries are preserved.

## Vanilla item references

'''
urls=['Silver_Sword_of_the_Astral_Plane','Halberd_%2B2','Bloodthirst','Corpsegrinder','Adamantine_Scimitar','Scimitar_%2B2','Penumbral_Armour','Marksmanship_Hat','Cloak_of_Displacement','Bonespike_Garb','Cindermoth_Cloak','Belm','Sylvan_Scimitar','Spidersilk_Armour',"Shar%27s_Spear_of_Evening","Sel%C3%BBne%27s_Spear_of_Night","Viconia%27s_Priestess_Robe","Viconia%27s_Walking_Fortress",'Moon_Devotion_Robe','Dark_Justiciar_Helmet']
for u in urls:sources+=f'- [{u.replace("_"," ")}](https://bg3.wiki/wiki/{u})\n'
sources+='\nCorrections verified against installed data: Corpsegrinder = MAG_SWA_Roaring_Maul; Walking Fortress = MAG_TheBulwark_Shield (not Justiciar Shield); Belm = MAG_PHB_OfSpeed_Scimitar; Jade dye = OBJ_Dye_BlackTeal. Exact values in the registry take precedence over guessed names.\n'
write('docs/SOURCES.md',sources)
write('docs/TESTING.md','''# TESTING

## What has been checked outside BG3

`test_armory.py` executes the actual runtime.lua in Lua through lupa with an instrumented mock of engine calls. It checks:

- SessionLoaded adds the action but creates zero items;
- actual Give() constructs 42 objects in preview / 29 in final;
- all 9 bags and every item have exactly their intended immediate owner;
- a second manual request creates another complete Armory;
- overlapping and combat requests are rejected;
- injected spawn and inventory failures roll back newly created objects;
- callbacks from an older session stop after loading another save;
- private/stable UUIDs, no vanilla stat replacement, native Light properties/selector flags, EN/RU text handles and preview/final separation.

`verify_package.py` extracts BOTH .pak files, compares all files against the build inputs, round-trips compiled roots/material banks and EN/RU localization with Divine, validates custom roots/resources and compares the two approved dragon templates with the saved 0.2.2 baseline.

These checks do not simulate BG3 rendering, native combat functors or actual engine API timing. No claim of successful in-game equip/combat/quest verification is made.

## First in-game pass

1. Use PREVIEW only, replacing the previous Dragon package. Restart BG3 fully, load a spare save. Confirm no unsolicited gear and that the new general action appears. Use it once outside combat.
2. Open outer bag, every character bag and both Shadowheart bags. Confirm names/icons/quantities, then request a second kit. Save/load and confirm no automatic third kit.
3. Equip the dragon pair: approved red/gold/fully red helmet preserved; armour medium AC16 + Dex up to2; helm has no medium-armour requirement; both keep the approved golden Legendary frame, with stats balanced around strong Very Rare equipment.
4. Oathbreaker: Carsomyr uses the requested Silver Sword model, only the grip is red; +3/radiant/ward apply. Cast Unweave against a whitelisted buff; confirm removal, action cost, short-rest recharge. Also confirm no removal of unrelated quest statuses.
5. Wyll at ordinary Warlock build: main-hand Claw + off-hand dagger without Dual Wielder; longsword proficiency and casting-ability attack/damage. Check sheath/weapon animations, Ashen Veil duration/no concentration, gauntlet +1AC only with Claw, counterspell reaction/level3/single long-rest charge. Test after unequip/re-equip and short/long rest.
6. Dagger: hit a living enemy with main/off hand and Extra Attack. Heal 1d4 at most once per turn. Check undead/construct exclusions, killing blow, damage immunity and full HP cases in combat log.
7. Karlach: confirm Dragon’s Breath is a red halberd (not an axe), then rage and use all five bonus-action element selectors. Exactly one 1d4 rider each hit; no original Hellflame Cleave, no accidental IsSpell/Rage interruption. Maul fire rider and critical Burning at most once/turn. Equip vanilla Bonespike + Cindermoth and apply Sinful dye manually.
8. Minthara: Icingdeath + Twinkle, both Light. +1AC while defender equipped, fire resistance/cold damage, Quench action and short rest. Try Long Cloak B with Jade/Swamp/Sage dyes and pick silhouette/colour. Check frost/blue glow does not flood surroundings.
9. Jaheira: Harper’s Woodland Armour uses Spidersilk Armour in wood-brown/green/bronze and is light armour, AC13 + Dex. Check her own body and at least one other body type; Belm/Sylvan dual wield unchanged.
10. Shadowheart Cleric: equip Shar spear/robe/fortress and helmet, then Selûne spear/moon robe. Compare palettes, robe skin/clipping, spear sheath, Moonbeam/Moonmote recharge, moon robe Mage Armour/Lunar Bulwark native dependency. Original quest weapons remain untouched, Selûne route remains unchanged.
11. Test dyes over custom wearable material overrides. Preview vanilla clothing intentionally starts native-coloured; supplied dyes perform the requested final colouring without global edits.
12. Confirm custom copied gear neither advances nor blocks original quests. Check cold/fire/lightning resistance, tooltip names and class requirements on the Russian and English clients.

## Finalization decisions still open

Vanilla displacement cloak, Bonespike, Cindermoth, Belm and chosen green cloak remain provisional natural-obtain candidates. Their possible inclusion in FINAL is a user decision after fitting. Final mode currently keeps custom gear and only four main dyes. Test-only comparison dyes are removed. See ITEMS.md for every row’s provisional status.

## Logs and failures

Lua writes `[Legacy Party Armory]` messages to Script Extender log/console; `LegacyPartyArmory.LastError` contains the latest rollback reason and `LastCreated` the last completed outer bag UUID. A request blocked during creation does not silently create a second kit.
''')
print('Documentation written')
