"""Renders workouts as a phone-first static website (one page per day + archive)."""

import json
from html import escape
from urllib.parse import quote_plus, urlencode

from functools import lru_cache

from .anim import render
from .anim_moves import M as MOVES
from .engine import Row, Workout


@lru_cache(maxsize=None)
def figure(name: str) -> str:
    """Looping stick-figure SVG for a move, or "" when the move has none."""
    return render(MOVES[name], name) if name in MOVES else ""

DEMO_URL = "https://www.youtube.com/results?search_query="
FOCUS_LABEL = {"upper": "Upper body", "lower": "Lower body", "core": "Core", "full": "Full body"}

CSS = """
:root{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1f;--muted:#6b6b70;--line:#e3e1dc;--accent:#e4572e;
--warm:#ffe9a8;--main:#ffd2c7;--cool:#cdebd3;--twist:#efe4fb;--twist-ink:#5b2a86;--new:#dff1fb;--ok:#2e7d32}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--card:#1e1e22;--ink:#f2f2f4;--muted:#a0a0a8;
--line:#33333a;--accent:#ff7a52;--warm:#4a3d12;--main:#4d2219;--cool:#1d3b24;--twist:#2e2140;
--twist-ink:#d9c2f5;--new:#173444;--ok:#7fd88a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:17px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:640px;margin:0 auto;padding:20px 16px 64px}
a{color:var(--accent)}h1{font-size:1.9rem;line-height:1.15;margin:.2em 0 .3em}
.date{color:var(--muted);font-size:.9rem;text-transform:uppercase;letter-spacing:.06em}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 16px}
.chip{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:3px 11px;font-size:.88rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin:12px 0}
.twist{background:var(--twist);color:var(--twist-ink);border:0;font-weight:600}
.progress{position:sticky;top:0;z-index:5;background:var(--bg);padding:10px 0}
.bar{height:10px;background:var(--line);border-radius:99px;overflow:hidden}
.bar>div{height:100%;width:0;background:var(--accent);transition:width .3s}
.progress small{color:var(--muted)}
h2{font-size:1.05rem;margin:22px 0 6px;padding:6px 12px;border-radius:10px}
h2.warm{background:var(--warm)}h2.main{background:var(--main)}h2.cool{background:var(--cool)}
h3{font-size:.95rem;color:var(--muted);margin:14px 4px 4px}
.move{display:flex;gap:12px;align-items:flex-start;background:var(--card);border:1px solid var(--line);
border-radius:12px;padding:12px;margin:6px 0;cursor:pointer}
.move input{width:26px;height:26px;flex:none;margin:2px 0 0;accent-color:var(--accent)}
.move.done{opacity:.5}.move.done b{text-decoration:line-through}
.move .body{flex:1;min-width:0}.move b{display:block}.do{font-weight:600;color:var(--accent)}
.cue{color:var(--muted);font-size:.92rem}.new{font-size:.72rem;background:var(--new);border-radius:6px;
padding:1px 6px;margin-left:6px;vertical-align:2px;font-weight:600}
.watch{display:inline-block;margin-top:4px;font-size:.85rem;text-decoration:none;white-space:nowrap}
.fig{flex:none;align-self:center;width:104px;height:78px;border-radius:10px;background:var(--bg);cursor:zoom-in}
.fig path,.fig circle{vector-effect:non-scaling-stroke}
.fig path{fill:none;stroke-width:2.8px;stroke-linecap:round;stroke-linejoin:round}
.fig .n{stroke:var(--ink)}.fig .f{stroke:var(--muted)}.fig .hd{fill:var(--bg);stroke:var(--ink);stroke-width:2.6px}
.fig .fl{stroke:var(--line);stroke-width:2px}.fig .pr{stroke:var(--accent);opacity:.6;stroke-width:2px}
.move.big .fig path{stroke-width:5px}.move.big .fig .hd{stroke-width:4.5px}.move.big .fig .fl,.move.big .fig .pr{stroke-width:3px}
.fig .mat{fill:var(--line);opacity:.7}
.move.big{flex-wrap:wrap}.move.big .fig{order:5;width:100%;height:auto;aspect-ratio:4/3;max-height:300px;cursor:zoom-out}
.score{display:flex;gap:10px;align-items:center;padding:8px 12px;color:var(--muted)}
.btn{display:inline-block;background:var(--accent);color:#fff;border:0;border-radius:12px;padding:12px 18px;
font:inherit;font-weight:600;text-decoration:none;cursor:pointer}
.btn.ghost{background:transparent;color:var(--accent);border:1px solid var(--accent)}
.row{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}
#celebrate{display:none;text-align:center;font-size:1.2rem;font-weight:700}
form label{display:block;font-weight:600;margin:12px 0 6px}
.rate{display:flex;gap:6px}.rate label{margin:0;flex:1}
.rate input{position:absolute;opacity:0}.rate span{display:block;text-align:center;font-size:1.6rem;padding:6px 0;
border:1px solid var(--line);border-radius:10px;cursor:pointer}.rate input:checked+span{border-color:var(--accent);
background:var(--twist)}.rate input:focus-visible+span{outline:2px solid var(--accent)}
select,textarea,input[type=text]{width:100%;font:inherit;color:var(--ink);background:var(--bg);
border:1px solid var(--line);border-radius:10px;padding:10px}
textarea{min-height:90px;resize:vertical}#fb-status{margin-top:10px;font-weight:600}
footer{color:var(--muted);font-size:.85rem;text-align:center;margin-top:30px}
ul.days{list-style:none;padding:0}ul.days li{margin:6px 0}
ul.days a{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;
text-decoration:none;color:var(--ink)}ul.days small{color:var(--muted);display:block}
"""

JS = """
const KEY='done-'+document.body.dataset.date;
let done={};try{done=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
const boxes=[...document.querySelectorAll('.move input')];
function paint(){let n=0;boxes.forEach(b=>{b.closest('.move').classList.toggle('done',b.checked);if(b.checked)n++});
document.querySelector('.bar>div').style.width=(boxes.length?100*n/boxes.length:0)+'%';
document.getElementById('count').textContent=n+' / '+boxes.length+' done';
document.getElementById('celebrate').style.display=(n&&n===boxes.length)?'block':'none'}
boxes.forEach(b=>{b.checked=!!done[b.id];b.addEventListener('change',()=>{done[b.id]=b.checked;
try{localStorage.setItem(KEY,JSON.stringify(done))}catch(e){}paint()})});
document.querySelectorAll('.watch').forEach(a=>a.addEventListener('click',e=>e.stopPropagation()));
const still=matchMedia('(prefers-reduced-motion: reduce)').matches;
document.querySelectorAll('.fig').forEach(f=>{if(still&&f.pauseAnimations)f.pauseAnimations();
f.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();
const big=f.closest('.move').classList.toggle('big');if(still&&f.pauseAnimations)big?f.unpauseAnimations():f.pauseAnimations()})});
paint();
const form=document.getElementById('feedback');
if(form){const cfg=JSON.parse(document.getElementById('fb-config').textContent);
form.addEventListener('submit',async e=>{e.preventDefault();const st=document.getElementById('fb-status');
const d=Object.fromEntries(new FormData(form).entries());
d.workout=cfg.workout;d.date=cfg.date;d.ticked=document.getElementById('count').textContent;
const text=`Workout: ${d.workout} (${d.date})\\nRating: ${d.rating||'-'}/5\\nFinished: ${d.finished||'-'}\\n`+
`Ticked: ${d.ticked}\\nFrom: ${d.name||'anon'}\\n\\n${d.comment||''}`;
if(!cfg.url){if(!cfg.repo){st.textContent='Feedback is not set up yet.';return}
location.href=`https://github.com/${cfg.repo}/issues/new?`+new URLSearchParams({title:`Feedback: ${d.workout} (${d.date})`,body:text});return}
st.textContent='Sending…';
try{const r=await fetch(cfg.url,{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},
body:JSON.stringify({...cfg.extra,subject:`Workout feedback: ${d.workout}`,message:text,...d})});
if(!r.ok)throw new Error(r.status);form.reset();st.textContent='Thanks! 💪 Got it.'}
catch(err){st.textContent='Could not send (are you offline?). Try again in a bit.'}})}
"""


def _page(title, body, date="", extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎲</text></svg>">
<style>{CSS}</style>{extra_head}</head>
<body data-date="{escape(date)}"><main>
{body}
</main></body></html>
"""


def _rows(rows: list[Row], prefix: str) -> str:
    out = []
    for i, r in enumerate(rows):
        if r.group:
            out.append(f"<h3>{escape(r.move)}</h3>")
        elif not r.cue and r.do == "____":  # score line
            out.append(f'<div class="score">✍️ {escape(r.move)}: ________</div>')
        else:
            new = '<span class="new">NEW</span>' if r.new else ""
            name = r.move.split(" = ")[-1]
            watch = (f'<a class="watch" target="_blank" rel="noopener" '
                     f'href="{DEMO_URL}{quote_plus(name + " exercise how to")}">▶ Video</a>') if r.cue else ""
            cue = f'<div class="cue">{escape(r.cue)}</div>' if r.cue else ""
            out.append(
                f'<label class="move"><input type="checkbox" id="{prefix}{i}">'
                f'<span class="body"><b>{escape(r.move)}{new}</b>'
                f'<span class="do">{escape(r.do)}</span>{cue}{watch}</span>{figure(name)}</label>')
    return "\n".join(out)


def workout_page(w: Workout, day: str, xlsx_name: str, site: dict, is_today: bool,
                 home="./", archive="archive.html") -> str:
    fb_cfg = {"url": site.get("feedback_url", ""), "extra": site.get("feedback_extra", {}),
              "repo": site.get("github_repo", ""), "workout": w.name, "date": day}
    label = "Today's workout" if is_today else "Workout from"
    body = f"""
<div class="date">{label} · {escape(day)}</div>
<h1>{escape(w.name)}</h1>
<div class="chips"><span class="chip">{FOCUS_LABEL[w.focus]}</span><span class="chip">⏱ {w.minutes} min</span>
<span class="chip">{escape(w.format_name)}</span><span class="chip">Level {w.level}</span></div>
<div class="card"><b>How it works</b><br>{escape(w.format_rules)}</div>
<div class="card twist">🎲 {escape(w.twist)}</div>
<div class="progress"><div class="bar"><div></div></div><small id="count"></small></div>
<h2 class="warm">Warm-up · 3 min</h2>
{_rows(w.warmup, "w")}
<h2 class="main">Main event</h2>
{_rows(w.main, "m")}
<h2 class="cool">Cool-down · 2 min</h2>
{_rows(w.cooldown, "c")}
<p id="celebrate">🎉 All done! That's a win. Tell me how it went ↓</p>
<div class="row"><a class="btn ghost" href="{escape(xlsx_name)}" download>⬇ Excel version</a>
<a class="btn ghost" href="{escape(archive)}">📅 Past workouts</a>
{'' if is_today else f'<a class="btn ghost" href="{escape(home)}">→ Today</a>'}</div>

<form id="feedback" class="card">
<b>How did it go?</b> <span class="cue">A new workout drops every morning. Your feedback shapes what comes next.</span>
<label>Fun?</label>
<div class="rate">{''.join(f'<label><input type="radio" name="rating" value="{n}"><span aria-label="{n} of 5">{e}</span></label>'
                            for n, e in enumerate(["😩", "😕", "😐", "🙂", "🤩"], 1))}</div>
<label for="fb-fin">Did you finish?</label>
<select id="fb-fin" name="finished"><option value="">Pick one</option><option>Yes, all of it</option>
<option>Partly</option><option>Didn't start</option></select>
<label for="fb-comment">Anything else? Too hard, too easy, boring bits, best bits</label>
<textarea id="fb-comment" name="comment" placeholder="e.g. the deck of cards was fun, wall sits were awful"></textarea>
<label for="fb-name">Your name (optional)</label>
<input id="fb-name" type="text" name="name" autocomplete="given-name">
<input type="checkbox" name="botcheck" style="display:none" tabindex="-1" autocomplete="off">
<div class="row"><button class="btn" type="submit">Send feedback</button></div>
<div id="fb-status" role="status"></div>
</form>
<script type="application/json" id="fb-config">{json.dumps(fb_cfg).replace("</", "<\\/")}</script>
<footer>New workout every day · never the same twice in a row 🎲</footer>
<script>{JS}</script>
"""
    return _page(f"{w.name} · Daily Workout", body, date=day)


def archive_page(days: list[tuple[str, Workout]], home="./", prefix="days/") -> str:
    items = "\n".join(
        f'<li><a href="{prefix}{d}.html"><b>{escape(w.name)}</b>'
        f'<small>{d} · {FOCUS_LABEL[w.focus]} · {escape(w.format_name)} · {w.minutes} min</small></a></li>'
        for d, w in days)
    body = f"""<div class="date">Archive</div><h1>Past workouts</h1>
<p><a href="{home}">→ Back to today</a></p><ul class="days">{items}</ul>"""
    return _page("Past workouts · Daily Workout", body)
