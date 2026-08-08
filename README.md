<!-- 2026-08-08 18:11 KST 작성 -->

# 손글씨 숫자 인식 (3장 실습)

마우스로 그린 숫자를 인식하는 앱이다. 같은 프로그램을 데스크톱과 웹 두 방식으로 만들어 나란히 두었다.

- **데스크톱** — `cd desktop_version && python3 app.py` (윈도우는 `py app.py`)
- **웹** — `cd web_version && python3 -m http.server 8000` 을 실행한 뒤 http://localhost:8000 접속
- **배포본** — https://logistex.github.io/Study01_MNIST_mac/

학습된 가중치(`desktop_version/mnist_cnn.pt`)가 들어 있으므로 **학습 없이 바로 실행된다.** 데스크톱 버전은 `torch` 가 필요하다(`pip install torch`).

다시 학습하려면 `cd desktop_version && python3 train.py` 를 실행한다. MNIST 원본은 용량 때문에 저장소에 없고 이때 자동으로 내려받는다. 자세한 내용은 [CLAUDE.md](CLAUDE.md) 를 참고한다.
