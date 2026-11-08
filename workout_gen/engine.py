"""Builds a randomized workout: warm-up -> one random format -> cool-down.

Novelty rules (the whole point for an ADHD brain):
  * the format (structure) can't repeat any of the last 3 workouts
  * exercises used in the last 5 workouts are strongly down-weighted
  * moves never done before get flagged as NEW on the sheet
"""

import json
import math
import random
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from . import data
from .data import Exercise

FOCUSES = ["upper", "lower", "core", "full"]
WARMUP_MIN = 3
COOLDOWN_MIN = 2
LEVEL_SCALE = {1: 0.7, 2: 1.0, 3: 1.3}
SUITS = ["♠", "♥", "♦", "♣"]
SUIT_NAMES = {"♠": "Spades", "♥": "Hearts", "♦": "Diamonds", "♣": "Clubs"}


# --------------------------------------------------------------------------
# Output model
# --------------------------------------------------------------------------
@dataclass
class Row:
    move: str = ""
    do: str = ""
    cue: str = ""
    group: bool = False  # a sub-header row like "Block 1"
    new: bool = False    # never done this move before


@dataclass
class Workout:
    name: str
    focus: str
    minutes: int
    level: int
    format_name: str
    format_rules: str
    twist: str
    warmup: list = field(default_factory=list)
    main: list = field(default_factory=list)
    cooldown: list = field(default_factory=list)
    exercises: list = field(default_factory=list)  # names, for history


# --------------------------------------------------------------------------
# History (novelty memory)
# --------------------------------------------------------------------------
class History:
    def __init__(self, path: Path):
        self.path = path
        self.entries = json.loads(path.read_text()) if path.exists() else []

    def recent_formats(self, n=3):
        return {e["format"] for e in self.entries[-n:]}

    def recent_exercises(self, n=5):
        return {x for e in self.entries[-n:] for x in e["exercises"]}

    def ever_done(self):
        return {x for e in self.entries for x in e["exercises"]}

    def add(self, w: Workout):
        self.entries.append({
            "date": datetime.now().isoformat(timespec="minutes"),
            "name": w.name, "focus": w.focus, "minutes": w.minutes,
            "format": w.format_name, "exercises": w.exercises,
        })
        self.path.write_text(json.dumps(self.entries, indent=2, ensure_ascii=False))


# --------------------------------------------------------------------------
# Exercise picking
# --------------------------------------------------------------------------
class Picker:
    def __init__(self, profile: dict, focus: str, history: History, rng: random.Random):
        self.rng = rng
        self.focus = focus
        self.level = profile["level"]
        self.scale = LEVEL_SCALE[self.level]
        self.recent = history.recent_exercises()
        self.ever = history.ever_done()
        self.used: list[Exercise] = []

        equip = set(profile.get("equipment", []))
        avoid = set(profile.get("avoid_tags", []))
        if profile.get("noise_sensitive"):
            avoid.add("noisy")
        banned = {b.lower() for b in profile.get("banned_moves", [])}

        self.pool = [
            e for e in data.EXERCISES
            if e.level <= self.level
            and set(e.equip) <= equip
            and not (set(e.tags) & avoid)
            and e.name.lower() not in banned
        ]
        # cycle used by "full" so every region gets hit
        self._full_cycle = []

    def _target_region(self) -> str:
        if self.focus == "full":
            if not self._full_cycle:
                self._full_cycle = ["lower", "upper", "core", "cardio"]
                self.rng.shuffle(self._full_cycle)
            return self._full_cycle.pop()
        # 75% on-focus, 25% support work (core / cardio) to keep it lively
        if self.rng.random() < 0.75:
            return self.focus
        return self.rng.choice([r for r in ("core", "cardio") if r != self.focus])

    def pick(self, n: int, reps_only=False) -> list[Exercise]:
        chosen = []
        for _ in range(n):
            region = self._target_region()
            cands = [e for e in self.pool if e not in self.used and e not in chosen
                     and (not reps_only or e.rep_based)]
            on_region = [e for e in cands if region in e.regions]
            cands = on_region or [e for e in cands if self.focus in e.regions or self.focus == "full"] or cands
            if not cands:
                break
            # a move's FIRST region is what it's really for; secondary tags count less
            weights = [(1.0 if e.regions[0] == region else 0.3)
                       * (0.2 if e.name in self.recent else 1.0) for e in cands]
            chosen.append(self.rng.choices(cands, weights=weights)[0])
        self.used.extend(chosen)
        return chosen

    # ---- prescriptions ----
    def amount(self, e: Exercise, factor=1.0) -> int:
        return max(1, round(e.amount * self.scale * factor))

    @staticmethod
    def fmt(e: Exercise, amt) -> str:
        return {
            "reps": f"{amt} reps",
            "reps/side": f"{amt} / side",
            "sec": f"{amt} sec",
            "sec/side": f"{amt} sec / side",
        }[e.unit]

    def row(self, e: Exercise, do: str) -> Row:
        return Row(move=e.name, do=do, cue=e.cue, new=e.name not in self.ever)


# --------------------------------------------------------------------------
# Formats. Each returns (rules_text, rows) for `mins` minutes of main work.
# --------------------------------------------------------------------------
def f_emom(p: Picker, mins):
    k = p.rng.choice([m for m in (2, 3, 4) if m * 2 <= mins] or [1])
    moves = p.pick(k)
    rounds = mins // k
    rows = []
    for i, e in enumerate(moves):
        amt = p.amount(e, 0.8) if e.rep_based else min(40, p.amount(e))
        minutes_list = ", ".join(str(i + 1 + k * r) for r in range(min(rounds, 3)))
        rows.append(p.row(e, f"{p.fmt(e, amt)}  (min {minutes_list}…)"))
    rules = (f"EMOM — Every Minute On the Minute, {mins} min. Start a timer. At the start of each "
             f"minute do the next move, then rest until the minute is up. Cycle through the "
             f"{k} moves {rounds} times. Can't finish in the minute? Drop the reps a bit.")
    return rules, rows


def f_amrap(p: Picker, mins):
    blocks = 2 if mins >= 16 else 1
    block_min = (mins - (blocks - 1)) // blocks
    rows = []
    for b in range(blocks):
        if blocks > 1:
            rows.append(Row(move=f"AMRAP {b + 1} — {block_min} min", group=True))
        for e in p.pick(p.rng.randint(3, 5)):
            rows.append(p.row(e, p.fmt(e, p.amount(e, 0.8))))
        rows.append(Row(move="Rounds completed", do="____", cue="Write your score. Bragging rights."))
    rest = " Rest 1 min between AMRAPs." if blocks > 1 else ""
    rules = (f"AMRAP — As Many Rounds As Possible. Set a {block_min}-min timer and loop through the "
             f"list nonstop, resting only when you need to. Count your rounds.{rest}")
    return rules, rows


def f_tabata(p: Picker, mins):
    blocks = max(1, (mins + 1) // 5)
    rows = []
    for b in range(blocks):
        rows.append(Row(move=f"Tabata {b + 1} — 4 min", group=True))
        for e in p.pick(2):
            rows.append(p.row(e, "20 s on / 10 s off ×4"))
    rules = ("TABATA — 20 seconds all-out, 10 seconds rest, 8 rounds = 4 minutes. Alternate the two "
             f"moves in each block. {blocks} block(s), 1 min rest between. Use any free interval "
             "timer app (search 'tabata timer').")
    return rules, rows


def f_ladder(p: Picker, mins):
    moves = p.pick(p.rng.choice([2, 3]), reps_only=True)
    if p.rng.random() < 0.5:
        rows = [p.row(e, "1 → 2 → 3 → … reps") for e in moves]
        rules = (f"LADDER UP — {mins}-min timer. Round 1: 1 rep of each move. Round 2: 2 reps of each. "
                 "Keep adding 1 rep per round until time runs out. Write down the highest rung you hit.")
        rows.append(Row(move="Highest rung", do="____"))
    else:
        top = 10 if p.level < 3 else 12
        rows = []
        for e in moves:
            t = max(4, min(top, p.amount(e)))
            rows.append(p.row(e, f"{t} → {t - 1} → … → 1" + (" / side" if "side" in e.unit else "")))
        rules = (f"LADDER DOWN — Do the top number of every move, then 1 less of each, all the way down "
                 f"to 1. For time, cap {mins} min. Write your finish time.")
        rows.append(Row(move="Finish time", do="____"))
    return rules, rows


def f_pyramid(p: Picker, mins):
    moves = p.pick(3, reps_only=True)
    rows = []
    for e in moves:
        step = max(1, round(p.amount(e) / 4))
        seq = [step * i for i in (1, 2, 3, 4, 3, 2, 1)]
        rows.append(p.row(e, "-".join(map(str, seq)) + (" / side" if "side" in e.unit else "")))
    rules = (f"PYRAMID — 7 rounds. Each round, do every move for that round's number (climb up, then back "
             f"down). Rest ~30 s between rounds. Cap {mins} min — stop wherever you are.")
    return rules, rows


def f_deck(p: Picker, mins):
    moves = p.pick(4, reps_only=True)
    while len(moves) < 4:
        moves.append(moves[len(moves) % max(1, len(moves))])
    suit_map = dict(zip(SUITS, moves))
    rows = [Row(move="The suits", group=True)]
    for s, e in suit_map.items():
        rows.append(Row(move=f"{s} {SUIT_NAMES[s]} = {e.name}", do="card value", cue=e.cue))
    rows.append(Row(move="The draw (pre-shuffled for you)", group=True))
    deck = [(v, s) for s in SUITS for v in range(2, 15)]
    p.rng.shuffle(deck)
    n_cards = max(8, int(mins * 60 / 35))
    labels = {11: "J", 12: "Q", 13: "K", 14: "A"}
    for i, (v, s) in enumerate(deck[:n_cards], 1):
        e = suit_map[s]
        base = 10 if v in (11, 12, 13) else (11 if v == 14 else v)
        reps = max(1, round(base * min(1.5, max(0.5, p.amount(e) / 10))))
        unit = " / side" if "side" in e.unit else ""
        rows.append(Row(move=f"Card {i}:  {labels.get(v, v)}{s}", do=f"{reps}{unit} {e.name.lower()}",
                        new=e.name not in p.ever))
    rules = ("DECK OF CARDS — each suit is a move; flip the next card and do that many reps "
             "(J/Q/K = 10, A = 11, already scaled to your level). No deck needed — the shuffle is "
             f"below. Go top to bottom, cap {mins} min. Got a real deck? Use it instead.")
    return rules, rows


def f_circuit(p: Picker, mins):
    work, rest = {1: (30, 30), 2: (40, 20), 3: (45, 15)}[p.level]
    stations = p.rng.randint(4, 6)
    moves = p.pick(stations)
    rounds = max(1, mins // len(moves)) if moves else 1
    rows = [p.row(e, f"{work} s work / {rest} s rest") for e in moves]
    rules = (f"CIRCUIT — {len(moves)} stations. Work {work} s, rest {rest} s, move to the next. "
             f"Do {rounds} rounds total. Every station is 1 minute, so a timer app on repeat makes this easy.")
    return rules, rows


def f_death_by(p: Picker, mins):
    moves = p.pick(2, reps_only=True)
    cap = min(mins, 14)
    rows = [p.row(e, "minute # = reps" + (" / side" if "side" in e.unit else "")) for e in moves]
    rows.append(Row(move="Minute you reached", do="____"))
    rest = ""
    if mins > cap:
        finisher = p.pick(1)
        if finisher:
            e = finisher[0]
            rows.append(Row(move="Then finisher", group=True))
            rows.append(p.row(e, f"{p.fmt(e, p.amount(e))} ×3 sets"))
            rest = " Then do the finisher."
    rules = (f"DEATH BY… — Minute 1: 1 rep. Minute 2: 2 reps. Minute 3: 3 reps… Alternate the two moves "
             f"each minute. Rest whatever's left of each minute. When you can't finish inside the minute, "
             f"you're out — write down the minute. Cap {cap} min.{rest}")
    return rules, rows


def f_chipper(p: Picker, mins):
    moves = p.pick(p.rng.randint(5, 7))
    # size each set so the whole chipper ≈ 60% of the time window (~4 s per rep incl. breathers)
    def secs(e, amt):
        per = 4 if e.rep_based else 1
        return amt * per * (2 if "side" in e.unit else 1)

    def friendly(e, amt):  # 37 -> 35 reps, 141 s -> 135 s
        step = 15 if not e.rep_based else (5 if amt > 15 else 1)
        return max(step, round(amt / step) * step)

    base_total = sum(secs(e, p.amount(e)) for e in moves) or 1
    factor = max(0.8, min(2.5, mins * 60 * 0.6 / base_total))
    rows = [p.row(e, p.fmt(e, friendly(e, p.amount(e, factor)))) for e in moves]
    rows.append(Row(move="Finish time", do="____"))
    rules = (f"CHIPPER — one big list, done ONCE from top to bottom. 'Chip away' at each number "
             f"(break it into mini-sets however you like), then move on. Cap {mins} min.")
    return rules, rows


def f_superset(p: Picker, mins):
    pairs = max(1, min(6, round(mins / 6)))
    rounds = max(3, round(mins / pairs / 2))  # ~2 min per round of a pair
    rows = []
    for i in range(pairs):
        pair = p.pick(2)
        letter = "ABCDEF"[i]
        rows.append(Row(move=f"Superset {letter} — {rounds} rounds", group=True))
        for j, e in enumerate(pair, 1):
            rows.append(p.row(e, f"{letter}{j}: {p.fmt(e, p.amount(e))}"))
    rules = ("SUPERSETS — do the two moves in a pair back-to-back with no rest, then rest 45 s. "
             f"Repeat {rounds} rounds, then move to the next pair.")
    return rules, rows


FORMATS = {
    "EMOM": f_emom,
    "AMRAP": f_amrap,
    "Tabata": f_tabata,
    "Ladder": f_ladder,
    "Pyramid": f_pyramid,
    "Deck of Cards": f_deck,
    "Circuit": f_circuit,
    "Death By": f_death_by,
    "Chipper": f_chipper,
    "Supersets": f_superset,
}


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------
def _warmup(rng):
    items = rng.sample(data.WARMUPS, 4)
    return [Row(move=n, do=d, cue=c) for n, d, c in items]


def _cooldown(rng, focus):
    region = focus if focus != "full" else None
    weights = [3 if region and region in r.split() else 1 for *_, r in data.COOLDOWNS]
    picks = []
    pool = list(zip(data.COOLDOWNS, weights))
    for _ in range(4):
        items, ws = zip(*pool)
        c = rng.choices(items, weights=ws)[0]
        picks.append(c)
        pool = [(i, w) for i, w in pool if i is not c]
    return [Row(move=n, do=d, cue=cue) for n, d, cue, _ in picks]


def generate(profile: dict, focus: str, minutes: int, history: History,
             rng: random.Random, format_name: str | None = None) -> Workout:
    if focus == "surprise":
        focus = rng.choice(FOCUSES)
    if focus not in FOCUSES:
        raise ValueError(f"focus must be one of {FOCUSES + ['surprise']}")
    main_min = max(5, minutes - WARMUP_MIN - COOLDOWN_MIN)

    if format_name is None:
        options = [f for f in FORMATS if f not in history.recent_formats()]
        format_name = rng.choice(options or list(FORMATS))
    picker = Picker(profile, focus, history, rng)
    rules, main_rows = FORMATS[format_name](picker, main_min)

    name = (f"The {rng.choice(data.NAME_ADJECTIVES)} {rng.choice(data.NAME_NOUNS[focus])} "
            f"{rng.choice(data.NAME_SUFFIXES)}")
    return Workout(
        name=name, focus=focus, minutes=minutes, level=profile["level"],
        format_name=format_name, format_rules=rules, twist=rng.choice(data.TWISTS),
        warmup=_warmup(rng),
        main=main_rows, cooldown=_cooldown(rng, focus),
        exercises=sorted({e.name for e in picker.used}),
    )
