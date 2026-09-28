# RimWorld Persian Translation Style Guide & Manual

This guide establishes the linguistic, typographic, and technical standards for contributing Persian (فارسی) translations to RimWorld. All contributors should follow these conventions to ensure a cohesive, professional, and immersive in-game experience.

---

## 1. Directory & File Organization

Translations in this repository mirror official Ludeon localization standards across each game module:

```text
<DLC_Folder>/Languages/Persian/
├── DefInjected/     # Translations injected into game definitions (weapons, buildings, traits, items)
├── Keyed/           # User interface strings, settings, menus, dialog options, gameplay prompts
├── Strings/         # Grammatical lookup lists, name generators, procedural titles
└── Backstories/     # Pawn biographical backstories (childhood, adulthood)
```

### Module Structure
- `Core/`: Base game content.
- `Royalty/`: Empire, psychic powers, titles, permits.
- `Ideology/`: Ideoligions, memes, rituals, relics, roles.
- `Biotech/`: Xenotypes, gene modding, mechanoids, reproduction.
- `Anomaly/`: Dark entities, rituals, containment, psychological phenomena.
- `Odyssey/`: Expansions currently in development.

---

## 2. Persian Typography & Character Rules

To prevent broken rendering, missing glyphs, or search index failures, strict character encoding standards are enforced across all XML files:

### 2.1. Standard Persian Characters vs Arabic Forms
Always use authentic Persian Unicode characters:
- **`ک` (U+06A9)**: Never use Arabic `ك` (U+0643).
- **`ی` (U+06CC)**: Never use Arabic `ي` (U+064A) or `ى` (U+0649).
- **Persian-Specific Letters**: Always use proper Persian Unicode points for `گ` (U+06AF), `چ` (U+0686), `پ` (U+067E), and `ژ` (U+0698).

### 2.2. Zero-Width Non-Joiner (ZWNJ / نیم‌فاصله)
Use the Zero-Width Non-Joiner (Unicode `U+200C`) where standard Persian orthography requires separated suffixes/prefixes:
- **Plurals**: `مهاجم‌ها` or `ساکنان` (use ZWNJ before `ها` where appropriate: `دستگاه‌ها`).
- **Verbal Prefixes**: `می‌شود` (never `میشود` or `می شود`).
- **Compound Adjectives/Nouns**: `تجهیزات جنگی`, `پایان‌ناپذیر`.

> [!TIP]
> In most Persian keyboards (ISIRI standard):
> - **Windows/Linux**: `Shift + Space` produces a Zero-Width Non-Joiner (`\u200c`).

### 2.3. Punctuation in Right-to-Left (RTL) Context
- **Persian Question Mark**: Use `؟` (U+061F), never the English `?`.
- **Persian Comma**: Use `،` (U+060C), never the English `,`.
- **Quotations**: Prefer traditional guillemets `« ... »` for titles, in-game quotes, and dialogue.
- **Numbers**: Within prose, standard Arabic/Persian digits or standard European digits can be used depending on context, but keep punctuation spacing tight to prevent BiDi inversion.

---

## 3. Formatting Tokens & Placeholder Rules

RimWorld's dialogue and notification engine dynamically injects numbers, names, genders, and objects at runtime. **Altering or translating dynamic placeholders will break in-game notifications or crash text rendering.**

### 3.1. Positional Variables
```xml
<!-- CORRECT -->
<!-- EN: {0} has died. Cause: {1}. -->
<LetterPawnDied>{0} جان باخت. علت: {1}.</LetterPawnDied>

<!-- WRONG (Do NOT translate inside braces) -->
<LetterPawnDied>{۰} جان باخت. علت: {۱}.</LetterPawnDied>
```

### 3.2. Named Variables
Named tokens represent game entities. Keep their casing and syntax identical:
- `{PAWN_nameDef}`
- `{PAWN_pronoun}`
- `{PAWN_possessive}`
- `{FACTION_name}`
- `{BASEKIND_label}`

### 3.3. Conditional Gender Syntax
RimWorld supports inline conditional grammar:
```xml
<!-- Syntax: {PAWN_gender ? masculine_text : feminine_text} -->
<ColonistEscaped>{PAWN_nameDef} توانست از زندان {PAWN_gender ? فرار کند : فرار کند}.</ColonistEscaped>
```
*Always preserve the internal delimiter `?` and `:` structure.*

### 3.4. XML Tag Integrity
- **Never translate XML tag names**: `<label>`, `<description>`, `<reportString>` must remain in English. Only translate the text **inside** the opening and closing tags.
- **Preserve the `<!-- EN: ... -->` comments**: RimWorld tools and our Python CI pipelines use these English comments to identify outdated or missing translations.

---

## 4. In-Game Terminology Glossary

Consistency is critical for an immersive translation. Refer to this standard glossary when translating:

| English Term | Standard Persian Translation | Notes / Context |
| :--- | :--- | :--- |
| **Colony** | مستعمره / کلونی | Context-dependent; "مستعمره" for official/lore, "کلونی" for concise UI |
| **Colonist** | ساکن / مهاجر | Inhabitant of the colony |
| **Pawn** | مهره / شخصیت | In-game character unit |
| **Raid** | شبیخون / حمله | Enemy raid event |
| **Ideoligion** | عقیده / آیین | Ideology expansion belief system |
| **Meme** | انگاره / بن‌مایه | Core cultural meme in Ideology |
| **Precept** | قاعده / باور | Ideological rule |
| **Anomaly** | ناهنجاری | Anomaly DLC entity or event |
| **Containment** | مهار / مهارسازی | Entity containment facility |
| **Mood** | روحیّه | Colonist psychological state |
| **Mental Break** | فروپاشی روانی | Extreme distress state |
| **Inspiration** | الهام | Positive colonist state |
| **Psychic** | فراروانی | Psychic phenomenon / psylink |
| **Mechanoid** | مکانوید | Robotic threat / controllable mech |
| **Xenotype** | نژاد ژنتیکی / زنوتایپ | Biotech genetic variety |

---

## 5. Review & Validation Checklist

Before submitting a Pull Request with translations:
1. [ ] **Validate XML Structure**: Run `python tools/rtl-processor/validate_xml.py` to ensure all XML tags are well-formed.
2. [ ] **Verify Placeholders**: Ensure all `{0}`, `{1}`, `{PAWN_nameDef}` tokens are present and intact.
3. [ ] **Check Character Encoding**: Verify that no Arabic `ك` or `ي` characters were accidentally introduced.
4. [ ] **Review Tone**: Ensure translations read naturally in contemporary Persian without awkward word-for-word literal phrasing.
