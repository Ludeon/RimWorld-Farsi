# Developer Workflow & Tooling Guide

This document describes the modern Python 2026 development environment, automated testing, quality gates, and synchronization workflows used in the **RimWorld-Farsi** project.

---

## 1. Prerequisites & Environment Setup

This repository uses a modern, standardized configuration defined in [`pyproject.toml`](../pyproject.toml) supporting **Python 3.11, 3.12, and 3.13**.

### Option A: Using `uv` (Recommended)
[`uv`](https://github.com/astral-sh/uv) provides high-performance package management and virtual environment management:

```bash
# Clone the repository
git clone https://github.com/Ludeon/RimWorld-Farsi.git
cd RimWorld-Farsi

# Create a virtual environment and install dev dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Install pre-commit git hooks
uv run pre-commit install
```

### Option B: Using Standard Python `venv`
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

---

## 2. Code Quality & Linting Gates

We enforce strict automated formatting, type-safety, and linting rules across all Python tooling:

```bash
# 1. Run Ruff linter (checks PEP 8, import sorting, security patterns)
ruff check .

# 2. Automatically fix lint issues where possible
ruff check --fix .

# 3. Format code to Black/PEP 8 standards
ruff format .

# 4. Run Mypy static type checking
mypy tools/

# 5. Run all pre-commit hooks manually on all files
pre-commit run --all-files
```

---

## 3. Running Unit Tests

Unit tests are located in `tools/rtl-processor/tests/` and test our RTL string processing, glyph shaping, and bidirectional handling:

```bash
# Run the test suite with coverage
pytest

# Run tests with verbose output
pytest -v
```

---

## 4. 5-Gate QA & XML Translation Validation

Before committing translation changes or creating releases, run the unified 5-gate QA suite and XML validator:

```bash
# Run all 5 QA gates across all 1,500+ translation XML files
python tools/qa/run_qa.py

# Or validate XML syntax standalone
python tools/rtl-processor/validate_xml.py
```

The suite verifies:
- XML syntax and well-formedness.
- Placeholder and gender macro integrity (`{0}`, `{PAWN_gender ? ...}`).
- Persian codepoints (`ک`/`ی`), punctuation, and ZWNJ rules.
- `reportString` trailing-period convention and `AGENTS.md` canonical terminology.

---

## 5. Game Synchronization (`tools/sync.sh`)

When developing translations locally or testing in-game changes, use the developer synchronization script:

### Push to Game
Copies translations from this repository directly into your local RimWorld installation:
```bash
./tools/sync.sh --gamepath "/path/to/RimWorld"
```

### Pull from Game
Pulls modifications made in-game back into the repository tree:
```bash
./tools/sync.sh --gamepath "/path/to/RimWorld" --direction pull
```

### English Reference Files (`src/english/`)
Original English game files (`Keyed/`, `Strings/`, and Core `DefInjected/`) are stored under `src/english/<Module>/`. To refresh them after a RimWorld update or check upstream diffs:
```bash
# Refresh src/english/ from a local RimWorld Data/ folder
python tools/translation-tools/sync_english.py --game-data-dir "/path/to/RimWorld/Data"

# Compare Persian translations against src/english/
python tools/translation-tools/check_upstream_diff.py
```

---

## 6. One-Click Installers (`install.bat` & `install.sh`)

We provide zero-friction installer scripts for players:
- **`install.bat`** (Windows): Auto-detects Steam/RimWorld installations, opens a PowerShell folder picker if needed, cleans cached `.tar` files, and deploys all DLC modules.
- **`install.sh`** (Linux & Steam Deck): Native shell script with automatic steam library detection, directory validation, and clean copy operations.

---

## 7. CI/CD Architecture

Every pull request and commit pushed to `master` or `beta` triggers automated GitHub Actions workflows:
- **Lint & Format**: Runs Ruff and verifies code style across all `tools/`.
- **Type Checking**: Runs `mypy tools/`.
- **Unit Tests**: Executes Pytest suite across Python 3.11, 3.12, and 3.13 plus C# build & xUnit tests via `dotnet test`.
- **QA & XML Validation**: Executes the 5-gate QA suite across all XML files in the repository.
- **Release Packaging**: Automatically builds, attests (SLSA), signs (Sigstore), and publishes releases on `master`.
