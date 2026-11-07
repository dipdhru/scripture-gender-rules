"""Inter-coder agreement between the first-pass codes and a second coder.

Usage:  python3 compare_coders.py <coder2 codes.txt>
Input:  data/coding/codes_*.txt (coder 1), data/coding/coder2_key.json
        (sample uid -> unit idx), data/coding/to_code.csv
Output: data/coding/agreement.csv (every sampled unit, both codes) and a
        printed report: % agreement and Cohen's kappa per code position.

Buddhist units are compared against their structural code (monks' code ->
1MNR, nuns' code -> 1WRN), as used in the results.
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CODING = ROOT / "data" / "coding"
POSITIONS = ["is_rule", "governs", "effect_on_women", "effect_on_men"]


def coder1():
    codes = {}
    for f in sorted(CODING.glob("codes_*.txt")):
        for line in f.read_text().split("\n"):
            if line.strip():
                i, c = line.split()
                codes[int(i)] = c
    for u in csv.DictReader((CODING / "to_code.csv").open(encoding="utf-8")):
        if u["religion"] == "Buddhism":
            codes[int(u["idx"])] = "1WRN" if u["book"].startswith("Bhikkhuni") else "1MNR"
    return codes


def parts(code):
    # a non-rule has no value in positions 2-4; '-' keeps it comparable
    return [code[0]] + (list(code[1:4]) if code != "0" else ["-", "-", "-"])


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(a) | set(b)) / (n * n)
    return po, (1.0 if pe == 1 else (po - pe) / (1 - pe))


def main(path):
    key = json.loads((CODING / "coder2_key.json").read_text())
    c1 = coder1()
    c2 = {}
    for line in Path(path).read_text().split("\n"):
        if line.strip():
            uid, code = line.split()[:2]
            c2[uid] = code.upper() if code != "0" else "0"
    bad = [u for u, c in c2.items() if not (c == "0" or (len(c) == 4 and c[0] == "1"
           and c[1] in "MWBG" and c[2] in "RPXN" and c[3] in "RPXN"))]
    missing = sorted(set(key) - set(c2))
    units = {int(u["idx"]): u for u in csv.DictReader((CODING / "to_code.csv").open(encoding="utf-8"))}

    rows = []
    for uid, idx in sorted(key.items()):
        if uid in c2 and uid not in bad:
            u = units[idx]
            rows.append({"uid": uid, "idx": idx, "religion": u["religion"],
                         "coder1": c1[idx], "coder2": c2[uid], "text": " ".join(u["text"].split())[:300]})
    with (CODING / "agreement.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    print(f"compared {len(rows)} units; missing {len(missing)}; malformed {bad}")
    print(f"exact code match: {sum(r['coder1'] == r['coder2'] for r in rows)}/{len(rows)}")
    for k, name in enumerate(POSITIONS):
        po, kp = kappa([parts(r["coder1"])[k] for r in rows], [parts(r["coder2"])[k] for r in rows])
        print(f"  {name:<16} agreement {po:5.0%}   kappa {kp:5.2f}")
    # positions 2-4 among units both coders call rules (avoids '-' inflating agreement)
    both = [r for r in rows if r["coder1"] != "0" and r["coder2"] != "0"]
    print(f"among {len(both)} units both coded as rules:")
    for k, name in enumerate(POSITIONS[1:], 1):
        po, kp = kappa([r["coder1"][k] for r in both], [r["coder2"][k] for r in both])
        print(f"  {name:<16} agreement {po:5.0%}   kappa {kp:5.2f}")
    print("per religion (exact match / is_rule match):")
    for rel in sorted({r["religion"] for r in rows}):
        g = [r for r in rows if r["religion"] == rel]
        ex = sum(r["coder1"] == r["coder2"] for r in g)
        ir = sum(r["coder1"][0] == r["coder2"][0] for r in g)
        print(f"  {rel:<13} n={len(g):>3}  exact {ex / len(g):4.0%}  is_rule {ir / len(g):4.0%}")
    print("confusion of is_rule (coder1 -> coder2):",
          dict(Counter((r["coder1"][0], r["coder2"][0]) for r in rows)))
    print("governs confusion among both-rule units:",
          dict(Counter((r["coder1"][1], r["coder2"][1]) for r in both if r["coder1"][1] != r["coder2"][1])))


if __name__ == "__main__":
    main(sys.argv[1])
