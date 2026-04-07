#!/usr/bin/env python3
"""Update Homebrew formula: main url/sha256 + all resource blocks."""
import json
import re
import subprocess
import sys
import urllib.request

PACKAGE = "mct-cli"


def pypi_json(name, version):
    url = f"https://pypi.org/pypi/{name}/{version}/json"
    with urllib.request.urlopen(url) as f:
        return json.loads(f.read())


def sdist_url_sha256(name, version):
    data = pypi_json(name, version)
    for u in data["urls"]:
        if u["packagetype"] == "sdist":
            return u["url"], u["digests"]["sha256"]
    raise RuntimeError(f"No sdist for {name}=={version}")


def get_deps(package, version):
    """Return {name: version} for all transitive pip deps (excluding the package itself)."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install",
         "--dry-run", "--ignore-installed", "--quiet",
         "--report", "-", f"{package}=={version}"],
        capture_output=True, text=True, check=True,
    )
    report = json.loads(result.stdout)
    pkg_names = {package.lower(), package.replace("-", "_").lower()}
    return {
        pkg["metadata"]["name"]: pkg["metadata"]["version"]
        for pkg in report["install"]
        if pkg["metadata"]["name"].lower() not in pkg_names
    }


def update_formula(formula_path, main_url, main_sha256, resources):
    with open(formula_path) as f:
        content = f.read()

    # Only replace the top-level url/sha256 (2-space indent, not inside resource blocks)
    content = re.sub(r'^  url ".*"', f'  url "{main_url}"', content, flags=re.MULTILINE)
    content = re.sub(r'^  sha256 ".*"', f'  sha256 "{main_sha256}"', content, flags=re.MULTILINE)

    # Rebuild resource blocks
    blocks = ""
    for name in sorted(resources):
        url, sha256 = resources[name]
        rb_name = name.lower().replace("_", "-")
        blocks += f'\n  resource "{rb_name}" do\n    url "{url}"\n    sha256 "{sha256}"\n  end\n'

    # Replace all existing resource blocks, insert before `def install`
    content = re.sub(r'\n  resource ".*?" do.*?end\n', "", content, flags=re.DOTALL)
    content = content.replace("\n  def install", blocks + "\n  def install")

    with open(formula_path, "w") as f:
        f.write(content)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <version> <formula_path>", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1]
    formula_path = sys.argv[2]

    print(f"Fetching {PACKAGE}=={version} from PyPI...")
    main_url, main_sha256 = sdist_url_sha256(PACKAGE, version)
    print(f"URL: {main_url}")
    print(f"SHA256: {main_sha256}")

    print("Resolving dependencies...")
    deps = get_deps(PACKAGE, version)
    for name, ver in deps.items():
        print(f"  {name}=={ver}")

    resources = {}
    for name, ver in deps.items():
        url, sha256 = sdist_url_sha256(name, ver)
        resources[name] = (url, sha256)

    update_formula(formula_path, main_url, main_sha256, resources)
    print("Formula updated successfully.")
