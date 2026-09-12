#!/usr/bin/env python3
"""Submit part 1. Usage: submit1.py <day> <answer> [year]"""
import subprocess
import sys
from pathlib import Path

if len(sys.argv) < 3:
    sys.exit("usage: submit1.py <day> <answer> [year]")
sys.exit(subprocess.call([sys.executable, str(Path(__file__).parent / "submit.py"),
                          sys.argv[1], "1", *sys.argv[2:]]))
