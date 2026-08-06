"""손글씨 숫자 인식 앱.

마우스로 숫자를 그리면 학습해 둔 CNN 모델이 0~9 중 무엇인지 알려 준다.

실행: python3 app.py   (먼저 python3 train.py 로 모델을 학습해 두어야 한다.)
"""

import tkinter as tk
from pathlib import Path
from tkinter import messagebox

import torch
import torch.nn.functional as F
from PIL import Image, ImageDraw

from model import 손글씨분류모델
from preprocess import mnist형식으로변환, 텐서로변환

# 화면 설정
캔버스크기 = 280          # 그림판 한 변의 길이(화소)
붓굵기 = 18              # MNIST 글씨 굵기와 비슷하게 맞춘 값

# 파인더에서 더블클릭해 실행하면 현재 폴더가 달라질 수 있으므로,
# 모델 파일은 이 스크립트가 있는 폴더를 기준으로 찾는다.
모델파일 = Path(__file__).resolve().parent / "mnist_cnn.pt"


class 손글씨인식앱:
    def __init__(self, 창):
        self.창 = 창
        창.title("손글씨 숫자 인식")
        창.resizable(False, False)

        self.모델 = self._모델불러오기()

        # 캔버스에 그린 내용을 그대로 따라 그릴 이미지.
        # (화면에서 직접 화소를 읽는 방법은 운영체제마다 달라 신뢰하기 어렵다.)
        self.그림 = Image.new("L", (캔버스크기, 캔버스크기), 0)
        self.붓 = ImageDraw.Draw(self.그림)
        self.이전좌표 = None

        self._화면구성()

    def _모델불러오기(self):
        """저장된 가중치를 불러와 예측 준비를 마친 모델을 돌려준다."""
        if not 모델파일.exists():
            messagebox.showerror(
                "모델 없음",
                f"{모델파일} 파일이 없습니다.\n먼저 터미널에서 python3 train.py 를 실행해 주세요.",
            )
            raise SystemExit(1)

        모델 = 손글씨분류모델()
        모델.load_state_dict(torch.load(모델파일, map_location="cpu"))
        모델.eval()      # 예측 모드로 전환 (드롭아웃 끄기)
        return 모델

    def _화면구성(self):
        바깥틀 = tk.Frame(self.창, padx=16, pady=16)
        바깥틀.pack()

        # --- 왼쪽: 그림판 ---
        왼쪽 = tk.Frame(바깥틀)
        왼쪽.grid(row=0, column=0, padx=(0, 16))

        tk.Label(왼쪽, text="이곳에 숫자를 크게 그려 주세요.").pack(pady=(0, 6))

        self.캔버스 = tk.Canvas(
            왼쪽, width=캔버스크기, height=캔버스크기,
            bg="black", cursor="pencil", highlightthickness=1,
            highlightbackground="#888888",
        )
        self.캔버스.pack()
        self.캔버스.bind("<Button-1>", self.그리기시작)
        self.캔버스.bind("<B1-Motion>", self.그리는중)
        self.캔버스.bind("<ButtonRelease-1>", self.그리기끝)

        단추틀 = tk.Frame(왼쪽)
        단추틀.pack(pady=(10, 0), fill="x")
        tk.Button(단추틀, text="지우기", width=12, command=self.지우기).pack(side="left")
        tk.Button(단추틀, text="인식하기", width=12, command=self.인식하기).pack(side="right")

        # --- 오른쪽: 결과 ---
        오른쪽 = tk.Frame(바깥틀)
        오른쪽.grid(row=0, column=1, sticky="n")

        tk.Label(오른쪽, text="인식 결과", font=("AppleGothic", 14)).pack()
        self.결과숫자 = tk.Label(오른쪽, text="?", font=("AppleGothic", 90))
        self.결과숫자.pack()
        self.확신도 = tk.Label(오른쪽, text="그림을 그리면 자동으로 인식합니다.",
                              font=("AppleGothic", 11), fg="#555555")
        self.확신도.pack(pady=(0, 10))

        tk.Label(오른쪽, text="가능성이 높은 후보", font=("AppleGothic", 11)).pack(anchor="w")
        self.후보표시 = []
        for _ in range(3):
            줄 = tk.Frame(오른쪽)
            줄.pack(anchor="w", pady=2)
            숫자라벨 = tk.Label(줄, text="-", font=("AppleGothic", 13), width=2)
            숫자라벨.pack(side="left")
            막대 = tk.Canvas(줄, width=140, height=14, highlightthickness=0, bg="#eeeeee")
            막대.pack(side="left", padx=6)
            비율라벨 = tk.Label(줄, text="", font=("AppleGothic", 10), width=6, anchor="w")
            비율라벨.pack(side="left")
            self.후보표시.append((숫자라벨, 막대, 비율라벨))

    # --- 그리기 처리 ---

    def 그리기시작(self, 사건):
        self.이전좌표 = (사건.x, 사건.y)
        # 점 하나만 찍었을 때도 보이도록 원을 그린다.
        반지름 = 붓굵기 / 2
        self.캔버스.create_oval(
            사건.x - 반지름, 사건.y - 반지름, 사건.x + 반지름, 사건.y + 반지름,
            fill="white", outline="white",
        )
        self.붓.ellipse(
            [사건.x - 반지름, 사건.y - 반지름, 사건.x + 반지름, 사건.y + 반지름], fill=255
        )

    def 그리는중(self, 사건):
        if self.이전좌표 is None:
            return
        지금좌표 = (사건.x, 사건.y)
        self.캔버스.create_line(
            *self.이전좌표, *지금좌표,
            fill="white", width=붓굵기, capstyle=tk.ROUND, smooth=True,
        )
        self.붓.line([self.이전좌표, 지금좌표], fill=255, width=붓굵기, joint="curve")
        # PIL은 선 끝을 둥글게 처리하지 않으므로 이음매에 원을 덧그린다.
        반지름 = 붓굵기 / 2
        self.붓.ellipse(
            [지금좌표[0] - 반지름, 지금좌표[1] - 반지름,
             지금좌표[0] + 반지름, 지금좌표[1] + 반지름], fill=255
        )
        self.이전좌표 = 지금좌표

    def 그리기끝(self, _사건):
        self.이전좌표 = None
        self.인식하기()          # 손을 떼면 바로 인식한다.

    def 지우기(self):
        self.캔버스.delete("all")
        self.붓.rectangle([0, 0, 캔버스크기, 캔버스크기], fill=0)
        self.결과숫자.config(text="?")
        self.확신도.config(text="그림을 그리면 자동으로 인식합니다.")
        for 숫자라벨, 막대, 비율라벨 in self.후보표시:
            숫자라벨.config(text="-")
            막대.delete("all")
            비율라벨.config(text="")

    # --- 인식 처리 ---

    def 인식하기(self):
        입력이미지 = mnist형식으로변환(self.그림)
        if 입력이미지 is None:
            self.확신도.config(text="아직 그린 내용이 없습니다.")
            return

        with torch.no_grad():
            점수 = self.모델(텐서로변환(입력이미지))
            확률 = F.softmax(점수, dim=1)[0]

        상위확률, 상위숫자 = 확률.topk(3)
        self.결과숫자.config(text=str(상위숫자[0].item()))
        self.확신도.config(text=f"확신도 {상위확률[0].item() * 100:.1f}%")

        for (숫자라벨, 막대, 비율라벨), 숫자, 값 in zip(self.후보표시, 상위숫자, 상위확률):
            숫자라벨.config(text=str(숫자.item()))
            막대.delete("all")
            막대.create_rectangle(0, 0, max(1, 140 * 값.item()), 14,
                                  fill="#3b7ddd", outline="")
            비율라벨.config(text=f"{값.item() * 100:.1f}%")


def main():
    창 = tk.Tk()
    손글씨인식앱(창)
    창.mainloop()


if __name__ == "__main__":
    main()
