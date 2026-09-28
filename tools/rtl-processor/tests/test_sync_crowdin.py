"""Unit tests for tools/crowdin-sync/sync_crowdin.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "crowdin-sync"))

# ruff: noqa: E402
from sync_crowdin import CrowdinSyncBridge


def test_export_and_import_bundle(tmp_path: Path):
    repo_dir = tmp_path / "repo"
    export_dir = tmp_path / "export"
    import_dir = tmp_path / "import"

    # Setup mock repo
    mod_dir = repo_dir / "Core" / "Keyed"
    mod_dir.mkdir(parents=True)
    xml_file = mod_dir / "Test.xml"
    xml_file.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<LanguageData>\n'
        '  <!-- EN: Hello World -->\n'
        '  <Greeting>سلام دنیا</Greeting>\n'
        '</LanguageData>\n',
        encoding="utf-8"
    )

    bridge = CrowdinSyncBridge(repo_root=repo_dir)

    # 1. Test Export
    exported = bridge.export_bundle(output_dir=export_dir, modules=["Core"])
    assert exported == 1

    json_file = export_dir / "Core" / "Keyed" / "Test.json"
    assert json_file.exists()
    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert data["Greeting"]["en"] == "Hello World"
    assert data["Greeting"]["fa"] == "سلام دنیا"

    # 2. Test Import update
    data["Greeting"]["fa"] = "درود بر جهان"
    import_file = import_dir / "Core" / "Keyed" / "Test.json"
    import_file.parent.mkdir(parents=True)
    import_file.write_text(json.dumps(data), encoding="utf-8")

    imported = bridge.import_bundle(input_dir=import_dir)
    assert imported == 1

    updated_xml = xml_file.read_text(encoding="utf-8")
    assert "<Greeting>درود بر جهان</Greeting>" in updated_xml
