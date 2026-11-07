"""Merge hand codes with the rule units and summarize them per religion.

Usage:  python3 summarize_codes.py
Input:  data/coding/to_code.csv, data/coding/codes_*.txt, data/rules_tagged.csv
Output: data/coded_rules.csv      (one row per confirmed gender-relevant rule)
        data/results_summary.csv  (one row per religion / section)

Code format (see CODEBOOK.md, "Hand coding"): '0' = not a rule, otherwise
4 characters: 1 + governs (M/W/B/G) + effect on women + effect on men
(R restricts, P protects/benefits, X mixed, N none).
"""

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
NT_BOOKS = {"Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians",
            "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians",
            "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus",
            "Philemon", "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John",
            "3 John", "Jude", "Revelation"}
GOVERNS = {"M": "men", "W": "women", "B": "both (named)", "G": "everyone"}


def load():
    codes = {}
    for f in sorted((DATA / "coding").glob("codes_*.txt")):
        for line in f.read_text().split("\n"):
            if line.strip():
                i, c = line.split()
                codes[int(i)] = c
    units = list(csv.DictReader((DATA / "coding" / "to_code.csv").open(encoding="utf-8")))
    rows = []
    for u in units:
        if u["religion"] == "Buddhism":
            continue  # coded structurally below, over the full Patimokkha
        c = codes[int(u["idx"])]
        if c != "0":
            rows.append(dict(u, code=c))
    # Every Patimokkha entry restricts the person whose code it belongs to, so
    # all 531 rules are coded from structure (20/20 spot-check agreed).
    for u in csv.DictReader((DATA / "rules_tagged.csv").open(encoding="utf-8")):
        if u["unit_type"] == "monastic_rule":
            nuns = u["book"].startswith("Bhikkhuni")
            rows.append(dict(u, idx="", code="1WRN" if nuns else "1MNR"))
    for r in rows:
        r["governs"] = GOVERNS[r["code"][1]]
        r["effect_on_women"], r["effect_on_men"] = r["code"][2], r["code"][3]
        r["section"] = ""
        if r["religion"] == "Christianity":
            r["section"] = "New Testament" if r["book"] in NT_BOOKS else "Old Testament"
    return rows


def summarize(group):
    g = Counter(r["code"][1] for r in group)
    w = Counter(r["effect_on_women"] for r in group)
    m = Counter(r["effect_on_men"] for r in group)
    return {"rules": len(group), "women_only": g["W"], "men_only": g["M"],
            "both_named": g["B"], "everyone": g["G"],
            "restrict_women": w["R"], "protect_women": w["P"], "mixed_women": w["X"],
            "restrict_men": m["R"], "protect_men": m["P"], "mixed_men": m["X"]}


def main():
    rows = load()
    keep = ["id", "religion", "section", "book", "chapter", "verse", "heading", "text",
            "code", "governs", "effect_on_women", "effect_on_men"]
    with (DATA / "coded_rules.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, keep, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    groups = []
    for rel in ["Buddhism", "Christianity", "Hinduism", "Islam", "Jainism", "Judaism", "Sikhism"]:
        groups.append((rel, "", [r for r in rows if r["religion"] == rel]))
        if rel == "Christianity":
            for sec in ["Old Testament", "New Testament"]:
                groups.append((rel, sec, [r for r in rows if r["section"] == sec]))
    fields = ["religion", "section"] + list(summarize(rows[:1]))
    with (DATA / "results_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        for rel, sec, g in groups:
            w.writerow({"religion": rel, "section": sec, **summarize(g)})
            s = summarize(g)
            print(f"{rel + (' / ' + sec if sec else ''):<30} " +
                  " ".join(f"{k}={v}" for k, v in s.items()))
    print(f"{len(rows)} coded rules -> data/coded_rules.csv, data/results_summary.csv")


if __name__ == "__main__":
    main()
