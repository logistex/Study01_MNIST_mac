<!-- 2026-08-08 18:11 KST 작성 -->

# 손글씨 숫자 인식 (3장 실습)

마우스로 그린 숫자를 인식하는 앱이다. 같은 프로그램을 데스크톱과 웹 두 방식으로 만들어 나란히 두었다.

- **데스크톱** — `cd desktop_version && python3 app.py` (윈도우는 `py app.py`)
- **웹** — `cd web_version && python3 -m http.server 8000` 을 실행한 뒤 http://localhost:8000 접속
- **배포본** — https://logistex.github.io/Study01_MNIST_mac/

학습된 가중치(`desktop_version/mnist_cnn.pt`)가 들어 있으므로 **학습 없이 바로 실행된다.**

## 필요한 것

| 무엇을 하려면 | 설치 |
|---|---|
| 데스크톱 앱 실행 | `pip install torch pillow` |
| 다시 학습까지 | `pip install torch torchvision` (`pillow` 가 함께 깔린다) |
| 웹 버전 | **없다.** 외부 라이브러리를 쓰지 않는다 |

`tkinter` 는 파이썬에 함께 들어 있다. `torch` 는 `pillow` 를 끌고 오지 않으므로 앱만 실행할 때도 `pillow` 를 따로 깔아야 한다.

## 다시 학습하기

`cd desktop_version && python3 train.py` 를 실행한다. **5 에포크에 1분 안팎 걸린다**(M2 맥북 에어 실측: GPU 50초, CPU 1분 30초). MNIST 원본은 용량 때문에 저장소에 없고 이때 자동으로 내려받는다.

자세한 내용은 [CLAUDE.md](CLAUDE.md) 를 참고한다.
