# Legacy Party Armory — equipment icon pass 0.3.15

18 private equipment icons are wired in PREVIEW and FINAL. The rule is BG2 design
for items from BG2, and the finished BG3 model/palette for custom items.

The two established dragon images are retained. Carsomyr is newly drawn from its
BG2 reference, following the user's explicit request to include it in this pass.

| Item key | Design reference | Artwork |
|---|---|---|
| `DragonArmor` | BG2 | `LPA_ICON_DragonArmor` |
| `DragonHelmet` | BG2 | `LPA_ICON_DragonHelmet` |
| `Carsomyr` | BG2 | `LPA_ICON_Carsomyr` |
| `CharonsClaw` | BG3 in-game model | `LPA_ICON_CharonsClaw` |
| `CharonsGauntlet` | BG3 in-game model | `LPA_ICON_CharonsGauntlet` |
| `EntreriDagger` | BG3 in-game model | `LPA_ICON_EntreriDagger` |
| `WyllLeatherArmor` | BG3 in-game model | `LPA_ICON_WyllLeatherArmor` |
| `WyllMarksmanHat` | BG3 in-game model | `LPA_ICON_WyllMarksmanHat` |
| `DragonsBreath` | BG2 | `LPA_ICON_DragonsBreath` |
| `InfernalMaul` | BG3 in-game model | `LPA_ICON_InfernalMaul` |
| `AshenHeartguard` | BG3 in-game model | `LPA_ICON_AshenHeartguard` |
| `Icingdeath` | BG2 | `LPA_ICON_Icingdeath` |
| `Twinkle` | BG2 | `LPA_ICON_Twinkle` |
| `MenzoberranzanVeil` | BG3 in-game model | `LPA_ICON_MenzoberranzanVeil` |
| `HarperFinery` | BG3 in-game model | `LPA_ICON_HarperFinery` |
| `SharSpear` | BG3 in-game model | `LPA_ICON_SharSpear` |
| `ViconiaRobe` | BG3 in-game model | `LPA_ICON_ViconiaRobe` |
| `WalkingFortress` | BG3 in-game model | `LPA_ICON_WalkingFortress` |

Each icon has a transparent PNG master, a 64px atlas tile, a 380px tooltip DDS,
and a 144px controller DDS. The atlas is private to the module; native atlases
and vanilla preview items are unchanged.

See `assets/icons/catalog.json` for template UUIDs and reference sources,
`assets/icons/prompts.json` for the prompt set, and `assets/icons/preview/` for
large previews alongside actual 64px tiles. New artwork uses built-in imagegen.

Compilation is deterministic from the saved masters with Python/Pillow. The
verification script decodes the release PAK and validates texture-bank identity,
UVs, all 18 root assignments, tile pixels, alpha and DDS dimensions. Automated
checks do not replace an in-game UI/art review.
