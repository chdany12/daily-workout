# Never-Boring Home Workout Generator (MVP)

Makes a randomized home workout as a phone-friendly Excel sheet. Built for a friend with ADHD who gets bored doing the same routine.

Equipment: floor, yoga mat, a sturdy chair or couch, a wall. Nothing else.

## Quick start

```bash
pip install openpyxl
python generate.py                              # surprise focus, 25 min
python generate.py --focus upper --minutes 15   # upper / lower / core / full / surprise
python generate.py --count 3                    # a batch to send for the week
```

The sheets go to `workouts/`. Send the .xlsx to your friend. It opens in Excel, Google Sheets or Numbers on a phone.

## Personalise

Edit `profile.json`:

| Field | Meaning |
|---|---|
| `level` | 1 beginner, 2 intermediate, 3 hard. Filters moves and scales reps |
| `equipment` | Remove `"chair"` or `"wall"` if not available |
| `noise_sensitive` | `true` removes all jumping (for downstairs neighbours) |
| `avoid_tags` | `["wrists"]` or `["knees"]` removes moves that load those joints |
| `banned_moves` | Exact names of moves they hate, e.g. `["Burpee"]` |

## How it stays fresh

- **10 formats**: EMOM, AMRAP, Tabata, Ladder, Pyramid, Deck of Cards, Circuit, Death By, Chipper, Supersets. A format never repeats within 3 workouts.
- **83 moves**. Anything used in the last 5 workouts is 5× less likely to come back. Never-done moves get a 🆕 badge.
- **A random twist** every session (Tempo mode, Commentator mode, Plank tax…) and a silly name.
- Memory lives in `history.json`. Delete it to reset.

Every sheet has: warm-up (3 min) → main event → cool-down (2 min), a ✅ tap column, a ▶ Watch link per move (opens a YouTube demo), and a short feedback box at the bottom.

## MVP success test

Your friend finishes **3 generated workouts in 2 weeks** and rates at least one as fun. The feedback box tells you what to change.

## Files

```
generate.py            CLI
profile.json           the person's settings
workout_gen/data.py    exercise library, warm-ups, stretches, twists, names
workout_gen/engine.py  selection, novelty memory, the 10 formats
workout_gen/excel.py   phone-friendly sheet writer
test_generate.py       python -m unittest -v
RESEARCH.md            field research and why each design choice was made
examples/              sample sheets
```

## Ideas for v2 (only if v1 gets used)

- Claude-written theme/story per workout ("Zombie Escape: 5 rounds…")
- A phone web page with built-in timers instead of Excel
- Read back the feedback box to tune difficulty automatically
