"""과별 새 단어를 vocab.json 에 추가하는 도구.

lessons/ 폴더의 L*.txt 파일을 읽어서 vocab.json 에 합칩니다 (이미 있는 단어는 건너뜀).
파일 형식 (한 줄에 한 단어, | 로 구분):
  N|단수|성|복수|뜻|메모            명사 (정관사형은 자동 계산, 필요하면 7·8번째 칸에 직접)
  A|남단|여단|남복|여복|뜻|메모     형용사
  V|부정사|eu tu el noi voi ei|과거분사|뜻|메모   동사 (6형태는 공백으로 구분)
  O|단어|뜻|분류                   기타
'#' 로 시작하는 줄은 무시.  사용법: python3 add_lessons.py && python3 build.py
"""
import json
import re
from pathlib import Path

here = Path(__file__).parent


def def_sg(sg, g):
    if sg in ("—", ""):
        return "—"
    head, sep, tail = sg.partition(" ")  # "față de masă" → 첫 단어만 변화
    w = head
    if g == "f":
        if w.endswith("ea") or (w.endswith("a") and not w.endswith("ă")):
            r = w + "ua"
        elif w.endswith("ă"):
            r = w[:-1] + "a"
        elif w.endswith("ie"):
            r = w[:-1] + "a"
        elif w.endswith("e"):
            r = w + "a"
        else:
            r = w + "a"
    else:
        if w.endswith("e"):
            r = w + "le"
        elif w.endswith("u"):
            r = w + "l"
        else:
            r = w + "ul"
    return r + sep + tail


def def_pl(pl, g):
    if pl in ("—", ""):
        return "—"
    head, sep, tail = pl.partition(" ")
    return (head + "i" if g == "m" else head + "le") + sep + tail


def write_vocab(data):
    """한 항목을 한 줄로 저장 (손으로 고치기 쉽게)."""
    out = ["{"]
    keys = list(data.keys())
    for i, k in enumerate(keys):
        v = data[k]
        comma = "," if i < len(keys) - 1 else ""
        if isinstance(v, list):
            out.append(json.dumps(k, ensure_ascii=False) + ": [")
            out.append(",\n".join(json.dumps(r, ensure_ascii=False) for r in v))
            out.append("]" + comma)
        else:
            out.append(json.dumps(k, ensure_ascii=False) + ": " + json.dumps(v, ensure_ascii=False) + comma)
    out.append("}")
    (here / "vocab.json").write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    data = json.loads((here / "vocab.json").read_text(encoding="utf-8"))
    have = {(t, r[0]) for t, key in (("N", "nouns"), ("A", "adjs"), ("V", "verbs"), ("O", "other")) for r in data[key]}
    added = 0
    for f in sorted((here / "lessons").glob("L*.txt"), key=lambda p: int(re.sub(r"\D", "", p.stem))):
        lesson = int(re.sub(r"\D", "", f.stem))
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            p = [x.strip() for x in line.split("|")]
            t = p[0]
            if (t, p[1]) in have:
                continue
            if t == "N":
                sg, g, pl, ko = p[1], p[2], p[3], p[4]
                note = p[5] if len(p) > 5 else ""
                d1 = p[6] if len(p) > 6 and p[6] else def_sg(sg, g)
                d2 = p[7] if len(p) > 7 and p[7] else def_pl(pl, g)
                data["nouns"].append([sg, g, pl, d1, d2, ko, lesson, note])
            elif t == "A":
                data["adjs"].append([p[1], p[2], p[3], p[4], p[5], lesson, p[6] if len(p) > 6 else ""])
            elif t == "V":
                forms = p[2].split()
                assert len(forms) == 6, line
                data["verbs"].append([p[1], forms, p[4], lesson, p[5] if len(p) > 5 else "", p[3]])
            elif t == "O":
                data["other"].append([p[1], p[2], p[3], lesson])
            else:
                raise ValueError(line)
            have.add((t, p[1]))
            added += 1
    write_vocab(data)
    print("추가:", added, {k: len(v) for k, v in data.items() if not k.startswith("_")})


if __name__ == "__main__":
    main()
