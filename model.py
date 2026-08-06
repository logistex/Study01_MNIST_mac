"""손글씨 숫자 인식용 신경망 구조 정의.

학습 스크립트(train.py)와 인식 앱(app.py)이 같은 구조를 써야 하므로
모델 정의를 이 파일 하나에 모아 둔다.
"""

import torch.nn as nn
import torch.nn.functional as F


class 손글씨분류모델(nn.Module):
    """28x28 흑백 이미지를 받아 0~9 중 하나로 분류하는 CNN."""

    def __init__(self):
        super().__init__()
        # 합성곱 층: 이미지에서 선, 곡선 같은 특징을 뽑아낸다.
        self.합성곱1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.합성곱2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)

        # 과적합을 줄이기 위한 드롭아웃
        self.드롭아웃1 = nn.Dropout(0.25)
        self.드롭아웃2 = nn.Dropout(0.5)

        # 완전연결 층: 뽑아낸 특징을 바탕으로 숫자를 판단한다.
        self.전결합1 = nn.Linear(64 * 7 * 7, 128)
        self.전결합2 = nn.Linear(128, 10)

    def forward(self, 입력):
        묶음 = F.relu(self.합성곱1(입력))
        묶음 = F.max_pool2d(묶음, 2)        # 28x28 -> 14x14

        묶음 = F.relu(self.합성곱2(묶음))
        묶음 = F.max_pool2d(묶음, 2)        # 14x14 -> 7x7

        묶음 = self.드롭아웃1(묶음)
        묶음 = 묶음.flatten(start_dim=1)     # 2차원 특징을 1줄로 편다.

        묶음 = F.relu(self.전결합1(묶음))
        묶음 = self.드롭아웃2(묶음)
        return self.전결합2(묶음)           # 숫자 0~9에 대한 점수 10개
