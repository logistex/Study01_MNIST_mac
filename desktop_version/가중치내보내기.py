"""학습된 가중치를 웹 버전이 읽을 수 있는 형식으로 내보낸다.

웹 버전은 파이썬 없이 도는 정적 페이지라서 mnist_cnn.pt 를 직접 읽지 못한다.
그래서 텐서를 float32 바이너리 한 덩어리로 풀어 쓰고, 각 텐서의 이름과 형상은
별도의 JSON 에 적어 둔다. 자바스크립트는 JSON 을 보고 바이너리를 잘라 쓴다.

형상과 정규화 상수를 자바스크립트에 직접 적지 않는 이유는, 파이썬 쪽을 고쳤을 때
웹 쪽이 조용히 어긋나는 일을 막기 위해서다. 값의 출처는 언제나 파이썬이다.

실행: python3 가중치내보내기.py
"""
# 2026-08-06 18:28 KST 생성

import json
from pathlib import Path

import torch

from preprocess import 표준편차, 평균

이폴더 = Path(__file__).resolve().parent
모델파일 = 이폴더 / "mnist_cnn.pt"
웹폴더 = 이폴더.parent / "web_version"

# 자바스크립트가 이 순서대로 바이너리를 잘라 읽는다. 순서를 바꾸면 웹이 깨진다.
내보낼순서 = [
    "합성곱1.weight", "합성곱1.bias",
    "합성곱2.weight", "합성곱2.bias",
    "전결합1.weight", "전결합1.bias",
    "전결합2.weight", "전결합2.bias",
]


def 내보내기():
    if not 모델파일.exists():
        raise SystemExit(f"{모델파일} 이 없습니다. 먼저 python3 train.py 를 실행해 주세요.")

    상태 = torch.load(모델파일, map_location="cpu")

    빠진것 = [이름 for 이름 in 내보낼순서 if 이름 not in 상태]
    if 빠진것:
        raise SystemExit(f"가중치에 다음 텐서가 없습니다: {빠진것}")

    조각들 = []
    정보 = []
    for 이름 in 내보낼순서:
        텐서 = 상태[이름].detach().cpu().contiguous()
        정보.append({"이름": 이름, "형상": list(텐서.shape)})
        # 애플 실리콘은 리틀엔디언이지만, 바이트 순서를 명시해 두면 오해가 없다.
        조각들.append(텐서.numpy().astype("<f4").tobytes())

    웹폴더.mkdir(exist_ok=True)
    (웹폴더 / "가중치.bin").write_bytes(b"".join(조각들))
    (웹폴더 / "가중치정보.json").write_text(
        json.dumps(
            {"텐서": 정보, "평균": 평균, "표준편차": 표준편차},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    총원소 = sum(상태[이름].numel() for 이름 in 내보낼순서)
    print(f"내보내기 완료: 텐서 {len(내보낼순서)}개, 파라미터 {총원소}개")
    print(f"  {웹폴더 / '가중치.bin'}")
    print(f"  {웹폴더 / '가중치정보.json'}")


if __name__ == "__main__":
    내보내기()
