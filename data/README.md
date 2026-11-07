# Religious texts dataset

`religious_texts.csv` contains one row per verse, rule or paragraph from the core rule-bearing text of seven religions. It is rebuilt by `python3 build_dataset.py` from the cached downloads in `raw/`.

## Columns

| column | meaning |
|---|---|
| `id` | unique row id, e.g. `ISL-000123` |
| `religion` | Christianity, Islam, Judaism, Buddhism, Hinduism, Jainism, Sikhism |
| `text_name` | e.g. Bible, Quran, Torah, Vinaya Pitaka |
| `translation` | English translator / edition |
| `section` | Old / New Testament (Bible only) |
| `book`, `chapter`, `verse` | location within the text (meaning varies, see below) |
| `text` | the English text |
| `source_url`, `license` | where it came from and its license |

## Contents

| Religion | Text | Translation | Rows | book / chapter / verse | Quality |
|---|---|---|---:|---|---|
| Christianity | Bible (OT + NT) | King James Version (1611) | 31,102 | book / chapter / verse | Clean |
| Islam | Quran | Pickthall (1930) | 6,236 | surah / surah no. / ayah | Clean |
| Judaism | Torah (Genesis–Deuteronomy) | JPS 1917 via Sefaria | 5,846 | book / chapter / verse | Clean |
| Buddhism | Pātimokkha for monks **and** nuns | Bhikkhu Brahmali, SuttaCentral | 1,698 | code / section / segment | Clean |
| Hinduism | Manusmriti (Laws of Manu) | Bühler, SBE 25 (1886) | 2,504 | — / chapter / verse | OCR, ~93% of 2,684 verses |
| Jainism | Ākārāṅga Sūtra | Jacobi, SBE 22 (1884) | 645 | book / lecture, lesson / paragraph no. | OCR, noisy |
| Sikhism | Sikh Rehat Maryada | Kulraj Singh, via sikhs.org | 176 | chapter / article / paragraph | Clean |

## Known limitations

- **Row ≠ rule.** Rows are verses or paragraphs. Many contain no rule (narrative, genealogy), and some contain several. Identifying rules is the next step of the analysis.
- **Different units across religions.** A Bible verse, a Jain paragraph and a Rehat article differ greatly in length, so compare shares and rates, not raw row counts.
- **Manusmriti** comes from an OCR scan. About 180 verses were lost to OCR damage, and about 38 rows still contain a stray footnote or page header.
- **Ākārāṅga Sūtra** comes from an OCR scan. Diacritics are garbled (e.g. `Brahma^a`), about a third of rows have OCR artefacts, and Book 2 lectures 8, 12 and 14 (verse sections without numbered paragraphs) are missing. The Kalpa Sūtra, also in SBE 22, is not included because it is mostly biography.
- **Old translations.** All translations are public domain and therefore 90–140 years old, and their gendered wording reflects their era. For close reading of a rule, check a modern translation or the original language.
- **Not included:** Hadith, Talmud, Guru Granth Sahib and the rest of the Tripitaka. They are large secondary or canonical sources you may want to add later.
- **Rehat Maryada license:** it is the SGPC's official text. The English translation is hosted on sikhs.org, so check their terms before publishing it.
