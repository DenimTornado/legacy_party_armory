# Legacy Party Armory

Исходники **0.3.3 PREVIEW** для Baldur’s Gate 3. Мод использует BG3 Script Extender (16+) и Lua. Комплект выдаётся только вручную действием **«Получить Legacy Party Armory»** вне боя.

## Исправления 0.3.3

Вещи создаются сразу внутри нужных рюкзаков через `TemplateAddTo`, с подтверждением каждого предмета. У наряда Орин убран ошибочный слот модели `VanityBody`; штатные данные модели наследуются целиком, а лагерный слот сохраняется в характеристиках. Добавлен `LegacyPartyArmory.log` в папке Script Extender.

При обновлении заменить предыдущую версию и для первой проверки загрузить сохранение до неудачной выдачи. 15 октября 2026 пользователь подтвердил: исправление устранило вылет в игре. Точная причина нативного сбоя не установлена по дампу. Подробности: [CHANGES_0.3.3.md](docs/CHANGES_0.3.3.md).

## Что изменено в 0.3.2

- Все custom-предметы остаются **Legendary**; ванильные preview-вещи сохраняют оригинальную редкость.
- Shadowheart: Selûne-набор удалён из выдачи. Остаётся один Shar-комплект.
- Shar’s Spear of Evening и Viconia’s Walking Fortress получают общую схему **чёрный/графит + глубокий лиловый** без постоянного emissive-glow.
- Dragon’s Breath: красным делается не только древко, но и металлическое лезвие. Постоянного glow нет.
- Постоянное свечение оставлено только для **Icingdeath** и **Twinkle**: Icingdeath — мягкое холодно-голубое, Twinkle — более заметное синее.
- Charon’s Claw, Carsomyr, Dragon’s Breath и кинжал Энтрери не имеют постоянного glow.
- Minthara PREVIEW: добавлена косметическая копия **Mutilated Carapace** в слот `VanityBody`, без боевых статов.
- Karlach PREVIEW: добавлены три варианта одного легендарного предмета **Ashen Heartguard / Страж Пепельного Сердца** с визуалами Unwanted Masterwork Scalemail, Bloodguzzler Garb и The Mighty Cloth.
- Страж Пепельного Сердца: AC 16 medium-armour baseline, Cold Resistance, 6 Temporary HP при входе в Rage и 2 Temporary HP раз в ход при нанесении Fire damage.

Финальный визуал брони Карлах пока **не выбран**: три варианта существуют только в PREVIEW. После примерки один останется, остальные будут удалены.

## Сборка

Нужны Windows PowerShell/PowerShell 7 и LSLib ExportTool / Divine.

```powershell
./Build.ps1 -Mode preview -Divine 'C:/Tools/ExportTool/Tools/Divine.exe'
./Build.ps1 -Mode final -Divine 'C:/Tools/ExportTool/Tools/Divine.exe'
```

`Build.ps1` копирует сохранённый рабочий snapshot `src/` во временную staging-папку, применяет `Apply-032.ps1`, компилирует LSX/XML через Divine и создаёт:

- `dist/LegacyPartyArmory_0.3.3_PREVIEW.pak`
- `dist/LegacyPartyArmory_0.3.3_FINAL.pak`

PREVIEW и FINAL одновременно не включать: UUID модуля общий.

## Структура Armory

Внешний `Legacy Party Armory` содержит Paladin, Wyll, Karlach, Minthara, Jaheira и Shadowheart. У Shadowheart теперь только вложенный набор **Shar**.

Выдача не происходит на загрузке сохранения, старте новой игры или переходе между уровнями. `LegacyPartyArmory.Give()` и игровое действие остаются единственными точками создания комплекта.

## Важное про PREVIEW

PREVIEW предназначен для живой примерки: туда входят custom-вещи, тестовые vanilla-вещи, dyes, три визуала Стража Пепельного Сердца и vanity-платье Орин. FINAL остаётся предварительным до визуального отбора.
