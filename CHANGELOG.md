# Changelog

All notable releases of **RimWorld Farsi** are documented on the [GitHub Releases](https://github.com/Ludeon/RimWorld-Farsi/releases) page.

## [v0.4.0] - 2026-11-27
- **Typography & BiDi Engine (`RTL_Persian_Support`):** Bundled `Vazirmatn.ttf` as the default Persian typeface alongside `IranianSans.ttf`, implemented standard `UAX #9` BiDi & paired-bracket reordering, added width-aware logical word wrapping (`FixForWidth`), and fixed world-map & UI clipping issues.
- **Three Editions & 1-Click Auto-Installers:** Introduced `With RTL Mod`, `Essential`, and `Full` OS-labeled ZIP packages plus standalone `autoinstall-windows.bat` and `autoinstall-linux.sh` launchers.
- **Localization & QA Tooling:** Added `src/english/` reference mirror, canonical glossary/terminology checks, deterministic placeholder AST parsing, and 82 unit tests.

## [v0.3.6] - 2026-09-28
- Preserved RimWorld grammar rule keywords and `->` operators in `PersianFixer`.
- Updated installers to fetch latest GitHub Release assets automatically with local fallback and module validation.

## [v0.3.5] - 2026-09-28
- Added `RTL_Persian_Support` C# Harmony mod (`ArabicSupport` shaping + custom font loading) via intermediate tag `v0.3.4`.
- Expanded translations across `Core`, `Royalty`, `Ideology`, `Biotech`, `Anomaly`, and `Odyssey` and aligned repo layout with Ludeon standards.

## [v0.3.3] - 2025-11-08 (Pre-release)
- Introduced Python RTL processor under `tools/rtl-processor/`, `README_FA.md`, XML validation, and Sigstore/SLSA CI checks.

## [v0.3.2] - 2025-07-13
- Updated translations to RimWorld `1.6.4516` and improved RTL letter contextualization.

## [v0.3.0] - [v0.3.1.1] - 2025-06 to 2025-07
- Updated translations for `1.5.4409`, added `LICENSE` & `CONTRIBUTING.md`, and modularized release CI workflows.

## [v0.1.0] - [v0.2.1] - 2022-12 to 2025-04
- Initial `1.4` and `1.5` main menu and Core/DLC translations, `PersianCorrection.yml` automation, and initial `AutoFaInstall.bat` Windows installer.
