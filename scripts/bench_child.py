#!/usr/bin/env python3
"""Run one variant/part once in a clean process and print JSON metrics on stdout.

Usage: bench_child.py <solution.py> <part> <input-file> [repeats]

Isolated in its own process so peak RSS and CPU time belong to this solution
alone, and so `perf stat` can be wrapped around it to count real CPU cycles.
"""
import importlib.util
import json
import os
import resource
import sys
import time
import tracemalloc

path, part, input_file = sys.argv[1], int(sys.argv[2]), sys.argv[3]
repeats = int(sys.argv[4]) if len(sys.argv) > 4 else 1

text = open(input_file).read()
spec = importlib.util.spec_from_file_location("variant_under_test", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
fn = getattr(mod, f"part{part}", None)
if fn is None:
    print(json.dumps({"missing": True}))
    sys.exit(0)

out = {"missing": False}
try:
    # Timed repeats first (fastest run wins — least noise from the scheduler).
    best_wall = best_cpu = float("inf")
    for _ in range(repeats):
        t0, c0 = time.perf_counter(), time.process_time()
        answer = fn(text)
        best_wall = min(best_wall, time.perf_counter() - t0)
        best_cpu = min(best_cpu, time.process_time() - c0)
    # Separate traced run: tracemalloc slows execution, so keep it out of timings.
    tracemalloc.start()
    fn(text)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    out.update(answer=str(answer), wall=best_wall, cpu=best_cpu, py_peak=peak)
except Exception as e:  # a broken variant must not kill the whole run
    out.update(answer=f"ERROR: {type(e).__name__}: {e}", wall=0.0, cpu=0.0, py_peak=0)

ru = resource.getrusage(resource.RUSAGE_SELF)
# ru_maxrss is KiB on Linux, bytes on macOS.
out["max_rss"] = ru.ru_maxrss * (1 if sys.platform == "darwin" else 1024)
out["baseline_rss"] = int(os.environ.get("BENCH_BASELINE_RSS", 0))
print(json.dumps(out))
