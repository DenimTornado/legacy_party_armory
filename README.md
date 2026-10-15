# Legacy Party Armory

Актуальная рабочая линия: **0.3.13 PREVIEW / FINAL** для Baldur’s Gate 3.

Мод использует BG3 Script Extender и Lua. Комплект выдаётся только вручную действием **«Получить Legacy Party Armory»** вне боя. Автоматической выдачи при загрузке сохранения нет.

## Текущая архитектура

`src/` — известный рабочий базовый snapshot. `Build.ps1` копирует его во временный staging и последовательно применяет только перечисленные в самом `Build.ps1` patch-файлы.

**Источник истины для содержимого мешков:**
- `config/preview.json`
- `config/final.json`

**Источник истины для runtime-поведения:**
- `src/Mods/DenimDragonArmor/ScriptExtender/Lua/BootstrapServer.lua`
- staging patches, которые явно вызываются из `Build.ps1`

Старые неиспользуемые color-patches удалены. Не добавляйте второй механизм окраски поверх `ItemDye`: для вещей Уилла, Минтары и Карлах начальный цвет задаётся только после создания экземпляра предмета через `BootstrapServer.lua`.

## 0.3.13

- Удалены все отдельные банки красок из PREVIEW и FINAL. Цветные consumable-предметы больше не должны появляться в рюкзаках Armory.
- Уилл:
  - **Доспех Клинка Фронтира** — custom Legendary copy Leather Armour +2;
  - **Взор Клинка Фронтира** — custom Legendary copy Marksmanship Hat;
  - оба предмета окрашиваются runtime-механизмом `ItemDye`;
  - броня ориентирована на spellblade/warlock: AC, spell attacks, Spell Save DC и Concentration;
  - шляпа — Initiative, ranged spell attack и Perception.
- Минтара:
  - **Покров Мензоберранзана** использует visual Mutilated Carapace;
  - рабочая схема слота остаётся `Body` на уровне equipment visual;
  - цвет задаётся только runtime `ItemDye`.
- Карлах:
  - **Страж Пепельного Сердца** использует visual её стартовой одежды;
  - механика остаётся: AC 16, Cold Resistance, 6 Temporary HP при входе в Rage, 2 Temporary HP раз в ход при нанесении Fire damage;
  - текущий тестовый цвет — **Boreal Blue**, через runtime `ItemDye`.
- Shadowheart:
  - без вложенного Shar-мешка;
  - копьё и щит используют custom material-параметры, а не dye consumables.
- Icingdeath использует vanilla frost-механику Mourning Frost.
- Twinkle использует vanilla Gleamdance light-механику.
- Dragon’s Breath использует визуальный fire-effect Everburn без дополнительного fire damage.

## Сборка

Нужны Windows PowerShell/PowerShell 7 и LSLib ExportTool / Divine.

```powershell
./Build.ps1 -Mode preview -Divine 'C:/Tools/ExportTool/Tools/Divine.exe'
./Build.ps1 -Mode final -Divine 'C:/Tools/ExportTool/Tools/Divine.exe'
```

Результат:

- `dist/LegacyPartyArmory_0.3.13_PREVIEW.pak`
- `dist/LegacyPartyArmory_0.3.13_FINAL.pak`

PREVIEW и FINAL одновременно не включать: UUID модуля общий.

## Структура Armory

Внешний `Legacy Party Armory` содержит мешки:
- Paladin
- Wyll
- Karlach
- Minthara
- Jaheira
- Shadowheart

У Shadowheart дополнительного вложенного мешка больше нет.

## Важное про authoring/

`authoring/` содержит исходную генераторную архитектуру и исторический spec ранней версии. Текущий `Build.ps1` **не регенерирует мод из `authoring/armory_spec.py`**. Не используйте старый spec как источник актуального состава без предварительной синхронизации с `config/*.json` и текущими staging patches.
