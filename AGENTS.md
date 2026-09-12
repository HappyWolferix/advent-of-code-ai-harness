# Advent of Code workflow

Everything is Python 3 with one shared venv: run scripts with `.venv/bin/python`.
Dependencies go in `requirements.txt` (installed into `.venv/`).

Solve a day with this loop:

1. `.venv/bin/python scripts/task.py <day>` — read the puzzle. After solving part 1, run again to see part 2.
2. `.venv/bin/python scripts/input.py <day>` — caches the input at `inputs/<year>-dayNN.txt`.
3. Write variants in `solutions/<year>/dayNN/`. Start with `simple.py`, verify against the example from the puzzle text, then add the others:
   - `simple.py` — most readable, no cleverness
   - `fast.py` — fastest wall-clock (better algorithm, precomputation, etc.)
   - `efficient.py` — lowest memory / best algorithmic complexity
   - `golf.py` — fewest non-comment lines
   Each variant must define `part1(text)` and `part2(text)` (raw input string in, answer out). Variants must produce identical answers.
4. `.venv/bin/python scripts/run.py <day>` — runs all variants on the real input, checks agreement, benchmarks (time / peak memory / LOC). Exit code 1 on mismatch.
5. `.venv/bin/python scripts/submit1.py <day> <answer>` then `submit2.py` — prints RESULT: CORRECT / WRONG (too high/low hint) / RATE LIMITED / ALREADY SOLVED. On WRONG, re-check the example first; on RATE LIMITED, wait.
6. `.venv/bin/python scripts/status.py` — stars overview.

Rules:
- Never commit `.env`, `.venv/`, `inputs/`, or `tasks/` (gitignored; puzzle text and inputs must not be redistributed).
- Default year is `AOC_YEAR` from `.env`; every script takes an optional trailing year argument.
- Prove correctness on the puzzle example before submitting; don't brute-force submissions (the site rate-limits).
- New third-party dependency → add to `requirements.txt` and pip-install into the shared venv; no per-day venvs.
