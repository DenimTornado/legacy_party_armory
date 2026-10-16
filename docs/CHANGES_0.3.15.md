# 0.3.15 — equipment icon pass

Private inventory, tooltip and controller icons cover all 18 custom equipment
items in FINAL and PREVIEW. The four original BG2 weapon designs are used as
references; custom equipment follows the existing BG3 model and selected colours.
The established dragon artwork is retained. Carsomyr is included again under the
user's explicit instruction to create a new BG2-based version.

The icon atlas is separate from native atlases. Root UUIDs, stats, models, dyes
and delivery stay unchanged from the current source revision.

Build now requires Python with Pillow in addition to Divine. Use `-Python` or
`BG3_PYTHON` to choose the executable. See `assets/icons/README.md` and the catalog
for the artwork, reference sources and compilation details.

Existing local fixes are retained: removal of stale baked palettes and escaped
PowerShell apostrophes in the English localization patches.

An in-game check is still needed for actual UI rendering and art approval.
