#!/usr/bin/env python3
"""
Convert Aarit's tab-indented outline format → standard markdown bullets.

Aarit writes notes like:
    parent line:
    	first child
    	second child
    		grand-child

Obsidian renders that as a nice nested tree, but Quartz / standard markdown
treats each indented line as plain paragraph text and collapses it. This
script rewrites the files in-place so each tab-indented line becomes a
markdown bullet at the correct nesting level, and consecutive non-tab
lines get hard line breaks so they don't merge.

Idempotent: running it on already-converted files is a no-op.
"""

import re
import sys
from pathlib import Path

LIST_MARKER_RE = re.compile(r"^([-*+]|\d+\.)\s+")
INDENTED_LIST_RE = re.compile(r"^\s*([-*+]|\d+\.)\s+")


def transform(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    in_code_block = False
    in_frontmatter = False
    saw_frontmatter_start = False

    for i, raw in enumerate(lines):
        # Detect frontmatter (--- at very top, --- to close)
        if i == 0 and raw.strip() == "---":
            in_frontmatter = True
            saw_frontmatter_start = True
            out.append(raw)
            continue
        if in_frontmatter:
            out.append(raw)
            if raw.strip() == "---" and saw_frontmatter_start and i > 0:
                in_frontmatter = False
            continue

        # Detect fenced code blocks
        if raw.lstrip().startswith("```"):
            in_code_block = not in_code_block
            out.append(raw)
            continue
        if in_code_block:
            out.append(raw)
            continue

        line = raw.rstrip()
        stripped = line.lstrip("\t")
        tabs = len(line) - len(stripped)

        # Blank line
        if not stripped:
            out.append("")
            continue

        if tabs > 0:
            # Tab-indented line — convert to bullet
            if LIST_MARKER_RE.match(stripped):
                # Already has a list marker (e.g. "1. foo"); preserve it
                indent = "  " * tabs
                converted = f"{indent}{stripped}"
            else:
                indent = "  " * (tabs - 1)
                converted = f"{indent}- {stripped}"

            # Need a blank line before a list block if the previous output
            # line is non-blank and not itself a list item
            if out and out[-1].strip() and not INDENTED_LIST_RE.match(out[-1]):
                out.append("")

            out.append(converted)
            continue

        # Non-tab, non-blank line — paragraph text
        # If the very next line is also a non-tab non-blank line (and
        # not a list item), add a hard line break so they don't merge.
        next_raw = lines[i + 1] if i + 1 < len(lines) else ""
        next_stripped_tabs = next_raw.lstrip("\t")
        next_tabs = len(next_raw) - len(next_stripped_tabs)
        next_content = next_stripped_tabs.rstrip()

        already_marked = LIST_MARKER_RE.match(stripped) or stripped.startswith("#")

        if (
            next_content
            and next_tabs == 0
            and not LIST_MARKER_RE.match(next_content)
            and not next_content.startswith("#")
            and not already_marked
        ):
            out.append(line + "  ")  # markdown hard line break
        else:
            out.append(line)

    return "\n".join(out)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: transform_tabs.py <directory>", file=sys.stderr)
        return 1

    target = Path(sys.argv[1])
    if not target.is_dir():
        print(f"Not a directory: {target}", file=sys.stderr)
        return 1

    md_files = sorted(target.glob("*.md"))
    changed = 0
    for f in md_files:
        original = f.read_text()
        rewritten = transform(original)
        if rewritten != original:
            f.write_text(rewritten)
            changed += 1
            print(f"  ✓ {f.name}")

    print(f"\nTransformed {changed}/{len(md_files)} files in {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
