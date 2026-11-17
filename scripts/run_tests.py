#!/usr/bin/env python3
"""Run tests with the pytest version declared by this checkout's existing pin."""
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    version = json.loads(Path("build/stack-pin.json").read_text())["quality"]["pytest"]["version"]
    return subprocess.call(["uvx", "--from", f"pytest=={version}", "pytest", "-q", *sys.argv[1:]])


if __name__ == "__main__":
    sys.exit(main())
