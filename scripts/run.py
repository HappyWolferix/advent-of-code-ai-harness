#!/usr/bin/env python3
"""Run all solution variants for a day, verify they agree, and benchmark them.

Usage: run.py <day> [year] [--variant NAME] [--part 1|2] [--repeats N] [--no-save]

Each variant is solutions/<year>/dayNN/<variant>.py exposing part1(text) and
part2(text), where text is the raw input file content.

Every variant/part runs in its own process and is measured for wall-clock time,
CPU time, CPU cycles + instructions (via `perf`, where the kernel allows it),
peak RSS and peak Python heap. Results are appended to benchmarks/<year>-dayNN.json
so scripts/report.py can compare them (and the AI cost of producing them).
"""
import argparse
import json
import sys
from datetime import datetime, timezone

import bench_lib as B
from aoc_lib import DEFAULT_YEAR, ROOT, VARIANTS, fetch_input, solution_dir

ap = argparse.ArgumentParser()
ap.add_argument("day", type=int)
ap.add_argument("year", type=int, nargs="?", default=DEFAULT_YEAR)
ap.add_argument("--variant", choices=VARIANTS)
ap.add_argument("--part", type=int, choices=[1, 2])
ap.add_argument("--repeats", type=int, default=3,
                help="timed runs per variant/part; fastest wins (default 3)")
ap.add_argument("--no-save", action="store_true", help="do not write benchmarks/")
args = ap.parse_args()

sdir = solution_dir(args.day, args.year)
names = [args.variant] if args.variant else VARIANTS
files = [(n, sdir / f"{n}.py") for n in names if (sdir / f"{n}.py").exists()]
if not files:
    sys.exit(f"no variants found in {sdir} (expected one of: {', '.join(VARIANTS)}.py)")

input_file = fetch_input(args.day, args.year)
parts = [args.part] if args.part else [1, 2]

ok_perf, why = B.perf_available()
if not ok_perf:
    print(f"note: CPU cycles unavailable ({why})\n", file=sys.stderr)

header = (f"{'variant':<10} {'part':<4} {'answer':<20} {'wall':>9} {'cpu':>9} "
          f"{'cycles':>9} {'instr':>9} {'rss':>9} {'pyheap':>9} {'loc':>4}")
print(header)
print("-" * len(header))

results, rows = {}, []
for name, path in files:
    lines = B.loc(path)
    for part in parts:
        m = B.measure(path, part, input_file, args.repeats)
        if m.get("missing"):
            continue
        results.setdefault(part, {})[name] = m["answer"]
        rows.append({"variant": name, "part": part, "answer": m["answer"],
                     "wall_s": m["wall"], "cpu_s": m["cpu"], "cycles": m["cycles"],
                     "instructions": m["instructions"], "rss_bytes": m["rss"],
                     "py_peak_bytes": m["py_peak"], "loc": lines})
        print(f"{name:<10} {part:<4} {str(m['answer'])[:20]:<20} "
              f"{B.fmt_time(m['wall']):>9} {B.fmt_time(m['cpu']):>9} "
              f"{B.fmt_count(m['cycles']):>9} {B.fmt_count(m['instructions']):>9} "
              f"{B.fmt_bytes(m['rss']):>9} {B.fmt_bytes(m['py_peak']):>9} {lines:4d}")

ok = True
for part, answers in results.items():
    real = {str(v) for v in answers.values() if not str(v).startswith("ERROR")}
    if len(real) > 1:
        ok = False
        print(f"\nMISMATCH part {part}: {answers}")
if ok and results:
    print("\nAll variants agree ✓")

if rows and not args.no_save:
    path = ROOT / "benchmarks" / f"{args.year}-day{args.day:02d}.json"
    path.parent.mkdir(exist_ok=True)
    data = json.loads(path.read_text()) if path.exists() else {}
    data["solutions"] = {"measured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                         "repeats": args.repeats, "perf_cycles": ok_perf, "rows": rows}
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"benchmarks written to {path.relative_to(ROOT)}")

sys.exit(0 if ok else 1)
