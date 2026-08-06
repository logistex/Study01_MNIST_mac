"""웹 버전이 파이썬과 같은 결과를 내는지 확인할 정답 데이터를 만든다.

MNIST 테스트 이미지를 앱 캔버스와 같은 280x280 으로 키운 그림과, 그 그림을
파이썬 경로(preprocess.py + 모델)로 통과시킨 결과를 함께 저장한다.
브라우저는 같은 그림을 자바스크립트 경로로 통과시켜 이 결과와 대조한다.

만들어진 검증데이터.json 은 git 에 넣지 않는다. 필요할 때 다시 만들면 된다.

실행: python3 검증데이터만들기.py
"""
# 2026-08-06 18:34 KST 생성

import base64
import io
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import datasets

from model import 손글씨분류모델
from preprocess import mnist형식으로변환, 텐서로변환

이폴더 = Path(__file__).resolve().parent
웹폴더 = 이폴더.parent / "web_version"

표본수 = 200
캔버스크기 = 280      # app.py 의 캔버스크기와 같은 값


def 그림을dataurl로(그림: Image.Image) -> str:
    """PIL 이미지를 브라우저가 바로 읽는 PNG data URL 로 바꾼다."""
    버퍼 = io.BytesIO()
    그림.save(버퍼, format="PNG")
    인코딩 = base64.b64encode(버퍼.getvalue()).decode("ascii")
    return f"data:image/png;base64,{인코딩}"


def 만들기():
    평가셋 = datasets.MNIST(root=str(이폴더 / "data"), train=False, download=False)

    모델 = 손글씨분류모델()
    모델.load_state_dict(torch.load(이폴더 / "mnist_cnn.pt", map_location="cpu"))
    모델.eval()

    항목들 = []
    for 번호 in range(표본수):
        원본, 라벨 = 평가셋[번호]

        # 앱 캔버스와 같은 크기로 키운다. 최근접 이웃을 쓰는 이유는, 여기서
        # 또 다른 리샘플링 차이가 끼어들면 파이썬과 자바스크립트를 비교하는
        # 의미가 흐려지기 때문이다.
        큰그림 = 원본.resize((캔버스크기, 캔버스크기), Image.NEAREST)

        입력이미지 = mnist형식으로변환(큰그림)
        if 입력이미지 is None:
            raise SystemExit(f"{번호}번 표본의 전처리 결과가 비어 있습니다.")

        with torch.no_grad():
            확률 = F.softmax(모델(텐서로변환(입력이미지)), dim=1)[0]

        항목들.append({
            "라벨": int(라벨),
            "그림": 그림을dataurl로(큰그림),
            # PIL 의 getdata 는 이 Pillow 버전에서 폐기 예정이라 numpy 로 편다.
            "전처리": np.array(입력이미지, dtype=np.uint8).flatten().tolist(),
            "확률": [float(값) for 값 in 확률],
        })

    웹폴더.mkdir(exist_ok=True)
    (웹폴더 / "검증데이터.json").write_text(
        json.dumps(
            {"표본수": 표본수, "캔버스크기": 캔버스크기, "항목": 항목들},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    맞힘 = sum(1 for 하나 in 항목들
               if max(range(10), key=lambda 숫자: 하나["확률"][숫자]) == 하나["라벨"])
    print(f"검증 데이터 {표본수}개를 만들었습니다.")
    print(f"파이썬 기준 정확도 {맞힘 / 표본수 * 100:.1f}% ({맞힘}/{표본수})")
    print(f"  {웹폴더 / '검증데이터.json'}")


if __name__ == "__main__":
    만들기()
