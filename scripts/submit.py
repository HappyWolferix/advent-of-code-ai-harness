#!/usr/bin/env python3
"""Submit an answer and interpret the verdict. Usage: submit.py <day> <part> <answer> [year]"""
import sys
from aoc_lib import DEFAULT_YEAR, html_to_text, post

if len(sys.argv) < 4:
    sys.exit("usage: submit.py <day> <part:1|2> <answer> [year]")
day, part, answer = int(sys.argv[1]), sys.argv[2], sys.argv[3]
year = int(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_YEAR
if part not in ("1", "2"):
    sys.exit("part must be 1 or 2")

text = html_to_text(post(f"/{year}/day/{day}/answer", {"level": part, "answer": answer}))
print(text)
print("---")

if "That's the right answer" in text:
    print("RESULT: CORRECT ⭐")
    sys.exit(0)
if "That's not the right answer" in text:
    hint = " (too high)" if "too high" in text else " (too low)" if "too low" in text else ""
    print(f"RESULT: WRONG{hint}")
    sys.exit(1)
if "You gave an answer too recently" in text:
    print("RESULT: RATE LIMITED - wait and retry")
    sys.exit(3)
if "Did you already complete it" in text:
    print("RESULT: ALREADY SOLVED (or wrong part/level)")
    sys.exit(4)
print("RESULT: UNKNOWN - read the response above")
sys.exit(5)
