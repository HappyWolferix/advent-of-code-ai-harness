#!/usr/bin/env python3
"""Download (and cache) your personalized input. Usage: input.py <day> [year]"""
import sys
from aoc_lib import day_year, fetch_input

day, year = day_year(sys.argv[1:], "input.py <day> [year]")
print(fetch_input(day, year).read_text(), end="")
