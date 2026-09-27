# RimWorld Farsi Translation

<div align="center">

[![RimWorld Version](https://img.shields.io/badge/RimWorld-1.5%2B-blue.svg?logo=steam)](https://rimworldgame.com/)
[![Latest Release](https://img.shields.io/github/v/release/Ludeon/RimWorld-Farsi?color=success&logo=github)](https://github.com/Ludeon/RimWorld-Farsi/releases)
[![CI/CD Pipeline](https://img.shields.io/github/actions/workflow/status/Ludeon/RimWorld-Farsi/persianCorrectionPythonBeta.yml?branch=main&label=CI%2FCD&logo=githubactions)](https://github.com/Ludeon/RimWorld-Farsi/actions)
[![Python Version](https://img.shields.io/badge/Python-3.12%20%7C%203.13%20%7C%20PEP%202026-3776AB.svg?logo=python&logoColor=white)](https://peps.python.org/pep-2026/)
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

This translation package is fully compatible with **RimWorld 1.5+** and supports all major expansions:

| Expansion / DLC | Status | Target Path in Game Directory |
| :--- | :---: | :--- |
| **RimWorld Core** | Supported | `Data/Core/Languages/Persian` |
| **Royalty DLC** | Supported | `Data/Royalty/Languages/Persian` |
| **Ideology DLC** | Supported | `Data/Ideology/Languages/Persian` |
| **Biotech DLC** | Supported | `Data/Biotech/Languages/Persian` |
| **Anomaly DLC** | Supported | `Data/Anomaly/Languages/Persian` |
| **Odyssey** | In Progress | `Data/Odyssey/Languages/Persian` |

---

## 🚀 Installation Instructions

Choose the installation method that fits your setup:

### Method A: Automated Installation on Windows (Recommended)

1. Download [`AutoFaInstall.bat`](AutoFaInstall.bat) or obtain it from the repository root.
2. Copy `AutoFaInstall.bat` into your main RimWorld installation folder (where `RimWorldWin64.exe` is located).
3. Run `AutoFaInstall.bat`. It will automatically fetch the latest release from GitHub and extract the translation folders into their appropriate DLC directories.

---

### Method B: Standard Manual Installation (All Platforms)

1. Download the latest release archive (`persian.language.zip`) from the [Releases Page](https://github.com/Ludeon/RimWorld-Farsi/releases).
2. Locate your game installation directory:
   * **Windows:** `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\`
   * **Linux:** `~/.steam/steam/steamapps/common/Rimworld/`
   * **macOS:** `~/Library/Application Support/Steam/steamapps/common/RimWorld/RimWorldMac.app` *(right-click and select "Show Package Contents")*
3. Extract each subfolder from the archive into the corresponding `Languages` folder inside `Data/<DLC>/Languages/`:
   * Extract `Core` to `<RimWorld>/Data/Core/Languages/Persian`
   * Extract `Royalty` to `<RimWorld>/Data/Royalty/Languages/Persian`
   * Extract `Ideology` to `<RimWorld>/Data/Ideology/Languages/Persian`
   * Extract `Biotech` to `<RimWorld>/Data/Biotech/Languages/Persian`
   * Extract `Anomaly` to `<RimWorld>/Data/Anomaly/Languages/Persian`

> [!IMPORTANT]
> If a `Persian` folder already exists in any of these directories, delete it before copying the new one to avoid obsolete files lingering.
> Ensure that each `Persian` directory contains the expected translation subfolders (`Keyed`, `DefInjected`, etc.) and `LanguageInfo.xml`.

---

### Method C: Development Setup (Symbolic Links)

If you have cloned this repository locally, you can create symbolic links to keep your game synced automatically with your git branch:

- **Windows (Command Prompt as Administrator):**
  ```cmd
  mklink /D "C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Languages\Persian" "C:\path\to\RimWorld-Farsi\Data\Core"
  ```
- **Linux / macOS:**
  ```bash
  ln -s ~/Documents/github/RimWorld-Farsi/Data/Core ~/.steam/steam/steamapps/common/Rimworld/Data/Core/Languages/Persian
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
   - Comprehensive test suite under `tools/rtl-processor/tests/` running on Python 3.12–3.13 and ready for **PEP 2026** calendar-versioned Python releases.
2. **In-Game Mod Patch (`mods/RTL_Persian_Support/`)**:
   - C# Harmony mod providing runtime text-shaping and font adjustments for complex UI elements.
3. **CI/CD Quality Gates (`.github/workflows/`)**:
   - Automated linting (Black, isort, Flake8), type checks (Mypy), security audits (pip-audit), and translation packaging upon PRs.

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
