#!/usr/bin/env python3
"""
RimWorld Deterministic AST Placeholder Parser.

Parses and validates RimWorld's GrammarResolver format tokens ({...})
including positional variables, named subsymbols, conditionals, and function macros.

Examples of supported syntax:
  - Positional: {0}, {1}, {2_label}, {0_gender}
  - Named: {PAWN_nameDef}, {FACTION_name}, {INITIATOR_pronoun}
  - Conditional: {0_gender ? he : she}, {PAWN_gender ? مرد : زن}
  - Function / Macro: {lookup: {0_label}; ezafeh; 1}, {replace: {0}; "old"; "new"}
  - Custom LanguageWorker: {ezafeh: {0}}

Usage:
  python tools/parse_placeholder.py "Hello {0_nameDef}, is {PAWN_gender ? he : she} here?"
  python tools/parse_placeholder.py --validate "File or text to validate"
  python tools/parse_placeholder.py --json "{0_gender ? مرد : زن}"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LiteralNode(ASTNode):
    """Raw text outside of or between placeholders."""
    text: str
    node_type: str = "Literal"


@dataclass
class PlaceholderNode(ASTNode):
    """Parsed {...} token representing a variable, conditional, or macro."""
    raw: str
    symbol: str = ""
    subsymbol: str | None = None
    is_conditional: bool = False
    condition_var: str | None = None
    if_true: str | None = None
    if_false: str | None = None
    is_macro: bool = False
    macro_name: str | None = None
    macro_args: list[str] = field(default_factory=list)
    nested_placeholders: list[PlaceholderNode] = field(default_factory=list)
    node_type: str = "Placeholder"



class PlaceholderParseError(ValueError):
    """Raised when placeholder syntax is malformed."""
    def __init__(self, message: str, position: int = -1, snippet: str = ""):
        super().__init__(message)
        self.position = position
        self.snippet = snippet


class PlaceholderParser:
    """
    Deterministic AST Parser for RimWorld translation placeholders.
    """

    @classmethod
    def parse_string(cls, text: str) -> list[ASTNode]:
        """
        Parses a full translation string containing literals and placeholders into a list of ASTNodes.
        """
        nodes: list[ASTNode] = []
        length = len(text)
        i = 0
        literal_start = 0

        while i < length:
            if text[i] == '{':
                # Capture preceding literal text
                if i > literal_start:
                    nodes.append(LiteralNode(text=text[literal_start:i]))

                # Find matching closing brace taking nesting into account
                brace_depth = 1
                token_start = i
                i += 1

                while i < length and brace_depth > 0:
                    if text[i] == '{':
                        brace_depth += 1
                    elif text[i] == '}':
                        brace_depth -= 1
                    i += 1

                if brace_depth != 0:
                    raise PlaceholderParseError(
                        f"Unclosed placeholder brace starting at index {token_start}",
                        position=token_start,
                        snippet=text[token_start:min(length, token_start + 40)]
                    )

                raw_token = text[token_start:i]
                node = cls.parse_token(raw_token)
                nodes.append(node)
                literal_start = i
            else:
                i += 1

        if literal_start < length:
            nodes.append(LiteralNode(text=text[literal_start:length]))

        return nodes

    @classmethod
    def parse_token(cls, raw: str) -> PlaceholderNode:
        """
        Parses a single {...} placeholder token into a structured PlaceholderNode.
        """
        raw = raw.strip()
        if not (raw.startswith('{') and raw.endswith('}')):
            raise PlaceholderParseError(f"Token must start with '{{' and end with '}}': {raw}")

        inner = raw[1:-1].strip()
        node = PlaceholderNode(raw=raw)

        # Check for nested placeholders inside inner (e.g. {lookup: {0_label}; ezafeh; 1})
        if '{' in inner:
            # Parse nested tokens
            nested_matches = re.finditer(r'\{[^{}]+\}', inner)
            for m in nested_matches:
                nested_node = cls.parse_token(m.group(0))
                node.nested_placeholders.append(nested_node)

        # 1. Macro function syntax: {name: arg1; arg2; ...} or {name: arg}
        if ':' in inner and ('?' not in inner or inner.find(':') < inner.find('?')):
            colon_pos = inner.find(':')
            macro_candidate = inner[:colon_pos].strip()
            # Verify macro candidate is a valid identifier (lookup, replace, case, ezafeh, etc.)
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', macro_candidate):
                node.is_macro = True
                node.macro_name = macro_candidate
                args_str = inner[colon_pos + 1:].strip()
                # Split args by semicolon outside nested braces
                args: list[str] = []
                cur_arg: list[str] = []
                depth = 0
                for ch in args_str:
                    if ch == '{':
                        depth += 1
                        cur_arg.append(ch)
                    elif ch == '}':
                        depth -= 1
                        cur_arg.append(ch)
                    elif ch == ';' and depth == 0:
                        args.append("".join(cur_arg).strip())
                        cur_arg = []
                    else:
                        cur_arg.append(ch)
                if cur_arg:
                    args.append("".join(cur_arg).strip())

                node.macro_args = args
                node.symbol = macro_candidate
                return node

        # 2. Conditional syntax: {var ? if_true : if_false}
        if '?' in inner:
            q_pos = inner.find('?')
            c_pos = inner.find(':', q_pos)
            if c_pos == -1:
                raise PlaceholderParseError(
                    f"Conditional token missing ':' branch: {raw}",
                    snippet=raw
                )
            cond_var = inner[:q_pos].strip()
            true_branch = inner[q_pos + 1:c_pos].strip()
            false_branch = inner[c_pos + 1:].strip()

            node.is_conditional = True
            node.condition_var = cond_var
            node.if_true = true_branch
            node.if_false = false_branch
            node.symbol = cond_var

            # Extract subsymbol if cond_var has one
            if '_' in cond_var:
                parts = cond_var.split('_', 1)
                node.symbol = parts[0]
                node.subsymbol = parts[1]

            return node

        # 3. Simple or Subsymbol Variable: {0}, {0_label}, {PAWN_nameDef}
        node.symbol = inner
        if '_' in inner:
            parts = inner.split('_', 1)
            node.symbol = parts[0]
            node.subsymbol = parts[1]

        return node

    @classmethod
    def validate_text(cls, text: str) -> list[str]:
        """
        Validates all placeholders in the text and returns a list of error descriptions (empty if valid).
        """
        errors: list[str] = []
        try:
            nodes = cls.parse_string(text)
        except PlaceholderParseError as e:
            errors.append(f"Parse error: {e}")
            return errors

        for node in nodes:
            if isinstance(node, PlaceholderNode):
                if node.is_conditional:
                    if not node.condition_var:
                        errors.append(f"Empty condition variable in: {node.raw}")
                    if node.if_true is None or node.if_false is None:
                        errors.append(f"Missing conditional branches in: {node.raw}")
                elif node.is_macro:
                    if not node.macro_name:
                        errors.append(f"Empty macro name in: {node.raw}")
                else:
                    if not node.symbol:
                        errors.append(f"Empty variable in: {node.raw}")
        return errors


def print_ast(nodes: Sequence[ASTNode], indent: int = 0) -> None:
    """Pretty prints the AST to stdout."""
    prefix = "  " * indent
    for node in nodes:
        if isinstance(node, LiteralNode):
            escaped = repr(node.text)
            print(f"{prefix}Literal: {escaped}")
        elif isinstance(node, PlaceholderNode):
            if node.is_conditional:
                print(f"{prefix}Placeholder (Conditional):")
                print(f"{prefix}  Var: {node.condition_var}")
                print(f"{prefix}  If True:  {repr(node.if_true)}")
                print(f"{prefix}  If False: {repr(node.if_false)}")
            elif node.is_macro:
                print(f"{prefix}Placeholder (Macro): {node.macro_name}")
                for idx, arg in enumerate(node.macro_args):
                    print(f"{prefix}  Arg[{idx}]: {arg}")
            else:
                sub = f" (Subsymbol: {node.subsymbol})" if node.subsymbol else ""
                print(f"{prefix}Placeholder (Var): {node.symbol}{sub}")
            if node.nested_placeholders:
                print(f"{prefix}  Nested:")
                print_ast(node.nested_placeholders, indent + 2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic AST Placeholder Parser for RimWorld Localization"
    )
    parser.add_argument("text", help="Text containing placeholders to parse or validate")
    parser.add_argument("--json", action="store_true", help="Output AST as JSON")
    parser.add_argument("--validate", action="store_true", help="Validate and exit with code 0/1")

    args = parser.parse_args()

    if args.validate:
        errors = PlaceholderParser.validate_text(args.text)
        if errors:
            print("Validation FAILED:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            return 1
        print("Validation PASSED: All placeholders are well-formed.")
        return 0

    try:
        nodes = PlaceholderParser.parse_string(args.text)
    except PlaceholderParseError as e:
        print(f"Error parsing placeholder: {e}", file=sys.stderr)
        return 1

    if args.json:
        dicts = [n.to_dict() for n in nodes]
        print(json.dumps(dicts, indent=2, ensure_ascii=False))
    else:
        print_ast(nodes)

    return 0


if __name__ == "__main__":
    sys.exit(main())
