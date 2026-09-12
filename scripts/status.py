#!/usr/bin/env python3
"""Star overview for a year. Usage: status.py [year]"""
import re
import sys
from aoc_lib import DEFAULT_YEAR, get

year = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_YEAR
page = get(f"/{year}")

stars = {}
for label in re.findall(r'aria-label="([^"]*)"', page):
    m = re.search(r"[Dd]ay (\d+)", label)
    if m:
        stars[int(m.group(1))] = 2 if "two stars" in label else 1 if "one star" in label else 0

total = sum(stars.values())
done = sum(1 for s in stars.values() if s == 2)
print(f"Advent of Code {year}\nday | stars\n----+------")
for d in range(1, 26):
    print(f"{d:3d} | {['-', '⭐', '⭐⭐'][stars.get(d, 0)]}")
print(f"----+------\nDays fully done: {done} / 25\nTotal stars:     {total} / 50")
