# Legacy Party Armory 0.3.4

Source-only visual/preview revision. No `.pak` was built as part of this change.

## Armory layout

Shadowheart now has one bag only. The obsolete nested `shar` bag is removed from both PREVIEW and FINAL configs; the remaining Shar gear is placed directly in `shadowheart`.

## Weapon effects

The previous material-only glow experiment is replaced with stock BG3 item mechanisms:

- **Icingdeath** receives `MAG_FROST_FROST_WEAPON`, the weapon status used by Mourning Frost. Because that status already carries the frost weapon damage, the old explicit `WeaponDamage(1d4,Cold)` is removed from Icingdeath to avoid stacking.
- **Twinkle** receives `MAG_FARLIN_DAGGER_LIGHT_TECHNICAL` and `MAG_Light_FarlinDagger_Passive`, matching Gleamdance Dagger's technical light/toggle approach.
- **Dragon's Breath** receives custom status `LPA_EVERBURN_VISUAL`, which reuses Everburn Blade's item VFX (`StatusEffectOverrideForItems`) without Everburn's damage boost. Dragon's Breath therefore keeps its existing selectable elemental `1d4` unchanged.

Experimental emissive multipliers on those three custom materials are zeroed so the stock status/VFX path owns the visible effect.

## Karlach

The rejected preview armour visuals are removed.

`Ashen Heartguard / Страж Пепельного Сердца` keeps stable custom root UUID `aef31c6f-07a7-5b20-9007-e910ca009ea1`, but its visual parent becomes Karlach's unique starter armour/clothes root `2e3a2651-18ce-44b0-b7bd-3e2565bf666c`.

Mechanics remain:

- Legendary
- AC 16
- Cold Resistance
- 6 Temporary Hit Points when Rage starts
- 2 Temporary Hit Points once per turn when dealing Fire damage

The two obsolete trial custom roots are removed from staging, and vanilla Bonespike/Cindermoth preview candidates are removed from Karlach's bag.

## Minthara / Orin

The working 0.3.3 Orin setup is retained: native `Body` equipment visual data, camp/vanity slot controlled by Stats.

The custom Orin dress now starts with the **Black and Furnace Red** colour preset (`963387ce-05e6-a6bf-ac25-4d81624fa8ff`). Green preview dyes were removed.

## Shadowheart palette

Shar spear and Walking Fortress remain black/lilac but are slightly brighter:

- `Color`: `0.16 0.035 0.24`
- `VariationColor`: `0.22 0.06 0.32`

No permanent glow is added.

## Wyll hat preview

PREVIEW adds several vanilla headwear candidates to test tiefling horns and clipping:

- Marksmanship Hat
- Birthright
- Hat of Fire Acuity
- Cap of Curing
- Circlet of Hunting
- Diadem of Arcane Synergy

No new Wyll hat is promoted to FINAL in this revision.
