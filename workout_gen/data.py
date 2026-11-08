"""Hand-curated exercise library for home workouts.

Equipment assumed: floor, (optional) yoga mat, a sturdy chair or couch, a wall.

Each exercise is tagged so the generator can filter and mix:
  regions : which focus it serves -> upper / lower / core / cardio
  level   : 1 = beginner-friendly, 2 = intermediate, 3 = hard
  amount  : a sensible working set at level 2 (reps, or seconds)
  unit    : "reps", "reps/side", "sec", "sec/side"
  equip   : extra equipment beyond the floor ("mat", "chair", "wall")
  tags    : "noisy" (jumping/stomping), "wrists", "knees" (joint stress)
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Exercise:
    name: str
    regions: tuple
    level: int
    amount: int
    unit: str
    cue: str
    equip: tuple = field(default_factory=tuple)
    tags: tuple = field(default_factory=tuple)

    @property
    def rep_based(self) -> bool:
        return self.unit.startswith("reps")


def E(name, regions, level, amount, unit, cue, equip=(), tags=()):
    return Exercise(name, tuple(regions.split()), level, amount, unit, cue, tuple(equip), tuple(tags))


EXERCISES = [
    # ---------------- UPPER ----------------
    E("Push-up", "upper", 2, 10, "reps", "Body in a straight line, chest to just above the floor.", tags=["wrists"]),
    E("Knee push-up", "upper", 1, 12, "reps", "Knees down, hips in line with shoulders. Chest to floor.", ["mat"], ["wrists"]),
    E("Incline push-up (hands on couch)", "upper", 1, 12, "reps", "Hands on couch/chair edge, body straight, lower chest to the edge.", ["chair"], ["wrists"]),
    E("Decline push-up (feet on couch)", "upper", 3, 8, "reps", "Feet up on the couch, hands on floor. Slow lower.", ["chair"], ["wrists"]),
    E("Wide push-up", "upper", 2, 10, "reps", "Hands wider than shoulders, elbows out at ~45°.", tags=["wrists"]),
    E("Diamond push-up", "upper", 3, 8, "reps", "Thumbs and index fingers touch under your chest.", tags=["wrists"]),
    E("Pike push-up", "upper", 2, 8, "reps", "Hips high like an upside-down V, lower your head toward the floor.", tags=["wrists"]),
    E("Elevated pike push-up (feet on chair)", "upper", 3, 6, "reps", "Feet on chair, hips stacked over shoulders, head to floor.", ["chair"], ["wrists"]),
    E("Chair dip", "upper", 2, 10, "reps", "Hands on chair edge behind you, legs straight, elbows bend to 90°.", ["chair"], ["wrists"]),
    E("Bent-knee chair dip", "upper", 1, 10, "reps", "Same as chair dip with feet close and knees bent. Easier.", ["chair"], ["wrists"]),
    E("Spiderman push-up", "upper core", 3, 8, "reps", "On the way down, bring one knee toward the same elbow. Alternate.", tags=["wrists"]),
    E("Hindu push-up", "upper", 3, 8, "reps", "Start in down-dog, swoop chest low and forward into cobra, push back.", tags=["wrists"]),
    E("Plank to down-dog", "upper core", 1, 10, "reps", "From high plank push hips up and back, then return.", ["mat"], ["wrists"]),
    E("Prone Y-T-W raises", "upper", 1, 8, "reps", "Lying face down, lift arms into a Y, then T, then W. Squeeze shoulder blades.", ["mat"]),
    E("Superman pull-down", "upper", 1, 12, "reps", "Face down, arms overhead, pull elbows down to ribs like a pull-up.", ["mat"]),
    E("Reverse snow angels", "upper", 1, 10, "reps", "Face down, arms hover, sweep from hips to overhead and back.", ["mat"]),
    E("Pseudo planche lean", "upper core", 3, 20, "sec", "High plank, fingers pointing back, lean shoulders past your hands.", tags=["wrists"]),
    E("Reverse plank hold", "upper core", 2, 25, "sec", "Sit, hands behind, lift hips so body is a straight ramp.", ["mat"], ["wrists"]),
    E("Bear crawl (forward & back)", "upper core cardio", 2, 30, "sec", "Knees hover an inch off the floor, crawl a few steps each way.", tags=["wrists"]),
    E("Crab walk", "upper core", 2, 30, "sec", "Hands behind, hips up, walk forward and back.", tags=["wrists"]),
    E("Shadow boxing", "upper cardio", 1, 40, "sec", "Jab-cross-hook combos, stay light on your feet."),
    E("Arm circle burnout", "upper", 1, 40, "sec", "Arms straight out, small fast circles. Switch direction halfway."),

    # ---------------- LOWER ----------------
    E("Bodyweight squat", "lower", 1, 15, "reps", "Feet shoulder-width, sit back and down, chest up."),
    E("Chair sit-to-stand", "lower", 1, 12, "reps", "Tap the chair with your butt, stand up without using hands.", ["chair"]),
    E("Sumo squat", "lower", 1, 15, "reps", "Wide stance, toes out, knees track over toes."),
    E("Split squat", "lower", 2, 10, "reps/side", "Staggered stance, drop the back knee straight down.", tags=["knees"]),
    E("Bulgarian split squat (foot on couch)", "lower", 3, 8, "reps/side", "Rear foot on couch, lower until front thigh is parallel.", ["chair"], ["knees"]),
    E("Reverse lunge", "lower", 1, 10, "reps/side", "Step back, both knees bend to 90°, push through front heel.", tags=["knees"]),
    E("Lateral lunge", "lower", 2, 8, "reps/side", "Big step to the side, sit into that hip, other leg straight."),
    E("Curtsy lunge", "lower", 2, 10, "reps/side", "Step one leg diagonally behind the other, like a curtsy.", tags=["knees"]),
    E("Chair step-up", "lower", 2, 10, "reps/side", "Sturdy chair only. Drive through the top foot, control the way down.", ["chair"]),
    E("Glute bridge", "lower", 1, 15, "reps", "On your back, feet flat, squeeze glutes and lift hips.", ["mat"]),
    E("Single-leg glute bridge", "lower", 2, 10, "reps/side", "One foot planted, other leg straight up. Lift hips.", ["mat"]),
    E("Couch hip thrust", "lower", 2, 15, "reps", "Upper back on couch edge, drive hips up, pause at top.", ["chair"]),
    E("Wall sit", "lower", 1, 40, "sec", "Back flat on wall, thighs parallel to floor.", ["wall"], ["knees"]),
    E("Calf raises", "lower", 1, 20, "reps", "Rise onto toes, pause, lower slowly. Hold a wall for balance.", ["wall"]),
    E("Single-leg calf raise", "lower", 2, 12, "reps/side", "One foot, full range, slow down.", ["wall"]),
    E("Donkey kicks", "lower", 1, 15, "reps/side", "On all fours, kick one heel toward the ceiling, knee bent.", ["mat"]),
    E("Fire hydrants", "lower", 1, 12, "reps/side", "On all fours, lift bent knee out to the side.", ["mat"]),
    E("Side-lying leg raise", "lower", 1, 15, "reps/side", "Lie on your side, lift the top leg, toes forward.", ["mat"]),
    E("Squat pulses", "lower", 2, 30, "sec", "Stay low in a squat, pulse up and down a few inches."),
    E("Cossack squat", "lower", 3, 6, "reps/side", "Wide stance, shift into one deep side squat, other leg straight.", tags=["knees"]),
    E("Jump squat", "lower cardio", 2, 10, "reps", "Squat then explode up. Land soft.", tags=["noisy", "knees"]),
    E("Good morning", "lower", 1, 12, "reps", "Hands behind head, hinge at hips with flat back, stand tall."),
    E("Single-leg RDL", "lower core", 2, 8, "reps/side", "Hinge on one leg, other leg reaches back, flat back.",),
    E("Tempo squat (5 s down)", "lower", 2, 6, "reps", "Take a full 5 seconds to lower. Stand up normal speed."),
    E("Frog pumps", "lower", 1, 20, "reps", "On your back, soles of feet together, knees out, pump hips up.", ["mat"]),

    # ---------------- CORE ----------------
    E("Plank", "core", 1, 30, "sec", "Forearms down, body straight, squeeze glutes."),
    E("Side plank", "core", 2, 20, "sec/side", "On forearm, hips stacked and lifted."),
    E("Side plank hip dips", "core", 2, 10, "reps/side", "From side plank, dip hip toward floor and lift back up."),
    E("Dead bug", "core", 1, 10, "reps/side", "On your back, lower opposite arm and leg, low back pressed down.", ["mat"]),
    E("Bird dog", "core", 1, 10, "reps/side", "On all fours, reach opposite arm and leg, hold 1 s.", ["mat"]),
    E("Hollow hold", "core", 2, 20, "sec", "On your back, arms and legs hovering, low back glued to floor.", ["mat"]),
    E("Bicycle crunch", "core", 1, 20, "reps", "Elbow to opposite knee, slow and controlled.", ["mat"]),
    E("Mountain climbers", "core cardio", 2, 30, "sec", "High plank, drive knees to chest fast.", tags=["wrists"]),
    E("Russian twist", "core", 2, 20, "reps", "Lean back, feet up if you can, rotate side to side.", ["mat"]),
    E("Lying leg raise", "core", 2, 12, "reps", "Legs straight, lower slowly, don't let low back arch.", ["mat"]),
    E("Flutter kicks", "core", 1, 30, "sec", "Legs straight and low, small fast kicks.", ["mat"]),
    E("Reverse crunch", "core", 2, 12, "reps", "Curl knees toward chest and lift hips off the floor.", ["mat"]),
    E("V-up", "core", 3, 10, "reps", "Lift arms and legs at the same time to meet in the middle.", ["mat"]),
    E("Sit-up", "core", 1, 15, "reps", "Feet flat (tuck them under the couch if needed).", ["mat"]),
    E("Plank jacks", "core cardio", 2, 30, "sec", "In plank, jump feet wide and back together.", tags=["noisy", "wrists"]),
    E("Bear hold", "core", 2, 30, "sec", "On all fours, hover knees 1 inch off the floor. Don't move.", tags=["wrists"]),
    E("Heel taps", "core", 1, 20, "reps", "Lying, shoulders lifted, reach side to side to tap your heels.", ["mat"]),
    E("Superman hold", "core", 1, 20, "sec", "Face down, lift arms and legs off the floor and hold.", ["mat"]),
    E("Seated knee tucks (chair edge)", "core", 2, 12, "reps", "Sit on edge, lean back, pull knees in and extend out.", ["chair"]),
    E("Plank shoulder taps", "core upper", 2, 20, "reps", "High plank, tap opposite shoulder, keep hips still.", tags=["wrists"]),
    E("Plank up-downs", "core upper", 2, 10, "reps", "Forearm plank to high plank and back, one arm at a time.", tags=["wrists"]),

    # ---------------- CARDIO / FULL BODY ----------------
    E("Jumping jacks", "cardio", 1, 40, "sec", "Classic. Stay light on your toes.", tags=["noisy"]),
    E("Step jacks (quiet)", "cardio", 1, 40, "sec", "Step one foot out while arms go up. Alternate. No jumping."),
    E("Burpee", "cardio upper lower core", 3, 8, "reps", "Squat, jump back to plank, chest down, jump up.", tags=["noisy", "wrists"]),
    E("No-jump burpee", "cardio upper lower core", 2, 8, "reps", "Step back to plank, step in, stand and reach. Quiet version.", tags=["wrists"]),
    E("High knees", "cardio", 1, 30, "sec", "Run in place, knees to hip height.", tags=["noisy"]),
    E("Marching high knees", "cardio", 1, 40, "sec", "Fast march, knees high, pump the arms. Quiet."),
    E("Butt kicks", "cardio", 1, 30, "sec", "Jog in place, heels to glutes.", tags=["noisy"]),
    E("Squat thrust", "cardio lower core", 2, 10, "reps", "Hands down, step or hop feet back to plank and back in.", tags=["wrists"]),
    E("Star jump", "cardio lower", 3, 8, "reps", "Explode up into an X shape. Land soft.", tags=["noisy", "knees"]),
    E("Speed skaters (step)", "cardio lower", 1, 30, "sec", "Big side steps, swing arms like a speed skater."),
    E("Squat to overhead reach", "cardio lower", 1, 12, "reps", "Squat down, stand up fast and reach for the ceiling."),
    E("Lunge with twist", "lower core", 2, 8, "reps/side", "Reverse lunge, rotate torso over the front leg.", tags=["knees"]),
    E("Tuck jump", "cardio lower", 3, 8, "reps", "Jump and pull knees to chest.", tags=["noisy", "knees"]),
    E("Fast feet", "cardio", 2, 20, "sec", "Quick tiny steps on the balls of your feet.", tags=["noisy"]),
    E("Inchworm", "cardio upper core", 1, 6, "reps", "Fold down, walk hands out to plank, walk back, stand.", tags=["wrists"]),
]


WARMUPS = [
    ("Arm circles", "30 sec", "Big circles forward, then back."),
    ("Hip circles", "30 sec", "Hands on hips, draw big circles each way."),
    ("Leg swings", "10 / side", "Hold the wall, swing each leg forward and back."),
    ("Cat-cow", "8 reps", "On all fours, round then arch your back slowly."),
    ("March in place", "45 sec", "Easy march, swing your arms."),
    ("Torso twists", "30 sec", "Feet planted, rotate side to side, let arms swing."),
    ("World's greatest stretch", "4 / side", "Lunge, elbow to instep, rotate arm to ceiling."),
    ("Bodyweight good morning", "10 reps", "Gentle hinge to wake up the hamstrings."),
    ("Shoulder rolls", "30 sec", "Roll shoulders up, back and down."),
    ("Slow air squats", "8 reps", "Half-speed squats, sit deep."),
    ("Wrist rolls", "20 sec", "Interlace fingers, roll wrists in circles."),
    ("Down-dog pedal", "30 sec", "In down-dog, alternate bending knees."),
]

# (name, prescription, cue, region bias)
COOLDOWNS = [
    ("Child's pose", "45 sec", "Knees wide, sit back, arms long.", "upper core"),
    ("Standing hamstring stretch", "30 sec", "Fold forward, soft knees, let your head hang.", "lower"),
    ("Standing quad stretch", "20 sec / side", "Hold the wall, pull heel to glute.", "lower"),
    ("Figure-4 stretch", "30 sec / side", "On your back, ankle on opposite knee, pull legs in.", "lower"),
    ("Wall chest stretch", "30 sec / side", "Forearm on wall, turn your body away.", "upper"),
    ("Cobra", "30 sec", "Lying face down, press up gently, hips stay down.", "core"),
    ("Cross-body shoulder stretch", "20 sec / side", "Pull arm across chest.", "upper"),
    ("Kneeling hip flexor stretch", "30 sec / side", "Half-kneel, tuck pelvis, lean forward slightly.", "lower"),
    ("Lying spinal twist", "30 sec / side", "On your back, drop both knees to one side.", "core"),
    ("Overhead triceps stretch", "20 sec / side", "Elbow up, hand down your back, gently press elbow.", "upper"),
    ("Deep belly breathing", "60 sec", "Lie down, 4 s in, 6 s out. You did it.", "core"),
]


TWISTS = [
    "TEMPO MODE: take 3 full seconds to lower on every rep.",
    "FREEZE FRAME: on the last rep of every set, hold the hardest position for 3 seconds.",
    "COMMENTATOR MODE: narrate yourself out loud like a sports announcer. Seriously.",
    "CLOCK DIGIT: look at the clock. The last digit of the minute = bonus reps added to your FIRST move every round.",
    "PLANK TAX: every time you pause mid-workout to check your phone, pay 10 seconds of plank.",
    "FINISHER: 60-second plank at the end. Every time you drop, 5 squats, then back in.",
    "SONG SWITCH: put a playlist on shuffle. Every new song = 5 squats before you continue.",
    "MIRROR DAY: if a move is per side, start with your weaker side.",
    "LEVEL UP: pick ONE move on this sheet and do the harder version of it today.",
    "SILENT MODE: no music. Do the whole thing as quietly as possible like a ninja.",
    "NO TWIST TODAY. Just vibes.",
    "NO TWIST TODAY. Just vibes.",
]


NAME_ADJECTIVES = [
    "Sneaky", "Turbo", "Feral", "Midnight", "Chaotic", "Silent", "Cosmic", "Spicy",
    "Grumpy", "Electric", "Rogue", "Velvet", "Stubborn", "Ninja", "Tiny", "Legendary",
    "Caffeinated", "Unhinged", "Polite", "Thunder",
]
NAME_NOUNS = {
    "upper": ["Gorilla", "Lobster", "Crane", "Kraken", "Gargoyle", "Octopus"],
    "lower": ["Kangaroo", "Flamingo", "Goat", "Frog", "Ostrich", "Rabbit"],
    "core": ["Turtle", "Cobra", "Pretzel", "Armadillo", "Dragon", "Plank Goblin"],
    "full": ["Couch Gremlin", "Raccoon", "Velociraptor", "Honey Badger", "Yeti", "Mongoose"],
}
NAME_SUFFIXES = ["Protocol", "Gauntlet", "Heist", "Ritual", "Rumble", "Quest", "Experiment", "Showdown"]
