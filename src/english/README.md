# RimWorld Original English Reference Files

This directory stores a verbatim mirror of RimWorld's official English language files (`<RimWorld>/Data/<Module>/Languages/English/`) across all six modules:

- `Core/` (`About.txt`, `DefInjected/`, `Keyed/`, `LangIcon.png`, `LanguageInfo.xml`, `Strings/`)
- `Royalty/` (`Keyed/`)
- `Ideology/` (`Keyed/`)
- `Biotech/` (`Keyed/`, `Strings/`)
- `Anomaly/` (`Keyed/`, `Strings/`)
- `Odyssey/` (`Keyed/`)

> **Note on `DefInjected/`**: In RimWorld, DLC `DefInjected` English strings originate from each module's `Data/<Module>/Defs/` definitions rather than `Languages/English/`. Consequently, `<!-- EN: ... -->` comments inside the Persian XML files remain the primary English reference for `DefInjected/` tags, while `src/english/` provides the complete official `Languages/English/` source tree (`Keyed/`, `Strings/`, `LanguageInfo.xml`, and Core `DefInjected/`).

## Updating from a Local RimWorld Installation

When a new RimWorld patch or DLC is released, refresh this reference directory using:

```bash
python tools/translation-tools/sync_english.py --game-data-dir "/path/to/RimWorld/Data"
```

## Comparing Translations Against English Source

```bash
python tools/translation-tools/check_upstream_diff.py
```
