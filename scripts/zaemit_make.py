#!/usr/bin/env python3
"""재밋 디자인 스킬 — 시안 키 받기·시안 만들기·질문 꺼내기·답 보내기(표준 라이브러리만).

  link   --fields plan.json         기획·문구(안내서 requests.link.body 모양) → 시안 키
  start  --key KEY                  시안 만들기 시작(answeredBy=caller) → 작업 id
  next   --job JOB [--wait 60]      새 질문을 zaemit-q/<id>.json 으로 꺼낸다. 끝나면 결과를 출력한다.
  answer --job JOB --id QID --file answer.json   답 보내기

주소는 환경 변수 ZAEMIT_DESIGN_BASE(기본 https://zaemit.ai/design).
"""
import argparse, json, os, sys, time, urllib.request, urllib.error

BASE = os.environ.get('ZAEMIT_DESIGN_BASE', 'https://zaemit.ai/design').rstrip('/')
QDIR = os.environ.get('ZAEMIT_QUESTION_DIR', 'zaemit-q')


def call(method, path, body=None):
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={'content-type': 'application/json', 'accept': 'application/json', 'user-agent': 'zaemit-design-skill/1'})
    try:
        with urllib.request.urlopen(req, timeout=120) as res:
            return res.status, json.loads(res.read().decode('utf-8') or '{}')
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode('utf-8') or '{}')
        except Exception:
            return e.code, {}


def fail(status, body):
    code = (body.get('error') or {}).get('code') if isinstance(body, dict) else None
    if code == 'JOB_NOT_FOUND':
        print('작업이 서버에서 없어졌어요(서버가 다시 시작됐을 수 있어요). 같은 시안 키로 start 부터 다시 하세요. '
              '질문 글이 앞과 똑같으면 앞서 쓴 답을 다시 보내도 됩니다.', file=sys.stderr)
        sys.exit(2)
    print(f'오류 {status}: {json.dumps(body.get("error", body), ensure_ascii=False)}', file=sys.stderr)
    sys.exit(1)


def left(q):
    try:
        from datetime import datetime, timezone
        end = datetime.fromisoformat(q['expiresAt'].replace('Z', '+00:00'))
        return f", 남은 시간 {max(0, int((end - datetime.now(timezone.utc)).total_seconds() // 60))}분"
    except Exception:
        return ''


def cmd_link(a):
    fields = json.load(open(a.fields, encoding='utf-8'))
    status, body = call('POST', '/link', fields)
    if status != 200: fail(status, body)
    url = body['data']['url']
    print(url.rsplit('#', 1)[-1])
    print(f'(시안 키 주소: {url})', file=sys.stderr)


def cmd_start(a):
    status, body = call('POST', '/make', {'key': a.key, 'answeredBy': 'caller', 'skipMaterials': True})
    if status not in (200, 202): fail(status, body)
    data = body['data']
    if data.get('existing') and data.get('result'):
        print('done'); print(json.dumps(data['result'], ensure_ascii=False, indent=1)); return
    print(data['jobId'])


def summary(q):
    if q['kind'] == 'chat':
        size = len(q.get('system', '')) + sum(len(m.get('content', '')) for m in q.get('messages', []))
        extra = f", 사진 {len(q['images'])}장" if q.get('images') else ''
        return f"chat {q['id']} — 글 {size}자{', JSON 으로' if q.get('json') else ''}{extra}{left(q)}"
    if q['kind'] == 'judge':
        return f"judge {q['id']} — 질문 {', '.join(q['questions'].keys())}{left(q)}"
    if q['kind'] == 'photos':
        return f"photos {q['id']} — 사진 칸 {len(q['slots'])}개{left(q)}"
    return f"{q['kind']} {q['id']}"


def cmd_next(a):
    os.makedirs(QDIR, exist_ok=True)
    until = time.time() + a.wait
    while True:
        status, body = call('GET', f'/make/{a.job}')
        if status != 200: fail(status, body)
        data = body['data']
        if data['stage'] in ('done', 'failed'):
            print(data['stage'])
            print(json.dumps(data.get('result') or data.get('error'), ensure_ascii=False, indent=1))
            return
        fresh = [q for q in data.get('questions', []) if not os.path.exists(os.path.join(QDIR, q['id'] + '.answered'))]
        if fresh:
            print(f"단계 {data['stage']} — 답할 질문 {len(fresh)}개")
            for q in fresh:
                path = os.path.join(QDIR, q['id'] + '.json')
                json.dump(q, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
                print(f'  {summary(q)} → {path}')
            return
        if time.time() > until:
            print(f"단계 {data['stage']} — 아직 질문 없음(다시 next)")
            return
        time.sleep(3)


def cmd_answer(a):
    raw = open(a.file, encoding='utf-8').read()
    try:
        answer = json.loads(raw)
    except json.JSONDecodeError:
        answer = raw  # chat 답 글 그대로
    status, body = call('POST', f'/make/{a.job}/answer', {'id': a.id, 'answer': answer})
    if status != 200: fail(status, body)
    os.makedirs(QDIR, exist_ok=True)
    open(os.path.join(QDIR, a.id + '.answered'), 'w').close()
    print('ok')


p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sub = p.add_subparsers(dest='cmd', required=True)
s = sub.add_parser('link'); s.add_argument('--fields', required=True); s.set_defaults(fn=cmd_link)
s = sub.add_parser('start'); s.add_argument('--key', required=True); s.set_defaults(fn=cmd_start)
s = sub.add_parser('next'); s.add_argument('--job', required=True); s.add_argument('--wait', type=int, default=60); s.set_defaults(fn=cmd_next)
s = sub.add_parser('answer'); s.add_argument('--job', required=True); s.add_argument('--id', required=True); s.add_argument('--file', required=True); s.set_defaults(fn=cmd_answer)
args = p.parse_args()
args.fn(args)
