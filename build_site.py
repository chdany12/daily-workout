#!/usr/bin/env python3
"""Daily site build (run by GitHub Actions every morning, safe to run by hand).

1. If today's workout doesn't exist yet, generate it into data/workouts/<date>.json
   and record it in data/history.json (the novelty memory).
2. Render the whole static site into site/: today's page, one page + Excel per day, an archive.
"""

import argparse
import json
import os
import random
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from workout_gen import engine, excel, html
from workout_gen.engine import Row, Workout

ROOT = Path(__file__).parent


def to_json(w: Workout) -> str:
    return json.dumps(asdict(w), indent=2, ensure_ascii=False)


def from_json(text: str) -> Workout:
    d = json.loads(text)
    for k in ("warmup", "main", "cooldown"):
        d[k] = [Row(**r) for r in d[k]]
    return Workout(**d)


def ensure_today(day: str, data_dir: Path, site: dict, profile: dict) -> bool:
    path = data_dir / "workouts" / f"{day}.json"
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    history = engine.History(data_dir / "history.json")
    rng = random.Random(day)  # same date -> same workout, so re-runs are stable
    focus = site.get("focus", "surprise")
    if focus == "surprise":  # never the same body part two days in a row
        last = history.entries[-1]["focus"] if history.entries else None
        focus = rng.choice([f for f in engine.FOCUSES if f != last])
    w = engine.generate(profile, focus, site.get("minutes", 25), history, rng)
    path.write_text(to_json(w))
    history.add(w)
    return True


def render(data_dir: Path, out: Path, site: dict) -> int:
    files = sorted((data_dir / "workouts").glob("*.json"), reverse=True)
    days = [(f.stem, from_json(f.read_text())) for f in files]
    if not days:
        raise SystemExit("no workouts yet")
    (out / "days").mkdir(parents=True, exist_ok=True)
    for i, (day, w) in enumerate(days):
        xlsx = f"{day}.xlsx"
        excel.write(w, out / "days" / xlsx)
        (out / "days" / f"{day}.html").write_text(
            html.workout_page(w, day, xlsx, site, is_today=(i == 0), home="../", archive="../archive.html"))
    today, tw = days[0]
    (out / "index.html").write_text(
        html.workout_page(tw, today, f"days/{today}.xlsx", site, is_today=True))
    (out / "archive.html").write_text(html.archive_page(days))
    (out / ".nojekyll").write_text("")
    return len(days)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", help="override today's date (YYYY-MM-DD)")
    ap.add_argument("--data", type=Path, default=ROOT / "data")
    ap.add_argument("--out", type=Path, default=ROOT / "site")
    args = ap.parse_args()

    site = json.loads((ROOT / "site.json").read_text())
    if not site.get("github_repo"):
        site["github_repo"] = os.environ.get("GITHUB_REPOSITORY", "")
    profile = json.loads((ROOT / "profile.json").read_text())
    day = args.date or datetime.now(ZoneInfo(site.get("timezone", "UTC"))).date().isoformat()

    created = ensure_today(day, args.data, site, profile)
    n = render(args.data, args.out, site)
    print(f"{'Generated' if created else 'Kept'} workout for {day}; rendered {n} day(s) into {args.out}/")


if __name__ == "__main__":
    main()
