#!/usr/bin/env python3
"""사진 칸 후보 — 상업 사용이 되는 무료 사진 후보를 받아 번호 붙인 한 장(sheet.jpg)으로 붙인다.

  python3 photo_candidates.py --query "fig bread" --aspect square --out cand/slot03

찾는 곳: Openverse(상업 사용 라이선스) → 결과가 없거나 막히면 위키미디어 공용(Wikimedia Commons, 자유 라이선스).
검색어 낱말을 모두 담은 사진만 나오므로, 결과가 없으면 앞 낱말부터 줄여 가며 다시 찾는다.
out 에 sheet.jpg(Pillow 가 없으면 0.jpg·1.jpg… 따로)와 candidates.json(번호·주소·작가·라이선스·원본 페이지)을 만든다.
sheet.jpg 를 직접 보고 칸에 맞는 번호를 고른 뒤, 그 후보의 url 과 credit 을 그대로 답에 넣는다(url 은 시안에 바로 쓰는 크기다).
"""
import argparse, io, json, os, re, time, urllib.parse, urllib.request

UA = {'User-Agent': 'zaemit-design-skill/1 (https://zaemit.ai/design)'}
LICENSE = {'by': 'CC BY', 'by-sa': 'CC BY-SA', 'cc0': 'CC0', 'pdm': 'Public Domain'}


def get(url, timeout=40, tries=3):
    last = None
    for n in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        except Exception as e:  # 잠깐 막히면(500·429·시간 초과) 조금 쉬었다 다시
            last = e
            time.sleep(1.5 * (n + 1))
    raise last


def shape_ok(w, h, aspect):
    if not w or not h: return True
    r = w / h
    return r < 0.9 if aspect == 'vertical' else (0.8 <= r <= 1.25 if aspect == 'square' else r > 1.1)


def openverse(query, aspect, any_shape):
    params = {'q': query, 'page_size': '12', 'license_type': 'commercial', 'mature': 'false'}
    if not any_shape:
        params['aspect_ratio'] = {'vertical': 'tall', 'square': 'square'}.get(aspect, 'wide')
    out = []
    for r in json.loads(get('https://api.openverse.org/v1/images/?' + urllib.parse.urlencode(params))).get('results', []):
        if (r.get('width') or 0) < 640: continue
        lic = LICENSE.get(r.get('license', ''), 'CC ' + r.get('license', '').upper())
        credit = None if r.get('license') in ('cc0', 'pdm') else {'author': r.get('creator') or 'unknown', 'license': f"{lic} {r.get('license_version') or ''}".strip(), 'source': r.get('foreign_landing_url') or r['url']}
        out.append({'url': r['url'], 'thumb': r.get('thumbnail') or r['url'], 'title': (r.get('title') or '')[:80], 'credit': credit})
    return out


def commons(query, aspect, any_shape):
    params = {'action': 'query', 'format': 'json', 'generator': 'search', 'gsrsearch': query + ' filetype:bitmap', 'gsrnamespace': '6', 'gsrlimit': '30',
              'prop': 'imageinfo', 'iiprop': 'url|extmetadata|size', 'iiurlwidth': '1600'}
    pages = sorted(json.loads(get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params))).get('query', {}).get('pages', {}).values(), key=lambda p: p.get('index', 0))
    out = []
    for pg in pages:
        ii = (pg.get('imageinfo') or [{}])[0]; md = ii.get('extmetadata', {})
        w, h = ii.get('width', 0), ii.get('height', 0)
        if w < 800 or (not any_shape and not shape_ok(w, h, aspect)): continue
        lic = (md.get('LicenseShortName', {}).get('value') or '').strip()
        if not lic or 'NC' in lic or 'ND' in lic: continue  # 상업 사용·수정이 안 되는 사진은 뺀다
        free = lic.lower() in ('cc0', 'public domain', 'pdm') or lic.lower().startswith('public domain')
        author = re.sub('<[^>]+>', '', md.get('Artist', {}).get('value', '') or 'unknown').strip()[:80]
        url = ii.get('thumburl') or ii['url']  # 1600px 크기(원본 주소는 요청 방식에 따라 막힌다)
        out.append({'url': url, 'thumb': re.sub(r'/\d+px-', '/500px-', url), 'title': pg['title'][:80],
                    'credit': None if free else {'author': author, 'license': lic, 'source': ii.get('descriptionurl')}})
    return out


p = argparse.ArgumentParser()
p.add_argument('--query', required=True)
p.add_argument('--aspect', default='horizontal', choices=['horizontal', 'vertical', 'square'])
p.add_argument('--out', required=True)
p.add_argument('--any-shape', action='store_true', help='비율이 달라도 후보로(결과가 적을 때)')
a = p.parse_args()
os.makedirs(a.out, exist_ok=True)

words = a.query.split()
queries = [' '.join(words[:n]) for n in range(len(words), 0, -1)][:3]
found, used, notes = [], '', []
for source in (openverse, commons):
    for q in queries:
        try:
            found = source(q, a.aspect, a.any_shape)
        except Exception as e:
            notes.append(f'{source.__name__} "{q}": {e}')
            break  # 이 곳이 막혔으면 다음 곳으로
        if found:
            used = f'{source.__name__} "{q}"'
            break
    if found: break

tiles, cands = [], []
for r in found:
    if len(cands) >= 9: break
    try:
        raw = get(r['thumb'], 30, 2)
    except Exception:
        continue
    cands.append({'n': len(cands), 'url': r['url'], 'title': r['title'], 'credit': r['credit']})
    tiles.append(raw)

try:
    from PIL import Image, ImageDraw
    if tiles:
        W, H = 270, 215
        sheet = Image.new('RGB', (W * 3, H * ((len(tiles) + 2) // 3)), 'white')
        draw = ImageDraw.Draw(sheet)
        for n, raw in enumerate(tiles):
            im = Image.open(io.BytesIO(raw)).convert('RGB'); im.thumbnail((260, 200))
            x, y = (n % 3) * W, (n // 3) * H
            sheet.paste(im, (x + 5, y + 5)); draw.rectangle([x + 5, y + 5, x + 30, y + 25], fill='black'); draw.text((x + 10, y + 8), str(n), fill='white')
        sheet.save(os.path.join(a.out, 'sheet.jpg'), quality=80)
except ImportError:
    for n, raw in enumerate(tiles):
        open(os.path.join(a.out, f'{n}.jpg'), 'wb').write(raw)

json.dump(cands, open(os.path.join(a.out, 'candidates.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for note in notes: print('  (막힘)', note)
if cands:
    print(f'{len(cands)}장 ({used}) → {a.out}/' + ('sheet.jpg' if os.path.exists(os.path.join(a.out, 'sheet.jpg')) else '0.jpg …'))
else:
    print('후보 없음 — 다른 낱말로 다시 찾거나 --any-shape 를 붙여 보세요. 끝내 없으면 이 칸은 "" 로 답합니다.')
