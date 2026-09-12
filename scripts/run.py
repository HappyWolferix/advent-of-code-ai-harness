#!/usr/bin/env python3
"""Run all solution variants for a day, verify they agree, and benchmark them.

Usage: run.py <day> [year] [--variant NAME] [--part 1|2]

Each variant is solutions/<year>/dayNN/<variant>.py exposing part1(text) and
part2(text), where text is the raw input file content.
"""
import argparse
import importlib.util
import sys
import time
import tracemalloc
from aoc_lib import DEFAULT_YEAR, VARIANTS, fetch_input, solution_dir

ap = argparse.ArgumentParser()
ap.add_argument("day", type=int)
ap.add_argument("year", type=int, nargs="?", default=DEFAULT_YEAR)
ap.add_argument("--variant", choices=VARIANTS)
ap.add_argument("--part", type=int, choices=[1, 2])
args = ap.parse_args()

sdir = solution_dir(args.day, args.year)
names = [args.variant] if args.variant else VARIANTS
files = [(n, sdir / f"{n}.py") for n in names if (sdir / f"{n}.py").exists()]
if not files:
    sys.exit(f"no variants found in {sdir} (expected one of: {', '.join(VARIANTS)}.py)")

text = fetch_input(args.day, args.year).read_text()
parts = [args.part] if args.part else [1, 2]

results = {}  # part -> {variant: answer}
print(f"{'variant':<10} {'part':<4} {'answer':<20} {'time':>10} {'peak mem':>10} {'loc':>4}")
for name, path in files:
    loc = sum(1 for line in path.read_text().splitlines()
              if line.strip() and not line.strip().startswith("#"))
    spec = importlib.util.spec_from_file_location(f"{name}_day{args.day}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for part in parts:
        fn = getattr(mod, f"part{part}", None)
        if fn is None:
            continue
        tracemalloc.start()
        t0 = time.perf_counter()
        try:
            answer = fn(text)
        except Exception as e:
            answer = f"ERROR: {e}"
        elapsed = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        results.setdefault(part, {})[name] = answer
        print(f"{name:<10} {part:<4} {str(answer):<20} {elapsed*1000:8.1f}ms {peak/1024:9.0f}K {loc:4d}")

ok = True
for part, answers in results.items():
    real = {str(v) for v in answers.values() if not str(v).startswith("ERROR")}
    if len(real) > 1:
        ok = False
        print(f"\nMISMATCH part {part}: {answers}")
if ok and results:
    print("\nAll variants agree ✓")
sys.exit(0 if ok else 1)
