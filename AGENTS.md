# 🤖 Contributor Guidelines & AI Agent Specification: RimWorld-Farsi

Welcome to the **RimWorld-Farsi** localization repository. This document serves as the canonical behavioral specification and rulebook for both human contributors and AI pair-programming assistants (Claude, GPT, Gemini, Cursor, Copilot, etc.).

All code, XML edits, and translation pull requests must strictly adhere to the standards outlined herein.

---

## 📌 Core Architectural Principles

1. **Human-Readable Source XML**:
   - All XML files under `Core/`, `Royalty/`, `Ideology/`, `Biotech/`, `Anomaly/`, and `Odyssey/` contain standard, modern **UTF-8 Persian** text.
   - Do **NOT** manually apply Unicode presentation forms (e.g. `\uFE80`–`\uFEFC`) to source XML files.
   - Dual-layer processing:
     - **Layer 1**: The CI/CD engine (`tools/rtl-processor/PersianFixer.py`) automatically compiles raw Persian into reversed presentation forms for vanilla mod-free players.
     - **Layer 2**: The C# Harmony mod (`mods/RTL_Persian_Support/`) dynamically injects the **Vazirmatn** font, corrects IMGUI alignments, and applies `LanguageWorker_Persian` for grammatical Ezāfeh.

2. **Zero-Defect CI/CD Quality Gate**:
   - Every commit and pull request is gated by `python tools/qa/run_qa.py --github`.
   - Broken placeholders, Arabic codepoints, or punctuation defects will immediately fail the build.

---

## 🔤 Typography & Linguistic Standards

### 1. Persian Alphabet vs. Arabic Codepoints
Strict Persian Unicode codepoints are mandatory. Never introduce Arabic variant letters:
- **`ک` (U+06A9)** — NEVER use Arabic `ك` (U+0643).
- **`ی` (U+06CC)** — NEVER use Arabic `ي` (U+064A) or `ى` (U+0649).

### 2. Persian Punctuation
Always use Persian punctuation marks in Persian sentences:
- Comma: **`،`** (U+060C) instead of Latin `,`
- Semicolon: **`؛`** (U+061B) instead of Latin `;`
- Question Mark: **`؟`** (U+061F) instead of Latin `?`

> **Note**: Do not alter semicolons or symbols inside `{...}` format tokens or `&...;` XML entities (e.g. `{lookup: {0_label}; ezafeh; 1}` or `&lt;`).

### 3. Zero-Width Non-Joiner (ZWNJ / نیم‌فاصله - U+200C) Rules
- **Verbal Prefixes**:
  - `می‌` and `نمی‌` MUST be separated from the verb by ZWNJ:
    - ✅ `می‌رود`, `نمی‌تواند`, `می‌سازد`
    - ❌ `می رود`, `میرود`, `نمی تواند`
- **Plural Suffix `ها`**:
  - Plural `ها` should be separated by ZWNJ:
    - ✅ `کتاب‌ها`, `استعمارگرها`, `ساختمان‌ها`
    - ❌ `کتاب ها` (space), `کتابها` (joined)
- **Comparative & Superlative Suffixes**:
  - `‌تر` and `‌ترین` should use ZWNJ:
    - ✅ `بزرگ‌تر`, `بهترین` (یا `به‌تر`)

### 4. RimWorld `reportString` Period Rule
RimWorld dynamically appends formatting when displaying pawn jobs from `reportString` tags (e.g. `در حال استراحت`).
- **RULE**: `reportString` tags **MUST NEVER** end with a period (`.` or `۔`).
  - ✅ `<reportString>در حال ساخت {0}</reportString>`
  - ❌ `<reportString>در حال ساخت {0}.</reportString>`

---

## 🧩 Placeholders & Format Tokens (`{...}`)

Placeholders are parsed by RimWorld's internal `GrammarResolverSimple` and must remain structurally intact.

1. **Positional Variables**:
   - Verify that all `{0}`, `{1}`, `{2}` tokens present in the English comment `<!-- EN: ... -->` are preserved in the Persian translation.
   - Do not drop or rename positional tokens.

2. **Named Variables & Subsymbols**:
   - `{PAWN_nameDef}`, `{PAWN_pronoun}`, `{PAWN_possessive}`, `{PAWN_objective}`, `{FACTION_name}`, `{0_label}`.
   - Maintain the exact English variable names inside the braces.

3. **Conditionals**:
   - Syntax: `{VARIABLE ? IF_TRUE : IF_FALSE}`
   - Example: `{PAWN_gender ? مرد : زن}`
   - Branches must be linguistically differentiated (never provide identical text for both branches).

4. **Macros & LanguageWorker Functions**:
   - `{lookup: {0_label}; ezafeh; 1}`
   - `{ezafeh: {0}}`
   - Test placeholder syntax using `python tools/parse_placeholder.py --validate "<text>"`.

---

## 📖 Official Persian RimWorld Glossary (واژه‌نامه مرجع)

Maintain strict consistency with the following canonical translations:

| English Term | Official Persian | Notes / Context |
| :--- | :--- | :--- |
| **Colonist** | استعمارگر | ساکنان مستعمره |
| **Colony** | مستعمره | پایگاه یا سکونت‌گاه بازیکن |
| **Pawn** | مهره / فرد / استعمارگر | اشاره به شخصیت‌ها در بازی |
| **Faction** | فرقه / گروه | جناح‌ها و گروه‌های مختلف |
| **Mechanoid** | مکانوید | ربات‌ها و ماشین‌های جنگی |
| **Raider** | غارتگر | دشمنان مهاجم |
| **Trader** | بازرگان / تاجر | کاروان‌های تجاری |
| **Caravan** | کاروان | سفر روی نقشه جهان |
| **Hediff** | وضعیت سلامت / وضعیت جسمانی | بیماری‌ها، جراحت‌ها و ایمپلنت‌ها |
| **Mood** | روحیه | وضعیت روانی مستعمره‌نشینان |
| **Need** | نیاز | غذا، استراحت، تفریح و ... |
| **Thought** | فکر / احساس | بازخوردهای ذهنی پاون‌ها |
| **Ideoligion** | آیین / باور | سیستم عقیدتی بسته گسترش Ideology |
| **Psycaster** | روان‌پیما | دارندگان توانایی‌های فراطبیعی (Royalty) |
| **Biotech / Xenotype** | بیوتک / گونه ژنتیکی | نژادها و ژن‌ها در بسته گسترش Biotech |
| **Anomaly / Entity** | ناهنجاری / ماهیت ناشناخته | موجودات و رخدادهای بسته گسترش Anomaly |
| **Study / Research** | پژوهش / تحقیق | بررسی موجودات یا توسعه فناوری |
| **Blueprint** | طرح اولیه | طرح سازه‌ها قبل از ساخته شدن |
| **Drop pod** | کپسول پرتاب | کپسول‌های حمل و نقل مداری |
| **Draft** | آماده‌باش نظامی | تغییر وضعیت پاون به حالت رزمی |

---

## 🛠️ Developer & Contributor Commands

Before opening a pull request or submitting code changes, execute the following test suite:

```bash
# 1. Run the unified 4-gate QA Linter suite
python tools/qa/run_qa.py

# 2. Run unit tests
pytest tools/rtl-processor/tests/

# 3. Check code formatting and linting
ruff check .

# 4. Check static typing
mypy tools/
```

To validate any single placeholder or translation sentence:
```bash
python tools/parse_placeholder.py --validate "متن دارای {0_nameDef} و {PAWN_gender ? او : وی}"
```

To update WordInfo grammatical lookup tables:
```bash
python tools/translation-tools/update_wordinfo.py
```
