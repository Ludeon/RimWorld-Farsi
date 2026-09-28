# RimWorld Farsi Translation

<div align="center">

[![RimWorld Version](https://img.shields.io/badge/RimWorld-1.5%2B-blue.svg?logo=steam)](https://rimworldgame.com/)
[![Latest Release](https://img.shields.io/github/v/release/Ludeon/RimWorld-Farsi?color=success&logo=github)](https://github.com/Ludeon/RimWorld-Farsi/releases)
[![CI/CD Pipeline](https://img.shields.io/github/actions/workflow/status/Ludeon/RimWorld-Farsi/persianCorrectionPythonBeta.yml?branch=main&label=CI%2FCD&logo=githubactions)](https://github.com/Ludeon/RimWorld-Farsi/actions)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type Checked: Mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

[![Translation Coverage](docs/badges/coverage.svg)](https://Ludeon.github.io/RimWorld-Farsi/)
[![QA Status](docs/badges/qa_status.svg)](https://Ludeon.github.io/RimWorld-Farsi/)
[![Corpus](docs/badges/corpus.svg)](https://Ludeon.github.io/RimWorld-Farsi/)
[![Engine](docs/badges/engine.svg)](https://Ludeon.github.io/RimWorld-Farsi/)

**[🌐 Official Documentation Portal (GitHub Pages)](https://Ludeon.github.io/RimWorld-Farsi/)** • **[🇮🇷 مطالعه این راهنما به زبان فارسی (README_FA.md)](README_FA.md)**

</div>

---

The **official community Persian (فارسی) localization** for **RimWorld**, maintained in collaboration with **Ludeon Studios**. This repository provides full translation coverage, automated bidirectional text processing, and zero-friction 1-click installers for players and translators.

---

## 📚 Documentation & Guides Hub

Explore detailed documentation tailored to your needs:

| Guide | Description | Target Audience |
| :--- | :--- | :--- |
| 🌐 **[Documentation Portal (GitHub Pages)](https://Ludeon.github.io/RimWorld-Farsi/)** | Interactive Web Portal with live grammar playground, searchable lexicon, and install guides. | Everyone |
| 📜 **[PEP 2026: Roadmap & Architecture](docs/TODO.md)** | Strategic architectural specification, 10 implementation phases, and interactive task matrix. | Contributors & AI |
| 🌌 **[Universe Lore & Style Guide](docs/LORE_AND_STYLE_GUIDE.md)** | Canonical Persian translations for world types, Archotechs, factions, and narrative tones. | Writers & Translators |
| 📖 **[Translation Style Guide](docs/TRANSLATION_GUIDE.md)** | Persian typography (`ک`/`ی`), ZWNJ rules, format tokens (`{0}`), and official terminology glossary. | Translators & Reviewers |
| 🧠 **[Technical Challenges & Engine Architecture](docs/TECHNICAL_CHALLENGES.md)** | Why Unity IMGUI lacks text meshes, RTL shaping failures, and the dual-layer solution ([Ludeon #11](https://github.com/Ludeon/RimWorld-ar/issues/11)). | Developers & Modders |
| 🛠️ **[Developer Workflow & Tooling](docs/DEVELOPER_WORKFLOW.md)** | Setup with `uv`, pre-commit hooks, Ruff, Mypy, Pytest, and the `./tools/sync.sh` synchronization script. | Developers & Maintainers |
| 🤝 **[Contributing Guidelines](CONTRIBUTING.md)** | PR branching rules, commit standards, and step-by-step contribution paths. | Everyone |
| 🤖 **[AI Contributor Specification (AGENTS.md)](AGENTS.md)** | Strict behavioral and linguistic rulebook for AI assistants (Gemini, Claude, GPT). | AI & Tooling |

---

## ⚡ Quick Start: 1-Click Installation

### Method A: Automated Installers (Recommended)

* **Windows**:
  1. Download or clone this repository.
  2. Double-click [`install.bat`](install.bat). It automatically detects your Steam/RimWorld installation, deploys translations, and purges cached `.tar` files.
* **Linux / Steam Deck**:
  1. Open terminal in the repository folder.
  2. Run `./install.sh` (or `./install.sh "/path/to/RimWorld"`).

---

### Method B: Manual Installation (All Platforms)

1. Download the latest release package (`persian.language.zip`) from [Releases](https://github.com/Ludeon/RimWorld-Farsi/releases).
2. Locate your game directory:
   * **Windows:** `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\`
   * **Linux:** `~/.steam/steam/steamapps/common/Rimworld/`
   * **macOS:** `~/Library/Application Support/Steam/steamapps/common/RimWorld/RimWorldMac.app`
3. Copy each module folder (`Core`, `Royalty`, `Ideology`, `Biotech`, `Anomaly`, `Odyssey`) into `<RimWorld>/Data/<DLC>/Languages/Persian (فارسی)`.
4. Delete any existing `Persian (فارسی).tar` file in those folders so RimWorld loads the fresh XML files.

---

## ⚙️ In-Game Activation

1. Launch **RimWorld**.
2. Click the **Options** menu (or the **Language Flag** icon).
3. Select **Persian (فارسی)** from the list. The UI reloads immediately.

> [!TIP]
> **100% Save Game Compatible**: Adding or removing this translation pack never alters game logic or breaks existing save files.

---

## 📦 Compatibility & DLC Support Matrix

| Expansion / DLC | Status | Repository Path | Target Game Directory |
| :--- | :---: | :---: | :--- |
| **RimWorld Core** | Supported | `Core/` | `<RimWorld>/Data/Core/Languages/Persian (فارسی)` |
| **Royalty DLC** | Supported | `Royalty/` | `<RimWorld>/Data/Royalty/Languages/Persian (فارسی)` |
| **Ideology DLC** | Supported | `Ideology/` | `<RimWorld>/Data/Ideology/Languages/Persian (فارسی)` |
| **Biotech DLC** | Supported | `Biotech/` | `<RimWorld>/Data/Biotech/Languages/Persian (فارسی)` |
| **Anomaly DLC** | Supported | `Anomaly/` | `<RimWorld>/Data/Anomaly/Languages/Persian (فارسی)` |
| **Odyssey** | In Progress | `Odyssey/` | `<RimWorld>/Data/Odyssey/Languages/Persian (فارسی)` |

---

## 🖼️ In-Game Preview

<div align="center">
  <img src="https://github.com/user-attachments/assets/87633f91-a012-4567-8f07-15aec21a4be2" alt="RimWorld Persian Translation Screenshot" width="850" />
</div>

---

## 🧩 Architectural Highlights & RTL Engine

RimWorld's UI is built on **Unity IMGUI**, which lacks text meshes and native complex text layout engines:

> *"RimWorld uses IMGUI. There are no text meshes."* — **Tynan Sylvester** ([Ludeon/RimWorld-ar#11](https://github.com/Ludeon/RimWorld-ar/issues/11))

To overcome disconnected letters (`پ ا ر س ی` vs `پارسی`) and inverted reading orders, this repository employs a **dual-layer architecture**:
1. **Static XML Presentation Forms Preprocessor (`tools/rtl-processor/`)**: Converts characters into Unicode Arabic Presentation Forms-B and inverts word order for pure vanilla compatibility without mod requirements.
2. **Runtime Harmony Patch (`mods/RTL_Persian_Support/`)**: Intercepts `GUI.Label` and UI routines dynamically for procedural pawn names, combat logs, and font injection (`IranianSans.ttf`).

For a deep technical analysis, see **[docs/TECHNICAL_CHALLENGES.md](docs/TECHNICAL_CHALLENGES.md)**.

---

## 🚫 Kept in English for Stability

To maintain mod compatibility and prevent gameplay bugs:
- **Preset character names and faction titles**: Untranslated where RimWorld lacks internal localization keys.
- **Developer Mode & Debug Logs**: Kept in original English for technical troubleshooting.
- **Keybinding Identifiers**: Retained to match physical keyboards.
- **Original Credits**: Preserved to honor the game's creators.

---

## 🏆 Contributors & Acknowledgements

### Maintainer & Lead Translator
* **Danial Pahlavan** ([@DanialPahlavan](https://github.com/DanialPahlavan))

### Past Contributors
* **Seyed Abdollahi** ([@SeyedAbdollahi](https://github.com/SeyedAbdollahi))

### Acknowledgements
* **Ludeon Studios** for creating RimWorld and supporting community localizations.
* **@mtimoustafa** & **@asidsx** for pioneering Arabic RTL shaping work in RimWorld ([Ludeon/RimWorld-ar#13](https://github.com/Ludeon/RimWorld-ar/issues/13)).

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](LICENSE) file for details.
