# Advent of Code — AI-driven

Minimal Python harness for solving [Advent of Code](https://adventofcode.com) with AI prompts,
producing multiple solution variants per day.

## Disclaimer — please don't compete with this

**Do not use this harness to compete against humans on the Advent of Code leaderboards.**
Letting an AI race people who are solving the puzzles by hand is unfair to them, and Advent
of Code's creator has asked people not to do it (see the [AoC about page](https://adventofcode.com/about)).
If you use this on a live puzzle, stay off the global leaderboard.

The goal of this repo is educational: to show how AI can be used to solve problems quickly
and efficiently by combining *code execution on your local CPU* with *AI orchestration and
debugging* — the AI reads the problem, writes and refines the code, the machine runs and
benchmarks it, and the measured results feed back into the next iteration. Best of both
worlds. Advent of Code just happens to be a great, well-scoped set of problems to
demonstrate that loop on. Use it to learn, not to win.

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

## Example prompts

Paste these into your agent as-is. `AGENTS.md` supplies the workflow, so the prompts
stay short — you are stating the goal, not the steps.

**Solve one day:**

```
Solve day 7.
```

```
Solve day 12 of 2023. Write all four variants and submit both parts once the
example checks out.
```

```
Solve day 5. Part 1 only for now — don't submit, just show me the answer and the
benchmark table.
```

**Solve every day:**

```
Solve all days of 2025 that I don't have both stars for yet. Work through them in
order, and stop and tell me if a day fails twice in a row.
```

```
Run scripts/status.py, then solve every unsolved day of 2023 one at a time. After
each day, run the benchmarks and log the AI cost before moving on.
```

Days differ wildly in difficulty, so a full year is a long session — expect to
babysit it, and expect the hard days (roughly 17+) to need your input.

**Measure an AI model:**

```
Solve day 9. Time yourself with scripts/ai_log.py from start to finish and record
your model id, token usage and turn count when you're done.
```

```
Solve days 1-5 of 2023, logging AI cost for each, then show me
scripts/report.py --by-model.
```

```
Compare the models I've logged so far: run scripts/report.py 2025 --by-model and
tell me which one produced the fastest code for the fewest tokens.
```

To compare two models fairly, point each one at the same days from a *finished* year
and let each record its own `ai_log.py` entry — then `report.py --by-model` puts the
token and time totals next to the runtime of the code they wrote.

## Scripts

| script | what it does |
|---|---|
| `scripts/task.py <day> [year]` | Print the puzzle text (parts 1+2 if unlocked), cached in `tasks/` |
| `scripts/input.py <day> [year]` | Download + cache your personal input (`inputs/`), print to stdout |
| `scripts/run.py <day> [year] [--variant N] [--part P] [--repeats N]` | Run solution variants, check they agree, benchmark |
| `scripts/ai_log.py start\|stop\|add\|show <day> [year]` | Record the AI cost of a day: model, tokens, wall time |
| `scripts/report.py [year] [--day N] [--by-model]` | Compare days, variants and AI models |
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

## Benchmarking

`scripts/run.py` measures every variant/part in its own subprocess, so the numbers
belong to that one solution and nothing else:

| column | what it is |
|---|---|
| `wall` | wall-clock time, fastest of `--repeats` runs (default 3) |
| `cpu` | CPU time actually burned by the process |
| `cycles` / `instr` | real CPU cycles and instructions retired, via `perf stat` |
| `rss` | peak resident memory, minus a bare interpreter's baseline |
| `pyheap` | peak Python heap from `tracemalloc` (measured in a separate untimed run) |
| `loc` | non-blank, non-comment lines |

```
variant    part answer                    wall       cpu    cycles     instr       rss    pyheap  loc
simple     1    55017                    533us     533us    1.71M     4.02M     1.2M     69.0K    8
golf       1    55017                    345us     345us    1.10M     2.61M     1.1M     69.9K    1
```

Cycle counting needs kernel permission; without it the column shows `n/a` and
`run.py` prints why. To enable it: `sudo sysctl kernel.perf_event_paranoid=1`.

### AI cost

The other half of the comparison is what the *model* spent. The harness cannot see
that by itself, so the agent (or you) records it:

```bash
.venv/bin/python scripts/ai_log.py start 1 --model claude-opus-5   # begin timing
# ... solve the day ...
.venv/bin/python scripts/ai_log.py stop 1 --in 41000 --out 6200 --cached 12000 --turns 9
```

Use `add ... --seconds N` instead if you already know the elapsed time. Token counts
come from the agent's own usage report or an API response's `usage` block.

Both halves land in `benchmarks/<year>-dayNN.json`, and `scripts/report.py` joins them:

```bash
.venv/bin/python scripts/report.py 2025              # per-day: variants + AI cost
.venv/bin/python scripts/report.py 2025 --by-model   # tokens and time per model
.venv/bin/python scripts/report.py 2025 --json       # raw data for your own charts
```

This is the point of the repo: the same puzzles, solved by different models, with
the runtime cost of the code and the cost of producing it side by side.
