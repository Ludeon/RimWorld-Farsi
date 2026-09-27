# Contributing to RimWorld Farsi Localization

Thank you for your interest in contributing to the **RimWorld Farsi Localization Project**! This project is the official community Persian translation pack for RimWorld, supported by Ludeon Studios.

Whether you are helping translate in-game text, polishing existing strings, reporting bugs, or improving our Python/C# tooling, your contributions directly impact Persian-speaking players around the world.

---

## 🧭 How to Contribute: Choose Your Track

We welcome two primary tracks of contributions:

1. **[Track A: Translation Contributors](#track-a-translation-contributors)** – Translate or improve XML strings (No programming required).  
   👉 **Read the comprehensive [Translation Style Guide & Manual](docs/TRANSLATION_GUIDE.md)** for glossary, typography, and placeholder rules.
2. **[Track B: Tooling & Automation Developers](#track-b-tooling--automation-developers)** – Develop Python RTL processing tools, C# mod patches, or CI/CD pipelines.  
   👉 **Read the [Developer Workflow Guide](docs/DEVELOPER_WORKFLOW.md)** and **[Technical Challenges & Engine Details](docs/TECHNICAL_CHALLENGES.md)**.

---

## Track A: Translation Contributors

### 1. Structure of Translation Files
All translation files are standard XML files organized by expansion at the repository root:
```text
RimWorld-Farsi/
├── Core/Languages/Persian/        # Base game strings
├── Royalty/Languages/Persian/     # Royalty DLC strings
├── Ideology/Languages/Persian/    # Ideology DLC strings
├── Biotech/Languages/Persian/     # Biotech DLC strings
├── Anomaly/Languages/Persian/     # Anomaly DLC strings
└── Odyssey/Languages/Persian/     # Odyssey expansion (WIP)
    ├── DefInjected/               # Injected entity and item definitions
    ├── Keyed/                     # UI, settings, menus, and gameplay prompts
    ├── Strings/                   # Grammatical lists and procedural terms
    └── Backstories/               # Colonist backstory histories
```

### 2. Editing Translation Keys
A typical translation entry looks like this:
```xml
<!-- EN: Colony animals -->
<Animals>حیوانات مستعمره</Animals>

<!-- EN: {0} has died. Cause: {1}. -->
<LetterPawnDied>{0} جان خود را از دست داد. علت: {1}.</LetterPawnDied>
```

> [!IMPORTANT]
> For complete guidelines on Persian typography (`ک`/`ی` vs Arabic forms), zero-width non-joiners (نیم‌فاصله), format tokens (`{0}`, `{PAWN_nameDef}`), and standard terminology, please refer to:  
> 📖 **[docs/TRANSLATION_GUIDE.md](docs/TRANSLATION_GUIDE.md)**

---

## Track B: Tooling & Automation Developers

The project maintains automated text processors, XML validators, and pre-commit test suites.

> [!NOTE]
> For in-depth developer documentation, please consult:
> - 🛠️ **[Developer Workflow & Tooling Guide](docs/DEVELOPER_WORKFLOW.md)**: Setup with `uv`, Ruff, Mypy, and Pytest.
> - 🧠 **[Technical Challenges & Engine Details](docs/TECHNICAL_CHALLENGES.md)**: Unity IMGUI limitations, RTL text shaping, and Harmony architecture.
Our tools run on modern Python (**3.11**, **3.12**, and **3.13**), adhering strictly to modern Python standards:
- **PEP 8**: Code style and formatting enforced by `black`, `isort`, and `flake8` / `ruff`.
- **PEP 518 / PEP 621**: Standardized project metadata and build dependencies defined in [`pyproject.toml`](pyproject.toml).
- **PEP 585 / PEP 604 / PEP 484**: Native built-in type hints (`dict`, `list`, `| None`) checked strictly with `mypy`.

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
uv pip install -e ".[dev]"
# Or: uv pip install -r tools/rtl-processor/requirements.txt

# Install pre-commit hooks
pre-commit install
```

### 3. Local Verification & Testing
Before submitting a pull request, ensure all tests and quality checks pass:

```bash
# Run code linting and formatting check
ruff check .
ruff format --check .

# Run the Persian RTL processing test suite
pytest

# Run static type checking
mypy tools/

# Run XML syntax and schema validation across all modules
python tools/rtl-processor/validate_xml.py

# Check pre-commit hooks across all files
pre-commit run --all-files
```

### 4. Syncing with Local Game Installation (`tools/sync.sh`)
You can quickly synchronize translations between this repository and your local RimWorld game directory using `tools/sync.sh`:

```bash
# Push translations to your RimWorld installation
./tools/sync.sh --gamepath "/path/to/RimWorld"

# Preview file transfers without modifying disk
./tools/sync.sh --gamepath "/path/to/RimWorld" --dry-run

# Pull modified translations from your game installation back into the repo
./tools/sync.sh --gamepath "/path/to/RimWorld" --direction pull
```

### 5. C# Mod Development (`mods/RTL_Persian_Support/`)
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
