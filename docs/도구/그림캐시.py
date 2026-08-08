# 2026-08-08 13:51 KST 작성
"""노션 그림을 UUID 로 캐시한다. 같은 그림을 두 번 내려받지 않는다.

노션이 주는 S3 주소는 300초 만에 만료되고 매번 서명이 바뀌지만,
경로의 두 번째 UUID(첨부 블록 ID)는 그림마다 고정이다. 그것을 캐시 키로 쓴다.

    https://prod-files-secure.s3.../{워크스페이스}/{첨부UUID}/{파일명}?X-Amz-...
                                                  ^^^^^^^^^^ 캐시 키

사용법
    python3 그림캐시.py seed  <옛img폴더> <옛목록.tsv>   # 이미 받아 둔 것을 캐시에 넣는다
    python3 그림캐시.py sync  <새노션.md> <작업폴더>      # 없는 것만 받고 작업폴더를 채운다
"""
import sys, os, re, csv, shutil, subprocess
from urllib.parse import urlparse

캐시폴더 = os.path.expanduser("~/.cache/notion그림/3장-데스크톱")


def 키뽑기(주소):
    조각 = urlparse(주소).path.strip("/").split("/")
    # /{워크스페이스}/{첨부UUID}/{파일명}
    if len(조각) < 3:
        return None
    첨부UUID, 파일명 = 조각[-2], 조각[-1]
    확장자 = os.path.splitext(파일명)[1] or ".png"
    return 첨부UUID + 확장자


def seed(옛폴더, 옛목록):
    os.makedirs(캐시폴더, exist_ok=True)
    넣음 = 이미 = 0
    with open(옛목록, encoding="utf-8") as f:
        for 줄 in csv.reader(f, delimiter="\t"):
            if len(줄) < 4:
                continue
            번호, 주소 = 줄[0], 줄[3]
            키 = 키뽑기(주소)
            원본 = os.path.join(옛폴더, 번호 + ".png")
            대상 = os.path.join(캐시폴더, 키)
            if not os.path.exists(원본):
                continue
            if os.path.exists(대상):
                이미 += 1
                continue
            shutil.copy2(원본, 대상)
            넣음 += 1
    print(f"캐시에 새로 넣음 {넣음}장, 이미 있던 것 {이미}장, 캐시 총 {len(os.listdir(캐시폴더))}장")


def sync(노션md, 작업폴더):
    os.makedirs(캐시폴더, exist_ok=True)
    os.makedirs(작업폴더, exist_ok=True)
    본문 = open(노션md, encoding="utf-8").read()
    주소들 = re.findall(r'https://prod-files-secure[^\s)"\']+', 본문)
    print(f"그림 {len(주소들)}장 발견")

    받을것 = []          # (키, 주소)
    순서 = []            # (번호, 키)
    본적 = set()
    for i, 주소 in enumerate(주소들, 1):
        키 = 키뽑기(주소)
        순서.append((f"{i:03d}", 키))
        if 키 in 본적:
            continue
        본적.add(키)
        if not os.path.exists(os.path.join(캐시폴더, 키)):
            받을것.append((키, 주소))

    print(f"고유 그림 {len(본적)}장 / 캐시에 없어 받아야 할 것 {len(받을것)}장")

    if 받을것:
        목록파일 = os.path.join(작업폴더, "_받을것.txt")
        with open(목록파일, "w", encoding="utf-8") as f:
            for 키, 주소 in 받을것:
                f.write(f"{os.path.join(캐시폴더, 키)}\t{주소}\n")
        # 서명이 300초 만에 만료되므로 병렬로 받는다
        subprocess.run(
            ["xargs", "-P", "30", "-L", "1", "sh", "-c",
             'curl -sS -f -o "$0" "$1" || echo "실패: $0" >&2'],
            stdin=open(목록파일, encoding="utf-8"),
            check=False,
        )
        os.remove(목록파일)
        실패 = [키 for 키, _ in 받을것 if not os.path.exists(os.path.join(캐시폴더, 키))]
        print(f"내려받기 완료. 실패 {len(실패)}장" + (f" {실패}" if 실패 else ""))
    else:
        print("내려받을 것이 없다. 전부 캐시에서 쓴다.")

    # 작업 폴더를 번호 순서대로 채운다(하드링크라 용량을 두 배로 쓰지 않는다)
    for 오래된 in os.listdir(작업폴더):
        if 오래된.endswith(".png"):
            os.remove(os.path.join(작업폴더, 오래된))
    없음 = 0
    for 번호, 키 in 순서:
        원본 = os.path.join(캐시폴더, 키)
        if not os.path.exists(원본):
            없음 += 1
            continue
        os.link(원본, os.path.join(작업폴더, f"{번호}.png"))
    print(f"작업 폴더 준비 완료: {len(순서) - 없음}장" + (f" (빠짐 {없음}장)" if 없음 else ""))


if __name__ == "__main__":
    명령 = sys.argv[1]
    if 명령 == "seed":
        seed(sys.argv[2], sys.argv[3])
    elif 명령 == "sync":
        sync(sys.argv[2], sys.argv[3])
