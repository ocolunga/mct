#!/usr/bin/env python3
"""Inject bottle do block into Homebrew formula from brew bottle --json output."""
import json
import re
import sys
from pathlib import Path

TAG_ORDER = ["arm64_tahoe", "arm64_sequoia"]


def collect_bottles(bottles_dir):
    """Return (tags, root_url, rebuild) from all .bottle.json files in the directory."""
    tags = {}
    root_url = None
    rebuild = 0
    for json_file in Path(bottles_dir).glob("*.bottle*.json"):
        data = json.loads(json_file.read_text())
        for formula_info in data.values():
            bottle = formula_info["bottle"]
            if root_url is None:
                root_url = bottle.get("root_url")
            rebuild = max(rebuild, bottle.get("rebuild", 0))
            for tag, tag_data in bottle["tags"].items():
                tags[tag] = {
                    "sha256": tag_data["sha256"],
                    "cellar": tag_data.get("cellar", ":any_skip_relocation"),
                }
    return tags, root_url, rebuild


def build_bottle_block(tags, root_url, rebuild):
    lines = ["  bottle do\n"]
    if root_url:
        lines.append(f'    root_url "{root_url}"\n')
    if rebuild:
        lines.append(f'    rebuild {rebuild}\n')
    for tag in TAG_ORDER:
        if tag in tags:
            cellar = tags[tag]["cellar"]
            sha256 = tags[tag]["sha256"]
            padding = " " * (14 - len(tag))
            lines.append(f'    sha256 cellar: {cellar}, {tag}:{padding}"{sha256}"\n')
    lines.append("  end\n")
    return "".join(lines)


def update_formula(formula_path, bottles_dir):
    tags, root_url, rebuild = collect_bottles(bottles_dir)
    if not tags:
        raise RuntimeError(f"No .bottle.json files found in {bottles_dir}")

    content = Path(formula_path).read_text()

    # Remove existing bottle block if present
    content = re.sub(r'\n  bottle do\n.*?  end\n', '\n', content, flags=re.DOTALL)

    # Insert after license line
    bottle_block = "\n" + build_bottle_block(tags, root_url, rebuild)
    content = re.sub(r'(  license ".*"\n)', r'\1' + bottle_block, content)

    Path(formula_path).write_text(content)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <bottles_dir> <formula_path>", file=sys.stderr)
        sys.exit(1)
    update_formula(sys.argv[2], sys.argv[1])
    print("Formula updated with bottle block.")
