# Legacy Party Armory — custom icon pass

The custom items listed below must receive unique BG3-style icons. Do not reuse vanilla inventory art for these items in the final package.

## Technical output per item

- 380x380 tooltip icon, transparent background, BG3-style lower fade.
- 144x144 controller icon, transparent background, no fade.
- 64x64 atlas tile.
- Shared basename across all three representations.
- Final 64px tiles packed into a dedicated `LegacyPartyArmory_Icons` atlas and wired through `GUI/Icons_Items.lsx` + UI atlas resource.

## Art direction

Match vanilla Baldur's Gate 3 inventory rendering: isolated object, painterly-realistic PBR materials, strong readable silhouette, three-quarter view, subtle rim light, restrained magical effects, transparent background. Avoid generic fantasy clip-art, flat vector art and excessive bloom.

## Active custom item set

### Paladin
- `DENIM_RedDragon_Armor` — red dragon scale cuirass, dark iron fittings.
- `DENIM_RedDragon_Helmet` — matching draconic helmet, cold metallic horns/edges.

### Wyll
- `LPA_CharonsClaw` — dark oxblood longsword, blackened steel, restrained infernal character.
- `LPA_CharonsGauntlet` — black leather/steel gauntlet with a small arcane ward sigil.
- `LPA_EntreriDagger` — slender dark dagger with muted crimson/necrotic accent.
- `LPA_WyllMarksmanHat` — Marksmanship Hat silhouette, dark leather, silver wing details, one subtle blue arcane glint. Display name: Deadeye of the Frontiers / Взор Пограничья.

### Karlach
- `LPA_DragonsBreath` — red-bladed halberd with active flame VFX suggested only at the edge.
- `LPA_InfernalMaul` — heavy blackened maul with ember seams.
- `LPA_AshenHeartguard` — Karlach starter-clothing silhouette treated as legendary armour: charcoal/black leather-metal base, cold steel, azure/cyan cooling accents.

### Minthara
- `LPA_Icingdeath` — scimitar with pale frost along the blade.
- `LPA_Twinkle` — scimitar with a cleaner saturated blue magical light.
- `LPA_OrinVanity` — black macabre dress/carapace silhouette, elegant drow presentation rather than gore-forward. Display name: Veil of Menzoberranzan / Покров Мензоберранзана.

### Jaheira
- `LPA_HarperFinery` — woodland studded leather, muted green/brown, bronze fittings, leaf/Harper visual language kept subtle.

### Shadowheart
- `LPA_SharSpear` — dark spear with electric royal-blue `0 0.3 1` accent rather than purple.
- `LPA_ViconiaRobe` — black Viconia robe, understated Shar detailing.
- `LPA_WalkingFortress` — dark shield with the same electric royal-blue accent as the spear.

## Naming

Recommended icon IDs:

- `LPA_ICON_DragonArmor`
- `LPA_ICON_DragonHelmet`
- `LPA_ICON_CharonsClaw`
- `LPA_ICON_CharonsGauntlet`
- `LPA_ICON_EntreriDagger`
- `LPA_ICON_WyllMarksmanHat`
- `LPA_ICON_DragonsBreath`
- `LPA_ICON_InfernalMaul`
- `LPA_ICON_AshenHeartguard`
- `LPA_ICON_Icingdeath`
- `LPA_ICON_Twinkle`
- `LPA_ICON_MenzoberranzanVeil`
- `LPA_ICON_HarperWoodlandArmor`
- `LPA_ICON_SharSpear`
- `LPA_ICON_ViconiaRobe`
- `LPA_ICON_WalkingFortress`

## Workflow rule

Generate/approve the visual set first. Only after the icon art is final should DDS conversion, atlas packing and RootTemplate `Icon` rewiring be committed. Keep the icon integration in a dedicated commit so it can be reverted independently from Stats/material changes.
