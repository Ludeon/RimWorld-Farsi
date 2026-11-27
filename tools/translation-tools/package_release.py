#!/usr/bin/env python3
"""
Package RimWorld-Farsi releases for Windows and Linux/macOS.

Creates flat, ready-to-extract archives for all three editions:
1. ``With-RTL-Mod``: Raw UTF-8 translation XMLs + English ``Strings/`` + ``mods/RTL_Persian_Support/``
2. ``Essential``: Processed offline Persian XMLs + English ``Strings/``
3. ``Full``: Complete processed offline Persian XMLs

Each edition is packaged once for Windows (``*-windows.zip`` containing ``install-windows.bat``)
and once for Linux/macOS/Steam Deck (``*-linux.zip`` containing executable ``install-linux.sh``),
alongside standalone ``autoinstall-windows.bat`` / ``autoinstall-linux.sh`` launchers and checksums.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

MODULES = ("Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey")
SUPPORTED_OS = ("windows", "linux")
MOD_SKIP_NAMES = {"Source", "bin", "obj", ".vs"}
MOD_REQUIRED_ASSETS = (
    Path("Assemblies") / "RTL_Persian_Support.dll",
    Path("Assemblies") / "0Harmony.dll",
    Path("Vazirmatn.ttf"),
    Path("IranianSans.ttf"),
    Path("About") / "About.xml",
)
MOD_DEPENDENCIES_BLOCK_RE = re.compile(
    r"\s*<modDependencies>.*?</modDependencies>\s*",
    re.DOTALL,
)


def _resolve_module_source(base_dir: Path, module_name: str) -> Path | None:
    """Resolve either flat ``base_dir/<Module>`` or nested ``base_dir/<Module>/<Module>``."""
    direct = base_dir / module_name
    if not direct.is_dir():
        return None
    nested = direct / module_name
    if nested.is_dir() and (
        (nested / "DefInjected").is_dir()
        or (nested / "Keyed").is_dir()
        or (nested / "LanguageInfo.xml").is_file()
    ):
        return nested
    return direct


def _copy_flattened_modules(src_dir: Path, dest_dir: Path) -> int:
    """Copy translation modules cleanly without double-nested ``<Mod>/<Mod>`` folders."""
    copied = 0
    for module in MODULES:
        resolved = _resolve_module_source(src_dir, module)
        if resolved is None:
            continue
        shutil.copytree(resolved, dest_dir / module)
        copied += 1
    return copied


def _strip_mod_dependencies(about_xml: Path) -> None:
    """Remove Workshop <modDependencies> in standalone bundles where 0Harmony.dll is bundled."""
    content = about_xml.read_text(encoding="utf-8")
    updated = MOD_DEPENDENCIES_BLOCK_RE.sub("\n    ", content)
    if updated != content:
        about_xml.write_text(updated, encoding="utf-8")


def _copy_runtime_mod(mod_src: Path, mod_dest: Path) -> None:
    """Copy compiled ``RTL_Persian_Support`` runtime assets cleanly into the bundle."""
    if not mod_src.is_dir():
        raise FileNotFoundError(f"RTL mod directory not found: {mod_src}")

    for rel_path in MOD_REQUIRED_ASSETS:
        if not (mod_src / rel_path).is_file():
            raise FileNotFoundError(
                f"Required RTL mod asset missing: {mod_src / rel_path}"
            )

    def _ignore(directory: str, names: list[str]) -> set[str]:
        if Path(directory) == mod_src:
            return {n for n in names if n in MOD_SKIP_NAMES}
        return {
            n
            for n in names
            if n in {".DS_Store", "Thumbs.db"} or n.endswith((".log", ".user"))
        }

    shutil.copytree(mod_src, mod_dest, ignore=_ignore)
    _strip_mod_dependencies(mod_dest / "About" / "About.xml")


def prepare_mod_edition_tree(repo_root: Path, dest_dir: Path) -> int:
    """Build raw UTF-8 Essential + RTL Support mod tree inside ``dest_dir``."""
    english_dir = repo_root / "src" / "english"
    if not english_dir.is_dir():
        raise FileNotFoundError(f"English reference directory not found: {english_dir}")

    copied = 0
    for module in MODULES:
        mod_src = repo_root / module
        if not mod_src.is_dir():
            continue
        mod_dst = dest_dir / module
        mod_dst.mkdir(parents=True, exist_ok=True)

        for item_name in ("DefInjected", "Keyed", "WordInfo"):
            src_sub = mod_src / item_name
            if src_sub.is_dir():
                shutil.copytree(src_sub, mod_dst / item_name)

        for file_name in ("LanguageInfo.xml", "LangIcon.png"):
            src_file = mod_src / file_name
            if src_file.is_file():
                shutil.copy2(src_file, mod_dst / file_name)

        en_strings = english_dir / module / "Strings"
        if en_strings.is_dir():
            shutil.copytree(en_strings, mod_dst / "Strings")

        copied += 1

    _copy_runtime_mod(
        repo_root / "mods" / "RTL_Persian_Support",
        dest_dir / "mods" / "RTL_Persian_Support",
    )
    return copied


def _write_checksums(file_path: Path) -> None:
    """Generate ``.sha256`` and ``.md5`` checksum sidecars matching GNU coreutils output."""
    data = file_path.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    md5 = hashlib.md5(data).hexdigest()
    file_path.with_name(f"{file_path.name}.sha256").write_text(
        f"{sha256}  {file_path.name}\n",
        encoding="utf-8",
    )
    file_path.with_name(f"{file_path.name}.md5").write_text(
        f"{md5}  {file_path.name}\n",
        encoding="utf-8",
    )


def _create_os_zip(
    staging_dir: Path,
    zip_path: Path,
    edition_code: str,
    target_os: str,
    repo_root: Path,
) -> None:
    """Package ``staging_dir`` plus OS-specific installer and ``.release-edition`` marker."""
    if target_os not in SUPPORTED_OS:
        raise ValueError(f"Unsupported OS target: {target_os}")

    if target_os == "windows":
        installer_src = repo_root / "install.bat"
        installer_name = "install-windows.bat"
    else:
        installer_src = repo_root / "install.sh"
        installer_name = "install-linux.sh"

    if not installer_src.is_file():
        raise FileNotFoundError(f"Installer script not found: {installer_src}")

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(staging_dir):
            dirs.sort()
            files.sort()
            root_path = Path(root)
            for fname in files:
                fpath = root_path / fname
                rel = fpath.relative_to(staging_dir).as_posix()
                zf.write(fpath, rel)

        # Write bundle edition marker for offline 1-click autodetection
        zf.writestr(".release-edition", f"{edition_code}\n")

        # Write OS-named installer with proper executable mode for Linux/macOS scripts
        installer_info = zipfile.ZipInfo(installer_name)
        installer_bytes = installer_src.read_bytes()
        if target_os == "linux":
            installer_info.external_attr = 0o100755 << 16
        else:
            installer_info.external_attr = 0o100644 << 16
        zf.writestr(installer_info, installer_bytes)

        for doc_name in ("README.md", "README_FA.md"):
            doc_path = repo_root / doc_name
            if doc_path.is_file():
                zf.write(doc_path, doc_name)

    _write_checksums(zip_path)


def package_all_releases(
    repo_root: Path,
    full_build_dir: Path,
    essential_build_dir: Path,
    output_dir: Path,
    version_tag: str,
    staging_root: Path | None = None,
) -> dict[str, Path]:
    """Build all 6 OS-specific release ZIPs and 2 standalone installers in ``output_dir``."""
    output_dir.mkdir(parents=True, exist_ok=True)
    own_staging = staging_root is None
    work_staging = (
        staging_root if staging_root is not None else output_dir / "_staging_tmp"
    )
    if work_staging.exists():
        shutil.rmtree(work_staging)
    work_staging.mkdir(parents=True, exist_ok=True)

    try:
        editions: list[tuple[str, str, Path]] = []

        # 1. With-RTL-Mod staging tree
        mod_stage = work_staging / "With-RTL-Mod"
        mod_stage.mkdir(parents=True)
        prepare_mod_edition_tree(repo_root, mod_stage)
        editions.append(("With-RTL-Mod", "mod", mod_stage))

        # 2. Essential staging tree (flattened)
        essential_stage = work_staging / "Essential"
        essential_stage.mkdir(parents=True)
        _copy_flattened_modules(essential_build_dir, essential_stage)
        for report_file in ("reports.txt", "build_info.json"):
            src_rep = essential_build_dir / report_file
            if src_rep.is_file():
                shutil.copy2(src_rep, essential_stage / report_file)
        editions.append(("Essential", "essential", essential_stage))

        # 3. Full staging tree (flattened)
        full_stage = work_staging / "Full"
        full_stage.mkdir(parents=True)
        _copy_flattened_modules(full_build_dir, full_stage)
        for report_file in ("reports.txt", "build_info.json"):
            src_rep = full_build_dir / report_file
            if src_rep.is_file():
                shutil.copy2(src_rep, full_stage / report_file)
        editions.append(("Full", "full", full_stage))

        created: dict[str, Path] = {}
        for label, edition_code, stage_path in editions:
            for target_os in SUPPORTED_OS:
                zip_name = f"RimWorld-Farsi-{label}-{version_tag}-{target_os}.zip"
                zip_path = output_dir / zip_name
                _create_os_zip(stage_path, zip_path, edition_code, target_os, repo_root)
                created[f"{edition_code}_{target_os}"] = zip_path

        # Standalone auto-install launchers placed alongside ZIPs on GitHub Releases
        win_launcher = output_dir / "autoinstall-windows.bat"
        linux_launcher = output_dir / "autoinstall-linux.sh"
        shutil.copy2(repo_root / "install.bat", win_launcher)
        shutil.copy2(repo_root / "install.sh", linux_launcher)
        linux_launcher.chmod(0o755)
        _write_checksums(win_launcher)
        _write_checksums(linux_launcher)
        created["launcher_windows"] = win_launcher
        created["launcher_linux"] = linux_launcher

        return created
    finally:
        if own_staging and work_staging.exists():
            shutil.rmtree(work_staging)


def main() -> int:
    """CLI entrypoint for CI release packaging."""
    parser = argparse.ArgumentParser(
        description="Package RimWorld-Farsi Windows and Linux release archives."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent,
        help="Path to RimWorld-Farsi repository root",
    )
    parser.add_argument(
        "--full-build",
        required=True,
        type=Path,
        help="Path to processed Full build directory (e.g. Data/)",
    )
    parser.add_argument(
        "--essential-build",
        required=True,
        type=Path,
        help="Path to processed Essential build directory (e.g. Data-essential/)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Destination directory for release ZIPs and launchers",
    )
    parser.add_argument(
        "--version-tag",
        required=True,
        help="Release version or build identifier (e.g. v0.4.0-beta.1)",
    )
    args = parser.parse_args()

    try:
        outputs = package_all_releases(
            repo_root=args.repo_root.resolve(),
            full_build_dir=args.full_build.resolve(),
            essential_build_dir=args.essential_build.resolve(),
            output_dir=args.output_dir.resolve(),
            version_tag=args.version_tag,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for key, path in outputs.items():
        print(f"Created [{key}]: {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
