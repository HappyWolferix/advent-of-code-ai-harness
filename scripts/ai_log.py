#!/usr/bin/env python3
"""Record what the AI side of a day cost: which model, how many tokens, how long.

    ai_log.py start <day> [year] --model claude-opus-5
    ai_log.py stop  <day> [year] --in 41000 --out 6200 [--cached 12000] [--note "..."]
    ai_log.py add   <day> [year] --model M --in N --out N --seconds S [--note "..."]
    ai_log.py show  <day> [year]

`start`/`stop` time a working session with a wall clock; `add` records one you
already timed. Token counts come from the agent's own usage report (or the API
response's `usage` block) — the harness cannot see them by itself.

Entries land in benchmarks/<year>-dayNN.json next to the solution benchmarks, so
scripts/report.py can compare models on both cost and the code they produced.
"""
import argparse
import json
import sys
from datetime import datetime, timezone

from aoc_lib import DEFAULT_YEAR, ROOT

STATE = ROOT / "benchmarks" / ".sessions.json"


def bench_path(day: int, year: int):
    return ROOT / "benchmarks" / f"{year}-day{day:02d}.json"


def load(path):
    return json.loads(path.read_text()) if path.exists() else {}


def save(path, data):
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def now():
    return datetime.now(timezone.utc)


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="cmd", required=True)
for cmd in ("start", "stop", "add", "show"):
    p = sub.add_parser(cmd)
    p.add_argument("day", type=int)
    p.add_argument("year", type=int, nargs="?", default=DEFAULT_YEAR)
    if cmd in ("start", "add"):
        p.add_argument("--model", required=True, help="e.g. claude-opus-5")
    if cmd in ("stop", "add"):
        p.add_argument("--in", dest="tokens_in", type=int, default=0, help="input/prompt tokens")
        p.add_argument("--out", dest="tokens_out", type=int, default=0, help="output tokens")
        p.add_argument("--cached", type=int, default=0, help="cache-read tokens (subset of --in)")
        p.add_argument("--turns", type=int, default=0, help="prompt/response round trips")
        p.add_argument("--note", default="")
    if cmd == "add":
        p.add_argument("--seconds", type=float, required=True, help="wall time spent by the AI")
args = ap.parse_args()

path = bench_path(args.day, args.year)
key = f"{args.year}-day{args.day:02d}"

if args.cmd == "start":
    state = load(STATE)
    state[key] = {"model": args.model, "started_at": now().isoformat(timespec="seconds")}
    save(STATE, state)
    print(f"timing {key} with {args.model}; finish with: ai_log.py stop {args.day} --in N --out N")

elif args.cmd in ("stop", "add"):
    if args.cmd == "stop":
        state = load(STATE)
        session = state.pop(key, None)
        if not session:
            sys.exit(f"no timing session running for {key} — use `ai_log.py start {args.day} "
                     f"--model ...` first, or `add ... --seconds N`")
        started = datetime.fromisoformat(session["started_at"])
        seconds, model = (now() - started).total_seconds(), session["model"]
        save(STATE, state)
    else:
        seconds, model = args.seconds, args.model

    entry = {"model": model, "recorded_at": now().isoformat(timespec="seconds"),
             "seconds": round(seconds, 1), "tokens_in": args.tokens_in,
             "tokens_out": args.tokens_out, "tokens_cached": args.cached,
             "tokens_total": args.tokens_in + args.tokens_out, "turns": args.turns,
             "note": args.note}
    data = load(path)
    data.setdefault("ai", []).append(entry)
    save(path, data)
    print(f"{key}: {model} — {entry['tokens_total']} tokens "
          f"({args.tokens_in} in / {args.tokens_out} out), {seconds / 60:.1f} min")

elif args.cmd == "show":
    data = load(path)
    if not data.get("ai"):
        sys.exit(f"no AI entries for {key}")
    for e in data["ai"]:
        print(f"{e['model']:<24} {e['tokens_total']:>9} tok "
              f"({e['tokens_in']} in / {e['tokens_out']} out)  "
              f"{e['seconds'] / 60:6.1f} min  {e.get('note', '')}")
