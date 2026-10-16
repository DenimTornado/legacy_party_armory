# Legacy Party Armory equipment icons

One private icon per active modified equipment item: 18 entries in `catalog.json`.
Vanilla preview-only items and bags keep their native icons.

- BG2 items: retain the original game's visual identity in BG3 painted item style.
  Carsomyr, Dragon's Breath, Icingdeath and Twinkle use original BG2 sprites as
  references. Sources are recorded per item in the catalog.
- Custom items: retain the current BG3 model silhouette and the mod's selected
  material/dye palette. Native 64px atlas crops are design references only.
- The already-approved red/gold dragon armour and all-red helmet artwork are
  retained as the set's established visual reference, with new private icon IDs.

`masters/` contains transparent full-resolution PNG artwork. New artwork uses the
built-in imagegen tool, with one independent generation per asset. `prompts.json`
records the subject/prompt set. No API-key or external generation service is used
by the build itself.

`authoring/build_icons.py` converts these masters deterministically during staging:

- 64px tiles in a private 512x256 RGBA DDS atlas with transparent gutters;
- 380px tooltip DDS, subtle lower-edge fade;
- 144px controller DDS;
- private GUI atlas descriptor and texture-bank entry;
- icon assignments on exactly the 18 custom root templates.

Requires Python with Pillow. Example:

```powershell
./Build.ps1 -Mode preview -Python C:/Python/python.exe -Divine C:/Tools/Divine.exe
```

The icon builder changes icon references only. It does not change any equipment
stats, visual models, materials, dye selections or delivery logic.
