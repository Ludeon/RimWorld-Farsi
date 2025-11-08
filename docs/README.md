# RimWorld Persian Translation Project - Documentation

## Project Structure

This document outlines the current project organization and directory structure.

### Root Level Directories

```
RimWorld-Farsi/
├── docs/                    # Documentation and guides
├── scripts/                 # Automation scripts and build tools
├── tools/                   # Translation processing tools
│   ├── rtl-processor/       # Main RTL text processing tools
│   └── translation-tools/   # Translation utility scripts
├── mods/                    # Community mod translations (future)
├── archive/                 # Deprecated tools and old files
├── english/                 # Source English translation files
├── Persian/                 # Persian translation files
└── .github/                 # GitHub Actions and workflows
```

### Tools Directory Structure

#### `tools/rtl-processor/`
Contains the main RTL (Right-to-Left) text processing tools:
- `PersianFixer.py` - Main script for processing Persian text
- `validate_xml.py` - XML validation utilities
- `requirements.txt` - Python dependencies
- `tests/` - Unit tests for RTL processing

#### `tools/translation-tools/`
Contains translation utility scripts:
- `find_missing_translations.py` - Identifies missing translations

### Archive Directory

The `archive/` directory contains deprecated tools and files:
- `RTL-Tools-Python/` - Old Python tools (superseded by rtl-processor)
- `PersianConverted/` - Old converted files directory
- `.bak` workflow files - Backup versions of GitHub workflows

### Scripts Directory

Reserved for automation scripts, build tools, and development utilities.

### Mods Directory

Reserved for community mod translations. Each mod should have its own subdirectory.

## Development Workflow

1. **Translation Processing**: Use tools in `tools/rtl-processor/`
2. **Finding Missing Translations**: Use `tools/translation-tools/find_missing_translations.py`
3. **CI/CD**: Automated via GitHub Actions in `.github/workflows/`

## Contributing

See `CONTRIBUTING.md` for detailed contribution guidelines.

## Documentation

- `README.md` - Main project README
- `CONTRIBUTING.md` - Contribution guidelines
- `TODO.md` - Future development tasks
- `issues.md` - Known issues and improvement recommendations
