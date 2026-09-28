"""Unit tests for tools/parse_placeholder.py AST parser."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ruff: noqa: E402
from tools.parse_placeholder import (
    LiteralNode,
    PlaceholderNode,
    PlaceholderParseError,
    PlaceholderParser,
)


def test_parse_simple_literal():
    nodes = PlaceholderParser.parse_string("متن ساده بدون متغیر")
    assert len(nodes) == 1
    assert isinstance(nodes[0], LiteralNode)
    assert nodes[0].text == "متن ساده بدون متغیر"


def test_parse_positional_variables():
    nodes = PlaceholderParser.parse_string("مورد {0} و {1_label}")
    assert len(nodes) == 4
    assert isinstance(nodes[1], PlaceholderNode)
    assert nodes[1].symbol == "0"
    assert nodes[1].subsymbol is None

    assert isinstance(nodes[3], PlaceholderNode)
    assert nodes[3].symbol == "1"
    assert nodes[3].subsymbol == "label"


def test_parse_conditional_syntax():
    nodes = PlaceholderParser.parse_string("او {PAWN_gender ? مرد : زن} است.")
    assert len(nodes) == 3
    ph = nodes[1]
    assert isinstance(ph, PlaceholderNode)
    assert ph.is_conditional
    assert ph.condition_var == "PAWN_gender"
    assert ph.if_true == "مرد"
    assert ph.if_false == "زن"


def test_parse_macro_syntax():
    nodes = PlaceholderParser.parse_string("نام: {lookup: {0_label}; ezafeh; 1}")
    assert len(nodes) == 2
    ph = nodes[1]
    assert isinstance(ph, PlaceholderNode)
    assert ph.is_macro
    assert ph.macro_name == "lookup"
    assert len(ph.macro_args) == 3
    assert ph.macro_args[0] == "{0_label}"
    assert ph.macro_args[1] == "ezafeh"
    assert ph.macro_args[2] == "1"
    assert len(ph.nested_placeholders) == 1
    assert ph.nested_placeholders[0].symbol == "0"
    assert ph.nested_placeholders[0].subsymbol == "label"


def test_parse_unclosed_brace_raises():
    with pytest.raises(PlaceholderParseError):
        PlaceholderParser.parse_string("متن خراب {0_label بدون بستن")


def test_validate_text_clean():
    errors = PlaceholderParser.validate_text("سلام {0_nameDef} به مستعمره!")
    assert len(errors) == 0


def test_validate_text_invalid():
    errors = PlaceholderParser.validate_text("متن {PAWN_gender ? فقط_یک_طرف} ناقص")
    assert len(errors) == 1
    assert "Parse error" in errors[0]
