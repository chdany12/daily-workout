#!/usr/bin/env python3
"""Generate randomized, never-boring home workouts as Excel sheets.

Examples:
  python generate.py                          # surprise focus, 25 min
  python generate.py --focus upper --minutes 15
  python generate.py --count 3                # a batch to send for the week
  python generate.py --focus core --format "Deck of Cards"
"""

import argparse
import json
import random
import re
from datetime import date
from pathlib import Path

from workout_gen import engine, excel

ROOT = Path(__file__).parent


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--focus", default="surprise", choices=engine.FOCUSES + ["surprise"])
    ap.add_argument("--minutes", type=int, default=25, help="total incl. warm-up & cool-down (presets: 15/25/35)")
    ap.add_argument("--count", type=int, default=1, help="how many workouts to generate")
    ap.add_argument("--format", dest="format_name", choices=list(engine.FORMATS), help="force a format")
    ap.add_argument("--profile", default=ROOT / "profile.json", type=Path)
    ap.add_argument("--history", default=ROOT / "history.json", type=Path)
    ap.add_argument("--out", default=ROOT / "workouts", type=Path)
    ap.add_argument("--seed", type=int, help="reproducible output (for testing)")
    ap.add_argument("--no-save-history", action="store_true", help="don't remember this workout")
    args = ap.parse_args()

    if args.minutes < 10:
        ap.error("--minutes must be at least 10 (3 min warm-up + 2 min cool-down + 5 min work)")

    profile = json.loads(args.profile.read_text())
    history = engine.History(args.history)
    rng = random.Random(args.seed)
    args.out.mkdir(parents=True, exist_ok=True)

    for _ in range(args.count):
        w = engine.generate(profile, args.focus, args.minutes, history, rng, args.format_name)
        path = args.out / f"{date.today()}_{w.focus}_{slug(w.format_name)}_{slug(w.name)}.xlsx"
        excel.write(w, path)
        if not args.no_save_history:
            history.add(w)
        print(f"✔ {w.name}  [{w.focus}, {w.format_name}, {w.minutes} min]  ->  {path}")


if __name__ == "__main__":
    main()
