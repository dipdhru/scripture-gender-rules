# Gendered rules in seven scriptures

How many rules does each religion's core text make that apply specifically to men or to women, and do those rules restrict or protect? This project collects one core rule text per religion, finds the gender-relevant rules, codes each one by hand, and checks the coding with an independent second coder.

**Start with [`explainer.ipynb`](explainer.ipynb)**, a step-by-step walkthrough with charts.

## Texts

| Religion | Text | Translation | Units |
|---|---|---|---:|
| Christianity | Bible (Old + New Testament) | King James Version, 1611 | 31,102 verses |
| Islam | Quran | Pickthall, 1930 | 6,236 ayahs |
| Judaism | Torah | JPS, 1917 | 5,846 verses |
| Hinduism | Manusmriti | Bühler, 1886 (OCR scan) | 2,504 verses |
| Buddhism | Pātimokkha, monks' and nuns' codes | Bhikkhu Brahmali (SuttaCentral) | 531 rules |
| Jainism | Ākārāṅga Sūtra | Jacobi, 1884 (OCR scan) | 645 paragraphs |
| Sikhism | Sikh Rehat Maryada | Kulraj Singh (sikhs.org) | 176 paragraphs |

## Results

Confirmed rules that mention a gender, coded by whose conduct they govern:

| Text | Rules | Only women | Only men | Both, named | Everyone | Restricts women | Protects women |
|---|---:|---:|---:|---:|---:|---:|---:|
| Buddhism · Pātimokkha | 531 | 304 | 227 | 0 | 0 | 304 | 0 |
| Hinduism · Manusmriti | 330 | 34 | 163 | 6 | 127 | 75 | 61 |
| Christianity · Old Testament | 263 | 23 | 86 | 13 | 141 | 49 | 35 |
| Christianity · New Testament | 60 | 6 | 6 | 5 | 43 | 9 | 11 |
| Judaism · Torah | 243 | 23 | 77 | 16 | 127 | 46 | 32 |
| Jainism · Ākārāṅga | 237 | 0 | 10 | 219 | 8 | 201 | 20 |
| Islam · Quran | 44 | 7 | 16 | 6 | 15 | 10 | 17 |
| Sikhism · Rehat Maryada | 48 | 1 | 3 | 26 | 18 | 20 | 12 |

- **Buddhism** is the only tradition with more women-only rules: the nuns' code has 304 rules, the monks' 227.
- **Manusmriti, the Torah and the Old Testament** mostly address men, including many rules about women (whom a man may marry, how he must treat his wife).
- **Jainism and Sikhism** mostly state one rule for both genders ("a monk or a nun", "he/she").
- **The Quran** is the one text where rules that protect women outnumber rules that restrict them.

**Reliability.** An independent second coder coded a stratified sample of 200 rules. Cohen's κ was 0.93 for "is it a rule", 0.87 for "whose conduct it governs", 0.82 for effect on women and 0.79 for effect on men. Details and the remaining judgement calls are in [`CODEBOOK.md`](CODEBOOK.md).

## How to run

Requires Python 3.10+. The pipeline scripts use only the standard library; the notebook needs pandas and matplotlib.

```bash
pip install -r requirements.txt
```

```bash
python3 build_dataset.py      # download the texts -> data/religious_texts.csv (cached in data/raw/)
```

```bash
python3 tag_rules.py          # keyword filter -> data/rules_tagged.csv
```

```bash
python3 summarize_codes.py    # merge hand codes -> data/coded_rules.csv, data/results_summary.csv
```

```bash
python3 compare_coders.py data/coding/coder2_codes.txt   # inter-coder agreement
```

```bash
jupyter notebook explainer.ipynb
```

## Files

| Path | What it is |
|---|---|
| `build_dataset.py` | Downloads and parses all seven texts into one CSV |
| `tag_rules.py` | Keyword-based first pass: candidate rules and the genders they mention |
| `summarize_codes.py` | Merges the hand codes and counts them per text |
| `compare_coders.py` | Agreement and Cohen's κ between the two coders |
| `CODEBOOK.md` | Every tag and code, the decision rules, measured accuracy and reliability |
| `explainer.ipynb` | Walkthrough notebook with charts |
| `data/religious_texts.csv` | All texts, one row per verse, rule or paragraph |
| `data/rules_tagged.csv` | Keyword tags for every unit |
| `data/coding/` | Hand codes (`codes_*.txt`), the coding sheet, second coder's instructions, codes and agreement table |
| `data/coded_rules.csv` | The 1,756 confirmed gender-relevant rules with their codes |
| `data/results_summary.csv` | Counts per text |
| `charts/index.html` | Source of the online dashboard page |

## Limitations

- One core text per religion. The Hadith, Talmud and later legal traditions contain far more gender rules.
- Old public-domain translations; gendered English wording doesn't always match the original language.
- Only rules that mention a gender were coded. Most rules in the Bible, Torah and Quran name no gender and use "he" as the default.
- Manusmriti (about 93% of verses recovered) and the Ākārāṅga Sūtra come from OCR scans.
- Coding involves judgement. Manusmriti's men-only count is best read as an upper bound (see `CODEBOOK.md`).

## Sources and licenses

- KJV Bible: public domain, via [thiagobodruk/bible](https://github.com/thiagobodruk/bible).
- Quran, Pickthall translation: public domain (US), via [alquran.cloud](https://alquran.cloud).
- Torah, JPS 1917: public domain, via [Sefaria](https://www.sefaria.org).
- Pātimokkha, Brahmali translation: CC0, via [SuttaCentral](https://suttacentral.net).
- Manusmriti (SBE 25) and Ākārāṅga Sūtra (SBE 22): public domain, via [archive.org](https://archive.org) scans.
- Sikh Rehat Maryada: official SGPC text; English translation hosted at [sikhs.org](https://www.sikhs.org/rehit.htm). Check its terms before redistributing.
