# Coding instructions: gendered rules in religious texts

You are the second, independent coder in a content-analysis study. Each unit in `units.csv` is one verse, rule or paragraph from a religious text, in an old public-domain English translation. An automatic keyword filter picked each one because it might be a rule mentioning a gender. Code every unit using only its text and the rules below.

## The code

Write one code per unit. A unit that isn't a rule gets `0`. A rule gets 4 characters:

| Position | Question | Values |
|---|---|---|
| 1 | Is it a rule? | `1` = yes (only when it's a rule; otherwise the whole code is `0`) |
| 2 | Whose conduct does it govern? | `M` men only · `W` women only · `B` both genders, named explicitly · `G` everyone; any gendered word is incidental |
| 3 | Effect on women | `R` restricts or burdens women · `P` protects or benefits women, or grants them a right · `X` mixed · `N` no specific effect on women |
| 4 | Effect on men | `R` · `P` · `X` · `N`, same meanings |

Examples of well-formed codes: `0`, `1GNN`, `1MPR`, `1WRN`, `1BRR`.

## Is it a rule? (position 1)

A **rule** commands, forbids, permits or penalizes a behaviour, as a norm for a group of people, now or going forward. That includes laws, prescribed rituals, penalties, conduct codes, and moral instructions given as general commands ("Honour thy father and thy mother", "Let every man be swift to hear").

**Not a rule (`0`):**
- narrative: what someone did or said
- a character's personal order to specific people in a story ("Take thy son…", a king's decree, an oath one person makes another swear)
- prophecy, curses and blessings ("thou shalt be desolate", "ye shall eat the flesh of your sons")
- prayers, hymns, rhetorical questions
- definitions or descriptions with no instruction
- commentary or footnotes

A story character quoting an established law is still a rule if the law is stated.

## Whose conduct it governs (position 2)

- **M**: the rule regulates only men's conduct. This includes rules addressed to men *about* women ("thou shalt not uncover the nakedness of thy sister", "a man shall not marry…"), rules for priests reserved to "Aaron and his sons", and rules for monks only.
- **W**: the rule regulates only women's conduct ("a woman shall…", "a wife must…", "if a woman bear a child she shall be unclean…").
- **B**: the rule names both genders and applies to them equally or jointly ("a monk or a nun should not…", "both the adulterer and the adulteress shall be put to death", "every Sikh man and woman…", "he/she should…").
- **G**: the rule applies to everyone, and the gendered words are incidental ("he that killeth any man", "every man according to his eating", "honour thy father and thy mother"). "He", "him" and "man" used as generic defaults don't make a rule **M**.

## Effect on women and on men (positions 3 and 4)

Judge the effect on each gender as a group, from the rule's own terms:
- **R**: limits their freedom, imposes a duty, burden or penalty, or treats them as lesser or as property.
- **P**: protects them, provides for them, honours them, or grants them a right or permission.
- **X**: clearly both (for example, protection that only applies under a restrictive condition).
- **N**: no specific effect on that gender.

Rules of thumb:
- A rule binding only men usually restricts men (`R` in position 4). Its effect on women is `N`, unless it clearly protects them (`P`, e.g. "must provide for his wife", "shall not sell her") or burdens them (`R`, e.g. avoiding a menstruating woman, excluding women).
- A rule binding both equally usually gets the same letter in positions 3 and 4 (`1BRR` for a shared duty or prohibition, `1BPP` for a shared right).
- A **G** rule with only incidental gender words is usually `1GNN`. Use `P`/`R` for a G rule only when the rule specifically benefits or burdens one gender (e.g. "ye shall not afflict any widow" → `1GPN`).
- Bodily or ritual-impurity rules about women (menstruation, childbirth) restrict women: `R`.

## Output

Write a file `codes.txt` in this same folder, one line per unit, in any order: the unit's `uid`, a space, the code. For example:

```
U000 1MNR
U001 0
```

Code all 200 units. Use only `units.csv` and this file. Don't open any other file or folder on this computer, and don't search the web. Work through the units carefully and independently. When you're done, reply with just the number of units coded and any you found genuinely ambiguous (uid plus a few words).
