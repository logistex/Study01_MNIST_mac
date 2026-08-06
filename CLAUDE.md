# CLAUDE.md

MNIST 손글씨 숫자 인식 프로젝트다. 같은 프로그램을 두 방식으로 구현해 나란히 비교한다.

| 폴더 | 무엇 | 지침 |
|---|---|---|
| `desktop_version/` | Tkinter로 만든 맥용 앱. 학습과 가중치 관리도 여기서 한다. | `desktop_version/CLAUDE.md` |
| `web_version/` | 브라우저에서 도는 정적 페이지. 외부 라이브러리 없음. | `web_version/CLAUDE.md` |

**작업할 폴더의 `CLAUDE.md`를 먼저 읽는다.** 환경 제약과 주의점이 그쪽에 있다.

## 두 버전의 관계

학습된 모델은 하나뿐이다. `desktop_version/`이 `mnist_cnn.pt`를 갖고, `가중치내보내기.py`로 웹이 읽을 형식으로 풀어 준다.

```
desktop_version/mnist_cnn.pt
        │
        │  python3 가중치내보내기.py
        ▼
web_version/가중치.bin + 가중치정보.json
```

**학습을 다시 했다면 내보내기도 다시 돌려야 한다.** 그러지 않으면 웹 버전만 옛 가중치를 쓴다.

웹 버전의 `모델.js`와 `전처리.js`는 각각 `model.py`와 `preprocess.py`를 손으로 옮긴 것이다. 파이썬 쪽을 고치면 자바스크립트도 함께 고치고, `web_version/검증.html`로 확인한다.

## 빠른 실행

```bash
cd desktop_version && python3 app.py                    # 데스크톱
cd web_version && python3 -m http.server 8000           # 웹 (그 뒤 localhost:8000 접속)
```

웹 버전은 `index.html` 더블클릭으로 열리지 않는다. HTTP 서버가 필요하다.

## 공통 규칙

- **식별자와 주석을 모두 한글로 쓴다.** 파이썬과 자바스크립트 모두 함수, 변수 이름이 한글이다. 예외는 셸 스크립트뿐이다. 셸은 변수 이름에 한글을 쓸 수 없다.
- **MNIST 전처리 세 단계를 지킨다.** 캔버스 그림을 그냥 28x28로 줄이면 인식률이 무너진다. ① 여백을 잘라내고 ② 비율 유지하며 20x20에 맞추고 ③ 밝기 무게중심을 28x28 한가운데로 옮긴다. 두 버전 모두 이 규칙을 구현하고 있다.
- **정규화 상수 `0.1307`, `0.3081`의 출처는 언제나 파이썬이다.** 자바스크립트에 직접 적지 않는다.
- 테스트 프레임워크는 없다. 검증은 임시 스크립트와 `web_version/검증.html`로 한다.

## 문서

- `docs/superpowers/specs/2026-08-06-웹-데스크톱-버전-분리-design.md` — 두 버전으로 나눈 설계와 그 과정의 결정 기록
- `CLAUDE_전역.md` — 전역 지침 스냅샷
