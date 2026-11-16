# Never-Boring Home Workout Generator (MVP)

A new randomized home workout every morning, on a phone-friendly web page (plus an Excel download). Built for a friend with ADHD who gets bored doing the same routine.

Equipment: floor, yoga mat, a sturdy chair or couch, a wall. Nothing else.

## Quick start

```bash
pip install openpyxl
python generate.py                              # surprise focus, 25 min
python generate.py --focus upper --minutes 15   # upper / lower / core / full / surprise
python generate.py --count 3                    # a batch to send for the week
```

The sheets go to `workouts/`. Send the .xlsx to your friend. It opens in Excel, Google Sheets or Numbers on a phone.

## The daily website (GitHub Pages)

Every morning a GitHub Action (`.github/workflows/daily.yml`) runs `build_site.py`. It:
1. generates today's workout into `data/workouts/<date>.json` and updates the novelty memory in `data/history.json`, then commits both,
2. renders `site/`: today's workout (`index.html`), a page + Excel file per day, and `archive.html`,
3. deploys `site/` to GitHub Pages.

The page has tap-to-tick moves with a progress bar (saved on the phone), ▶ Watch demo links, and a **feedback box** at the bottom.

### One-time setup
1. Push this repo to GitHub.
2. **Settings → Pages → Source: GitHub Actions.**
3. **Actions → Daily workout → Run workflow** to publish the first one. After that it runs daily at 11:07 UTC.

### Where feedback goes
Static sites can't store anything, so feedback goes through a free form service. Set it in `site.json`:

| Service | `feedback_url` | `feedback_extra` |
|---|---|---|
| [Web3Forms](https://web3forms.com) (no account, just your email) | `https://api.web3forms.com/submit` | `{"access_key": "YOUR-KEY"}` |
| [Formspree](https://formspree.io) | `https://formspree.io/f/YOUR-FORM-ID` | `{}` |

Both email you each submission. Leave `feedback_url` empty and the button opens a pre-filled GitHub issue on this repo instead (needs a GitHub account).

Other `site.json` settings: `timezone` (when "today" starts), `minutes`, `focus` (`surprise` = a different body part every day).

### Preview locally
```bash
python build_site.py && python -m http.server -d site
```

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
- Body part changes every day on the site.
- Memory lives in `data/history.json` (site) or `history.json` (CLI). Delete it to reset.

Every sheet has: warm-up (3 min) → main event → cool-down (2 min), a ✅ tap column, a ▶ Watch link per move (opens a YouTube demo), and a short feedback box at the bottom.

## MVP success test

Your friend finishes **3 generated workouts in 2 weeks** and rates at least one as fun. The feedback box tells you what to change.

## Files

```
generate.py            CLI: one-off Excel workouts
build_site.py          daily website build (run by GitHub Actions)
site.json              website settings (timezone, feedback service)
.github/workflows/     the daily schedule
data/                  saved daily workouts + novelty memory (written by the Action)
profile.json           the person's settings
workout_gen/data.py    exercise library, warm-ups, stretches, twists, names
workout_gen/engine.py  selection, novelty memory, the 10 formats
workout_gen/excel.py   phone-friendly sheet writer
workout_gen/html.py    web page renderer
test_generate.py       python -m unittest -v
RESEARCH.md            field research and why each design choice was made
examples/              sample sheets
```

## Ideas for v2 (only if v1 gets used)

- Claude-written theme/story per workout ("Zombie Escape: 5 rounds…")
- Built-in interval timers on the page
- Animated demos instead of YouTube links
- Read back the feedback box to tune difficulty automatically
