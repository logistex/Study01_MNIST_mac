# 2026-08-08 13:55 KST 작성
"""노션 fetch 원본에서 그림 주소를 걷어내 읽을 수 있는 크기로 줄인다.

그림은 `[그림 NNN | 캡션]` 으로 바꾸고, 같은 번호가 img/NNN.png 파일과 맞는다.
토글(<details><summary>) 경로도 함께 뽑아 그림마다 어디에 있는지 적는다.

사용법
    python3 읽기용만들기.py <노션원본.txt> <결과폴더>
"""
import re, json, os, sys

원본경로, 여기 = sys.argv[1], sys.argv[2]
os.makedirs(여기, exist_ok=True)
원본 = open(원본경로, encoding="utf-8").read()

try:
    원본 = json.loads(원본)["text"]
except Exception:
    pass

번호 = [0]
경로 = []          # 현재 토글 스택
그림목록 = []      # (번호, 경로, 캡션)


def 그림치환(m):
    캡션 = m.group(1).strip()
    번호[0] += 1
    n = f"{번호[0]:03d}"
    그림목록.append((n, " ▸ ".join(경로), 캡션 or "(캡션없음)"))
    return f"[그림 {n} | {캡션 or '캡션없음'}]"


결과 = []
for 줄 in 원본.split("\n"):
    벗긴 = 줄.strip()
    if 벗긴.startswith("<summary>"):
        경로.append(re.sub(r"</?summary>", "", 벗긴).strip())
    elif 벗긴 == "</details>" and 경로:
        경로.pop()
    결과.append(re.sub(r"!\[([^\]]*)\]\(https://prod-files-secure[^)]*\)", 그림치환, 줄))

읽기용 = "\n".join(결과)
open(os.path.join(여기, "읽기용.md"), "w", encoding="utf-8").write(읽기용)

with open(os.path.join(여기, "그림위치.tsv"), "w", encoding="utf-8") as f:
    for n, p, c in 그림목록:
        f.write(f"{n}\t{p}\t{c}\n")

print(f"원본 {len(원본):,}자 → 읽기용 {len(읽기용):,}자")
print(f"그림 {len(그림목록)}장, 캡션 있는 것 {sum(1 for _, _, c in 그림목록 if c != '(캡션없음)')}장")
print("걷어내지 못한 주소:", 읽기용.count("prod-files-secure"))
