"""Build one CSV of core rule-bearing texts from seven religions.

Usage:  python3 build_dataset.py
Output: data/religious_texts.csv  (one row per verse / rule / paragraph)
Raw downloads are cached in data/raw/ so re-runs don't hit the network.
Only the Python standard library is used.
"""

import csv
import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "religious_texts.csv"
UA = {"User-Agent": "religion-text-research/1.0 (personal study)"}

FIELDS = ["id", "religion", "text_name", "translation", "section",
          "book", "chapter", "verse", "text", "source_url", "license"]


def fetch(url, cache_name, timeout=300):
    """Download url once into data/raw/<cache_name>; return its text."""
    path = RAW / cache_name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            path.write_bytes(r.read())
        time.sleep(0.3)  # be polite to free APIs
    return path.read_text(encoding="utf-8-sig", errors="replace")


def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", s).strip()


def row(religion, text_name, translation, book, chapter, verse, text,
        source_url, license, section=""):
    return {"religion": religion, "text_name": text_name,
            "translation": translation, "section": section, "book": book,
            "chapter": chapter, "verse": verse, "text": text,
            "source_url": source_url, "license": license}


# --- Christianity: King James Bible (OT + NT) ------------------------------

def christianity():
    url = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/en_kjv.json"
    books = json.loads(fetch(url, "christianity/en_kjv.json"))
    for b_idx, book in enumerate(books):
        section = "Old Testament" if b_idx < 39 else "New Testament"
        for c, verses in enumerate(book["chapters"], 1):
            for v, text in enumerate(verses, 1):
                # this edition marks KJV italics as {word}; drop the braces
                text = re.sub(r"[{}]", "", text)
                yield row("Christianity", "Bible", "King James Version (1611)",
                          book["name"], c, v, clean(text), url,
                          "Public domain", section)


# --- Islam: Quran ------------------------------------------------------------

def islam():
    url = "https://api.alquran.cloud/v1/quran/en.pickthall"
    data = json.loads(fetch(url, "islam/quran_en_pickthall.json"))["data"]
    for s in data["surahs"]:
        for a in s["ayahs"]:
            yield row("Islam", "Quran", "Marmaduke Pickthall (1930)",
                      f'{s["number"]}. {s["englishName"]}', s["number"],
                      a["numberInSurah"], clean(a["text"]), url,
                      "Public domain (US)")


# --- Judaism: Torah (five books of Moses) -----------------------------------

TORAH = {"Genesis": 50, "Exodus": 40, "Leviticus": 27, "Numbers": 36,
         "Deuteronomy": 34}
JPS = "The Holy Scriptures: A New Translation (JPS 1917)"


def judaism():
    for book, n_ch in TORAH.items():
        for c in range(1, n_ch + 1):
            url = (f"https://www.sefaria.org/api/v3/texts/{book}.{c}?version="
                   + urllib.parse.quote(f"english|{JPS}"))
            data = json.loads(fetch(url, f"judaism/{book}.{c}.json"))
            for v, text in enumerate(data["versions"][0]["text"], 1):
                # strip Sefaria's inline footnotes before removing tags
                text = re.sub(r'<sup class="footnote-marker">.*?</sup>\s*'
                              r'<i class="footnote">.*?</i>', "", text, flags=re.S)
                yield row("Judaism", "Torah", "JPS 1917", book, c, v,
                          clean(text), f"https://www.sefaria.org/{book}.{c}",
                          "Public domain")


# --- Buddhism: monastic codes for monks and nuns ----------------------------

def buddhism():
    for uid, name in [("pli-tv-bu-pm", "Bhikkhu Patimokkha (monks)"),
                      ("pli-tv-bi-pm", "Bhikkhuni Patimokkha (nuns)")]:
        url = f"https://suttacentral.net/api/bilarasuttas/{uid}/brahmali"
        data = json.loads(fetch(url, f"buddhism/{uid}.json"))
        tr = data["translation_text"]
        for seg in data["keys_order"]:
            text = clean(tr.get(seg, ""))
            if not text:
                continue
            chapter, _, verse = seg.split(":")[1].partition(".")
            yield row("Buddhism", "Vinaya Pitaka", "Bhikkhu Brahmali (SuttaCentral)",
                      name, chapter, verse, text,
                      f"https://suttacentral.net/{uid}/en/brahmali",
                      "CC0 public domain dedication")


# --- Hinduism: Laws of Manu (Manusmriti), from an OCR scan ------------------

ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7,
         "VIII": 8, "IX": 9, "X": 10, "XI": 11, "XL": 11, "XII": 12}
# Bühler's footnotes cite parallel law books with these abbreviations.
FOOTNOTE = re.compile(r"\b(Gaut|Vas|Baudh|Ap|Vi|Ya[gj]n|Medh|Gov|Kull|Nar|"
                      r"Nand|Sm|Mahabh|Taitt|Sat)\.")


def paragraphs(lines):
    buf = []
    for ln in lines:
        if ln.strip():
            buf.append(ln.strip())
        elif buf:
            yield " ".join(buf)
            buf = []
    if buf:
        yield " ".join(buf)


def dehyphen(s):
    return re.sub(r"(\w)- (\w)", r"\1\2", re.sub(r"\s+", " ", s)).strip()


def hinduism():
    url = "https://archive.org/download/lawsofmanu00manuuoft/lawsofmanu00manuuoft_djvu.txt"
    lines = fetch(url, "hinduism/manu_buhler_djvu.txt").splitlines()
    start = next(i for i, l in enumerate(lines) if re.match(r"^Chapter\s+I\.", l))
    # drop running page headers ("52  LAWS  OF  MANU.  II, 12") and printer marks
    body = [l for l in lines[start:]
            if not re.search(r"LAWS\s+OF\s+MANU", l)
            # odd-page headers: "VI, 63.  THE ASCETIC.  209"
            and not re.match(r"^\s*[IVXLl]+,\s*\d+\.\s+[A-Z][A-Z' ;:,.J]+\d*\s*$", l)
            and not re.fullmatch(r"\s*[A-Z\[\]\d\s]{0,8}\s*", l) or not l.strip()]

    chapter, last, verses = 0, 0, {}
    for p in paragraphs(body):
        if re.match(r"^Chapter\s+([IVXL]+)", p):
            chapter, last = ROMAN.get(re.match(r"^Chapter\s+([IVXL]+)", p).group(1),
                                      chapter + 1), 0
            continue
        # OCR sometimes reads verse "1." as "i."
        m = re.match(r"^(\d{1,3}|i)\.\s+(.*)", p)
        if m:
            n = 1 if m.group(1) == "i" else int(m.group(1))
            text = m.group(2)
            if FOOTNOTE.search(text) or not text[:1].isalpha() and text[:1] not in "('\"":
                continue  # footnote, not a verse
            if n == 1 and last > 50:  # chapter header lost in OCR
                chapter, last = chapter + 1, 0
            # verses only move forward (footnotes repeat old numbers); the window
            # tolerates a few verse numbers the OCR dropped
            if last < n <= last + 10:
                verses[(chapter, n)] = text
                last = n
        elif last and not FOOTNOTE.search(p) and (chapter, last) in verses:
            verses[(chapter, last)] += " " + p  # verse continued after a page break
        if chapter == 12 and last >= 126:
            break
    for (c, v), text in sorted(verses.items()):
        yield row("Hinduism", "Manusmriti (Laws of Manu)",
                  "Georg Bühler, SBE vol. 25 (1886)", "Laws of Manu", c, v,
                  dehyphen(text), url, "Public domain")


# --- Jainism: Akaranga Sutra (monastic conduct), from an OCR scan -----------

ORD = ["FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH",
       "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH", "THIRTEENTH",
       "FOURTEENTH", "FIFTEENTH", "SIXTEENTH"]


def jainism():
    url = ("https://archive.org/download/jainasutrasparti029233mbp/"
           "jainasutrasparti029233mbp_djvu.txt")
    lines = fetch(url, "jainism/jaina_sutras_sbe22_djvu.txt").splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("FIRST LECTURE"))
    end = next(i for i, l in enumerate(lines) if i > start and l.startswith("THE KALPA SUTRA"))

    book, lecture, lesson = 0, 0, 0
    chunks = {}  # (book, lecture, lesson) -> body text
    for p in paragraphs(lines[start:end]):
        head = re.match(rf"^({'|'.join(ORD)}) (LECTURE|LESSON)", p)
        if head:
            n = ORD.index(head.group(1)) + 1
            if head.group(2) == "LECTURE":
                book += n == 1
                lecture, lesson = n, 0
            else:
                lesson = n
            continue
        # skip footnotes ("1 Suyakkhawdha..."), page headers and signature marks
        if (re.match(r"^[\d*†]\s?\S", p) or re.match(r"^BOOK [IV]+, LECTURE", p)
                or re.match(r"^\[\d+\]", p) or len(p) < 25 or p.isupper()):
            continue
        chunks.setdefault((book, lecture, lesson), []).append(p)

    for (b, lec, les), parts in chunks.items():
        text = dehyphen(" ".join(parts))
        text = re.sub(r"\s\d\s?(?=[,.;:/!'])", "", text)  # stray footnote markers
        # Jacobi numbers each sentence-group "(1)", "(2)"... at its end
        pieces = re.split(r"\((\d{1,3}|i)\)", text)
        for k in range(0, len(pieces) - 1, 2):
            seg = pieces[k].strip()
            if len(seg) > 15:
                num = pieces[k + 1].replace("i", "1")
                yield row("Jainism", "Akaranga Sutra",
                          "Hermann Jacobi, SBE vol. 22 (1884)", f"Book {b}",
                          f"Lecture {lec}" + (f", Lesson {les}" if les else ""),
                          num, seg, url, "Public domain")


# --- Sikhism: Sikh Rehat Maryada (official code of conduct) ------------------

# The source misspells some headings ("Aritcle IV", "Ariticle 1").
ARTICLE = r"Ar[it]{2,3}cle\s+([IVXL]+|1)"


def sikhism():
    token = re.compile(rf"<h3[^>]*>(?P<ch>.*?)</h3>|<i>\s*(?P<art>{ARTICLE})\s*</i>"
                       r"|<(?:p|dt|dd|li)[\s>][^>]*>?(?P<p>.*?)"
                       r"(?=<(?:p|dt|dd|li)[\s>]|</(?:dl|ul|ol|td|table|div)>)", re.S | re.I)
    for page in range(1, 7):
        url = f"https://www.sikhs.org/reht{page}.htm"
        src = fetch(url, f"sikhism/reht{page}.htm")
        chapter, article, n = "", "", 0
        for m in token.finditer(src):
            if m.group("ch"):
                chapter = clean(m.group("ch"))
            elif m.group("art"):
                num = re.search(ARTICLE, m.group("art")).group(1).replace("1", "I")
                article, n = f"Article {num}", 0
            else:
                text = clean(m.group("p"))
                # some pages put the chapter/article heading inside a <p>
                head = re.search(ARTICLE + "$", text)
                if head and len(text) < 150:
                    article, n = f"Article {head.group(1).replace('1', 'I')}", 0
                    ch = re.search(r"Chapter\s+[IVXL]+", text)
                    chapter = ch.group(0) if ch else chapter
                    continue
                if not article:  # skip intro/navigation before the first article
                    continue
                if len(text) > 3 and not text.startswith(("Home", "Next", "Previous")):
                    n += 1
                    yield row("Sikhism", "Sikh Rehat Maryada",
                              "Kulraj Singh (English, via sikhs.org)", chapter,
                              article, n, text, url,
                              "SGPC official text; check terms before redistribution")


def main():
    sources = [christianity, islam, judaism, buddhism, hinduism, jainism, sikhism]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        for source in sources:
            count = 0
            for r in source():
                count += 1
                r["id"] = f"{r['religion'][:3].upper()}-{count:06d}"
                w.writerow(r)
            print(f"{source.__name__:<13} {count:>7,} rows")
            total += count
    print(f"{'TOTAL':<13} {total:>7,} rows -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
