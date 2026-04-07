#!/usr/bin/env python3
"""Inject bottle do block into Homebrew formula from brew bottle --json output."""
import json
import re
import sys
from pathlib import Path

TAG_ORDER = ["arm64_tahoe", "arm64_sequoia"]


def collect_bottles(bottles_dir):
    """Return {tag: {sha256, cellar}} from all .bottle.json files in the directory."""
    bottles = {}
    for json_file in Path(bottles_dir).glob("*.bottle.json"):
        data = json.loads(json_file.read_text())
        for formula_info in data.values():
            for tag, tag_data in formula_info["bottle"]["tags"].items():
                bottles[tag] = {
                    "sha256": tag_data["sha256"],
                    "cellar": tag_data.get("cellar", ":any_skip_relocation"),
                }
    return bottles


def build_bottle_block(bottles):
    lines = ["  bottle do\n"]
    for tag in TAG_ORDER:
        if tag in bottles:
            cellar = bottles[tag]["cellar"]
            sha256 = bottles[tag]["sha256"]
            padding = " " * (14 - len(tag))
            lines.append(f'    sha256 cellar: {cellar}, {tag}:{padding}"{sha256}"\n')
    lines.append("  end\n")
    return "".join(lines)


def update_formula(formula_path, bottles_dir):
    bottles = collect_bottles(bottles_dir)
    if not bottles:
        raise RuntimeError(f"No .bottle.json files found in {bottles_dir}")

    content = Path(formula_path).read_text()

    # Remove existing bottle block if present
    content = re.sub(r'\n  bottle do\n.*?  end\n', '\n', content, flags=re.DOTALL)

    # Insert after license line
    bottle_block = "\n" + build_bottle_block(bottles)
    content = re.sub(r'(  license ".*"\n)', r'\1' + bottle_block, content)

    Path(formula_path).write_text(content)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <bottles_dir> <formula_path>", file=sys.stderr)
        sys.exit(1)
    update_formula(sys.argv[2], sys.argv[1])
    print("Formula updated with bottle block.")
