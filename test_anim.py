import unittest
import xml.etree.ElementTree as ET

from workout_gen import data
from workout_gen.anim import render
from workout_gen.anim_moves import M
from workout_gen.html import figure

ALL_MOVES = ([e.name for e in data.EXERCISES] + [w[0] for w in data.WARMUPS] + [c[0] for c in data.COOLDOWNS])


class AnimationTests(unittest.TestCase):
    def test_every_move_has_an_animation(self):
        missing = [n for n in ALL_MOVES if n not in M]
        self.assertEqual(missing, [], "add poses for these in workout_gen/anim_moves.py")

    def test_every_animation_is_valid_svg(self):
        for name in ALL_MOVES:
            with self.subTest(name=name):
                svg = ET.fromstring(render(M[name], name))
                anims = svg.findall(".//{http://www.w3.org/2000/svg}animate")
                self.assertTrue(anims)
                for a in anims:
                    n_values = len(a.get("values").split(";"))
                    self.assertEqual(n_values, len(a.get("keyTimes").split(";")))

    def test_unknown_move_gets_no_figure(self):
        self.assertEqual(figure("Card 3: 7♠"), "")


if __name__ == "__main__":
    unittest.main()
