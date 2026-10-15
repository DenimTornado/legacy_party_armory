# 0.3.3 — inventory crash investigation hotfix

The reported failure happened when opening inventory **after** delivery finished.
There is no crash dump establishing the native fault location. This build fixes
an invalid equipment model slot and removes the world-spawn delivery path.
On 2026-10-15 the user confirmed that this hotfix resolves the reported crash
in game. The exact native fault location remains unconfirmed.

- Orin's cosmetic outfit no longer overrides `Equipment` with an unsupported
  `VanityBody` model slot. It inherits the complete native model configuration,
  including `Body` and race visuals. Its **stats** still use `VanityBody`, so it
  remains camp clothing without combat bonuses.
- Delivery uses native `TemplateAddTo(template, holder, 1, 0)` directly into the
  intended inventory. `CreateAt` and subsequent `ToInventory` are removed.
- Each step waits for `TemplateAddedTo` and verifies actual ownership before
  creating the next object. Delayed callbacks never repeat a creation request.
  Concurrent requests are rejected. Failed deliveries remove only instances
  recorded by that invocation.
- Session changes cancel queued work. Loading a save only adds the manual action.
- `LegacyPartyArmory.log` records the version, each request, confirmed instances,
  completion and errors in the Script Extender profile directory.
- Module UUID and equipment template IDs stay stable. Module Version64 increases
  from `36028797019013121` to `36028797019013122`.

The 0.3.2 selection, stats, colours and materials remain in this build. The three
Karlach armour options and Orin outfit remain in PREVIEW.

Validation: 14 Python/Lua tests, both package builds and decoded package checks.
Lua tests cover synchronous/asynchronous events, duplicate/unrelated events,
inventory ownership, native errors, missing events, combat and session changes.
These tests do not emulate native rendering; the in-game confirmation above
comes from the user's check of the delivered PREVIEW build.

Install the 0.3.3 PREVIEW package in place of 0.3.2, with the game closed. For the
first check, load a save from **before** the failed delivery and request a fresh
Armory with the manual action. This avoids testing already-created bad instances.
Enable only one version and one mode of this module.

Native API references:
[TemplateAddTo](https://docs.baldursgate3.game/index.php?title=TemplateAddTo),
[TemplateAddedTo](https://docs.baldursgate3.game/index.php?title=TemplateAddedTo).
