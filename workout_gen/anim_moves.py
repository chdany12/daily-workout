"""Key poses for every move in data.py (exercises, warm-ups and cool-downs).

See anim.py for the pose format. Side view faces right; "front" faces the viewer;
"top" looks down on someone lying on a mat.
"""

import math

from .anim import Move, ik, ikp


def P(base=None, **kw):
    d = dict(base or {})
    d.update(kw)
    return d


def breathe(p, dur=3.6, dt=0.0, dc=1.5, view="side", props=()):
    """A hold: the pose, gently breathing."""
    return Move([p, P(p, t=p["t"] + dt, curve=p.get("curve", 0) + dc)], view=view, dur=dur, props=list(props))


# ---------------------------------------------------------------- standing
STAND = dict(t=180, a1=(-4, -2), a2=(5, 8), l1=(2, 0), l2=(-2, 0))
ARMS_FWD = dict(a1=(88, 90), a2=(84, 86))
ARMS_UP = dict(a1=(172, 176), a2=(178, 182))
SQUAT = P(STAND, t=145, l1=(84, -22), l2=(80, -24), **ARMS_FWD)
HANDS_HEAD = dict(a1=(130, -90), a2=(125, -95))
HIPS = dict(a1=(-25, 60), a2=(-20, 65))           # hands on hips (side view)

# front view
F_STAND = dict(t=180, a1=(8, 4), a2=(-8, -4), l1=(3, 3), l2=(-3, -3))
F_CLASP = dict(a1=(30, -150), a2=(-30, 150))      # hands together at the chest
F_HIPS = dict(a1=(35, -40), a2=(-35, 40))


# ---------------------------------------------------------------- planks
def line(sh_y, ankle=(-40, 4)):
    """Straight body from the ankles up to shoulder height sh_y. Returns (pose, neck)."""
    s = (sh_y - ankle[1]) / 69
    th = math.degrees(math.asin(max(-0.95, min(0.95, s))))
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    hip = (ankle[0] + 39 * c, ankle[1] + 39 * s)
    neck = (hip[0] + 30 * c, hip[1] + 30 * s)
    pose = dict(hip=hip, t=90 + th, h=95 + th, l1=ik(*ankle), l2=ik(ankle[0] - 1, ankle[1]), f1=15, f2=15)
    return pose, neck


def plank(sh_y=29, hand_x=None, ankle=(-40, 4), hand_y=0):
    p, n = line(sh_y, ankle)
    hx = n[0] if hand_x is None else hand_x
    return P(p, a1=ik(hx, hand_y), a2=ik(hx - 1, hand_y))


def forearm_plank(ankle=(-40, 4)):
    p, n = line(16.5, ankle)
    return P(p, a1=(2, 90), a2=(0, 88))


HIGH, _N = line(29)
HAND_X = _N[0]
PLANK_HI = plank(29)
PUSH_DOWN = plank(12, HAND_X)


def knee_line(sh_y, knee=(-18, 2)):
    s = (sh_y - knee[1]) / 50
    th = math.degrees(math.asin(s))
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    hip = (knee[0] + 20 * c, knee[1] + 20 * s)
    neck = (hip[0] + 30 * c, hip[1] + 30 * s)
    return dict(hip=hip, t=90 + th, h=95 + th, l1=(th - 90, -100), l2=(th - 91, -101), f1=-160, f2=-160), neck


# ---------------------------------------------------------------- floor
SUPINE = dict(hip=(0, 4), t=-90, h=-100, a1=(90, 90), a2=(91, 91), l1=(90, 90), l2=(91, 91))
KNEES_UP = dict(l1=ik(22, 1), l2=ik(21, 1), f1=95, f2=95)
PRONE = dict(hip=(0, 4), t=90, h=100, a1=(-90, -90), a2=(-91, -91), l1=(-90, -90), l2=(-91, -91), f1=-95, f2=-95)
FOURS = dict(hip=(0, 21.5), t=104, h=115, a1=ik(29, 0), a2=ik(28, 0), l1=(0, -92), l2=(-1, -92), f1=-100, f2=-100)
BEAR = dict(hip=(0, 23), t=104, h=115, a1=ik(29, 0), a2=ik(28, 0), l1=ik(-18, 5), l2=ik(-19, 5), f1=-20, f2=-20)
DOG = dict(hip=(-2, 36), t=58, h=28, a1=ik(40, 0), a2=ik(39, 0), l1=ik(-22, 3), l2=ik(-23, 3), f1=95, f2=95)


def bridge(hip_y, neck=(-30, 4)):
    """Shoulders stay on the floor while the hips lift."""
    dy = hip_y - neck[1]
    hip_x = neck[0] + math.sqrt(max(0, 900 - dy * dy))
    t = math.degrees(math.atan2(neck[0] - hip_x, -(neck[1] - hip_y)))
    return dict(hip=(hip_x, hip_y), t=t, h=-100, a1=(90, 90), a2=(91, 91))


def from_neck(neck, hip_y):
    """Hip placed so the neck lands on a fixed point (couch hip thrust)."""
    dy = neck[1] - hip_y
    hip_x = neck[0] + math.sqrt(max(0, 900 - dy * dy))
    t = math.degrees(math.atan2(neck[0] - hip_x, -(neck[1] - hip_y)))
    return dict(hip=(hip_x, hip_y), t=t)


def side_plank(hip_drop=0.0):
    ankle = (37, 3)
    th = math.radians(17)
    hip = (ankle[0] - 39 * math.cos(th), ankle[1] + 39 * math.sin(th))
    neck = (hip[0] - 30 * math.cos(th), hip[1] + 30 * math.sin(th))
    hip = (hip[0], hip[1] - hip_drop)
    t = math.degrees(math.atan2(neck[0] - hip[0], -(neck[1] - hip[1])))
    return dict(hip=hip, t=t, h=t - 10, a1=(170, 175), a2=(0, -90), l1=ik(37, 6.5), l2=ik(37, 2))


CROUCH = dict(hip=(4, 12), t=110, h=125, a1=ik(26, 0), a2=ik(25, 0), l1=ik(12, 0), l2=ik(11, 0))
B_STAND = P(STAND, x=8)


def lunge(front=1, hip=(-4, 22), front_x=1, back=(-30, 3)):
    f, b = (f"l{front}", f"l{3 - front}")
    return {"hip": hip, "t": 180, f: ik(front_x, 0), b: ik(*back), f"f{3 - front}": -40}


def mirror(p):
    """Swap near/far limbs (for alternating sides)."""
    q = dict(p)
    for a, b in (("a1", "a2"), ("l1", "l2"), ("f1", "f2")):
        if a in p or b in p:
            q[a], q[b] = p.get(b, q.get(b)), p.get(a, q.get(a))
            if q[a] is None: del q[a]
            if q[b] is None: del q[b]
    return q


def fmirror(p):
    """Mirror left/right for front-view poses."""
    def flip(spec):
        if spec is None:
            return None
        if isinstance(spec, tuple):
            return (-spec[0], -spec[1])
        return ik(-spec.x, spec.y, -spec.bend, spec.flat) if not isinstance(spec.x, str) else spec
    q = dict(p)
    for a, b in (("a1", "a2"), ("l1", "l2")):
        q[a], q[b] = flip(p.get(b)), flip(p.get(a))
        if q[a] is None: del q[a]
        if q[b] is None: del q[b]
    for k in ("f1", "f2"):
        q.pop(k, None)
    if "f1" in p: q["f2"] = -p["f1"]
    if "f2" in p: q["f1"] = -p["f2"]
    if "hip" in p: q["hip"] = (-p["hip"][0], p["hip"][1])
    if "x" in p: q["x"] = -p["x"]
    for k in ("t", "h"):
        if k in p:
            q[k] = 360 - p[k] if p[k] > 0 else -p[k]
    return q


CHAIR_BEHIND = ("chair", -34, 22, "left")

# ---------------------------------------------------------------- the moves
M = {}

# ---- upper
M["Push-up"] = Move([PLANK_HI, PUSH_DOWN], dur=2.2)
_kt, _kn = knee_line(29)
_kb, _ = knee_line(12)
M["Knee push-up"] = Move([P(_kt, a1=ik(28, 0), a2=ik(27, 0)), P(_kb, a1=ik(28, 0), a2=ik(27, 0))], dur=2.2)
M["Incline push-up (hands on couch)"] = Move(
    [plank(48, 17, hand_y=20), plank(33, 17, hand_y=20)], dur=2.2, props=[("couch", 12, 24, "right")])
M["Decline push-up (feet on couch)"] = Move(
    [plank(29, 26, ankle=(-40, 21)), plank(13, 26, ankle=(-40, 21))], dur=2.4, props=[("couch", -54, 24, "left")])
M["Wide push-up"] = M["Push-up"]
M["Diamond push-up"] = Move([plank(29, HAND_X + 3), plank(12, HAND_X + 3)], dur=2.2)
M["Pike push-up"] = Move([DOG, P(DOG, hip=(2, 35), t=40, h=20, a1=ik(40, 0), a2=ik(39, 0))], dur=2.2)
M["Elevated pike push-up (feet on chair)"] = Move(
    [dict(hip=(-6, 55), t=18, h=12, a1=ik(12, 0), a2=ik(11, 0), l1=ik(-24, 21), l2=ik(-25, 21), f1=180, f2=180),
     dict(hip=(2, 50), t=4, h=2, a1=ik(12, 0), a2=ik(11, 0), l1=ik(-24, 21), l2=ik(-25, 21), f1=180, f2=180)],
    dur=2.4, props=[("chair", -44, 22, "left")])
_dip_up = dict(hip=(-7, 20), t=-172, h=-178, a1=ik(-13, 20), a2=ik(-14, 20), l1=ik(28, 2), l2=ik(27, 2), f1=175, f2=175)
M["Chair dip"] = Move([_dip_up, P(_dip_up, hip=(-7, 6))], dur=2.2, props=[CHAIR_BEHIND])
_bdip = P(_dip_up, l1=ik(16, 0), l2=ik(15, 0), f1=95, f2=95)
M["Bent-knee chair dip"] = Move([_bdip, P(_bdip, hip=(-7, 6))], dur=2.2, props=[CHAIR_BEHIND])
M["Spiderman push-up"] = Move([PLANK_HI, P(PUSH_DOWN, l1=(78, -40), f1=40), PLANK_HI, P(PUSH_DOWN, l2=(78, -40), f2=40)], dur=4)
_cobra_hi = dict(hip=(19, 4), t=140, h=150, a1=ik(40, 0), a2=ik(39, 0), l1=ik(-20, 3), l2=ik(-21, 3), f1=-100, f2=-100)
_dd = P(DOG, l1=ik(-20, 3), l2=ik(-21, 3))
M["Hindu push-up"] = Move([_dd, dict(_dd, hip=(10, 12), t=96, h=105, l1=ik(-20, 3, -1), l2=ik(-21, 3, -1)), _cobra_hi],
                          dur=3.2, weights=[1, 1, 1.4])
_p2d = plank(29, 24)
M["Plank to down-dog"] = Move(
    [_p2d, dict(hip=(-15, 37), t=48, h=25, a1=ik(24, 0), a2=ik(23, 0), l1=ik(-40, 4), l2=ik(-41, 4), f1=60, f2=60)], dur=2.6)
_T = dict(t=180, l1=(3, 3), l2=(-3, -3))
M["Prone Y-T-W raises"] = Move(
    [P(_T, a1=(150, 150), a2=(-150, -150)), P(_T, a1=(90, 90), a2=(-90, -90)), P(_T, a1=(45, 150), a2=(-45, -150))],
    view="top", dur=3.6)
M["Superman pull-down"] = Move(
    [P(PRONE, t=96, h=105, a1=(100, 100), a2=(99, 99)), P(PRONE, t=96, h=105, a1=(-115, 60), a2=(-112, 62))], dur=2.2)
M["Reverse snow angels"] = Move([P(_T, a1=(12, 12), a2=(-12, -12)), P(_T, a1=(168, 168), a2=(-168, -168))], view="top", dur=3)
M["Pseudo planche lean"] = Move([plank(28, 20), plank(22, 20)], dur=3.2)
_rp = dict(hip=(3.6, 18), t=-111, h=-120, a1=ik(-27, 0), a2=ik(-28, 0), l1=ik(40, 4), l2=ik(39, 4), f1=170, f2=170)
M["Reverse plank hold"] = breathe(_rp)
M["Bear crawl (forward & back)"] = Move(
    [BEAR, P(BEAR, a1=ik(35, 0), l2=ik(-13, 5)), BEAR, P(BEAR, a2=ik(35, 0), l1=ik(-13, 5))], dur=1.8)
_crab = dict(hip=(0, 20), t=-108, h=-125, a1=ik(-30, 0), a2=ik(-31, 0), l1=ik(24, 0), l2=ik(23, 0), f1=95, f2=95)
M["Crab walk"] = Move([_crab, P(_crab, l1=ik(30, 0), a2=ik(-25, 0)), _crab, P(_crab, l2=ik(30, 0), a1=ik(-25, 0))], dur=1.8)
_guard = P(STAND, t=176, a1=(30, 165), a2=(25, 160), l1=(12, -2), l2=(-14, -4))
M["Shadow boxing"] = Move([_guard, P(_guard, a1=(90, 90), t=172), _guard, P(_guard, a2=(90, 90), t=168)], dur=1.6)
_ac = P(F_STAND, a1=(88, 88), a2=(-88, -88))
M["Arm circle burnout"] = Move([_ac, P(_ac, a1=(95, 98), a2=(-95, -98)), P(_ac, a1=(90, 92), a2=(-90, -92)),
                                P(_ac, a1=(83, 80), a2=(-83, -80))], view="front", dur=0.8)

# ---- lower
M["Bodyweight squat"] = Move([STAND, SQUAT], dur=2.2)
_sit = P(STAND, x=-20.6, t=162, l1=(88, 2), l2=(86, 0), **ARMS_FWD)
M["Chair sit-to-stand"] = Move([STAND, _sit], dur=2.4, props=[("chair", -32, 22, "left")])
_sumo = P(F_STAND, l1=(29, 29), l2=(-29, -29), **F_CLASP)
M["Sumo squat"] = Move([_sumo, P(_sumo, l1=(70, 0), l2=(-70, 0))], view="front", dur=2.2)
_ss = dict(hip=(0, 37), t=180, **HIPS, l1=ik(15, 0), l2=ik(-18, 3), f2=-40)
M["Split squat"] = Move([_ss, P(_ss, hip=(0, 22))], dur=2.2)
_bss = dict(hip=(0, 37), t=176, **HIPS, l1=ik(16, 0), l2=ik(-26, 21), f2=-100)
M["Bulgarian split squat (foot on couch)"] = Move([_bss, P(_bss, hip=(-2, 21), t=172)], dur=2.4,
                                                  props=[("couch", -48, 24, "left")])
_st = dict(hip=(0, 38.5), t=180, a1=(-4, -2), a2=(5, 8), l1=ik(1, 0), l2=ik(-1, 0))
M["Reverse lunge"] = Move([_st, P(lunge(1), a1=(-20, 10), a2=(25, 40)), _st,
                           P(lunge(2, hip=(-5, 22), front_x=-1), a1=(25, 40), a2=(-20, 10))], dur=3.6)
_wide = dict(hip=(0, 33.5), t=180, **F_CLASP, l1=ik(24, 0), l2=ik(-24, 0))
M["Lateral lunge"] = Move([_wide, P(_wide, hip=(12, 20), t=172), _wide, P(_wide, hip=(-12, 20), t=188)],
                          view="front", dur=3.6)
_cst = dict(hip=(0, 38.5), t=180, **F_CLASP, l1=ik(5, 0, flat=0.55), l2=ik(-5, 0, flat=0.55))
# near (right) leg steps behind and across; the front knee bends toward the viewer
_curtsy = P(_cst, hip=(-4, 20), t=184, h=182, l2=ik(-10, 0, flat=0.6), l1=ik(-20, 3, flat=0.55), f1=-40)
M["Curtsy lunge"] = Move([_cst, _curtsy, _cst, fmirror(_curtsy)], view="front", dur=3.6)
_su0 = dict(hip=(0, 38.5), t=180, a1=(-4, -2), a2=(5, 8), l1=ik(0, 0), l2=ik(-2, 0))
_su1 = dict(_su0, hip=(2, 37), t=172, l1=ik(20, 21), f1=90)
_su2 = dict(_su0, hip=(19, 58), t=178, l1=ik(20, 21), l2=ik(27, 34), f1=90, a1=(10, 20), a2=(-15, -5))
M["Chair step-up"] = Move([_su0, _su1, _su2, _su1], dur=3.6, props=[("chair", 12, 22, "right")])
_gb = P(SUPINE, **KNEES_UP)
M["Glute bridge"] = Move([_gb, P(_gb, **bridge(22))], dur=2.2)
_sgb = P(_gb, l1=(150, 150), f1=240)
M["Single-leg glute bridge"] = Move([_sgb, P(_sgb, **bridge(20), l1=(128, 128))], dur=2.2)
_ht = dict(h=-100, a1=(-95, -95), a2=(-96, -96), l1=ik(24, 0), l2=ik(23, 0), f1=95, f2=95)
M["Couch hip thrust"] = Move([P(_ht, **from_neck((-26, 22), 6)), P(_ht, **from_neck((-26, 22), 22))], dur=2.4,
                             props=[("couch", -46, 20)])
M["Wall sit"] = breathe(P(STAND, x=-8, t=180, l1=(90, 0), l2=(89, -1), a1=(60, 95), a2=(58, 93)),
                        dc=1, props=[("wall", -10.5)])
_cr = P(STAND, a1=(55, 75), a2=(50, 72))
M["Calf raises"] = Move([P(_cr, f1=90, f2=90), P(_cr, f1=35, f2=35, hold=0.3)], dur=2, props=[("wall", 25)])
_scr = P(_cr, l2=(-5, -110))
M["Single-leg calf raise"] = Move([P(_scr, f1=90), P(_scr, f1=35, hold=0.3)], dur=2, props=[("wall", 25)])
M["Donkey kicks"] = Move([FOURS, P(FOURS, l1=(-115, 175), f1=-90)], dur=1.6)
M["Fire hydrants"] = Move([FOURS, P(FOURS, l1=(-35, -125), f1=-120)], dur=1.6)
_sl = dict(t=-90, h=-95, a1=(0, 0), a2=(-90, -88), l1=(90, 90), l2=(91, 91), f1=180, f2=180)
M["Side-lying leg raise"] = Move([_sl, P(_sl, l1=(125, 125), f1=215)], view="front", dur=2)
M["Squat pulses"] = Move([SQUAT, P(SQUAT, t=150, l1=(66, -20), l2=(62, -22))], dur=0.8)
_cw = dict(hip=(0, 30), t=180, **F_CLASP, l1=ik(26, 0), l2=ik(-26, 0))
M["Cossack squat"] = Move([_cw, P(_cw, hip=(16, 10), t=168, f2=180), _cw, P(_cw, hip=(-16, 10), t=192, f1=180)],
                          view="front", dur=4)
M["Jump squat"] = Move([P(SQUAT, a1=(-40, -30), a2=(-35, -25)), P(STAND, up=12, a1=(160, 170), a2=(165, 175), f1=25, f2=25)],
                       dur=1.4)
_gm = P(STAND, **HANDS_HEAD)
M["Good morning"] = Move([_gm, P(_gm, t=98, h=100, l1=(8, -6), l2=(6, -8))], dur=2.4)
M["Single-leg RDL"] = Move([STAND, P(STAND, t=96, h=100, a1=(4, 4), a2=(2, 2), l1=(6, -4), l2=(-84, -84), f2=-10)], dur=2.6)
M["Tempo squat (5 s down)"] = Move([STAND, SQUAT], dur=6, weights=[5, 1])
_fp = P(SUPINE, l1=ik(14, 1), l2=ik(13, 1), f1=95, f2=95)
M["Frog pumps"] = Move([_fp, P(_fp, **bridge(14))], dur=1.4)

# ---- core
M["Plank"] = breathe(forearm_plank())
_spk = side_plank()
M["Side plank"] = breathe(_spk, view="front", dc=1)
M["Side plank hip dips"] = Move([_spk, side_plank(9)], view="front", dur=2)
_db = P(SUPINE, a1=(180, 180), a2=(178, 178), l1=(180, 90), l2=(178, 88), f1=175, f2=175)
M["Dead bug"] = Move([_db, P(_db, a1=(-100, -100), l2=(95, 95)), _db, P(_db, a2=(-100, -100), l1=(95, 95))], dur=3.6)
M["Bird dog"] = Move([FOURS, P(FOURS, a1=(95, 95), l2=(-90, -90), f2=-95, hold=0.4), FOURS,
                      P(FOURS, a2=(95, 95), l1=(-90, -90), f1=-95, hold=0.4)], dur=4)
M["Hollow hold"] = breathe(dict(hip=(0, 3.5), t=-102, h=-115, curve=2, a1=(-106, -106), a2=(-105, -105),
                                l1=(102, 102), l2=(101, 101), f1=190, f2=190), dc=0.8)
_bc = dict(hip=(0, 3.5), t=-108, h=-120, curve=2, a1=(150, -60), a2=(146, -64))
M["Bicycle crunch"] = Move([P(_bc, l1=(160, 85), l2=(100, 100), f2=190), P(_bc, l2=(160, 85), l1=(100, 100), f1=190)], dur=1.6)
M["Mountain climbers"] = Move([P(PLANK_HI, l1=(45, -40), f1=40), P(PLANK_HI, l2=(45, -40), f2=40)], dur=0.7)
_rt = dict(hip=(0, 3.5), t=-158, h=-165, curve=2, l1=(125, 70), l2=(123, 68), f1=165, f2=165)
M["Russian twist"] = Move([P(_rt, a1=(25, 70), a2=(35, 80)), P(_rt, a1=(80, 120), a2=(85, 125))], dur=1.4)
M["Lying leg raise"] = Move([P(SUPINE, l1=(93, 93), l2=(94, 94)), P(SUPINE, l1=(178, 178), l2=(176, 176))], dur=2.6)
_fk = P(SUPINE, t=-96, h=-110)
M["Flutter kicks"] = Move([P(_fk, l1=(100, 100), l2=(114, 114)), P(_fk, l1=(114, 114), l2=(100, 100))], dur=0.7)
_rc = P(SUPINE, l1=(175, 85), l2=(173, 83), f1=175, f2=175)
M["Reverse crunch"] = Move([_rc, P(_rc, hip=(-2, 8), t=-80, l1=(-155, 120), l2=(-157, 118), f1=210, f2=210)], dur=2)
M["V-up"] = Move([P(SUPINE, a1=(-92, -92), a2=(-93, -93)),
                  P(SUPINE, t=-140, h=-145, a1=(140, 140), a2=(138, 138), l1=(140, 140), l2=(138, 138), f1=230, f2=230)],
                 dur=2.2)
_su = P(SUPINE, a1=(140, 140), a2=(138, 138), l1=ik(20, 0), l2=ik(19, 0), f1=95, f2=95)
M["Sit-up"] = Move([_su, P(_su, t=162, h=150, curve=3, a1=(100, 100), a2=(98, 98))], dur=2.4)
_pj = dict(t=180, a1=(14, 12), a2=(-14, -12), l1=(4, 4), l2=(-4, -4))
M["Plank jacks"] = Move([_pj, P(_pj, l1=(24, 24), l2=(-24, -24))], view="top", dur=0.9)
M["Bear hold"] = breathe(BEAR, dc=1)
_ht2 = dict(SUPINE, t=-106, h=-118, curve=2, **KNEES_UP)
M["Heel taps"] = Move([P(_ht2, a1=(84, 84), a2=(94, 96)), P(_ht2, a1=(94, 96), a2=(84, 84))], dur=1.4)
M["Superman hold"] = breathe(P(PRONE, curve=-2, h=112, a1=(108, 108), a2=(106, 106), l1=(-104, -104), l2=(-103, -103)), dc=-1)
_kt0 = dict(hip=(-12, 21), t=-160, h=-170, a1=ik(-16, 20), a2=ik(-17, 20))
M["Seated knee tucks (chair edge)"] = Move([P(_kt0, l1=(82, 82), l2=(80, 80), f1=175, f2=175),
                                            P(_kt0, t=-168, l1=(140, 20), l2=(138, 18))],
                                           dur=1.8, props=[CHAIR_BEHIND])
M["Plank shoulder taps"] = Move([PLANK_HI, P(PLANK_HI, a1=ikp("n", -2, -3)), PLANK_HI, P(PLANK_HI, a2=ikp("n", -2, -3))], dur=2)
_fp1 = forearm_plank()
_mid = P(line(22)[0], a1=ik(HAND_X, 0), a2=(0, 90))
M["Plank up-downs"] = Move([_fp1, _mid, PLANK_HI, P(line(22)[0], a1=(0, 90), a2=ik(HAND_X, 0))], dur=3.6)

# ---- cardio / full body
_jj0 = P(F_STAND)
_jj1 = P(F_STAND, a1=(150, 168), a2=(-150, -168), l1=(18, 18), l2=(-18, -18))
M["Jumping jacks"] = Move([_jj0, _jj1], view="front", dur=1)
M["Step jacks (quiet)"] = Move([_jj0, P(_jj1, l2=(-3, -3)), _jj0, P(_jj1, l1=(3, 3))], view="front", dur=2.4)
_pl = plank(29, 26)
_pd = plank(12, 26)
M["Burpee"] = Move([B_STAND, CROUCH, _pl, _pd, _pl, CROUCH, P(STAND, x=8, up=12, **ARMS_UP, f1=25, f2=25)],
                   dur=5, weights=[1, 0.7, 0.8, 0.8, 0.7, 1, 1])
_half = P(CROUCH, l1=ik(-40, 4), hip=(-6, 16), t=100)
M["No-jump burpee"] = Move([B_STAND, CROUCH, _half, _pl, _half, CROUCH, P(STAND, x=8, **ARMS_UP)], dur=6)
_hk = P(STAND, l1=(95, 0), l2=(-4, -8), a1=(-35, 30), a2=(50, 140), f1=100)
M["High knees"] = Move([P(_hk, up=3), P(mirror(_hk), up=3)], dur=0.6)
_mk = P(STAND, l1=(80, 0), l2=(0, 0), a1=(-30, 10), a2=(40, 120), f1=100)
M["Marching high knees"] = Move([_mk, mirror(_mk)], dur=1.1)
_bk = P(STAND, l1=(-8, -168), l2=(2, 0), a1=(-25, 60), a2=(25, 120), f1=-80)
M["Butt kicks"] = Move([P(_bk, up=3), P(mirror(_bk), up=3)], dur=0.6)
M["Squat thrust"] = Move([CROUCH, _pl], dur=1.6)
_sjc = P(F_STAND, l1=(45, -15), l2=(-45, 15), a1=(15, 30), a2=(-15, -30))
M["Star jump"] = Move([_sjc, P(F_STAND, up=14, a1=(140, 140), a2=(-140, -140), l1=(28, 28), l2=(-28, -28), f1=110, f2=-110)],
                      view="front", dur=1.4)
# land on the right leg (knee bending toward the viewer), left leg sweeps behind it,
# arms swing across like a skater; then the mirror image
_sk = dict(hip=(14, 27), t=166, h=172, l1=ik(16, 0, flat=0.35), l2=ik(38, 9, flat=0.9), f2=150,
           a1=(115, 125), a2=(35, 50))
_sk_mid = dict(hip=(0, 31), t=180, l1=ik(4, 2, flat=0.4), l2=ik(-4, 2, flat=0.4), a1=(25, 30), a2=(-25, -30))
M["Speed skaters (step)"] = Move([_sk, _sk_mid, fmirror(_sk), _sk_mid], view="front", dur=2.4,
                                 weights=[1, 1, 1, 1])
M["Squat to overhead reach"] = Move([SQUAT, P(STAND, **ARMS_UP, f1=40, f2=40)], dur=2)
_lt = P(lunge(1), a1=(60, 70), a2=(70, 80), t=176)
M["Lunge with twist"] = Move([P(_st, a1=(40, 110), a2=(38, 108)), _lt, P(_st, a1=(40, 110), a2=(38, 108)),
                              P(lunge(2, hip=(-5, 22), front_x=-1), a1=(60, 70), a2=(70, 80), t=176)], dur=4)
M["Tuck jump"] = Move([P(SQUAT, t=150), P(STAND, t=165, up=16, l1=(140, 15), l2=(135, 12), a1=(80, 70), a2=(75, 65))], dur=1.2)
_ff = P(STAND, t=160, l1=(45, -20), l2=(42, -22), a1=(30, 100), a2=(25, 95))
M["Fast feet"] = Move([P(_ff, l1=(60, -10)), P(_ff, l2=(57, -12))], dur=0.4)
def _inchworm():
    """Stand, fold, walk the hands out one at a time to a plank, walk them back, stand."""
    stand = dict(hip=(-40, 38.5), t=180, a1=(-4, -2), a2=(5, 8), l1=ik(-40, 0), l2=ik(-41, 0))
    fold_hip, fold_t, fold_x = (-44, 36), 40, -18
    pl = plank(29, 24)
    pl_hip, pl_t, pl_x = pl["hip"], pl["t"], 24

    def body(u, h1, h2, lift=None):
        hip = (fold_hip[0] + (pl_hip[0] - fold_hip[0]) * u,
               fold_hip[1] + (pl_hip[1] - fold_hip[1]) * u + 9 * math.sin(math.pi * u))
        ank = 4 * u
        p = dict(hip=hip, t=fold_t + (pl_t - fold_t) * u, curve=4 * (1 - u),
                 l1=ik(-40, ank), l2=ik(-41, ank), f1=90 - 75 * u, f2=90 - 75 * u,
                 a1=ik(h1, 0), a2=ik(h2 - 1, 0))
        p["h"] = p["t"] - 15 * (1 - u)
        if lift:                                  # the moving hand, mid-step, off the floor
            p[lift] = ik((h1 if lift == "a1" else h2) , 5)
        return p

    steps = 6
    xs = [fold_x + (pl_x - fold_x) * i / steps for i in range(steps + 1)]
    out_walk, h = [], [fold_x, fold_x]
    for i in range(1, steps + 1):
        mover = (i - 1) % 2                       # alternate hands
        old = h[mover]
        h[mover] = xs[i]
        u_mid, u_end = (i - 0.5) / steps, i / steps
        mid = list(h)
        mid[mover] = (old + xs[i]) / 2
        out_walk.append(body(u_mid, mid[0], mid[1], lift=("a1", "a2")[mover]))
        out_walk.append(body(u_end, h[0], h[1]))
    out_walk[-1] = P(out_walk[-1], hold=0.6)
    back = [body(0.0, fold_x, fold_x)]
    walk_back = out_walk[-2::-1]                  # same steps in reverse: lift, land, lift...
    poses = [stand, body(0.0, fold_x, fold_x)] + out_walk + walk_back + back
    weights = [2, 2] + [1] * (len(out_walk) + len(walk_back)) + [2]
    return Move(poses, dur=10, weights=weights)


M["Inchworm"] = _inchworm()

# ---- warm-ups
M["Arm circles"] = Move([P(STAND, a1=(0, 0), a2=(4, 4)), P(STAND, a1=(90, 90), a2=(94, 94)),
                         P(STAND, a1=(180, 180), a2=(184, 184)), P(STAND, a1=(-90, -90), a2=(-86, -86))], dur=1.8)
_hc = dict(t=180, **F_HIPS, l1=ik(5, 0), l2=ik(-5, 0))
M["Hip circles"] = Move([P(_hc, hip=(5, 37.5), t=184), P(_hc, hip=(0, 36.5)), P(_hc, hip=(-5, 37.5), t=176),
                         P(_hc, hip=(0, 38.5))], view="front", dur=2.4)
_ls = P(STAND, a1=(55, 75), a2=(50, 72))
M["Leg swings"] = Move([P(_ls, l1=(65, 65), f1=150), P(_ls, l1=(-35, -35), f1=50)], dur=1.4, props=[("wall", 25)])
M["Cat-cow"] = Move([P(FOURS, curve=-4, h=135), P(FOURS, curve=5, h=55)], dur=3.2)
M["March in place"] = Move([P(STAND, l1=(55, -5), a1=(-25, -10), a2=(30, 50), f1=100),
                            P(STAND, l2=(55, -5), a2=(-25, -10), a1=(30, 50), f2=100)], dur=1.2)
_tw = dict(F_STAND, a1=(85, 85), a2=(55, 95))
M["Torso twists"] = Move([_tw, fmirror(_tw)], view="front", dur=1.6)
_wg = dict(hip=(0, 18), t=112, h=120, l1=ik(22, 0), l2=ik(-36, 3), f2=-40, a1=ik(20, 0), a2=ik(19, 0))
M["World's greatest stretch"] = Move([_wg, P(_wg, t=100, h=100, a1=(0, 30)), _wg, P(_wg, t=125, h=150, a2=(180, 180), hold=0.5)],
                                     dur=5)
M["Bodyweight good morning"] = M["Good morning"]
M["Shoulder rolls"] = Move([P(STAND, so=(2, 0)), P(STAND, so=(0, 5)), P(STAND, so=(-3.5, 2)), P(STAND, so=(0, -2))],
                           dur=2)
M["Slow air squats"] = Move([STAND, SQUAT], dur=4)
# close-up: forearms out in front, hands circling at the wrist
_wr = P(STAND, t=180)
M["Wrist rolls"] = Move(
    [P(_wr, a1=(28, 90), a2=(26, 88), w1=150, w2=148), P(_wr, a1=(28, 97), a2=(26, 95), w1=90, w2=88),
     P(_wr, a1=(28, 90), a2=(26, 88), w1=30, w2=28), P(_wr, a1=(28, 83), a2=(26, 81), w1=90, w2=88)],
    dur=1.6, hands=True, focus=("hd", "n", "p", "e1", "w1", "hn1", "e2", "w2", "hn2"))
M["Down-dog pedal"] = Move([P(DOG, l1=ik(-17, 9), f1=45), P(DOG, l2=ik(-18, 9), f2=45)], dur=1.6)

# ---- cool-downs
M["Child's pose"] = breathe(dict(hip=(0, 10), t=72, h=80, curve=1, a1=(88, 90), a2=(87, 89),
                                 l1=(62, -96), l2=(61, -97), f1=-95, f2=-95), dur=4, dc=1.2)
M["Standing hamstring stretch"] = breathe(dict(hip=(-3, 37), t=40, h=25, curve=4, a1=(5, 5), a2=(3, 3),
                                               l1=ik(1, 0), l2=ik(0, 0)), dur=4, dc=1)
M["Standing quad stretch"] = breathe(dict(hip=(0, 38.5), t=180, a1=ikp("a1", 0, 1), a2=(75, 85),
                                          l1=(-4, -168), l2=ik(0, 0), f1=-80), dc=0.6, props=[("wall", 28)])
M["Figure-4 stretch"] = breathe(P(SUPINE, h=-105, l2=(165, 95), l1=ikp("k2", 3, 3), a1=ikp("k2", -4, 0), a2=ikp("k2", -5, -1)),
                                dur=4, dc=0.8)
M["Wall chest stretch"] = breathe(P(STAND, a1=(-95, -100), a2=(5, 8)), dt=-4, dc=0, props=[("wall", -30)])
M["Cobra"] = breathe(P(PRONE, t=132, h=145, curve=-3, a1=ik(26, 0), a2=ik(25, 0)), dt=4, dc=-1)
M["Cross-body shoulder stretch"] = breathe(dict(F_STAND, a1=(-80, -90), a2=ikp("e1", 1, -1)), view="front", dc=0)
_kh = dict(hip=(0, 21), t=180, a1=ikp("k1", -2, 2), a2=ikp("k1", -3, 1), l1=ik(20, 0), l2=ik(-18, 1.5), f2=-95)
M["Kneeling hip flexor stretch"] = Move([_kh, P(_kh, hip=(4, 20), t=176)], dur=4)
M["Lying spinal twist"] = breathe(dict(t=180, a1=(90, 90), a2=(-90, -90), l1=(45, -40), l2=(50, -30)), view="top", dc=0)
M["Overhead triceps stretch"] = breathe(dict(F_STAND, a1=(172, 8), a2=ikp("e1", -1, 0)), view="front", dc=0)
M["Deep belly breathing"] = Move([P(SUPINE, **KNEES_UP), P(SUPINE, **KNEES_UP, curve=-2.5)], dur=5, weights=[4, 6])
