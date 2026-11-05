# 재밋 디자인 스킬 (Zaemit Design Skill)

Claude에게 "재밋으로 꽃집 홈페이지 디자인해 줘"라고 말하면, 대화 한 번으로 홈페이지·랜딩 페이지 시안을 만들어 주는 Claude 스킬입니다.

Claude가 사이트 기획과 문구를 쓰고, [재밋](https://zaemit.ai) 디자인 엔진이 그 기획으로 시안을 만듭니다. 만드는 도중 엔진이 내리는 판단(섹션마다 어떤 화면을 둘지, 문구를 화면에 어떻게 배치할지, 어떤 사진을 넣을지)에는 Claude가 직접 답합니다.

> **English** — A Claude skill that turns one conversation into a homepage or landing-page draft. Claude writes the plan and copy, the [Zaemit](https://zaemit.ai) design engine builds the draft, and Claude answers the engine's decisions along the way. Install it, then ask: *"Design a homepage for my flower shop with Zaemit."*

## 만들어지는 것

시안이 끝나면 Claude가 아래를 알려 줍니다.

- **시안 보기** 링크: 브라우저에서 바로 열어 보는 완성된 메인 페이지
- **HTML 받기** 링크: 파일로 받아 직접 고치거나 서브페이지를 이어서 만들 수 있습니다
- **재밋에 올리기** 링크: 재밋에 로그인하면 바로 수정할 수 있는 코드를 받아, 서브페이지와 데이터베이스 연동까지 이어서 만들 수 있습니다. 문의 폼·게시판·예약·지도 같은 기능 칸은 이때부터 실제로 작동합니다
- **사진 출처**: 어떤 사진을 어디서 가져왔고 어떤 라이선스인지
- **검사 결과**: 글자색 대비처럼 다듬으면 좋은 곳

## 설치

### Claude Code

```bash
git clone https://github.com/zaemitai/zaemit-design-skill ~/.claude/skills/zaemit-design
```

설치한 뒤 Claude Code를 다시 열고 이렇게 말하면 됩니다.

```
재밋으로 꽃집 홈페이지 디자인해 줘
```

### claude.ai

[https://zaemit.ai/design/skill.zip](https://zaemit.ai/design/skill.zip) 을 내려받아 claude.ai 설정의 스킬 메뉴에 올립니다. 시안을 만들려면 Claude의 코드 실행 환경에서 `zaemit.ai` 로 요청을 보낼 수 있어야 합니다. 막혀 있으면 설정에서 네트워크 접근을 허용해 주세요.

## 필요한 것

- Python 3.8 이상
- [Pillow](https://pypi.org/project/Pillow/) — 사진 후보를 한 장으로 모아 Claude가 직접 보고 고를 때 씁니다 (`pip install Pillow`)
- 인터넷 연결 (`zaemit.ai`, 사진 검색에 쓰는 `api.openverse.org`·`commons.wikimedia.org`)

가입이나 API 키 없이 바로 쓸 수 있습니다.

## 들어 있는 것

| 파일 | 하는 일 |
|---|---|
| `SKILL.md` | Claude가 따르는 순서: 규칙 읽기 → 기획과 문구 → 시안 만들기 → 사진 고르기 → 제작 보고 |
| `scripts/zaemit_make.py` | 시안 키 받기, 시안 만들기 시작, 엔진 질문 꺼내기, 답 보내기 |
| `scripts/photo_candidates.py` | 상업적으로 쓸 수 있는 사진 후보를 찾아 한 장으로 모으기 |

기획 규칙(섹션 수, 문구 쓰는 법, 사진 설명 쓰는 법)은 이 저장소에 옮겨 적지 않습니다. Claude가 시안을 만들 때마다 [재밋 안내서](https://zaemit.ai/design?format=json)를 읽고 따르므로, 규칙이 바뀌어도 스킬을 다시 받을 필요가 없습니다.

## 사진

사진은 이 순서로 고릅니다.

1. 사용자가 준 사진
2. Claude가 만들 수 있으면 직접 만든 사진
3. 상업적으로 쓸 수 있는 무료 사진 (Openverse에서 찾고, 없으면 위키미디어 공용에서 찾습니다)

후보는 Claude가 직접 보고 칸 내용에 맞는 것만 넣고, 맞는 사진이 없으면 빈 자리로 둡니다. 작가 표기가 필요한 사진(CC BY 등)은 시안 맨 아래에 작가와 라이선스가 적힙니다. Unsplash나 Pexels API 키가 있으면 그쪽 사진을 써도 됩니다.

무료 사진의 라이선스는 사진 속 사람의 초상권이나 간판·상표까지 허락하지 않습니다. 실제로 쓰실 때는 가게에서 직접 찍은 사진으로 바꾸는 것을 권합니다.

## 설정

| 환경 변수 | 기본값 | 뜻 |
|---|---|---|
| `ZAEMIT_DESIGN_BASE` | `https://zaemit.ai/design` | 재밋 디자인 서버 주소 |
| `ZAEMIT_QUESTION_DIR` | `zaemit-q` | 엔진 질문을 꺼내 두는 폴더 |

## 라이선스

이 저장소의 파일은 [MIT License](LICENSE)를 따릅니다.

'재밋'·'Zaemit' 이름과 로고는 이 라이선스가 허락하는 범위에 들어가지 않습니다. 시안을 만드는 재밋 엔진과 서비스는 이 저장소에 포함되지 않으며, [재밋](https://zaemit.ai) 서비스 이용약관을 따릅니다.

문의와 제안은 [Issues](https://github.com/zaemitai/zaemit-design-skill/issues)에 남겨 주세요.
