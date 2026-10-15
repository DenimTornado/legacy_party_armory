# Legacy Party Armory

Исходники **0.3.4 PREVIEW** для Baldur’s Gate 3. Мод использует BG3 Script Extender (16+) и Lua. Комплект выдаётся только вручную действием **«Получить Legacy Party Armory»** вне боя.

## 0.3.4 — визуальный проход

- Shadowheart: лишний вложенный мешок Shar удалён. Единственный тёмный комплект лежит сразу в мешке Shadowheart.
- Shar’s Spear of Evening и Viconia’s Walking Fortress оставлены чёрно-лиловыми, но палитра немного осветлена.
- Icingdeath использует штатный frost-эффект Mourning Frost.
- Twinkle использует штатный light-механизм Gleamdance Dagger.
- Dragon’s Breath использует визуальный fire-effect Everburn Blade без дополнительного огненного урона: выбранная стихия оружия остаётся единственным `1d4`.
- Старый экспериментальный emissive для этих трёх custom-оружий отключён.
- Наряд Орин сохраняет рабочую схему 0.3.3 (`Body` в Equipment + лагерный слот в Stats) и стартует с палитрой Black and Furnace Red.
- Karlach: три тестовых варианта брони удалены. **Ashen Heartguard / Страж Пепельного Сердца** теперь использует внешний вид её уникальной стартовой одежды, сохраняя утверждённые характеристики: AC 16, Cold Resistance, 6 Temporary HP при входе в Rage и 2 Temporary HP раз за ход при нанесении Fire damage.
- Wyll PREVIEW: добавлены несколько ванильных головных уборов для живой проверки рогов/клиппинга. В FINAL они пока не попадают.

## Стабильная база 0.3.3

Вещи создаются сразу внутри нужных рюкзаков через `TemplateAddTo`, с подтверждением каждого предмета. Для наряда Орин используется штатный `Body` model slot; эта схема была проверена в игре и устранила вылет при открытии инвентаря.

## Сборка

Нужны Windows PowerShell/PowerShell 7 и LSLib ExportTool / Divine.

```powershell
./Build.ps1 -Mode preview -Divine 'C:/Tools/ExportTool/Tools/Divine.exe'
./Build.ps1 -Mode final -Divine 'C:/Tools/ExportTool/Tools/Divine.exe'
```

`Build.ps1` копирует известный рабочий snapshot `src/` во временную staging-папку, применяет `Apply-032.ps1` и `Apply-034.ps1`, затем компилирует LSX/XML и создаёт:

- `dist/LegacyPartyArmory_0.3.4_PREVIEW.pak`
- `dist/LegacyPartyArmory_0.3.4_FINAL.pak`

PREVIEW и FINAL одновременно не включать: UUID модуля общий.

## Структура Armory

Внешний `Legacy Party Armory` содержит мешки Paladin, Wyll, Karlach, Minthara, Jaheira и Shadowheart. У Shadowheart больше нет дополнительного вложенного мешка.

Выдача не происходит на загрузке сохранения, старте новой игры или переходе между уровнями. `LegacyPartyArmory.Give()` и игровое действие остаются единственными точками создания комплекта.

## PREVIEW

PREVIEW предназначен для живой примерки. В набор Wyll дополнительно положены:

- Marksmanship Hat;
- Birthright;
- Hat of Fire Acuity;
- Cap of Curing;
- Circlet of Hunting;
- Diadem of Arcane Synergy.

Они добавлены только для оценки того, какие модели нормально работают с рогами Уилла. Финальный головной убор пока не выбран.

FINAL остаётся предварительным до этой визуальной проверки.
