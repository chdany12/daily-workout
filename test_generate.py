"""Smoke + rule tests. Run: python -m unittest -v"""

import random
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from workout_gen import data, engine, excel

BASE = {"level": 2, "equipment": ["floor", "mat", "chair", "wall"], "noise_sensitive": False,
        "avoid_tags": [], "banned_moves": []}


def hist(tmp):
    return engine.History(Path(tmp) / "h.json")


class TestGenerate(unittest.TestCase):
    def test_every_format_focus_length_level(self):
        with tempfile.TemporaryDirectory() as tmp:
            for level in (1, 2, 3):
                prof = {**BASE, "level": level}
                for fmt in engine.FORMATS:
                    for focus in engine.FOCUSES:
                        for mins in (10, 15, 25, 35, 60):
                            w = engine.generate(prof, focus, mins, hist(tmp), random.Random(1), fmt)
                            moves = [r for r in w.main if not r.group and r.cue]
                            self.assertTrue(moves, f"{fmt}/{focus}/{mins}/L{level} empty")
                            excel.write(w, Path(tmp) / "t.xlsx")

    def test_noise_and_avoid_filters(self):
        noisy = {e.name for e in data.EXERCISES if {"noisy", "wrists"} & set(e.tags)}
        prof = {**BASE, "level": 3, "noise_sensitive": True, "avoid_tags": ["wrists"]}
        with tempfile.TemporaryDirectory() as tmp:
            for seed in range(200):
                w = engine.generate(prof, "surprise", 35, hist(tmp), random.Random(seed))
                self.assertFalse(set(w.exercises) & noisy, w.exercises)

    def test_no_chair_means_no_chair_moves(self):
        chair = {e.name for e in data.EXERCISES if "chair" in e.equip}
        prof = {**BASE, "equipment": ["floor", "mat"]}
        with tempfile.TemporaryDirectory() as tmp:
            for seed in range(100):
                w = engine.generate(prof, "full", 25, hist(tmp), random.Random(seed))
                self.assertFalse(set(w.exercises) & chair)

    def test_format_does_not_repeat_within_3(self):
        with tempfile.TemporaryDirectory() as tmp:
            h = hist(tmp)
            rng = random.Random(7)
            fmts = []
            for _ in range(30):
                w = engine.generate(BASE, "surprise", 25, h, rng)
                h.add(w)
                fmts.append(w.format_name)
            for i in range(3, len(fmts)):
                self.assertNotIn(fmts[i], fmts[i - 3:i])

    def test_excel_has_checkboxes_and_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = engine.generate(BASE, "upper", 25, hist(tmp), random.Random(3))
            p = Path(tmp) / "w.xlsx"
            excel.write(w, p)
            ws = load_workbook(p).active
            text = " ".join(str(c.value) for row in ws.iter_rows() for c in row if c.value)
            for s in ("WARM-UP", "MAIN EVENT", "COOL-DOWN", w.name):
                self.assertIn(s, text)
            self.assertTrue(ws.data_validations.dataValidation)


if __name__ == "__main__":
    unittest.main()
