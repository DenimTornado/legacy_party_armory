# SOURCES

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
| MAG_GreaterSilver_Greatsword | `MAG_GreaterSilver_Greatsword` | `f01c3f5d-c542-420f-86c5-bdddf7819e29` | `bfaa0020-b21f-5195-37b2-7adf50b7907a` | `../xml_gustav/Public/GustavDev/RootTemplates/_merged.lsx` |
| WPN_HUM_Longsword_A_2 | `WPN_Longsword_2` | `e3b2adb6-7493-466e-9c65-4281fb74e83f` | `910f74da-8b12-9762-1e97-f6f3457d80de` | `../xml/Public/Shared/RootTemplates/_merged.lsx` |
| ARM_Gloves_Leather | `ARM_Gloves_Leather` | `8e34fd76-8b6d-48a5-89e3-942289bec31e` | `4fbb8bb3-9eb4-2ef7-b1f6-d843dcdd628f` | `../xml/Public/Shared/RootTemplates/_merged.lsx` |
| MAG_WYR_Orin_Bhaalist_Dagger | `MAG_WYR_Orin_Bhaalist_Dagger` | `d90abf24-3c4e-4bbf-84aa-def05ca9962a` | `f67bf9d2-2bd7-4d3f-5723-6e41f8e0ee3f` | `../xml_gustav/Public/GustavDev/RootTemplates/_merged.lsx` |
| WPN_HUM_Halberd_A_2 | `WPN_Halberd_2` | `0e3b29e8-572f-459d-b382-234ec53b1c08` | `f35f653b-af18-d127-0eca-045fa60d5dbe` | `../xml/Public/Shared/RootTemplates/_merged.lsx` |
| MAG_SWA_Roaring_Maul | `MAG_SWA_Roaring_Maul` | `c1aa1bf6-2bb8-4472-9e18-b5285101c4b3` | `86ec3b25-0a9f-3ed1-e225-bf38870a2a1f` | `../xml_gustav/Public/GustavDev/RootTemplates/_merged.lsx` |
| WPN_HUM_Scimitar_Adamantine_A | `MAG_MeleeDebuff_AttackDebuff1_OnDamage_Scimitar` | `503b4f8d-da61-4fc1-a4b7-cad124a10c69` | `238323eb-451a-858f-1ccc-6860228d61f1` | `../xml_gustav/Public/Gustav/RootTemplates/_merged.lsx` |
| WPN_HUM_Scimitar_A_2 | `WPN_Scimitar_2` | `5193af64-48c1-406f-90bf-87f7f01b4684` | `26931062-ac78-ded7-8bd2-6417ef9dc4af` | `../xml/Public/Shared/RootTemplates/_merged.lsx` |
| GOB_DrowCommander_Armor_Leather | `ARM_StuddedLeather_Body_Drow` | `c0c0534c-b7fc-4d0b-a335-b8f4c548852d` | `b81997b7-91ee-3c84-5ff4-e0abf8919d9a` | `../xml/Public/Shared/RootTemplates/_merged.lsx` |
| MAG_SHA_SharBlessing_Spear | `MAG_SHA_SharBlessing_Spear` | `61f31bf6-47ec-41e1-9385-2f6c26facc87` | `83da4a21-b02c-6d9c-43e9-f0219359164e` | `../xml/Public/SharedDev/RootTemplates/_merged.lsx` |
| MAG_Viconia_Robe | `MAG_Viconia_Robe` | `bf59b289-5603-479f-8fd3-7cb258d31ba5` | `16a6dbf2-888c-a986-ad5c-49e5d861f76c` | `../xml_gustav/Public/GustavDev/RootTemplates/_merged.lsx` |
| MAG_TheBulwark_Shield | `MAG_TheBulwark_Shield` | `4f313dde-14bb-43a2-abdd-07b2eb38b33a` | `dc37c116-c43b-e9fd-4f52-b601ccff8766` | `../xml_gustav/Public/GustavDev/RootTemplates/_merged.lsx` |
| MAG_SHA_SeluneBlessing_Spear | `MAG_SHA_SeluneBlessing_Spear` | `2eeabe97-8f29-4f4f-827e-6cfcd8fd1779` | `83da4a21-b02c-6d9c-43e9-f0219359164e` | `../xml/Public/SharedDev/RootTemplates/_merged.lsx` |
| MAG_Selunite_Isobel_Robe | `MAG_Selunite_Isobel_Robe` | `3b498702-834f-4989-a9d1-c0f3b38fbcfc` | `f13d8fa8-590f-0958-4b61-a11a003c3dc1` | `../xml_gustav/Public/GustavDev/RootTemplates/_merged.lsx` |
| MAG_Shadow_StealthBonusWhileObscured_Armor | `MAG_Shadow_StealthBonusWhileObscured_Armor` | `3ce4d5d2-3ed0-470e-8cea-bdac81a60583` | `5792b6ab-628b-e1cf-4c37-34c3124f5d5e` | `../xml_gustav/Public/GustavDev/RootTemplates/_merged.lsx` |
| MAG_Generic_01_Wizard_Hat_E | `MAG_ofMarksmanship_Hat` | `f67b0733-ad73-4d1b-94fd-e3e0236623ca` | `502b4b13-7b3f-7454-c7ef-f96f26ba6ea0` | `../xml_gustav/Public/GustavDev/RootTemplates/_merged.lsx` |
| MAG_PHB_CloakOfDisplacement_Cloak | `MAG_PHB_CloakOfDisplacement_Cloak` | `257aed3e-370d-40b3-b464-de10257dd82b` | `824260e2-4b43-de06-5e6d-ed8d314b2e35` | `../xml_gustav/Public/GustavDev/RootTemplates/_merged.lsx` |
| LOOT_Dye_BlackRed_01 | `OBJ_Dye_BlackRed` | `bb108620-186f-4a00-b7de-af9329d5497b` | `0adb9e3a-c865-1cf7-aad1-6fbf9261ccbe` | `../xml/Public/Shared/RootTemplates/_merged.lsx` |
| LOOT_Dye_BlackBlue_01 | `OBJ_Dye_BlackBlue` | `02bb51c0-00e5-408c-8e11-8de7b9580c04` | `0adb9e3a-c865-1cf7-aad1-6fbf9261ccbe` | `../xml/Public/Shared/RootTemplates/_merged.lsx` |
| MAG_BarbMonk_Cloth_B_1 | `MAG_Barbarian_BoneSpike_Armor` | `7cca51a5-bfa6-4c65-b2d9-ef0167762a19` | `e90a01fe-f187-f592-93d3-02549c8e24af` | `../xml_gustav/Public/GustavDev/RootTemplates/_merged.lsx` |
| MAG_Fire_BurningOnDamaged_Cloak | `MAG_Fire_BurningOnDamaged_Cloak` | `8a31c554-1545-4647-b24d-93cf5d81df18` | `e0982a2a-910a-badd-b519-a26b87b66bdf` | `../xml_gustav/Public/GustavDev/RootTemplates/_merged.lsx` |
| LOOT_Dye_WhiteRed_01 | `OBJ_Dye_WhiteRed` | `1d0d3883-6196-4ccd-8a49-8e4fb84f6c6b` | `0adb9e3a-c865-1cf7-aad1-6fbf9261ccbe` | `../xml/Public/Shared/RootTemplates/_merged.lsx` |
| ARM_Cloak_Long_B | `ARM_Cloak_Long_B` | `8ed92d35-159c-493c-a8da-fba455f181e4` | `e0982a2a-910a-badd-b519-a26b87b66bdf` | `../xml/Public/SharedDev/RootTemplates/_merged.lsx` |
| LOOT_Dye_BlackTeal_01 | `OBJ_Dye_BlackTeal` | `94ef7170-1c1d-489a-9c18-55209d864e3a` | `0adb9e3a-c865-1cf7-aad1-6fbf9261ccbe` | `../xml/Public/Shared/RootTemplates/_merged.lsx` |
| LOOT_Dye_GreenSwamp_01 | `OBJ_Dye_GreenSwamp` | `a13f6fad-bca8-40c0-b5b1-592832c73050` | `0adb9e3a-c865-1cf7-aad1-6fbf9261ccbe` | `../xml/Public/Shared/RootTemplates/_merged.lsx` |
| LOOT_Dye_GreenSage_01 | `OBJ_Dye_GreenSage` | `ad60be55-7a95-4dcb-ae55-908a97f9955a` | `0adb9e3a-c865-1cf7-aad1-6fbf9261ccbe` | `../xml/Public/Shared/RootTemplates/_merged.lsx` |
| MAG_PHB_OfSpeed_Scimitar | `MAG_PHB_OfSpeed_Scimitar` | `d60524f4-583e-4b16-91b2-871221d441cf` | `9b9763fc-50a2-5d32-de45-3e0765f11ae7` | `../xml_gustav/Public/GustavDev/RootTemplates/_merged.lsx` |
| MAG_HAV_Sylvan_Scimitar | `MAG_HAV_Sylvan_Scimitar` | `b9656931-da39-4024-92a2-f45264593b14` | `b75b6daa-a57a-9093-652e-dbd5f0ebef13` | `../xml/Public/SharedDev/RootTemplates/_merged.lsx` |
| UNI_DarkJusticiar_Helmet | `UNI_DarkJusticiar_Helmet` | `3523b640-e9da-4d89-b031-6ffe1d5fd3ed` | `050e3c99-7a12-422f-10ab-4f5544cf7b10` | `../xml_gustav/Public/GustavDev/RootTemplates/_merged.lsx` |
| LOOT_Dye_WhiteBlack_01 | `OBJ_Dye_WhiteBlack` | `ffdb4490-cbaf-4eac-97f8-893564d7ead9` | `0adb9e3a-c865-1cf7-aad1-6fbf9261ccbe` | `../xml/Public/Shared/RootTemplates/_merged.lsx` |

For wearable items, one root VisualTemplate is the inventory/world mesh. Equipped visual maps are kept in `Equipment.Visuals` for each body/race; the clone pass remaps these to private VisualBank IDs. All map entries are preserved.

## Vanilla item references

- [Silver Sword of the Astral Plane](https://bg3.wiki/wiki/Silver_Sword_of_the_Astral_Plane)
- [Halberd %2B2](https://bg3.wiki/wiki/Halberd_%2B2)
- [Bloodthirst](https://bg3.wiki/wiki/Bloodthirst)
- [Corpsegrinder](https://bg3.wiki/wiki/Corpsegrinder)
- [Adamantine Scimitar](https://bg3.wiki/wiki/Adamantine_Scimitar)
- [Scimitar %2B2](https://bg3.wiki/wiki/Scimitar_%2B2)
- [Penumbral Armour](https://bg3.wiki/wiki/Penumbral_Armour)
- [Marksmanship Hat](https://bg3.wiki/wiki/Marksmanship_Hat)
- [Cloak of Displacement](https://bg3.wiki/wiki/Cloak_of_Displacement)
- [Bonespike Garb](https://bg3.wiki/wiki/Bonespike_Garb)
- [Cindermoth Cloak](https://bg3.wiki/wiki/Cindermoth_Cloak)
- [Belm](https://bg3.wiki/wiki/Belm)
- [Sylvan Scimitar](https://bg3.wiki/wiki/Sylvan_Scimitar)
- [Spidersilk Armour](https://bg3.wiki/wiki/Spidersilk_Armour)
- [Shar%27s Spear of Evening](https://bg3.wiki/wiki/Shar%27s_Spear_of_Evening)
- [Sel%C3%BBne%27s Spear of Night](https://bg3.wiki/wiki/Sel%C3%BBne%27s_Spear_of_Night)
- [Viconia%27s Priestess Robe](https://bg3.wiki/wiki/Viconia%27s_Priestess_Robe)
- [Viconia%27s Walking Fortress](https://bg3.wiki/wiki/Viconia%27s_Walking_Fortress)
- [Moon Devotion Robe](https://bg3.wiki/wiki/Moon_Devotion_Robe)
- [Dark Justiciar Helmet](https://bg3.wiki/wiki/Dark_Justiciar_Helmet)

Corrections verified against installed data: Corpsegrinder = MAG_SWA_Roaring_Maul; Walking Fortress = MAG_TheBulwark_Shield (not Justiciar Shield); Belm = MAG_PHB_OfSpeed_Scimitar; Jade dye = OBJ_Dye_BlackTeal. Exact values in the registry take precedence over guessed names.
