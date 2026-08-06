"""MNIST 손글씨 숫자 인식 모델 학습 스크립트.

MNIST 데이터셋으로 간단한 합성곱 신경망(CNN)을 학습하고,
학습이 끝난 가중치를 mnist_cnn.pt 파일로 저장한다.

실행: python3 train.py
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from model import 손글씨분류모델

# 학습 설정
배치크기 = 128
학습횟수 = 5          # 전체 데이터를 몇 번 반복 학습할지
학습률 = 0.001
저장경로 = "mnist_cnn.pt"


def 장치선택():
    """사용 가능한 연산 장치를 고른다. (애플 실리콘 GPU > CPU)"""
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def 데이터불러오기():
    """MNIST 학습용, 평가용 데이터로더를 만든다.

    데이터가 없으면 data 폴더에 자동으로 내려받는다.
    """
    # 이미지를 텐서로 바꾸고, MNIST 전체 평균과 표준편차로 정규화한다.
    변환 = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,)),
    ])

    학습셋 = datasets.MNIST(root="data", train=True, download=True, transform=변환)
    평가셋 = datasets.MNIST(root="data", train=False, download=True, transform=변환)

    학습로더 = DataLoader(학습셋, batch_size=배치크기, shuffle=True)
    평가로더 = DataLoader(평가셋, batch_size=1000, shuffle=False)
    return 학습로더, 평가로더


def 한번학습(모델, 로더, 최적화기, 장치, 회차):
    """한 에포크만큼 모델을 학습시킨다."""
    모델.train()
    누적손실 = 0.0

    for 묶음번호, (이미지, 정답) in enumerate(로더, start=1):
        이미지, 정답 = 이미지.to(장치), 정답.to(장치)

        최적화기.zero_grad()            # 이전 기울기 초기화
        예측 = 모델(이미지)              # 순전파
        손실 = F.cross_entropy(예측, 정답)
        손실.backward()                 # 역전파
        최적화기.step()                 # 가중치 갱신

        누적손실 += 손실.item()
        if 묶음번호 % 100 == 0:
            print(f"  [{회차}회차] {묶음번호}/{len(로더)} 묶음 처리, "
                  f"평균 손실 {누적손실 / 묶음번호:.4f}")

    return 누적손실 / len(로더)


def 평가하기(모델, 로더, 장치):
    """평가용 데이터로 정확도를 계산한다."""
    모델.eval()
    맞힌개수 = 0
    전체개수 = 0

    with torch.no_grad():               # 평가할 때는 기울기 계산이 필요 없다.
        for 이미지, 정답 in 로더:
            이미지, 정답 = 이미지.to(장치), 정답.to(장치)
            예측 = 모델(이미지)
            맞힌개수 += (예측.argmax(dim=1) == 정답).sum().item()
            전체개수 += 정답.size(0)

    return 맞힌개수 / 전체개수


def main():
    장치 = 장치선택()
    print(f"연산 장치: {장치}")

    학습로더, 평가로더 = 데이터불러오기()
    모델 = 손글씨분류모델().to(장치)
    최적화기 = torch.optim.Adam(모델.parameters(), lr=학습률)

    for 회차 in range(1, 학습횟수 + 1):
        평균손실 = 한번학습(모델, 학습로더, 최적화기, 장치, 회차)
        정확도 = 평가하기(모델, 평가로더, 장치)
        print(f"{회차}회차 완료 - 평균 손실 {평균손실:.4f}, "
              f"테스트 정확도 {정확도 * 100:.2f}%")

    torch.save(모델.state_dict(), 저장경로)
    print(f"학습이 끝났습니다. 모델을 {저장경로} 에 저장했습니다.")


if __name__ == "__main__":
    main()
