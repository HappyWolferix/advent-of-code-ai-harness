#!/usr/bin/env python3
"""Compare benchmark results across days, variants and AI models.

    report.py [year] [--day N] [--by-model] [--json]

Reads benchmarks/<year>-dayNN.json (written by run.py and ai_log.py) and prints
a per-day table of the solutions plus the AI cost of producing them. --by-model
aggregates the AI side so models can be compared head to head.
"""
import argparse
import json
from collections import defaultdict

import bench_lib as B
from aoc_lib import DEFAULT_YEAR, ROOT

ap = argparse.ArgumentParser()
ap.add_argument("year", type=int, nargs="?", default=DEFAULT_YEAR)
ap.add_argument("--day", type=int, help="only this day")
ap.add_argument("--by-model", action="store_true", help="aggregate AI cost per model")
ap.add_argument("--json", action="store_true", help="dump the raw joined data")
args = ap.parse_args()

bdir = ROOT / "benchmarks"
pattern = f"{args.year}-day{args.day:02d}.json" if args.day else f"{args.year}-day*.json"
files = sorted(bdir.glob(pattern))
if not files:
    raise SystemExit(f"no benchmarks in {bdir} for {args.year} — run scripts/run.py first")

days = {f.stem: json.loads(f.read_text()) for f in files}

if args.json:
    print(json.dumps(days, indent=2))
    raise SystemExit(0)

if args.by_model:
    agg = defaultdict(lambda: defaultdict(int))
    for data in days.values():
        for e in data.get("ai", []):
            a = agg[e["model"]]
            a["days"] += 1
            a["seconds"] += e["seconds"]
            a["tokens_in"] += e["tokens_in"]
            a["tokens_out"] += e["tokens_out"]
            a["tokens_cached"] += e.get("tokens_cached", 0)
            a["turns"] += e.get("turns", 0)
    if not agg:
        raise SystemExit("no AI entries recorded yet — see scripts/ai_log.py")
    head = (f"{'model':<24} {'days':>5} {'tokens in':>11} {'cached':>9} {'tokens out':>11} "
            f"{'turns':>6} {'time':>9} {'time/day':>9}")
    print(head)
    print("-" * len(head))
    for model, a in sorted(agg.items(), key=lambda kv: -kv[1]["seconds"]):
        print(f"{model:<24} {a['days']:>5} {a['tokens_in']:>11,} {a['tokens_cached']:>9,} "
              f"{a['tokens_out']:>11,} {a['turns']:>6} "
              f"{a['seconds'] / 60:>8.1f}m {a['seconds'] / a['days'] / 60:>8.1f}m")
    raise SystemExit(0)

for key, data in days.items():
    print(f"\n=== {key} ===")
    sol = data.get("solutions")
    if sol:
        head = (f"{'variant':<10} {'part':<4} {'wall':>9} {'cpu':>9} {'cycles':>9} "
                f"{'instr':>9} {'rss':>9} {'pyheap':>9} {'loc':>4}")
        print(head)
        print("-" * len(head))
        for r in sol["rows"]:
            print(f"{r['variant']:<10} {r['part']:<4} {B.fmt_time(r['wall_s']):>9} "
                  f"{B.fmt_time(r['cpu_s']):>9} {B.fmt_count(r['cycles']):>9} "
                  f"{B.fmt_count(r['instructions']):>9} {B.fmt_bytes(r['rss_bytes']):>9} "
                  f"{B.fmt_bytes(r['py_peak_bytes']):>9} {r['loc']:>4}")
    else:
        print("(no solution benchmarks — run scripts/run.py)")
    for e in data.get("ai", []):
        print(f"AI  {e['model']:<20} {e['tokens_total']:>9,} tok "
              f"({e['tokens_in']:,} in / {e['tokens_out']:,} out)  "
              f"{e['seconds'] / 60:6.1f} min  {e.get('note', '')}")
