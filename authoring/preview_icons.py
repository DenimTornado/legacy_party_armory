"""Create a review sheet and local gallery from the final icon masters."""
from pathlib import Path
import html
import json
from PIL import Image, ImageDraw, ImageFont
from build_icons import fit_icon

ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / 'assets/icons/catalog.json').read_text(encoding='utf-8'))
out = ROOT / 'assets/icons/preview'
out.mkdir(parents=True, exist_ok=True)
sheet = Image.new('RGB', (1320, 840), '#151a21')
draw = ImageDraw.Draw(sheet)
font_path = Path('C:/Windows/Fonts/segoeui.ttf')
font = ImageFont.truetype(str(font_path), 15) if font_path.exists() else ImageFont.load_default()
cards = []
for i, row in enumerate(rows):
    key = row['key']
    path = ROOT / 'assets/icons/masters' / (key + '.png')
    x, y = (i % 6) * 220, (i // 6) * 280
    draw.rounded_rectangle((x+6, y+6, x+214, y+274), radius=8, fill='#242b35')
    if path.exists():
        master = Image.open(path).convert('RGBA')
        image = fit_icon(master, 168, 7)
        sheet.paste(image, (x+26, y+12), image)
        tile = fit_icon(master, 64, 2)
        tile.save(out / (key + '_64.png'))
        sheet.paste(tile, (x+78, y+183), tile)
        content = f'<img class="large" src="../masters/{key}.png"><img class="tile" src="{key}_64.png">'
    else:
        draw.text((x+35, y+100), 'Awaiting artwork', font=font, fill='#aaaaaa')
        content = '<div class="pending">Awaiting artwork</div>'
    draw.text((x+12, y+251), key, font=font, fill='#e4e8ef')
    cards.append(f'<article>{content}<b>{html.escape(key)}</b><small>{html.escape(row["design_source"])}</small></article>')
sheet.save(out / 'equipment-icons.png')
(out / 'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Legacy Party Armory — icon review</title>
<style>body{background:#151a21;color:#e4e8ef;font:16px Segoe UI,sans-serif;margin:24px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}article{background:#242b35;padding:16px;border-radius:10px;display:flex;flex-direction:column;align-items:center;gap:10px}.large{width:168px;height:168px;object-fit:contain}.tile{width:64px;height:64px;image-rendering:auto}small{color:#aab6c5}.pending{height:242px;display:grid;place-content:center}</style>
<h1>Legacy Party Armory — 18 equipment icons</h1><p>Large preview above, actual 64px inventory tile below.</p><main>'''+''.join(cards)+'</main>', encoding='utf-8')
print(out / 'equipment-icons.png')
