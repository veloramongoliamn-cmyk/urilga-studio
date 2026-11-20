"""Урилга Студи сайтыг бүтээнэ: python3 _build/build.py
_build/events.py-ийн мэдээллээр <slug>/index.html, index.html үүсгэнэ."""
import json, html, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / '_build'))
from events import EVENTS, COVER_POS
from times import TIMES

STUDIO = dict(
    phone='9144-4989',     # захиалга авах утас
    messenger='61596697291671',  # Facebook хуудасны ID (m.me/<энэ>)
    facebook='https://www.facebook.com/profile.php?id=61596697291671',
    instagram='',          # TODO: https://instagram.com/...
)

SITE = ROOT
inv_tpl = (ROOT / '_build/invite.html').read_text()
land_tpl = (ROOT / '_build/landing.html').read_text()
esc = html.escape

def theme_css(t):
    return ''.join(f'--{k}:{v};' for k, v in t.items() if k not in ('disp', 'body')) + f"--disp:{t['disp']};--body:{t['body']};"

def arch_style(e):
    t = e['theme']
    return f"background:radial-gradient(120% 90% at 50% 20%,{t['acc2']},transparent 60%),linear-gradient(165deg,{t['acc']},{t['stage']})"

# assets дотор cover-<slug>.jpg, voice-<slug>.mp3 байвал автоматаар холбоно
for e in EVENTS:
    s = e['slug']
    if (SITE/'assets'/f'cover-{s}.jpg').exists():
        e['cover'] = f'../assets/cover-{s}.jpg'; e.setdefault('coverAlt', e['type'] + ' урилгын зураг')
    if s in COVER_POS: e['coverPos'] = COVER_POS[s]
    if (SITE/'assets'/f'voice-{s}.mp3').exists():
        e['voice'] = f'../assets/voice-{s}.mp3'
        if s in TIMES and 'times' not in e: e['times'] = TIMES[s]['times']; e['end'] = TIMES[s]['end']

for e in EVENTS:
    data = {k: e.get(k) for k in ('type','title','titleHtml','seal','cover','coverAlt','coverPos','voice','times','end','music',
                                 'bless','inviteLines','msg','date','time','venue','addr','program','dress','phone','particles','khee','theme')}
    data['mapLink'] = e.get('mapLink', ''); data['siteLink'] = e.get('siteLink', '')
    data = {k: v for k, v in data.items() if v is not None}
    page = (inv_tpl.replace('@@DATA@@', json.dumps(data, ensure_ascii=False))
                   .replace('@@THEME@@', theme_css(e['theme']))
                   .replace('@@TITLE@@', esc(f"{e['title']} · {e['type']}"))
                   .replace('@@DESC@@', esc(e['bless'].split('\n')[0] + ' ' + e['type'] + ' урилга'))
                   .replace('@@OGIMG@@', e.get('cover', '../assets/cover-hurim.jpg'))
                   .replace('@@PAPER@@', e['theme']['paper']))
    out = SITE / e['slug'] / 'index.html'; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(page)

PLAY = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4v16l13-8z"/></svg>'
cards = []
for e in EVENTS:
    t = e['theme']
    if e.get('cover'):
        face = f'<img src="{e["cover"].replace("../", "")}" alt="{esc(e.get("coverAlt", e["title"]))}" loading="lazy" style="object-position:{e.get("coverPos","50% 50%")}">'
    else:
        size = '64px' if len(e['seal']) <= 3 else '40px'
        face = f'<span class="seal" style="font-family:{esc(t["disp"])};color:{t["paper"]};font-size:{size}">{esc(e["seal"])}</span>'
    badge = '<span class="vb">Дуутай ерөөл</span>' if e.get('voice') else ''
    cards.append(f'''<a class="card" href="{e['slug']}/index.html" data-cat="{e['cat']}">
  <div class="a" style="{arch_style(e)}">{face}{badge}<span class="play">{PLAY}</span></div>
  <div><h3>{esc(e['type'])}</h3><p>{esc(e['title'])}</p></div></a>''')
options = ''.join(f'<option>{esc(e["type"])}</option>' for e in EVENTS) + '<option>Бусад</option>'

land = (land_tpl.replace('@@CARDS@@', '\n'.join(cards)).replace('@@OPTIONS@@', options)
        .replace('@@STUDIO_PHONE@@', STUDIO['phone']).replace('@@STUDIO_MESSENGER@@', STUDIO['messenger'])
        .replace('@@STUDIO_FACEBOOK@@', STUDIO['facebook']).replace('@@STUDIO_INSTAGRAM@@', STUDIO['instagram']))
# preview.html: Claude дээр урьдчилан харах (skeleton-гүй); index.html: Vercel/GitHub-д бүтэн баримт
(ROOT / '_build/preview.html').write_text(land)
head, body = land.split('<header', 1)
head = head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
full = ('<!doctype html>\n<html lang="mn" translate="no" class="notranslate">\n<head>\n<meta charset="utf-8">\n<meta name="google" content="notranslate">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        + head + '</head>\n<body>\n<header' + body + '\n</body>\n</html>\n')
full = full.replace('body{background:var(--bg)', 'body{margin:0;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);background:var(--bg)')
(SITE / 'index.html').write_text(full)
print('OK:', len(EVENTS), 'урилга + нүүр хуудас')
