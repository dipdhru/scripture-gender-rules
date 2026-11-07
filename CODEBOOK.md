# Codebook: tagging rules and gender

`tag_rules.py` reads `data/religious_texts.csv` and writes `data/rules_tagged.csv` (one row per unit) and `data/validation_sample.csv` (140 rows for hand-checking). Every tag comes from a visible keyword pattern in the script. This is a **baseline**: its accuracy is measured below and isn't good enough yet to publish final numbers.

## Unit

One verse, rule or paragraph, except the Buddhist Pātimokkha. There, each rule spans several segments under a heading (e.g. "Expulsion 3: killing a human being") and is merged into one unit. Recitation formulas are labelled `liturgy` and are never rules.

## Tags

| Tag | Values | Definition |
|---|---|---|
| `is_rule` | 0 / 1 | The unit commands, forbids, permits or penalizes a behaviour. |
| `rule_type` | prohibition / permission / obligation | Prohibition if any negative cue ("shalt not", "forbidden", "is not proper", "commits an offense"); else permission ("lawful", "no sin", "may"); else obligation. |
| `mentions_women`, `mentions_men` | 0 / 1 | An explicitly gendered word appears (woman, wife, daughter, nun, she, her… / husband, son, monk, "a man"…). **he/him/his do not count**, because they are the grammatical default for everyone in these translations. |
| `gender_focus` | women / men / both / neither | Combines the two columns above: which genders the rule is *about*. |
| `addressee_guess` | women / men / both / general | Who must comply. Uses "both" for paired phrases ("a monk or a nun", "man or woman"), otherwise the first gendered word, otherwise "general". For Buddhism it is set by the code (monks' code → men, nuns' code → women). |
| `domain` | sexuality, marriage_family, purity_body, dress_appearance, inheritance_property, legal_justice, food_drink, worship_ritual, social_hierarchy, violence_war, monastic_conduct, other | The first matching keyword group, checked in that order. |

## Two cue sets, by genre

- **Law codes** (Manusmriti, Rehat Maryada, Ākārāṅga, Pātimokkha): any modal verb counts ("shall", "should", "may", "cannot", "is proper", "penance"). Nearly every unit is normative.
- **Scripture with narrative** (Bible, Torah, Quran): only second-person or legal formulas count ("thou shalt", "ye shall", "let him", "O ye who believe", "it is lawful", clause-initial commands like "Marry not", and case law "If a man… shall"). This avoids prophecy and purpose clauses ("thine enemies shall perish", "that He may reward").

## Measured accuracy (hand-checked, 2026-11-07, round 2 on a fresh sample)

| Religion | Tagged rules that really are rules | Non-rules correctly skipped |
|---|---|---|
| Buddhism | 15/15 | 5/5 |
| Jainism | 15/15 | 5/5 |
| Sikhism | 15/15 | ~3/5 (fixed after) |
| Hinduism | 13/15 | 3/5 |
| Judaism | 8/10 | 3/4 |
| Christianity | 8/12 | 6/6 |
| Islam | 7/12 | 6/6 |
| *Rules mentioning women, all religions* | *15/24* | — |

**Main error sources**
1. **Narrative commands.** One character ordering another ("Let her glean", Laban's speech) looks like a rule. This is the biggest error for the Bible, Torah and Quran.
2. **`addressee_guess` is unreliable** for rules *about* women that are *addressed to* men ("the nakedness of thy sister… thou shalt not uncover"; "a Brahmana must not look at a woman…"). Use `gender_focus` for "rules on women"; addressee needs human or LLM coding.
3. **Prophetic "thou shalt"** ("thou shalt be broken…") still passes the strict cues.

**Sanity check:** Islamic scholarship traditionally counts about 500 legal verses (āyāt al-aḥkām) in the Quran. The tagger finds 379, so it's the right order of magnitude.

## Hand coding (2026-11-07)

All 1,789 gender-relevant units outside Buddhism were read and coded by hand (Claude, one coder). Codes are in `data/coding/codes_*.txt`, and `summarize_codes.py` merges them into `data/coded_rules.csv` and `data/results_summary.csv`.

| Position | Meaning | Values |
|---|---|---|
| 1 | Is it a rule? | `0` not a rule (narrative, prophecy, prayer, definition, a character's personal order); `1` rule |
| 2 | Whose conduct it governs | `M` men only · `W` women only · `B` both, named explicitly · `G` everyone, gender incidental |
| 3 | Effect on women | `R` restricts/burdens · `P` protects/benefits/grants a right · `X` mixed · `N` none |
| 4 | Effect on men | same values |

Decisions applied throughout:
- A rule addressed to men about women ("thou shalt not uncover the nakedness of…") governs **M**. Its effect on women is **N** unless it clearly protects or burdens them.
- A rule that applies identically to both genders ("a monk or a nun should not…") is **B** and restricts both (`1BRR`).
- Priestly rules reserved for "Aaron and his sons" govern **M**: `1MNP` where they confer the office, `1MNN` for procedures.
- Biblical laws are coded the same way in the Torah (JPS) and the Old Testament (KJV). Results for Christianity are split by Testament, because most Christian traditions don't treat the Mosaic law as binding.
- **Buddhism** is coded from structure: every Pātimokkha entry restricts its own code's owner (monks' code → `1MNR`, nuns' code → `1WRN`). A 20-rule spot-check agreed 20/20.

**Reliability, stated honestly:** a blind re-code of 100 random units matched the first pass 100%. Because both passes were made by the same coder in one session with prior decisions in context, this is **not** independent evidence of reliability. It shows only that the codes are internally consistent. Inter-coder agreement still needs a second, independent coder.

## Inter-coder reliability (2026-11-07)

An independent second coder (a separate Claude agent with no access to the first codes) coded a stratified random sample of 200 units: 30 per religion, 35 for the Bible and 15 for Buddhism. It worked only from `data/coding/coder2_instructions.md`. Its codes are in `data/coding/coder2_codes.txt`, and `compare_coders.py` writes every unit with both codes to `data/coding/agreement.csv`.

| Code position | Agreement | Cohen's κ (before fix) | κ (after fix) |
|---|---:|---:|---:|
| Is it a rule? | 98% | 0.93 | 0.93 |
| Whose conduct it governs | 90% | 0.87 | 0.87 |
| Effect on women | 86% | 0.80 | 0.82 |
| Effect on men | 85% | 0.76 | 0.79 |

κ above 0.8 is usually read as strong agreement, and 0.6–0.8 as substantial.

**The fix:** coder 1 had coded every Jain "a monk or a nun…" rule as a shared restriction. Permissions ("…may accept…") are shared rights (`1BPP`). Twenty Jain rules whose main clause is a permission were recoded. The "after" column is slightly flattering, because this fix was found by looking at the disagreements.

**Remaining disagreements are judgement calls, left as coded:**
- *Manusmriti's "he".* Coder 1 read rules for "him" (the student, the householder) as men-only (`M`); coder 2 read "he" as generic (`G`). Manu addresses male twice-born men throughout, so both readings are defensible. This is most of why Manusmriti has the lowest exact match (50%). Its men-only count should be read as an upper bound.
- *Ceremony steps* (Sikh weddings, Jain begging procedure): whether "the couple should bow" is neutral procedure (`N`) or a duty (`R`).
- *Mixed effects* (a captive woman's protections, levirate marriage "if she consents"): `P` against `X`.

## Recommended next step

Hand-code, or have an LLM code with human checks, only the gender-relevant subset: rules where `gender_focus` ≠ neither, about 2,160 units. Record `is_rule`, the true addressee, and whether the rule restricts, protects or grants a right. Measure agreement between coders (Cohen's κ) on 100 shared units before trusting the numbers.
