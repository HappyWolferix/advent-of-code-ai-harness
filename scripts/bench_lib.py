"""Measuring a single solution variant: wall time, CPU time, RAM, CPU cycles.

Every measurement happens in a fresh child process (see bench_child.py) so that
peak RSS and CPU counters describe that one solution and nothing else.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

CHILD = Path(__file__).resolve().parent / "bench_child.py"
PERF_EVENTS = "cycles,instructions"

_perf_state: dict = {}


def perf_available() -> tuple[bool, str]:
    """Can `perf stat` count cycles here? Cached; returns (ok, reason-if-not)."""
    if not _perf_state:
        if not shutil.which("perf"):
            _perf_state.update(ok=False, why="perf not installed")
        else:
            probe = subprocess.run(
                ["perf", "stat", "-x,", "-e", PERF_EVENTS, "--", sys.executable, "-c", "pass"],
                capture_output=True, text=True)
            if re.search(rf"^\d+,+({PERF_EVENTS.split(',')[0]})", probe.stderr, re.M):
                _perf_state.update(ok=True, why="")
            else:
                paranoid = Path("/proc/sys/kernel/perf_event_paranoid")
                lvl = paranoid.read_text().strip() if paranoid.exists() else "?"
                _perf_state.update(
                    ok=False,
                    why=f"perf cannot read counters (perf_event_paranoid={lvl}; "
                        f"needs <=2, e.g. sudo sysctl kernel.perf_event_paranoid=1)")
    return _perf_state["ok"], _perf_state["why"]


def _parse_perf(stderr: str) -> dict:
    """Pull counter values out of `perf stat -x,` CSV output."""
    counters = {}
    for line in stderr.splitlines():
        cols = line.split(",")
        if len(cols) >= 3 and cols[0].strip().isdigit():
            counters[cols[2].strip()] = int(cols[0])
    return counters


def _baseline_rss() -> int:
    """RSS of a bare interpreter, so reported memory excludes Python itself."""
    if "baseline" not in _perf_state:
        out = subprocess.run(
            [sys.executable, "-c",
             "import resource,sys;r=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;"
             "print(r*(1 if sys.platform=='darwin' else 1024))"],
            capture_output=True, text=True)
        _perf_state["baseline"] = int(out.stdout.strip() or 0)
    return _perf_state["baseline"]


def measure(path: Path, part: int, input_file: Path, repeats: int = 1) -> dict:
    """Run one variant/part and return its metrics (or {'missing': True})."""
    cmd = [sys.executable, str(CHILD), str(path), str(part), str(input_file), str(repeats)]
    use_perf, _ = perf_available()
    if use_perf:
        cmd = ["perf", "stat", "-x,", "-e", PERF_EVENTS, "--"] + cmd

    proc = subprocess.run(cmd, capture_output=True, text=True,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    try:
        result = json.loads(proc.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"missing": False, "answer": f"ERROR: child failed: {proc.stderr.strip()[-200:]}",
                "wall": 0.0, "cpu": 0.0, "py_peak": 0, "rss": 0, "cycles": None,
                "instructions": None}
    if result.get("missing"):
        return result

    counters = _parse_perf(proc.stderr) if use_perf else {}
    result["cycles"] = counters.get("cycles")
    result["instructions"] = counters.get("instructions")
    result["rss"] = max(0, result.pop("max_rss", 0) - _baseline_rss())
    return result


def fmt_time(seconds: float) -> str:
    if seconds >= 1:
        return f"{seconds:.2f}s"
    if seconds >= 1e-3:
        return f"{seconds * 1e3:.1f}ms"
    return f"{seconds * 1e6:.0f}us"


def fmt_bytes(n: int) -> str:
    if n == 0:
        return "~0"
    for unit, scale in (("M", 1 << 20), ("K", 1 << 10)):
        if n >= scale:
            return f"{n / scale:.1f}{unit}"
    return f"{n}B"


def fmt_count(n) -> str:
    if n is None:
        return "n/a"
    for unit, scale in (("G", 1e9), ("M", 1e6), ("K", 1e3)):
        if n >= scale:
            return f"{n / scale:.2f}{unit}"
    return str(n)


def loc(path: Path) -> int:
    return sum(1 for line in path.read_text().splitlines()
               if line.strip() and not line.strip().startswith("#"))
