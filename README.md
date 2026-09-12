# Advent of Code — AI-driven

Minimal Python harness for solving [Advent of Code](https://adventofcode.com) with AI prompts,
producing multiple solution variants per day.

## Setup

```bash
cp .env.example .env        # paste your session cookie into AOC_SESSION
python3 -m venv .venv       # (--without-pip + get-pip.py if ensurepip is missing)
.venv/bin/pip install -r requirements.txt
```

The session cookie: log in at adventofcode.com, DevTools → Cookies → copy `session`.
All commands below assume the venv python: `.venv/bin/python` (or activate the venv).

## How to run

One-time setup (see above for the venv). Then, solving a day — e.g. day 1 of the default year:

```bash
.venv/bin/python scripts/task.py 1      # read the puzzle
.venv/bin/python scripts/input.py 1     # download your input (cached in inputs/)

# write solutions/2025/day01/simple.py with part1(text) / part2(text), then:
.venv/bin/python scripts/run.py 1       # run + benchmark all variants

.venv/bin/python scripts/submit1.py 1 <answer>   # submit part 1
.venv/bin/python scripts/task.py 1               # re-fetch to see part 2
.venv/bin/python scripts/submit2.py 1 <answer>   # submit part 2

.venv/bin/python scripts/status.py      # stars overview
```

Every script takes an optional year as the last argument (e.g. `scripts/task.py 5 2024`).
After `source .venv/bin/activate` you can drop the `.venv/bin/` prefix.

To verify your token works, try `scripts/status.py 2024` against a year with real data.

Or don't run any of this yourself: open your AI coding agent in this repo and say
"solve day 1" — `AGENTS.md` instructs the session to run the whole loop (task → input →
variants → verify on the example → benchmark → submit) for you. `CLAUDE.md` just points
at `AGENTS.md`, so any agent that reads either convention works.

## Scripts

| script | what it does |
|---|---|
| `scripts/task.py <day> [year]` | Print the puzzle text (parts 1+2 if unlocked), cached in `tasks/` |
| `scripts/input.py <day> [year]` | Download + cache your personal input (`inputs/`), print to stdout |
| `scripts/run.py <day> [year] [--variant N] [--part P]` | Run solution variants, check they agree, benchmark |
| `scripts/submit1.py <day> <answer> [year]` | Submit part 1, interpret the server verdict |
| `scripts/submit2.py <day> <answer> [year]` | Submit part 2, interpret the server verdict |
| `scripts/status.py [year]` | Per-day stars and totals for the year |

`submit*.py` exit codes: 0 correct, 1 wrong (with too high/low hint), 3 rate-limited, 4 already solved.

## Solution variants

Each day lives in `solutions/<year>/dayNN/` with up to four Python variants:

- `simple.py` — the most readable, straightforward solution
- `fast.py` — optimized for wall-clock time
- `efficient.py` — optimized for memory / algorithmic efficiency
- `golf.py` — fewest lines of code

Every variant exposes `part1(text)` and `part2(text)` taking the raw input string
and returning the answer. `scripts/run.py` runs them all against your input,
verifies the answers agree, and reports time, peak memory and lines of code.

`inputs/` and `tasks/` are personal/copyrighted content and are gitignored.
