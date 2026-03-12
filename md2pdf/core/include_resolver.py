"""Include resolver for ![[file.md | key=value]] syntax.

Supports:
- Variable substitution with {{variable}} placeholders
- Nested includes (up to max_depth levels)
- Circular include detection
- Frontmatter defaults in sub-files
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Matches ![[filename.md]] or ![[filename.md | key=value | key2=value2]]
INCLUDE_RE = re.compile(
    r"!\[\[([^\]|]+?)(?:\|([^\]]*))?\]\]"
)

# Matches {{variable_name}}
PLACEHOLDER_RE = re.compile(r"\{\{(\w+)\}\}")


@dataclass
class IncludeError:
    message: str
    hint: str = ""
    line: int | None = None
    file: Path | None = None

    def __str__(self) -> str:
        parts = [self.message]
        if self.file:
            parts.append(f"  → in {self.file}")
        if self.line:
            parts.append(f"  → Zeile {self.line}")
        if self.hint:
            parts.append(f"  Hinweis: {self.hint}")
        return "\n".join(parts)


@dataclass
class ResolveResult:
    content: str
    warnings: list[str] = field(default_factory=list)
    errors: list[IncludeError] = field(default_factory=list)
    included_files: set[Path] = field(default_factory=set)


def _parse_include_params(params_str: str | None) -> dict[str, str]:
    """Parse 'key=value | key2=value2' into a dict."""
    if not params_str:
        return {}
    params: dict[str, str] = {}
    for part in params_str.split("|"):
        part = part.strip()
        if "=" in part:
            k, _, v = part.partition("=")
            params[k.strip()] = v.strip().strip('"').strip("'")
    return params


def _extract_sub_frontmatter_defaults(text: str) -> tuple[dict[str, Any], str]:
    """Pull defaults out of sub-file frontmatter."""
    if not text.startswith("---"):
        return {}, text
    lines = text.split("\n")
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}, text
    fm_text = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1:])
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        fm = {}
    return fm.get("defaults", {}), body


def _substitute_placeholders(
    text: str,
    variables: dict[str, str],
    warnings: list[str],
    source_file: Path,
) -> str:
    """Replace {{var}} with values. Warn on unresolved placeholders."""
    def replacer(m: re.Match) -> str:
        name = m.group(1)
        if name in variables:
            return variables[name]
        warnings.append(
            f"⚠  Ungelöster Platzhalter '{{{{ {name} }}}}' in {source_file.name}"
        )
        return m.group(0)  # leave as-is

    return PLACEHOLDER_RE.sub(replacer, text)


def resolve_includes(
    text: str,
    source_file: Path,
    variables: dict[str, str] | None = None,
    _stack: list[Path] | None = None,
    _depth: int = 0,
    max_depth: int = 10,
) -> ResolveResult:
    """Recursively resolve all ![[...]] includes in text.

    Args:
        text: Markdown content to process.
        source_file: Absolute path of the file containing this text.
        variables: Variable substitutions passed from parent include.
        _stack: Internal — tracks include chain for circular detection.
        _depth: Internal — current recursion depth.
        max_depth: Maximum allowed nesting depth.

    Returns:
        ResolveResult with resolved content, warnings, errors, and included_files set.
    """
    variables = variables or {}
    _stack = _stack or [source_file.resolve()]
    result = ResolveResult(content="")
    included: set[Path] = set()

    lines = text.split("\n")
    output_lines: list[str] = []

    for line_no, line in enumerate(lines, 1):
        match = INCLUDE_RE.search(line)
        if not match:
            output_lines.append(line)
            continue

        raw_path = match.group(1).strip()
        params = _parse_include_params(match.group(2))

        # Resolve path relative to the current file's directory
        target = (source_file.parent / raw_path).resolve()

        # Circular include detection
        if target in _stack:
            chain = " → ".join(str(p.name) for p in _stack) + f" → {target.name}"
            err = IncludeError(
                message=f"✗  Zirkulärer Include erkannt:",
                hint=chain,
                line=line_no,
                file=source_file,
            )
            result.errors.append(err)
            output_lines.append(f"<!-- CIRCULAR INCLUDE: {raw_path} -->")
            continue

        # Depth check
        if _depth >= max_depth:
            err = IncludeError(
                message=f"✗  Maximale Include-Tiefe ({max_depth}) erreicht",
                hint=f"Include von '{raw_path}' wird übersprungen",
                line=line_no,
                file=source_file,
            )
            result.errors.append(err)
            output_lines.append(f"<!-- MAX DEPTH REACHED: {raw_path} -->")
            continue

        # File existence check
        if not target.exists():
            err = IncludeError(
                message=f"✗  Include nicht gefunden: {raw_path}",
                line=line_no,
                file=source_file,
            )
            result.errors.append(err)
            output_lines.append(f"<!-- FILE NOT FOUND: {raw_path} -->")
            continue

        # Load sub-file
        sub_text = target.read_text(encoding="utf-8")
        sub_defaults, sub_body = _extract_sub_frontmatter_defaults(sub_text)

        # Merge variables: include params > sub defaults > parent variables
        merged_vars = {**variables, **sub_defaults, **params}

        # Recurse
        sub_result = resolve_includes(
            text=sub_body,
            source_file=target,
            variables=merged_vars,
            _stack=[*_stack, target],
            _depth=_depth + 1,
            max_depth=max_depth,
        )

        result.warnings.extend(sub_result.warnings)
        result.errors.extend(sub_result.errors)
        included.add(target)
        included.update(sub_result.included_files)

        # Substitute placeholders in resolved sub-content
        resolved_sub = _substitute_placeholders(
            sub_result.content, merged_vars, result.warnings, target
        )

        # Replace the include line with the resolved content
        prefix = line[: match.start()]
        suffix = line[match.end():]
        block = prefix + resolved_sub + suffix
        output_lines.append(block)

    result.content = "\n".join(output_lines)
    result.included_files = included
    return result
