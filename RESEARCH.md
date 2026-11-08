# Field research notes

What I looked at before writing the generator, and how each finding shaped it.

## 1. Why ADHD + workouts break down

- The common pattern: early enthusiasm, then novelty wears off around week 3, and one missed session can kill the habit.
- Practitioner advice is consistent: **planned variety** (not chaos), **low friction**, and **shorter fallback versions** so a bad day doesn't end the streak.
- Caveat: most of this comes from blogs, coaches and app vendors. I found no rigorous trial showing variety *specifically* improves exercise adherence in adults with ADHD. The novelty/dopamine story is plausible but not proven. That's why the MVP has a feedback box and a success test (3 workouts in 2 weeks).

Sources: [Darebee ADHD workouts collection](https://darebee.com/collections/adhd-workouts.html) · [7 Gym Consistency Tips for People With ADHD (psychologist)](https://www.aol.com/lifestyle/7-gym-consistency-tips-people-195255520.html) · [Running for ADHD beginner guide](https://www.findyouredge.app/news/running-for-adhd-beginner-guide-2026) · [Exercise for ADHD — Lifestack](https://lifestack.ai/blog/exercise-for-adhd)

**→ Design decisions**
| Finding | In the generator |
|---|---|
| Novelty fades | 10 structurally different formats; the same format never repeats within 3 workouts |
| Same moves = boring | Moves from the last 5 workouts are down-weighted 5×, and never-done moves get a 🆕 badge |
| Friction kills | One tab, big text, tap-to-check ✅ column, no account, no app |
| Bad days happen | 15-min preset; every format has a time cap so it never runs over |
| Game-ification helps | Silly workout names, a random "twist" each session, Deck of Cards draws, scores to write down |

## 2. How popular home workouts are actually built

Almost every popular bodyweight workout (CrossFit WODs, Darebee, HIIT classes, YouTube follow-alongs) is **a format × a short list of moves**. The format is what makes it *feel* different. That's the key insight: we don't need to scrape thousands of workouts. Combining 83 moves with 10 formats plus twists already gives far more variety than a scraped list would.

Formats implemented (all common in the sources below):

| Format | Structure | Why it's ADHD-friendly |
|---|---|---|
| EMOM | Do X reps at the top of every minute, rest the rest | The clock does the thinking |
| AMRAP | Loop a short list as many rounds as possible | Score to beat, no counting sets |
| Tabata | 20 s on / 10 s off × 8 | Over in 4 minutes, very intense |
| Ladder (up/down) | 1-2-3… or 10-9-8…1 reps | Visible progress, "one more rung" |
| Pyramid | 2-4-6-8-6-4-2 | Halfway point feels like a win |
| Deck of Cards | Suit = move, card = reps | Pure randomness, a game |
| Circuit | Timed stations | Constant switching |
| Death By | Minute N = N reps until you fail | Built-in boss fight |
| Chipper | Big list, done once | Ticking boxes off a long list |
| Supersets | Two moves back-to-back | Classic gym structure, fast pace |

Sources: [Men's Fitness — Tabata vs EMOM & other HIIT types](https://mensfitness.co.uk/workouts/high-intensity/) · [AMRAP vs EMOM vs Tabata — Sole](https://www.soletreadmills.com/blogs/news/amrap-vs-emom-vs-tabata-differences-benefits-examples) · [2POOD — 5 types of bodyweight workouts](https://2pood.com/blogs/liftheavy/5-types-of-bodyweight-workouts-you-can-do-from-home) · [Tom's Guide — 4-move ladder workout](https://tomsguide.com/news/this-4-move-ladder-workout-builds-muscle-and-strength-all-over-without-weights) · [Bodybuilding.com — fun fat-burning workouts](https://bodybuilding.com/content/6-fun-and-effective-fat-burning-workouts.html) · [Colorado College bodyweight workouts](https://www.coloradocollege.edu/other/fitnesscenter/fitness-programming/BodyweightWorkouts_Week31.pdf) · [intervaltimer.com WOD archive](https://www.intervaltimer.com/wod)

## 3. Why not scraping (yet)

- Most fitness sites forbid scraping in their terms, and the content is copyrighted.
- Scraped workouts are mostly the same ~50 moves in the same few formats. They'd be duplicates, not novelty.
- A clean, tagged library (level, equipment, noise, joint stress) is what makes filtering safe. Scraped text doesn't have those tags.

If more moves are needed later, the open-source [wger](https://wger.de) exercise database (CC-BY-SA) is the legitimate place to pull from.
