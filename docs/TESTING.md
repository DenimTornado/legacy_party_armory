# TESTING

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
