# 2026-08-07 01:38 KST 생성
#
# 한글 마크다운을 PDF 로 바꾼다. 맥에 pandoc, weasyprint 가 없어서
# 마크다운 -> HTML -> Chrome 헤드리스 인쇄 경로를 쓴다.
#
# 사용: python3 md2pdf.py 입력.md 출력.pdf

import subprocess
import sys
from pathlib import Path

import markdown

크롬 = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

스타일 = """
@page { size: A4; margin: 18mm 16mm; }
body {
  font-family: "Apple SD Gothic Neo", "AppleGothic", sans-serif;
  font-size: 10.5pt; line-height: 1.7; color: #1a1a1a;
}
h1 { font-size: 20pt; border-bottom: 2px solid #333; padding-bottom: 6px; margin-top: 0; }
h2 { font-size: 15pt; margin-top: 26px; border-bottom: 1px solid #ccc; padding-bottom: 4px; }
h3 { font-size: 12pt; margin-top: 20px; }
h2, h3 { page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 9.5pt; }
th, td { border: 1px solid #bbb; padding: 5px 8px; text-align: left; vertical-align: top; }
th { background: #f0f0f0; font-weight: 600; }
code {
  font-family: "SF Mono", Menlo, monospace; font-size: 9pt;
  background: #f4f4f4; padding: 1px 4px; border-radius: 3px;
}
pre {
  background: #f7f7f7; border: 1px solid #ddd; border-left: 3px solid #888;
  padding: 9px 12px; overflow-x: auto; page-break-inside: avoid;
}
pre code { background: none; padding: 0; font-size: 8.5pt; line-height: 1.5; }
blockquote {
  border-left: 3px solid #999; margin: 12px 0; padding: 2px 14px;
  color: #444; background: #fafafa;
}
hr { border: 0; border-top: 1px solid #ddd; margin: 22px 0; }
a { color: #0645ad; text-decoration: none; }
li { margin: 3px 0; }
strong { font-weight: 600; }
"""


def 변환(입력, 출력):
    입력, 출력 = Path(입력).resolve(), Path(출력).resolve()
    본문 = markdown.markdown(
        Path(입력).read_text(),
        extensions=["tables", "fenced_code", "sane_lists", "nl2br"],
    )
    제목 = Path(입력).stem
    html = (
        f'<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        f"<title>{제목}</title><style>{스타일}</style></head>"
        f"<body>{본문}</body></html>"
    )
    임시 = Path(출력).with_suffix(".html")
    임시.write_text(html)

    subprocess.run(
        [크롬, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={출력}", 임시.as_uri()],
        check=True, capture_output=True,
    )
    임시.unlink()
    print(f"{출력}  ({Path(출력).stat().st_size:,} 바이트)")


if __name__ == "__main__":
    변환(sys.argv[1], sys.argv[2])
