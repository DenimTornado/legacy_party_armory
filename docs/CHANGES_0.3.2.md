# 0.3.2 visual/gameplay pass

## Решения

- Custom rarity: все собственные предметы Legacy Party Armory — Legendary. Оригинальные vanilla preview-items сохраняют штатную rarity.
- Shadowheart: Selûne branch исключён из PREVIEW/FINAL distribution. Тёмный Shar/Viconia комплект признан основным.
- Shar weapon + shield palette: graphite/black base, deep lilac magical/decorative accents, no permanent emissive glow.
- Dragon’s Breath: entire halberd, including blade, should read as red metal; no permanent glow.
- Permanent weapon glow is intentionally limited to Icingdeath (restrained pale/cold blue) and Twinkle (brighter saturated blue).
- Charon’s Claw remains non-emissive; its magical identity is ash/smoke rather than a permanent neon blade.
- Carsomyr, Entreri dagger and Dragon’s Breath remain non-emissive.

## Karlach — Ashen Heartguard / Страж Пепельного Сердца

PREVIEW contains three identical-stat copies to compare visuals:

1. Unwanted Masterwork Scalemail
2. Bloodguzzler Garb
3. The Mighty Cloth

Shared mechanics:

- Legendary
- medium-armour combat baseline, AC 16
- Cold Resistance
- entering Rage: 6 Temporary Hit Points
- once per turn when dealing Fire damage: 2 Temporary Hit Points

Lore:

> Внутренние пластины отводят жар от инфернального двигателя, не позволяя ему пожрать носителя изнутри. Такое горячее сердце нельзя погасить — его можно только удержать достаточно холодным, чтобы оно билось дальше.

The final armour visual is deliberately not selected before another in-game fitting pass.

## Minthara vanity

PREVIEW receives a custom copy of Mutilated Carapace: visual inherited from Orin’s outfit, `VanityBody` slot, no combat bonuses, custom Legendary presentation, dyeable through inherited visuals/materials.

## Build implementation

`src/` remains the known-good 0.3.1 snapshot. `Apply-032.ps1` patches the staging copy before Divine compilation, which keeps the baseline recoverable while making the 0.3.2 build reproducible.
