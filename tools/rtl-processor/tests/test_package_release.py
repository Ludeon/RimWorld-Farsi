import importlib.util
import zipfile
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "translation-tools"
    / "package_release.py"
)
SPEC = importlib.util.spec_from_file_location("package_release", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
package_release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package_release)


def _create_fake_repo(root: Path) -> None:
    """Populate a minimal RimWorld-Farsi repository fixture."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "install.bat").write_text("@echo off\r\necho win\r\n", encoding="utf-8")
    (root / "install.sh").write_text(
        "#!/usr/bin/env bash\necho lin\n", encoding="utf-8"
    )
    (root / "README.md").write_text("# RimWorld Farsi\n", encoding="utf-8")

    # Raw repo translation + English reference Strings
    for mod in ("Core", "Odyssey"):
        (root / mod / "Keyed").mkdir(parents=True)
        (root / mod / "DefInjected").mkdir(parents=True)
        (root / mod / "Strings" / "Words").mkdir(parents=True)
        (root / mod / "Keyed" / "Menus.xml").write_text(
            "<LanguageData><OK>تایید</OK></LanguageData>", encoding="utf-8"
        )
        (root / mod / "Strings" / "Words" / "Old.txt").write_text(
            "فارسی ناقص", encoding="utf-8"
        )

        en_strings = root / "src" / "english" / mod / "Strings" / "Words"
        en_strings.mkdir(parents=True)
        (en_strings / "Nouns.txt").write_text("apple\n", encoding="utf-8")

    # Compiled RTL mod fixture
    mod_dir = root / "mods" / "RTL_Persian_Support"
    (mod_dir / "Assemblies").mkdir(parents=True)
    (mod_dir / "About").mkdir(parents=True)
    (mod_dir / "Source").mkdir(parents=True)
    (mod_dir / "Assemblies" / "RTL_Persian_Support.dll").write_bytes(b"DLL")
    (mod_dir / "Assemblies" / "0Harmony.dll").write_bytes(b"HARMONY")
    (mod_dir / "Vazirmatn.ttf").write_bytes(b"TTF1")
    (mod_dir / "IranianSans.ttf").write_bytes(b"TTF2")
    (mod_dir / "Source" / "RTL_Support.cs").write_text("// src", encoding="utf-8")
    (mod_dir / "About" / "About.xml").write_text(
        "<ModMetaData>\n"
        "    <name>Persian RTL Support</name>\n"
        "    <modDependencies>\n"
        "        <li><packageId>brrainz.harmony</packageId></li>\n"
        "    </modDependencies>\n"
        "    <loadAfter><li>brrainz.harmony</li></loadAfter>\n"
        "</ModMetaData>\n",
        encoding="utf-8",
    )


def _create_processed_build(base: Path, nested: bool) -> None:
    """Create a processed build fixture (supporting nested module artifact layout)."""
    for mod in ("Core", "Odyssey"):
        mod_root = base / mod / mod if nested else base / mod
        (mod_root / "Keyed").mkdir(parents=True)
        (mod_root / "Strings").mkdir(parents=True)
        (mod_root / "Keyed" / "Menus.xml").write_text(
            "<LanguageData><OK>ﺪﯿﯾﺎﺗ</OK></LanguageData>", encoding="utf-8"
        )
        (mod_root / "Strings" / "Test.txt").write_text("test\n", encoding="utf-8")
    (base / "reports.txt").write_text("report", encoding="utf-8")


def test_package_all_releases_structure_and_permissions(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    full_build = tmp_path / "Data"
    essential_build = tmp_path / "Data-essential"
    out_dir = tmp_path / "dist"

    _create_fake_repo(repo)
    _create_processed_build(full_build, nested=True)
    _create_processed_build(essential_build, nested=True)

    outputs = package_release.package_all_releases(
        repo_root=repo,
        full_build_dir=full_build,
        essential_build_dir=essential_build,
        output_dir=out_dir,
        version_tag="v0.4.0-beta.1",
    )

    assert len(outputs) == 8
    assert (out_dir / "autoinstall-windows.bat").is_file()
    assert (out_dir / "autoinstall-linux.sh").is_file()
    assert (out_dir / "autoinstall-windows.bat.sha256").is_file()

    # Check Mod Windows archive
    mod_win_zip = out_dir / "RimWorld-Farsi-With-RTL-Mod-v0.4.0-beta.1-windows.zip"
    assert mod_win_zip.is_file()
    assert mod_win_zip.with_name(mod_win_zip.name + ".sha256").is_file()
    assert mod_win_zip.with_name(mod_win_zip.name + ".md5").is_file()

    with zipfile.ZipFile(mod_win_zip) as zf:
        names = set(zf.namelist())
        assert ".release-edition" in names
        assert zf.read(".release-edition").decode("utf-8").strip() == "mod"
        assert "install-windows.bat" in names
        assert "install-linux.sh" not in names
        # Flattened Raw UTF-8 XML + English Strings + Mod binary without Source/
        assert "Core/Keyed/Menus.xml" in names
        assert "Core/Strings/Words/Nouns.txt" in names
        assert "Core/Strings/Words/Old.txt" not in names
        assert "Core/Core/Keyed/Menus.xml" not in names
        assert "mods/RTL_Persian_Support/Vazirmatn.ttf" in names
        assert "mods/RTL_Persian_Support/Assemblies/RTL_Persian_Support.dll" in names
        assert "mods/RTL_Persian_Support/Source/RTL_Support.cs" not in names
        about_text = zf.read("mods/RTL_Persian_Support/About/About.xml").decode("utf-8")
        assert "<modDependencies>" not in about_text
        assert "<loadAfter>" in about_text

    # Check Essential Linux archive: flattened, +x permission, no mod
    ess_linux_zip = out_dir / "RimWorld-Farsi-Essential-v0.4.0-beta.1-linux.zip"
    with zipfile.ZipFile(ess_linux_zip) as zf:
        names = set(zf.namelist())
        assert zf.read(".release-edition").decode("utf-8").strip() == "essential"
        assert "install-linux.sh" in names
        assert "install-windows.bat" not in names
        assert "Core/Keyed/Menus.xml" in names
        assert "Core/Core/Keyed/Menus.xml" not in names
        assert "mods/RTL_Persian_Support/Vazirmatn.ttf" not in names
        info = zf.getinfo("install-linux.sh")
        mode = (info.external_attr >> 16) & 0o777
        assert mode == 0o755
