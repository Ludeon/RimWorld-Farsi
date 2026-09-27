# Contributing to RimWorld Farsi Localization

Thank you for your interest in contributing to the **RimWorld Farsi Localization Project**! This project is the official community Persian translation pack for RimWorld, supported by Ludeon Studios.

Whether you are helping translate in-game text, polishing existing strings, reporting bugs, or improving our Python/C# tooling, your contributions directly impact Persian-speaking players around the world.

---

## 🧭 How to Contribute: Choose Your Track

We welcome two primary tracks of contributions:

1. **[Track A: Translation Contributors](#track-a-translation-contributors)** – Translate or improve XML strings (No programming required).
2. **[Track B: Tooling & Automation Developers](#track-b-tooling--automation-developers)** – Develop Python RTL processing tools, C# mod patches, or CI/CD pipelines.

---

## Track A: Translation Contributors

### 1. Structure of Translation Files
All translation files are standard XML files located under the `Data/` folder for each DLC:
```text
Data/
├── Core/Languages/Persian/
├── Royalty/Languages/Persian/
├── Ideology/Languages/Persian/
├── Biotech/Languages/Persian/
└── Anomaly/Languages/Persian/
    ├── DefInjected/     # Translations injected into game definitions
    ├── Keyed/           # User interface, settings, and gameplay prompts
    ├── Strings/         # Words, names, and general text lists
    └── Backstories/     # Pawn background histories
```

### 2. Editing Translation Keys
A typical translation entry looks like this:
```xml
<!-- EN: Colony animals -->
<Animals>حیوانات مستعمره</Animals>

<!-- EN: {0} has died. Cause: {1}. -->
<LetterPawnDied>{0} جان خود را از دست داد. علت: {1}.</LetterPawnDied>
```

#### Key Translation Rules:
- **Never modify `<!-- EN: ... -->`**: The English comment is RimWorld's reference text. It is used by comparison tools to detect updates.
- **Preserve placeholders and variables**:
  - Tokens like `{0}`, `{1}`, `{2}`, `{PAWN_nameDef}`, or `{BASEKIND_label}` are replaced dynamically by the game engine at runtime. **Do not translate, remove, or alter these bracketed tokens**.
  - Dynamic conditional tokens like `{PAWN_gender ? او : وی}` must retain their exact internal syntax.
- **RTL and Punctuation**:
  - Place Persian punctuation marks (period `.` and question mark `؟`) in appropriate natural reading order.
  - Numbers inside Persian sentences should match natural readability in-game.
- **Consistency**:
  - Stick to established in-game terminology (consult existing translated files in `Keyed/` or `DefInjected/` to match terminology for game mechanics like *Mood*, *Needs*, *Ideoligion*, *Anomaly*, etc.).
- **Recommended Editor**:
  - Use [Visual Studio Code](https://code.visualstudio.com/) with the **XML Tools** or **XML** extension for syntax highlighting and automatic closing tags.

---

## Track B: Tooling & Automation Developers

The project maintains automated text processors, XML validators, and pre-commit test suites.

### 1. Modern Python Environment (PEP Standards & 2026 Readiness)
Our tools run on modern Python (**3.12** and **3.13**), designed with **PEP 2026** (Calendar Versioning) forward compatibility:
- **PEP 8**: Strict code style enforced by `black` and `flake8`.
- **PEP 518 / PEP 621**: Modern tool configuration maintained in [`tools/rtl-processor/pyproject.toml`](tools/rtl-processor/pyproject.toml).
- **PEP 484 / PEP 526**: Static type hinting checked strictly with `mypy`.

### 2. Setting Up Your Development Environment
We recommend using [`uv`](https://github.com/astral-sh/uv) (or standard `venv`):

```bash
# Clone the repository
git clone https://github.com/Ludeon/RimWorld-Farsi.git
cd RimWorld-Farsi

# Create a virtual environment using Python 3.12 or 3.13
uv venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# Install dependencies and development tools
uv pip install -r tools/rtl-processor/requirements.txt

# Install pre-commit hooks
pre-commit install
```

### 3. Local Verification & Testing
Before submitting a pull request, ensure all tests and quality checks pass:

```bash
# Run the Persian RTL processing test suite
python -m pytest tools/rtl-processor/tests/ -v

# Run XML syntax and schema validation
python tools/rtl-processor/validate_xml.py

# Check code formatting and static types
pre-commit run --all-files
```

### 4. C# Mod Development (`mods/RTL_Persian_Support/`)
The in-game patch mod uses **Harmony** to adjust bidirectional font layout in Unity:
- Open [`RimWorld-Farsi.sln`](RimWorld-Farsi.sln) using Visual Studio 2022+ or Rider.
- References RimWorld assembly files (`Assembly-CSharp.dll`, `UnityEngine.dll`) from your local RimWorld installation.
- Maintain minimal performance overhead in Harmony transpilers/postfixes.

---

## 🌿 Git Branching Strategy & PR Workflow

1. **Fork the Repository**:
   - Create your personal fork on GitHub.
2. **Branch from `beta`**:
   - For all translations, bug fixes, and tooling improvements, base your branch on the `beta` branch:
     ```bash
     git checkout beta
     git pull origin beta
     git checkout -b translation/biotech-genes-fa
     ```
   - *Note: `master`/`main` is reserved for stable releases tagged for game updates.*
3. **Commit Messages**:
   - Write clear, concise commit messages following standard conventions:
     - `trans(biotech): translate cosmetic gene definitions`
     - `fix(rtl): resolve character joining issue in dialogue prompt`
     - `tools(xml): add schema validation check for missing closing tags`
4. **Submit a Pull Request**:
   - Open a PR targeting the `beta` branch.
   - Fill out the PR description with:
     - The DLC or tool modified.
     - A brief explanation of the translations or fixes introduced.
     - Confirmation that local validation or tests passed.
5. **CI/CD Checks**:
   - GitHub Actions will automatically run the XML validator, test suites, and formatting checks on your pull request.

---

## ❓ Need Help or Have Questions?

- **Issues**: If you notice a typo, mistranslation, or bug, please open an [Issue](https://github.com/Ludeon/RimWorld-Farsi/issues).
- **Discussions**: Check existing issues or reach out via PR discussions to coordinate on large translation tasks.

Thank you for helping bring the RimWorld universe to Persian-speaking players!
