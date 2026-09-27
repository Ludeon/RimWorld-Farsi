# RimWorld Farsi Translation

<div align="center">

[![RimWorld Version](https://img.shields.io/badge/RimWorld-1.5%2B-blue.svg?logo=steam)](https://rimworldgame.com/)
[![Latest Release](https://img.shields.io/github/v/release/Ludeon/RimWorld-Farsi?color=success&logo=github)](https://github.com/Ludeon/RimWorld-Farsi/releases)
[![CI/CD Pipeline](https://img.shields.io/github/actions/workflow/status/Ludeon/RimWorld-Farsi/persianCorrectionPythonBeta.yml?branch=main&label=CI%2FCD&logo=githubactions)](https://github.com/Ludeon/RimWorld-Farsi/actions)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checked: Mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

**[🇮🇷 مطالعه این راهنما به زبان فارسی (README_FA.md)](README_FA.md)**

</div>

---

This repository hosts the **official community Farsi (Persian) localization pack** for **RimWorld**, created in collaboration with **Ludeon Studios** and actively maintained by the community.

Because translations bundled directly with the game updates may not always reflect the latest fixes, players can download and install the most up-to-date translation pack directly from this repository.

---

## 📦 Compatibility & DLC Support Matrix

This translation package is fully compatible with **RimWorld 1.5+** and supports all major expansions following official Ludeon Studios localization standards:

| Expansion / DLC | Status | Repository Module | Target Path in Game Directory |
| :--- | :---: | :---: | :--- |
| **RimWorld Core** | Supported | `Core/` | `<RimWorld>/Data/Core/Languages/Persian (فارسی)` |
| **Royalty DLC** | Supported | `Royalty/` | `<RimWorld>/Data/Royalty/Languages/Persian (فارسی)` |
| **Ideology DLC** | Supported | `Ideology/` | `<RimWorld>/Data/Ideology/Languages/Persian (فارسی)` |
| **Biotech DLC** | Supported | `Biotech/` | `<RimWorld>/Data/Biotech/Languages/Persian (فارسی)` |
| **Anomaly DLC** | Supported | `Anomaly/` | `<RimWorld>/Data/Anomaly/Languages/Persian (فارسی)` |
| **Odyssey** | In Progress | `Odyssey/` | `<RimWorld>/Data/Odyssey/Languages/Persian (فارسی)` |

---

## 🚀 Installation Instructions

Choose the installation method that fits your setup:

### Method A: Automated Installation (Recommended)

* **Windows**:
  1. Download or clone this repository.
  2. Double-click [`install.bat`](install.bat). It automatically detects your Steam/RimWorld installation or prompts you to select the folder, deploys the latest translations, and removes cached `.tar` files.
* **Linux / Steam Deck**:
  1. Open terminal in the repository directory.
  2. Run `./install.sh` (or `./install.sh "/path/to/RimWorld"`).

---

### Method B: Standard Manual Installation (All Platforms)

1. Download the latest release archive (`persian.language.zip`) or clone the repository.
2. Locate your game installation directory:
   * **Windows:** `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\`
   * **Linux:** `~/.steam/steam/steamapps/common/Rimworld/`
   * **macOS:** `~/Library/Application Support/Steam/steamapps/common/RimWorld/RimWorldMac.app` *(right-click and select "Show Package Contents")*
3. Copy each module folder from the repository (`Core`, `Royalty`, `Ideology`, `Biotech`, `Anomaly`, `Odyssey`) into the game's corresponding `Data/<DLC>/Languages/Persian (فارسی)` directory:
   * Copy `Core` contents to `<RimWorld>/Data/Core/Languages/Persian (فارسی)`
   * Copy `Royalty` contents to `<RimWorld>/Data/Royalty/Languages/Persian (فارسی)`
   * Copy `Ideology` contents to `<RimWorld>/Data/Ideology/Languages/Persian (فارسی)`
   * Copy `Biotech` contents to `<RimWorld>/Data/Biotech/Languages/Persian (فارسی)`
   * Copy `Anomaly` contents to `<RimWorld>/Data/Anomaly/Languages/Persian (فارسی)`
4. Delete any existing `Persian (فارسی).tar` or `Persian.tar` files in those `Languages` folders to ensure the game reads the updated files directly.

---

### Method C: Developer Synchronization (`tools/sync.sh`)

If you are developing translations or keeping your game synced with your git branch, use the built-in sync tool:

```bash
# Push translations from repo into game
./tools/sync.sh --gamepath "/path/to/RimWorld"

# Pull translations from game back into repo
./tools/sync.sh --gamepath "/path/to/RimWorld" --direction pull
```

---

## ⚙️ In-Game Activation

1. Launch RimWorld.
2. In the main menu, click the **Options** menu or the **Flag icon**.
3. Select **Persian (فارسی)** from the language list.
4. The user interface will reload immediately with Persian text applied.

> [!TIP]
> **Save Game Compatibility**: This translation is 100% safe to add to or remove from existing saves. It does not alter game logic or break save files.

---

## 🖼️ Preview

<div align="center">
  <img src="https://github.com/user-attachments/assets/87633f91-a012-4567-8f07-15aec21a4be2" alt="RimWorld Persian Translation Screenshot" width="850" />
</div>

---

## 🛠️ Tooling & Architecture

To address RimWorld's bidirectional text rendering and XML schema requirements, this repository includes:

1. **RTL Text Preprocessor (`tools/rtl-processor/`)**:
   - Python-based text shaping and bidirectional normalization pipeline (`PersianFixer.py`).
   - Automated XML validation and integrity verification (`validate_xml.py`).
   - Comprehensive test suite under `tools/rtl-processor/tests/` running on Python 3.11–3.13 and strictly adhering to modern PEP standards (PEP 8, PEP 585, PEP 604, PEP 621).
2. **In-Game Mod Patch (`mods/RTL_Persian_Support/`)**:
   - C# Harmony mod providing runtime text-shaping and font adjustments for complex UI elements.
3. **CI/CD Quality Gates (`.github/workflows/`)**:
   - Automated linting and formatting (Ruff), strict type checks (Mypy), security audits (pip-audit), and translation packaging upon PRs.

---

## 🤝 Contributing

Contributions from both translators and software developers are warmly welcomed!

- For translation guides, formatting rules, and developer toolchain setup, please consult **[CONTRIBUTING.md](CONTRIBUTING.md)**.
- Before starting a major translation section, check open [Issues](https://github.com/Ludeon/RimWorld-Farsi/issues) or open a new one to coordinate with maintainers.

---

## 🚫 What is Kept in English

Some game components intentionally remain untranslated to maintain mod compatibility and prevent gameplay bugs:
- **Preset character names and faction titles**: Untranslated where RimWorld lacks internal localization keys.
- **Developer Mode & Debug Logs**: Kept in original English for technical troubleshooting.
- **Keybinding Identifiers**: Retained to match physical keyboards and documentation.
- **Original Credits**: Preserved to honor the game's original creators.

---

## 🏆 Contributors & Acknowledgements

### Maintainer & Active Translator
* **Danial Pahlavan** ([@DanialPahlavan](https://github.com/DanialPahlavan))

### Past Contributors
* **Seyed Abdollahi** ([@SeyedAbdollahi](https://github.com/SeyedAbdollahi))

### Acknowledgements
* **@mtimoustafa** & **@asidsx** for their pioneering work on Arabic RTL text-shaping tools in RimWorld.

---

## 📜 License

This project is open-source and released under the **GNU General Public License v3.0**. See the [LICENSE](LICENSE) file for more information.
