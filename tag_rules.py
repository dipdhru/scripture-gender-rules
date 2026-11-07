"""First-pass, keyword-based tagging of rules and their gender focus.

Usage:  python3 tag_rules.py
Input:  data/religious_texts.csv         (from build_dataset.py)
Output: data/rules_tagged.csv            (one row per unit, with tags)
        data/validation_sample.csv       (random sample to check by hand)

This is a transparent baseline, not a final classifier: every tag comes from
a pattern below, so you can see exactly why a row got it. CODEBOOK.md
defines each tag; the accuracy measured on the validation sample says how
far to trust it.
"""

import csv
import random
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "data" / "religious_texts.csv"
OUT = ROOT / "data" / "rules_tagged.csv"
SAMPLE = ROOT / "data" / "validation_sample.csv"


def rx(*words):
    return re.compile(r"\b(?:" + "|".join(words) + r")\b", re.I)


# --- Is this unit a rule? ----------------------------------------------------
# Two cue sets, because genre matters. Law codes (Manu, Rehat Maryada, Jain
# and Buddhist monastic codes) are almost entirely normative, so any modal verb
# counts. Bible, Torah and Quran mix law with narrative and prophecy, where
# "shall", "should" and "may" are usually future tense or purpose clauses
# ("thine enemies shall perish", "that He may reward"), so they need
# stricter, second-person or legal-formula cues.
LAW_CODES = {"Hinduism", "Jainism", "Sikhism", "Buddhism"}

# Clause-initial negative imperative: "Marry not", "Slay not", "Approach not".
NEG_IMPERATIVE = re.compile(
    r"(?:^|[.!:;] |, and )(?:And |But |So )?(?!(?:Is|Was|Are|Were|Have|Hath|Had|Shall|Will|"
    r"Would|Could|Should|Did|Doth|Do|Can|Knowest|Seest|He|She|It|They|We|I|Ye|Thou|Who|Which|"
    r"Why|Art|Am|Wilt|Saw|Know|Fear|Be)\b)[A-Z][a-z]+ not\b")
# Clause-initial commands common in the Quran and the Torah's law sections.
IMPERATIVE = re.compile(
    r"(?:^|[.!:;] |, and )(?:And |So |Then )?(?:Establish|Pay|Fight|Slay|Marry|Wed|Spend|Fulfil|"
    r"Observe|Perform|Lower|Guard|Obey|Divorce|Restrain|Honour|Remember the sabbath|Keep "
    r"(?:my|the|your)|Give (?:unto|the|them|full|women)|Eat (?:of|ye)|Wash)\b")

PROHIBITION_STRICT = rx(
    r"thou shalt not", r"ye shall not", r"you shall not", r"shall ye not", r"shalt thou not",
    r"thou shalt neither", r"ye shall neither", r"thou mayest not",
    r"let (?:him|her|them|no man|not) [\w\s,]{0,30}not", r"let no (?:man|one|woman)",
    r"(?:is|are) (?:forbidden|prohibited|unlawful|not lawful)", r"forbidden unto you",
    r"shall not be (?:eaten|done|made|seen)", r"must not",
)
PERMISSION_STRICT = rx(
    r"(?:it is|is made|are made) lawful", r"lawful (?:unto|for) you", r"(?:is|are) permitted",
    r"it is no sin", r"no sin for", r"no blame", r"ye may eat", r"thou mayest (?:eat|take)",
)
OBLIGATION_STRICT = rx(
    r"thou shalt", r"ye shall", r"you shall", r"shall (?:surely )?be put to death",
    r"let (?:him|her|them|every man|each)\b(?! (?:alone|go)\b)", r"O ye who believe",
    r"prescribed (?:for|unto) you", r"decreed for you", r"(?:is|are) enjoined",
    r"commanded (?:you|thee)", r"(?:a |an )?statute for ever", r"(?:is|are) obligatory",
    r"it is (?:a|his|her|their|your) duty", r"must", r"the priest shall",
)
# Conditional law: "If a man ...", "When a woman ...", "Whosoever ..." + shall.
CASE_LAW = re.compile(
    r"\b(?:if|when|whosoever|whoso|whatsoever|every) (?:a |any |the )?(?:man|woman|soul|person|"
    r"ox|one|priest|thy|ye|thou|he|she|they|beast|wife|husband|daughter|son|servant)\b"
    r".{0,200}\bshall\b", re.I | re.S)

PROHIBITION_BROAD = rx(
    r"shalt not", r"shall not", r"shall no", r"must not", r"should not", r"ought not",
    r"may not", r"do not", r"don['’]t", r"let (?:him|her|them|no) [\w\s,]{0,30}not",
    r"let (?:no|none)", r"(?:is|are) (?:forbidden|prohibited|unlawful|not lawful|not allowed)",
    r"never (?:shall|should|let)", r"nor shall", r"abstain from", r"cannot", r"can not",
    r"(?:is|are) not proper", r"improper",
    r"(?:commits?|committing) an offense", r"is expelled", r"offense entailing",
    r"(?:he|she) is (?:also )?(?:expelled|excluded)", r"neither \w+ nor", r"should neither",
)
PERMISSION_BROAD = rx(
    r"(?:it is|is made|are made) lawful", r"(?:is|are) permitted", r"(?:is|are) allowed",
    r"it is no sin", r"no blame", r"there is no offense", r"may", r"(?:is|are) entitled",
    r"(?:is|are) optional",
)
OBLIGATION_BROAD = rx(
    r"shall", r"shalt", r"must", r"should", r"ought to", r"let (?:him|her|them|every|a|the|each|one)",
    r"is (?:enjoined|ordained|prescribed|incumbent)", r"(?:is|are) obligatory", r"can only",
    r"(?:is|are) to be", r"it is (?:his|her|their) duty", r"is the duty", r"(?:be|is) punished",
    r"(?:be|is) fined", r"(?:shall|must) pay", r"deserves", r"(?:is|are) ordained",
    r"(?:is|are) (?:proper|desirable|necessary)", r"penance", r"expiat\w*", r"atone\w*",
)
# Rehat Maryada lists its rules as lettered/numbered clauses under a stem
# ("A Sikh's living ... should accord with the Guru's tenets: (a) ... (b) ...").
CLAUSE = re.compile(r"^\((?:[a-z]|[ivx]+|\d+)\)\s")

# --- Who is the rule about? ----------------------------------------------------
# Only explicitly gendered words count. Masculine pronouns (he/him/his) and
# "man/men" in the sense of "people" are grammatical defaults in these
# translations, so they are NOT counted as evidence of a men-only rule.
FEMALE = rx(
    r"wom[ae]n", r"wi(?:fe|ves)", r"daughters?(?:-in-law)?", r"maid(?:en)?s?", r"virgins?",
    r"widows?", r"mothers?", r"girls?", r"females?", r"handmaids?", r"maidservants?",
    r"sisters?", r"nuns?", r"bhikkhunis?", r"concubines?", r"harlots?", r"brides?",
    r"queens?", r"she", r"her", r"hers", r"herself", r"menstruat\w*", r"pregnan\w*",
    r"wet-nurses?", r"nurses?",
)
MALE = rx(
    r"husbands?", r"sons?", r"fathers?", r"brothers?", r"males?", r"monks?", r"bhikkhus?",
    r"bridegrooms?", r"boys?", r"manservants?", r"menservants?", r"sons-in-law",
    r"bachelors?", r"eunuchs?", r"(?:a|any|every|the) man\b(?! of God)",
)

# --- Domain of life the rule regulates (first match wins, most specific first)
DOMAINS = [
    ("sexuality", rx(r"adulter\w*", r"fornicat\w*", r"lie with", r"nakedness",
                     r"sexual\w*", r"intercourse", r"chast\w*", r"lust\w*", r"harlot\w*",
                     r"whore\w*", r"seduc\w*", r"rape", r"sodom\w*", r"physical contact")),
    ("marriage_family", rx(r"marr\w*", r"wedlock", r"wed\w*", r"divorc\w*", r"dowry", r"bride\w*",
                           r"husband\w*", r"wi(?:fe|ves)", r"betroth\w*", r"widow\w*", r"spouse",
                           r"concubine\w*", r"suckl\w*", r"orphan\w*", r"guardian\w*")),
    ("purity_body", rx(r"unclean\w*", r"menstru\w*", r"impur\w*", r"purif\w*", r"defile\w*",
                       r"wash\w*", r"bath\w*", r"leprosy", r"issue of (?:her|his) blood",
                       r"childbirth", r"circumcis\w*", r"hair", r"shav\w*")),
    ("dress_appearance", rx(r"garments?", r"cloth\w*", r"robes?", r"veils?", r"head-?covering",
                            r"adorn\w*", r"jewel\w*", r"ornaments?", r"turban", r"sarong",
                            r"apparel", r"attire", r"cover (?:their|her|his)")),
    ("inheritance_property", rx(r"inherit\w*", r"heirs?", r"estates?", r"propert\w*", r"bequest",
                                r"usury", r"debts?", r"loan\w*", r"wages", r"sell\w*", r"buy\w*",
                                r"money", r"gold", r"silver", r"possessions?")),
    ("legal_justice", rx(r"witness\w*", r"testif\w*", r"judg\w*", r"punish\w*", r"fine[ds]?",
                         r"put to death", r"stoned?", r"stripes", r"lashes", r"theft", r"thie[fv]\w*",
                         r"murder\w*", r"kill\w*", r"slay\w*", r"retaliation", r"court", r"lawsuit")),
    ("food_drink", rx(r"eat\w*", r"food", r"drink\w*", r"wine", r"meat", r"flesh", r"swine",
                      r"alms", r"fast\w*", r"alcohol", r"tobacco", r"intoxica\w*")),
    ("worship_ritual", rx(r"pray\w*", r"sacrific\w*", r"offering\w*", r"altar", r"sabbath",
                          r"worship\w*", r"recit\w*", r"pilgrim\w*", r"feast", r"tithe\w*",
                          r"temple", r"gurdwara", r"mosque", r"ritual\w*", r"ceremon\w*",
                          r"veda", r"scripture\w*", r"initiation")),
    ("social_hierarchy", rx(r"caste\w*", r"brahman\w*", r"kshatriya\w*", r"vaisya\w*", r"sudra\w*",
                            r"slaves?", r"servants?", r"bondm[ae]n", r"strangers?", r"outcast\w*",
                            r"king\w*")),
    ("violence_war", rx(r"war\w*", r"fight\w*", r"battle\w*", r"weapon\w*", r"sword\w*")),
    ("monastic_conduct", rx(r"monastic\w*", r"sangha", r"community", r"ascetic\w*", r"novice\w*",
                            r"ordain\w*", r"preceptor", r"begging", r"lodging", r"dwelling")),
]

TAG_FIELDS = ["is_rule", "rule_type", "mentions_women", "mentions_men", "gender_focus",
              "addressee_guess", "domain"]


def load_units():
    """One unit per row, except the Buddhist codes: there a rule spans several
    segments under a heading like 'Expulsion 3: killing a human being', so
    segments are merged into one unit per heading."""
    units, current = [], None
    heading = re.compile(r"^[A-Z][\w’' ]+ \d+: ")
    for r in csv.DictReader(SRC.open(encoding="utf-8")):
        if r["religion"] != "Buddhism":
            units.append(dict(r, unit_type="verse"))
            continue
        if r["verse"].startswith("0") and heading.match(r["text"]):
            current = dict(r, unit_type="monastic_rule", heading=r["text"], text="")
            units.append(current)
        elif r["verse"].startswith("0") or current is None or current["chapter"] != r["chapter"]:
            # recitation formulas, section titles, closing lines: not rules
            current = None
            units.append(dict(r, unit_type="liturgy"))
        else:
            current["text"] = (current["text"] + " " + r["text"]).strip()
    return units


def tag(u):
    text = u["text"]
    women = bool(FEMALE.search(text))
    men = bool(MALE.search(text))

    if u["unit_type"] == "monastic_rule":
        # every Patimokkha entry is a rule, by construction of the code
        is_rule = True
        rule_type = "prohibition"  # the codes list offenses, i.e. forbidden acts
        addressee = "men" if u["book"].startswith("Bhikkhu ") else "women"
    elif u["unit_type"] == "liturgy":
        is_rule, rule_type, addressee = False, "", ""
    elif u["religion"] in LAW_CODES:
        pro, per, obl = (bool(p.search(text)) for p in
                         (PROHIBITION_BROAD, PERMISSION_BROAD, OBLIGATION_BROAD))
        obl = obl or (u["religion"] == "Sikhism" and bool(CLAUSE.match(text)))
        is_rule = pro or per or obl
        rule_type = "prohibition" if pro else "permission" if per else "obligation" if obl else ""
        addressee = first_gender(text) if is_rule else ""
    else:
        pro = bool(PROHIBITION_STRICT.search(text) or NEG_IMPERATIVE.search(text))
        per = bool(PERMISSION_STRICT.search(text))
        obl = bool(OBLIGATION_STRICT.search(text) or IMPERATIVE.search(text)
                   or CASE_LAW.search(text))
        is_rule = pro or per or obl
        rule_type = "prohibition" if pro else "permission" if per else "obligation" if obl else ""
        addressee = first_gender(text) if is_rule else ""

    focus = ("both" if women and men else "women" if women else
             "men" if men else "neither")
    domain = ""
    if is_rule:
        domain = next((name for name, p in DOMAINS if p.search(text)), "other")
    return {"is_rule": int(is_rule), "rule_type": rule_type,
            "mentions_women": int(women), "mentions_men": int(men),
            "gender_focus": focus if is_rule else "", "addressee_guess": addressee,
            "domain": domain}


# "a monk or a nun", "men and women", "he/she", "sons and daughters"
_M = r"(?:monks?|m[ae]n|males?|sons?|brothers?|husbands?|he|his|him|boys?|bhikkhus?)"
_F = r"(?:nuns?|wom[ae]n|females?|daughters?|sisters?|wi(?:fe|ves)|she|her|girls?|bhikkhunis?)"
_J = r"(?:\s+also)?\s*(?:or|and|/)\s*(?:a |an |the )?"
PAIR = re.compile(rf"\b(?:{_M}{_J}{_F}|{_F}{_J}{_M})\b", re.I)


def first_gender(text):
    """Guess who the rule regulates: 'both' when it names the genders as a
    pair ('a monk or a nun'), otherwise the gender of the first explicitly
    gendered word ('If a woman...' -> women). With no gendered word it is
    'general' (the rule applies to everyone, at least grammatically)."""
    if PAIR.search(text):
        return "both"
    f, m = FEMALE.search(text), MALE.search(text)
    if not f and not m:
        return "general"
    if f and (not m or f.start() < m.start()):
        return "women"
    return "men"


def main():
    units = load_units()
    fields = (["id", "religion", "text_name", "unit_type", "book", "chapter", "verse"]
              + TAG_FIELDS + ["heading", "text"])
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fields, extrasaction="ignore")
        w.writeheader()
        for u in units:
            u.update(tag(u))
            u.setdefault("heading", "")
            w.writerow(u)

    # stratified sample: 15 tagged rules + 5 non-rules per religion, so both
    # precision (are the rules real?) and misses (did we skip rules?) get checked
    random.seed(42)
    by = defaultdict(lambda: {0: [], 1: []})
    for u in units:
        by[u["religion"]][u["is_rule"]].append(u)
    sample = []
    for rel, g in sorted(by.items()):
        sample += random.sample(g[1], min(15, len(g[1])))
        sample += random.sample(g[0], min(5, len(g[0])))
    with SAMPLE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fields + ["check_is_rule", "check_addressee", "note"],
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(sample)

    rules = [u for u in units if u["is_rule"]]
    print(f"{len(units):,} units, {len(rules):,} tagged as rules -> {OUT.relative_to(ROOT)}")
    print(f"{len(sample)} rows for hand-checking -> {SAMPLE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
