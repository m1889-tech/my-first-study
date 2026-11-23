"""vocab.json → index.html(웹 단어장) + 단어장.md(깃허브에서 보기용)

사용법:  python3 build.py
vocab.json 에 단어를 추가한 뒤 이 스크립트를 실행하면 두 파일이 새로 만들어집니다.
"""
import json
from pathlib import Path

here = Path(__file__).parent
data = json.loads((here / "vocab.json").read_text(encoding="utf-8"))

lessons = sorted({r[6] for r in data["nouns"]} | {r[5] for r in data["adjs"]} | {r[3] for r in data["verbs"]})

# 1) index.html
tpl = (here / "template.html").read_text(encoding="utf-8")
payload = json.dumps({k: v for k, v in data.items() if not k.startswith("_")}, ensure_ascii=False, separators=(",", ":"))
(here / "index.html").write_text(tpl.replace("/*__DATA__*/null", payload).replace('<span id="range">1–9과</span>', f'<span id="range">{lessons[0]}–{lessons[-1]}과</span>'), encoding="utf-8")

# 2) 단어장.md
G = {"m": "남성", "f": "여성", "n": "중성"}
out = [f"# 루마니아어 단어장 (Limba română, {lessons[0]}–{lessons[-1]}과)", "",
       "성: **m** 남성 · **f** 여성 · **n** 중성. 굵은 글씨는 사전형에서 바뀌는 부분.", ""]


def bold_diff(word, form):
    if not form or form == "—":
        return "—"
    p = 0
    while p < min(len(word), len(form)) and word[p] == form[p]:
        p += 1
    if p == len(word) == len(form):
        return form
    return form[:p] + "**" + form[p:] + "**" if p >= 2 else "**" + form + "**"


for l in lessons:
    out.append(f"## {l}과")
    nouns = [r for r in data["nouns"] if r[6] == l]
    if nouns:
        out += ["", "### 명사", "", "| 단어 | 성 | 복수 | 단수+정관사 | 복수+정관사 | 뜻 | 메모 |", "|---|---|---|---|---|---|---|"]
        for r in nouns:
            out.append(f"| {r[0]} | {r[1]} | {bold_diff(r[0], r[2])} | {bold_diff(r[0], r[3])} | {bold_diff(r[0], r[4])} | {r[5]} | {r[7]} |")
    adjs = [r for r in data["adjs"] if r[5] == l]
    if adjs:
        out += ["", "### 형용사", "", "| 남·중 단수 | 여 단수 | 남 복수 | 여·중 복수 | 뜻 | 메모 |", "|---|---|---|---|---|---|"]
        for r in adjs:
            out.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[6]} |")
    verbs = [r for r in data["verbs"] if r[3] == l]
    if verbs:
        out += ["", "### 동사 (현재형)", "", "| 부정사 | eu | tu | el/ea | noi | voi | ei/ele | 과거분사 | 뜻 |", "|---|---|---|---|---|---|---|---|---|"]
        for r in verbs:
            out.append(f"| {r[0]} | " + " | ".join(r[1]) + f" | {r[5] if len(r) > 5 else ''} | {r[2]} |")
    out.append("")

out += ["## 기타 (대명사·의문사·부사·전치사·숫자 등)", "", "| 단어 | 뜻 | 분류 | 과 |", "|---|---|---|---|"]
for r in data["other"]:
    out.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |")
(here / "단어장.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("index.html, 단어장.md 생성 완료")
