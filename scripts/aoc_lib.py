"""Shared helpers for the AoC scripts."""
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

BASE_URL = "https://adventofcode.com"
UA = "github.com/radovan-durec advent-of-code scripts (python requests)"

SESSION = os.environ.get("AOC_SESSION", "")
if not SESSION:
    sys.exit("AOC_SESSION is not set - copy .env.example to .env and fill it in")
DEFAULT_YEAR = int(os.environ.get("AOC_YEAR") or 2025)

VARIANTS = ["simple", "fast", "efficient", "golf"]


def get(path: str) -> str:
    r = requests.get(f"{BASE_URL}{path}", headers={"User-Agent": UA},
                     cookies={"session": SESSION}, timeout=30)
    r.raise_for_status()
    return r.text


def post(path: str, data: dict) -> str:
    r = requests.post(f"{BASE_URL}{path}", data=data, headers={"User-Agent": UA},
                      cookies={"session": SESSION}, timeout=30)
    r.raise_for_status()
    return r.text


def html_to_text(html: str) -> str:
    """Extract <article> blocks and strip HTML to readable text."""
    articles = re.findall(r"<article.*?</article>", html, re.S) or [html]
    text = "\n\n".join(articles)
    text = re.sub(r"<pre><code>", "\n```\n", text)
    text = re.sub(r"</code></pre>", "\n```\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    for ent, ch in [("&gt;", ">"), ("&lt;", "<"), ("&quot;", '"'), ("&#39;", "'"), ("&amp;", "&")]:
        text = text.replace(ent, ch)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def day_year(argv: list[str], usage: str) -> tuple[int, int]:
    if not argv:
        sys.exit(f"usage: {usage}")
    day = int(argv[0])
    year = int(argv[1]) if len(argv) > 1 else DEFAULT_YEAR
    return day, year


def input_path(day: int, year: int) -> Path:
    return ROOT / "inputs" / f"{year}-day{day:02d}.txt"


def fetch_input(day: int, year: int) -> Path:
    path = input_path(day, year)
    if not path.exists() or path.stat().st_size == 0:
        path.parent.mkdir(exist_ok=True)
        path.write_text(get(f"/{year}/day/{day}/input"))
        print(f"downloaded input to {path.relative_to(ROOT)}", file=sys.stderr)
    return path


def solution_dir(day: int, year: int) -> Path:
    return ROOT / "solutions" / str(year) / f"day{day:02d}"
