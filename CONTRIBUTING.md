# 기여 안내

재밋 디자인 스킬에 관심을 가져 주셔서 고맙습니다. 버그 신고, 제안, 고치는 코드 모두 반갑게 받습니다.

## 이슈 남기기

- **버그**: [버그 신고](https://github.com/zaemitai/zaemit-design-skill/issues/new?template=bug_report.yml) 양식으로 남겨 주세요. 무엇을 했는지, 어떤 오류가 나왔는지가 있으면 가장 빨리 고칠 수 있어요.
- **제안**: [기능 제안](https://github.com/zaemitai/zaemit-design-skill/issues/new?template=feature_request.yml) 양식으로 남겨 주세요.
- 시안 링크나 오류 내용에 공개하면 안 되는 정보(전화번호, 주소, 아직 발표하지 않은 내용)가 있으면 지우고 올려 주세요.

## 코드 보내기

1. 저장소를 포크하고 새 브랜치에서 고쳐 주세요.
2. 아래를 지켜 주세요.
   - `scripts/zaemit_make.py`는 파이썬 표준 라이브러리만 씁니다. 설치할 것을 늘리지 않습니다.
   - Python 3.8에서도 돌아가야 합니다.
   - 기획 규칙(섹션 수, 문구 쓰는 법, 사진 설명 쓰는 법)은 [재밋 안내서](https://zaemit.ai/design?format=json)가 정본입니다. `SKILL.md`에 옮겨 적지 않습니다.
   - `SKILL.md`의 제작 보고 형식(제작 완료 및 설명 · 사진 출처 · 검사 · 계속 제작하는 방법)은 사용자가 보는 결과라서, 바꾸려면 이슈에서 먼저 이야기해 주세요.
3. 고친 뒤 최소한 이것은 돌려 봐 주세요.
   ```bash
   python3 scripts/zaemit_make.py --help
   python3 scripts/photo_candidates.py --query "flower bouquet" --aspect horizontal --out /tmp/cand-test
   ```
4. 무엇을 왜 바꿨는지 적어 Pull Request를 보내 주세요.

## 재밋 서비스에 대한 문의

시안을 만드는 엔진과 재밋 서비스는 이 저장소에 들어 있지 않아요. 서비스 이용 문의는 [재밋 도움말](https://zaemit.ai/help-center)과 [고객센터](https://zaemit.ai/customer-center)에서 받습니다.
