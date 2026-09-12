#!/usr/bin/env python3
"""Print the puzzle description (parts 1+2 if unlocked). Usage: task.py <day> [year]"""
import sys
from aoc_lib import ROOT, day_year, get, html_to_text

day, year = day_year(sys.argv[1:], "task.py <day> [year]")
text = html_to_text(get(f"/{year}/day/{day}"))

cache = ROOT / "tasks" / f"{year}-day{day:02d}.md"
cache.parent.mkdir(exist_ok=True)
cache.write_text(text + "\n")

print(text)
print(f"\n(saved to {cache.relative_to(ROOT)})", file=sys.stderr)
