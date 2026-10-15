# Build and source snapshot

The root `Build.ps1` builds the checked-in 0.3.1 snapshot independently of the original research directory. It requires an external LSLib Divine.exe and its normal dependencies. No unpacked BG3 package database is needed for this snapshot build.

LSF banks were decoded to LSX with the same Divine used for the original packages. Localization LOCA files were decoded to XML. The build compiles only the resources listed in `config/resource-files.json`; other LSX files, including GUI icon atlases and module metadata, retain their native text format. DDS files are included as assets, including the grip selection mask and red gradient lookup table.

PREVIEW and FINAL share definitions, UUIDs, visuals and stats. Only the nested delivery manifest and mode metadata differ. The generated Lua manifest is derived from the matching config JSON at build time. Original LSF compression may produce different binary hashes after round-trip; decoded resource content must remain equivalent.

## Editing

- Edit Lua in `src/Mods/DenimDragonArmor/ScriptExtender/Lua/BootstrapServer.lua`.
- Edit gameplay in `src/Public/DenimDragonArmor/Stats/Generated/Data/`.
- Edit template/model/material definitions in the corresponding `src/Public/DenimDragonArmor/**/*.lsx` files.
- Edit EN/RU text in `src/Localization/English/DenimDragonArmor.xml` and `src/Localization/Russian/DenimDragonArmor.xml`.
- Edit which items are granted in `config/preview.json` and `config/final.json`.

The source snapshot preserves the original package paths and stable UUIDs. GUI/controller icons under `src/Public/Game` have custom icon names; these do not replace vanilla icon identifiers.

## Original authoring tools

`authoring/` contains the original generators and tests, preserved without pretending they are portable standalone tools. They expect the earlier Dragon Armor build helpers, `baseline_0.2.2`, a native-game `index.json`, resource caches, and selected shader/mesh exports. Those caches are intentionally excluded because they contain bulk unpacked game data. The original tests also require Python/lupa and their original directory layout.

`make_grip_mask.py` generates the custom grip selection from the exported stock sword mesh; it does not repaint the entire native blade texture. The precomputed DDS needed by the current version is already included in `src/`. Divine model conversion may need Granny2.dll from the user's existing toolchain; it is not redistributed here.

`verification/` records checks of the original 0.3.1 packages. A build made from this repository should be verified by decoding its output and comparing templates, stats, localization and manifests; compressed package hashes are not a reliable semantic comparison after XML round-trips.

## Repository checks

```powershell
python -m unittest discover -s tests -v
```

These checks validate source/config consistency and the latest requested model, rarity and material changes. They do not replace in-game rendering, animation and combat checks.
