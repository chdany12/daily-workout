"""Stick-figure animations, rendered as small looping inline SVGs.

A move is a short list of key poses. The renderer blends between them and writes
SMIL <animate> tags, so the page needs no JavaScript or image files, and the
figure takes its colours from the page (dark mode included).

Coordinates: the floor is y = 0, up is +y, the figure faces +x.
Angles (degrees) give the direction of a body segment, measured from straight
down: 0 = down, 90 = forward (+x), 180 = up, -90 = backward.

A pose is a dict:
  t        torso direction, pelvis -> neck (180 = upright)
  h        head direction, neck -> head (defaults to t)
  curve    spine bend; positive rounds the back, negative arches it
  a1 a2    arms  (near, far): (upper, lower) angles, or ik(x, y) / ik("point")
  l1 l2    legs  (near, far): (thigh, shin) angles, or ik(...)
  f1 f2    foot angles (default: at right angles to the shin)
  hip      (x, y) pelvis position. Leave it out to stand the figure on the
           floor automatically (its lowest point touches y = up).
  x, up    with automatic standing: pelvis x, and height off the floor (jumps)
  w1 w2    hand angles (only drawn for moves with hands=True)
  hold     seconds to pause on this pose
ik targets are world points, or the name of a point already placed
("k1" knee, "a2" ankle, "e1" elbow, "n" neck...) plus an optional offset.
"""

import math
from dataclasses import dataclass, field
from html import escape

SEG = dict(torso=30, neck=9, head=6.5, ua=15, fa=14, th=20, sh=19, ft=5, hand=5)
SHOULDER_W, HIP_W = 7, 4          # half widths, used in front/top views


@dataclass(frozen=True)
class IK:
    x: object                     # number, or a point name
    y: float = 0.0
    bend: int = 0                 # +1 / -1 picks which way the joint folds; 0 = limb default
    dx: float = 0.0
    dy: float = 0.0
    flat: float = 1.0             # < 1 pulls the knee/elbow toward the straight line, as if it
                                  # bent toward the viewer (front views: knees going forward)


def ik(x, y=0.0, bend=0, flat=1.0):
    """Pin a hand or foot to the world point (x, y)."""
    return IK(x, y, bend, flat=flat)


def ikp(name, dx=0.0, dy=0.0, bend=0):
    """Pin a hand or foot to a named point on the body, e.g. ikp("k2") = far knee."""
    return IK(name, 0.0, bend, dx, dy)


@dataclass
class Move:
    poses: list
    view: str = "side"            # side | front | top (seen from above, on a mat)
    dur: float = 2.0              # seconds for one full loop
    weights: list = None          # relative length of each transition
    props: list = field(default_factory=list)
    hands: bool = False           # draw hands (angles w1 / w2, default: in line with the forearm)
    focus: tuple = None           # frame only these points (a close-up), e.g. the upper body


# ---------------------------------------------------------------- geometry

def _d(a):
    r = math.radians(a)
    return math.sin(r), -math.cos(r)


def _ang(vx, vy):
    return math.degrees(math.atan2(vx, -vy))


def _add(p, a, length):
    dx, dy = _d(a)
    return p[0] + dx * length, p[1] + dy * length


def _lerp_ang(a, b, u):
    diff = (b - a + 180) % 360 - 180
    return a + diff * u


def _solve(root, target, l1, l2, bend, flat=1.0):
    """Two-bone reach. Returns (upper, lower) angles, plus drawn lengths when flattened."""
    dx, dy = target[0] - root[0], target[1] - root[1]
    dist = max(abs(l1 - l2) + 1e-3, min(l1 + l2 - 1e-3, math.hypot(dx, dy)))
    base = _ang(dx, dy)
    cos_a = (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist)
    upper = base + bend * math.degrees(math.acos(max(-1.0, min(1.0, cos_a))))
    joint = _add(root, upper, l1)
    if flat >= 1:
        return upper, _ang(target[0] - joint[0], target[1] - joint[1])
    end = _add(root, base, dist)                  # the reachable point on the line to the target
    ux, uy = _d(base)
    along = (joint[0] - root[0]) * ux + (joint[1] - root[1]) * uy
    on_line = (root[0] + ux * along, root[1] + uy * along)
    j = (on_line[0] + (joint[0] - on_line[0]) * flat, on_line[1] + (joint[1] - on_line[1]) * flat)
    return (_ang(j[0] - root[0], j[1] - root[1]), _ang(end[0] - j[0], end[1] - j[1]),
            math.hypot(j[0] - root[0], j[1] - root[1]), math.hypot(end[0] - j[0], end[1] - j[1]))


def _limb(spec, upper_len, lower_len):
    """(upper, lower[, upper_len, lower_len]) -> angles and lengths."""
    if len(spec) == 4:
        return spec
    return spec[0], spec[1], upper_len, lower_len


def _skeleton(p, view, hip):
    """Joint positions for a pose whose limbs are already plain angles."""
    wide = view != "side"
    pts = {"p": hip}
    n = _add(hip, p["t"], SEG["torso"])
    pts["n"] = n
    pts["hd"] = _add(n, p.get("h", p["t"]), SEG["neck"])
    side = _d(p["t"] + 90)                       # across the body, for front views
    for i, s in ((1, 1), (2, -1)):
        sh = (n[0] - side[0] * s * SHOULDER_W, n[1] - side[1] * s * SHOULDER_W) if wide else n
        sh = (sh[0] - _d(p["t"])[0] * 2.5, sh[1] - _d(p["t"])[1] * 2.5) if wide else sh
        hp = (hip[0] - side[0] * s * HIP_W, hip[1] - side[1] * s * HIP_W) if wide else hip
        so = p.get("so", (0, 0))                 # shoulder shrug / roll offset
        sh = (sh[0] + so[0], sh[1] + so[1])
        pts[f"s{i}"], pts[f"h{i}"] = sh, hp
        u, l, lu, ll = _limb(p[f"a{i}"], SEG["ua"], SEG["fa"])
        pts[f"e{i}"] = _add(sh, u, lu)
        pts[f"w{i}"] = _add(pts[f"e{i}"], l, ll)
        pts[f"hn{i}"] = _add(pts[f"w{i}"], p.get(f"w{i}", l), SEG["hand"])
        u, l, lu, ll = _limb(p[f"l{i}"], SEG["th"], SEG["sh"])
        pts[f"k{i}"] = _add(hp, u, lu)
        pts[f"a{i}"] = _add(pts[f"k{i}"], l, ll)
        toe = l + 90 if (i == 1 or not wide) else l - 90   # front views: both feet turn out
        pts[f"t{i}"] = _add(pts[f"a{i}"], p.get(f"f{i}", toe), SEG["ft"])
    return pts


def _place(p, view, hip):
    """Resolve ik limbs to angles (legs first, so arms can reach for them), then build."""
    q = dict(p)
    for i in (1, 2):
        q.setdefault(f"a{i}", (0, 0))
        q.setdefault(f"l{i}", (0, 0))
    for group, defaults in (("l", (1, (SEG["th"], SEG["sh"]))), ("a", (-1, (SEG["ua"], SEG["fa"])))):
        bend_default, (l1, l2) = defaults
        for i in (1, 2):
            spec = p.get(f"{group}{i}")
            if not isinstance(spec, IK):
                continue
            pts = _skeleton({**q, **{f"{g}{j}": (q[f"{g}{j}"] if not isinstance(q[f"{g}{j}"], IK) else (0, 0))
                                      for g in "al" for j in (1, 2)}}, view, hip)
            if isinstance(spec.x, str):
                base = pts[spec.x]
                target = (base[0] + spec.dx, base[1] + spec.dy)
            else:
                target = (spec.x, spec.y)
            root = pts[("h" if group == "l" else "s") + str(i)]
            if view != "side":                    # front views: joints fold outward, mirrored
                bend_default = 1 if i == 1 else -1
            q[f"{group}{i}"] = _solve(root, target, l1, l2, spec.bend or bend_default, spec.flat)
    return q, _skeleton(q, view, hip)


def _lowest(pts):
    body = (y for k, (_, y) in pts.items() if k != "hd" and not k.startswith("hn"))
    return min(min(body), pts["hd"][1] - SEG["head"])


def _frame(p, view):
    """Pose -> (resolved angle pose, joint positions)."""
    if "hip" in p:
        return _place(p, view, tuple(p["hip"]))
    q, pts = _place(p, view, (p.get("x", 0.0), 0.0))
    if view == "top":
        return q, pts
    shift = p.get("up", 0.0) - _lowest(pts)
    q2, pts2 = _place(p, view, (p.get("x", 0.0), shift))
    return q2, pts2


def _blend(a, b, u, view):
    """Pose between key poses a and b. Pinned (ik) limbs stay pinned while blending."""
    qa, _ = _frame(a, view)
    qb, _ = _frame(b, view)
    out = {}
    for k in ("t", "h"):
        out[k] = _lerp_ang(qa.get(k, qa["t"]), qb.get(k, qb["t"]), u)
    out["curve"] = a.get("curve", 0) + (b.get("curve", 0) - a.get("curve", 0)) * u
    for k in ("a1", "a2", "l1", "l2"):
        sa, sb = a.get(k), b.get(k)
        if isinstance(sa, IK) and isinstance(sb, IK) and isinstance(sa.x, (int, float)) \
                and isinstance(sb.x, (int, float)) and "hip" in a and "hip" in b:
            out[k] = IK(sa.x + (sb.x - sa.x) * u, sa.y + (sb.y - sa.y) * u, sa.bend or sb.bend,
                        flat=sa.flat + (sb.flat - sa.flat) * u)
        elif isinstance(sa, IK) and isinstance(sb, IK) and sa.x == sb.x and isinstance(sa.x, str):
            out[k] = IK(sa.x, 0.0, sa.bend or sb.bend, sa.dx + (sb.dx - sa.dx) * u, sa.dy + (sb.dy - sa.dy) * u,
                        flat=sa.flat + (sb.flat - sa.flat) * u)
        else:
            lens = (SEG["ua"], SEG["fa"]) if k[0] == "a" else (SEG["th"], SEG["sh"])
            la, lb = _limb(qa[k], *lens), _limb(qb[k], *lens)
            out[k] = (_lerp_ang(la[0], lb[0], u), _lerp_ang(la[1], lb[1], u),
                      la[2] + (lb[2] - la[2]) * u, la[3] + (lb[3] - la[3]) * u)
    for k in ("w1", "w2"):
        arm = "a" + k[1]
        if k in a or k in b:
            out[k] = _lerp_ang(a.get(k, qa[arm][1]), b.get(k, qb[arm][1]), u)
    for k in ("f1", "f2"):
        turn = -90 if (k == "f2" and view != "side") else 90
        fa = a.get(k, qa[k.replace("f", "l")][1] + turn)
        fb = b.get(k, qb[k.replace("f", "l")][1] + turn)
        out[k] = _lerp_ang(fa, fb, u)
    sa, sb = a.get("so", (0, 0)), b.get("so", (0, 0))
    out["so"] = (sa[0] + (sb[0] - sa[0]) * u, sa[1] + (sb[1] - sa[1]) * u)
    if "hip" in a and "hip" in b:
        out["hip"] = tuple(a["hip"][j] + (b["hip"][j] - a["hip"][j]) * u for j in (0, 1))
    elif "hip" in a or "hip" in b:
        _, pa = _frame(a, view)
        _, pb = _frame(b, view)
        out["hip"] = tuple(pa["p"][j] + (pb["p"][j] - pa["p"][j]) * u for j in (0, 1))
    else:
        out["x"] = a.get("x", 0) + (b.get("x", 0) - a.get("x", 0)) * u
        out["up"] = a.get("up", 0) + (b.get("up", 0) - a.get("up", 0)) * u
    return _frame(out, view)


# ---------------------------------------------------------------- rendering

def _frames(m: Move, steps=8):
    n = len(m.poses)
    weights = m.weights or [1] * n
    holds = [p.get("hold", 0) for p in m.poses]
    total_move = sum(weights)
    move_time = max(0.2, m.dur - sum(holds))
    times, frames, t = [], [], 0.0
    for i in range(n):
        a, b = m.poses[i], m.poses[(i + 1) % n]
        if holds[i]:
            q, pts = _frame(a, m.view)
            times.append(t); frames.append((q, pts)); t += holds[i]
        seg = move_time * weights[i] / total_move
        for s in range(steps):
            u = (1 - math.cos(math.pi * s / steps)) / 2
            times.append(t + seg * s / steps)
            frames.append(_blend(a, b, u, m.view) if n > 1 else _frame(a, m.view))
        t += seg
    times.append(t)
    frames.append(frames[0])
    return times, frames


def _f(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def _pt(p):
    return f"{_f(p[0])},{_f(-p[1])}"


def _spine(q, pts):
    hip, n = pts["p"], pts["n"]
    c = q.get("curve", 0) * 2                     # control point sits twice as far as the bulge
    nx, ny = _d(q["t"] + 90)                      # points toward the figure's back
    mid = ((hip[0] + n[0]) / 2 + nx * c, (hip[1] + n[1]) / 2 + ny * c)
    return f"M{_pt(hip)}Q{_pt(mid)} {_pt(n)}L{_pt(_toward(n, pts['hd'], SEG['neck'] - SEG['head'] + 1))}"


def _toward(a, b, length):
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy) or 1
    return a[0] + dx / d * length, a[1] + dy / d * length


def _paths(q, pts, view, hands=False):
    h1 = f" {_pt(pts['hn1'])}" if hands else ""
    h2 = f" {_pt(pts['hn2'])}" if hands else ""
    out = {
        "arm2": f"M{_pt(pts['s2'])}L{_pt(pts['e2'])} {_pt(pts['w2'])}{h2}",
        "leg2": f"M{_pt(pts['h2'])}L{_pt(pts['k2'])} {_pt(pts['a2'])} {_pt(pts['t2'])}",
        "body": _spine(q, pts),
        "leg1": f"M{_pt(pts['h1'])}L{_pt(pts['k1'])} {_pt(pts['a1'])} {_pt(pts['t1'])}",
        "arm1": f"M{_pt(pts['s1'])}L{_pt(pts['e1'])} {_pt(pts['w1'])}{h1}",
    }
    if view != "side":
        out["body"] += f"M{_pt(pts['s1'])}L{_pt(pts['s2'])}M{_pt(pts['h1'])}L{_pt(pts['h2'])}"
    return out


def _prop_shapes(props):
    """Static furniture. Returns (svg, points for the view box)."""
    svg, pts = [], []
    for pr in props:
        kind, x = pr[0], pr[1]
        if kind in ("chair", "couch"):
            w = pr[2] if len(pr) > 2 else 22
            back = pr[3] if len(pr) > 3 else None
            h = 19
            d = f"M{_f(x)},0V{-h}H{_f(x + w)}V0"
            pts += [(x, 0), (x + w, h)]
            if back == "left":
                d += f"M{_f(x)},{-h}V{-h - 20}"; pts.append((x, h + 20))
            elif back == "right":
                d += f"M{_f(x + w)},{-h}V{-h - 20}"; pts.append((x + w, h + 20))
            svg.append(f'<path class="pr" d="{d}"/>')
        elif kind == "wall":
            svg.append(f'<path class="pr" d="M{_f(x)},2V-92"/>')
            pts += [(x, 0), (x, 30)]
    return "".join(svg), pts


def render(m: Move, label="") -> str:
    times, frames = _frames(m)
    total = times[-1]
    key_times = ";".join(f"{t / total:.3f}".rstrip("0").rstrip(".") or "0" for t in times)
    paths = [_paths(q, pts, m.view, m.hands) for q, pts in frames]
    heads = [pts["hd"] for _, pts in frames]

    props_svg, prop_pts = _prop_shapes(m.props)
    xs, ys = [], []
    for _, pts in frames:
        for k, (x, y) in pts.items():
            if k.startswith("hn") and not m.hands:
                continue
            if m.focus and k not in m.focus:
                continue
            r = SEG["head"] if k == "hd" else 2
            xs += [x - r, x + r]; ys += [y - r, y + r]
    if not m.focus:
        for x, y in prop_pts:
            xs.append(x); ys.append(y)
    pad = 5
    x0, x1 = min(xs) - pad, max(xs) + pad
    y_top = max(ys) + pad
    y_bot = min(ys) - pad if (m.view == "top" or m.focus) else -4
    w, h = x1 - x0, y_top - y_bot
    ratio = 4 / 3                                 # every figure gets the same box shape
    if w / h < ratio:
        extra = h * ratio - w; x0 -= extra / 2; w = h * ratio
    else:
        y_top += w / ratio - h; h = w / ratio
    vb = f"{_f(x0)} {_f(-y_top)} {_f(w)} {_f(h)}"

    dur = f"{_f(total)}s"
    anim = 'dur="{d}" keyTimes="{k}" repeatCount="indefinite" calcMode="linear"'.format(d=dur, k=key_times)
    els = []
    if m.view == "top":
        els.append(f'<rect class="mat" x="{_f(x0 + 4)}" y="{_f(-y_top + 3)}" width="{_f(w - 8)}" '
                   f'height="{_f(h - 6)}" rx="5"/>')
    else:
        els.append(f'<path class="fl" d="M{_f(x0)},1.5H{_f(x0 + w)}"/>')
    els.append(props_svg)
    far = "n" if m.view != "side" else "f"
    for key, cls in (("arm2", far), ("leg2", far), ("body", "n")):
        vals = ";".join(p[key] for p in paths)
        els.append(f'<path class="{cls}" d="{paths[0][key]}"><animate attributeName="d" values="{vals}" {anim}/></path>')
    hx = ";".join(_f(p[0]) for p in heads)
    hy = ";".join(_f(-p[1]) for p in heads)
    els.append(f'<circle class="hd" cx="{_f(heads[0][0])}" cy="{_f(-heads[0][1])}" r="{SEG["head"]}">'
               f'<animate attributeName="cx" values="{hx}" {anim}/><animate attributeName="cy" values="{hy}" {anim}/></circle>')
    for key in ("leg1", "arm1"):
        vals = ";".join(p[key] for p in paths)
        els.append(f'<path class="n" d="{paths[0][key]}"><animate attributeName="d" values="{vals}" {anim}/></path>')
    title = f"<title>{escape(label)} animation</title>" if label else ""
    return (f'<svg class="fig" viewBox="{vb}" xmlns="http://www.w3.org/2000/svg" role="img">'
            f'{title}{"".join(els)}</svg>')
