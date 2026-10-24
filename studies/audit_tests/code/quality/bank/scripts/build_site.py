#!/usr/bin/env python3
"""Generate the BugBank website into site/ from the entries.

Usage:  python3 scripts/build_site.py   (from the repo root; needs pyyaml)

Blueprint design: dark slate, monospace accents, and a constellation view of
the collection (entries as nodes, `related` links as edges). Produces a single
self-contained site/index.html (entry data embedded as JSON), a deposit form
site/deposit.html (client-side validation mirroring scripts/build_db.py), and
site/fly.svg. Works from file:// and any static host; math is rendered with
MathJax and Markdown with marked, both loaded from CDNs.
"""
import json
import re
import sys
from pathlib import Path

import yaml

try:
    from . import active_release, site_assets
except ImportError:  # direct script invocation
    import active_release, site_assets

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site"

FLY_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" role="img" aria-label="BugBank fly logo">
<g stroke="#2c3f52" stroke-width=".8" fill="none" opacity=".9">
<circle cx="60" cy="60" r="52" stroke-dasharray="3 4"/>
<line x1="60" y1="4" x2="60" y2="116"/><line x1="4" y1="60" x2="116" y2="60"/>
</g>
<g stroke="#8fb8e8" stroke-width="2" fill="none" stroke-linecap="round">
<ellipse cx="38" cy="42" rx="24" ry="11" transform="rotate(-30 38 42)"/>
<ellipse cx="82" cy="42" rx="24" ry="11" transform="rotate(30 82 42)"/>
<ellipse cx="60" cy="73" rx="19" ry="17"/>
<circle cx="60" cy="46" r="13"/>
<path d="M53 34 Q48 26 43 23"/><path d="M67 34 Q72 26 77 23"/>
<path d="M46 84 Q37 93 31 96"/><path d="M60 90 L60 101"/><path d="M74 84 Q83 93 89 96"/>
<path d="M44 68 Q60 75 76 68"/><path d="M46 78 Q60 85 74 78"/>
</g>
<circle cx="55" cy="44" r="2.6" fill="#8fb8e8"/><circle cx="65" cy="44" r="2.6" fill="#8fb8e8"/>
</svg>"""


def parse_entry(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.DOTALL)
    if not m:
        sys.exit(f"bad entry (no frontmatter): {path}")
    meta = yaml.safe_load(m.group(1))
    src = meta.get("source") or {}
    return {
        "id": meta["id"],
        "title": meta["title"],
        "type": meta["type"],
        "domain": meta["domain"],
        "subdomain": meta.get("subdomain", ""),
        "tags": meta.get("tags") or [],
        "refutes": (meta.get("refutes") or "").strip(),
        "statement": (meta.get("statement") or "").strip(),
        "true_theorem": (meta.get("true_theorem") or "").strip(),
        "hypothesis_violated": (meta.get("hypothesis_violated") or "").strip(),
        "difficulty": meta.get("difficulty", 0),
        "status": meta.get("status", ""),
        "source_book": src.get("book") or "",
        "source_chapter": str(src.get("chapter") or ""),
        "formalized": meta.get("formalized") or [],
        "related": meta.get("related") or [],
        "body": m.group(2).strip(),
        "source_correspondence_status": meta.get("source_correspondence_status", ""),
        "formal_status": meta.get("formal_status", ""),
        "human_review_status": meta.get("human_review_status", ""),
    }


CSS = """
:root{--page:#0d0d0d;--surface:#1a1a19;--ink:#ffffff;--muted:#c3c2b7;--faint:#898781;
--rule:#2c2c2a;--accent:#3987e5;--accent-soft:#8fb8e8;--edge:#383835;}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);font-family:system-ui,-apple-system,'Segoe UI',sans-serif;font-size:16px;line-height:1.55}
header{max-width:960px;margin:0 auto;padding:38px 24px 10px;display:flex;gap:20px;align-items:center}
header svg{flex:none}
h1{font-family:ui-monospace,'SF Mono',Menlo,monospace;font-size:34px;margin:0;font-weight:600;letter-spacing:1px}
h1 .cursor{color:var(--accent)}
.tagline{color:var(--muted);margin:2px 0 0;font-size:15px}
main{max-width:960px;margin:0 auto;padding:8px 24px 60px}
.searchrow{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0 6px}
#q{flex:1 1 300px;font-family:ui-monospace,'SF Mono',Menlo,monospace;font-size:15px;padding:13px 16px;border:1px solid var(--edge);border-radius:8px;background:var(--surface);color:var(--ink);outline:none}
#q:focus{border-color:var(--accent)}
select{font-family:ui-monospace,monospace;font-size:13px;padding:10px 12px;border:1px solid var(--edge);border-radius:8px;background:var(--surface);color:var(--muted)}
#constellation{background:var(--surface);border:1px solid var(--rule);border-radius:12px;margin:14px 0 4px}
#constellation .node{cursor:pointer;transition:opacity .15s}
#constellation .node:hover{stroke:#fff;stroke-width:1.5}
#constellation .domlabel{cursor:pointer}
#constellation .domlabel:hover{fill:var(--accent-soft)}
.vizcap{color:var(--faint);font-size:13px;margin:2px 2px 14px;font-family:ui-monospace,monospace}
.card{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:15px 19px;margin:10px 0;cursor:pointer}
.card:hover{border-color:var(--accent)}
.card h3{margin:0 0 4px;font-size:17.5px;font-weight:600}
.card .kills{color:var(--muted);font-size:14.5px}
.card .kills b{color:var(--accent-soft);font-weight:600}
.card .sub{color:var(--faint);font-size:12.5px;margin-top:7px;font-family:ui-monospace,monospace}
.detail{background:var(--surface);border:1px solid var(--rule);border-radius:12px;padding:28px 32px;margin:14px 0}
.detail h2{font-weight:650}
.meta{color:var(--faint);font-family:ui-monospace,monospace;font-size:13px;margin-bottom:14px}
.back{font-family:ui-monospace,monospace;font-size:13px;color:var(--accent);background:none;border:none;cursor:pointer;padding:0 0 12px}
.label{font-family:ui-monospace,monospace;font-size:11px;text-transform:uppercase;letter-spacing:1.5px;color:var(--faint);margin-bottom:3px}
.refutesbox{border-left:3px solid var(--accent);padding:2px 0 2px 14px;margin:14px 0}
.truebox,.fieldbox{border-left:3px solid var(--edge);padding:2px 0 2px 14px;margin:14px 0}
.body{font-size:16px}
.body h2{font-size:17px;border-bottom:1px solid var(--rule);padding-bottom:4px}
.rel{color:var(--accent);cursor:pointer;text-decoration:underline}
.links a{color:var(--accent-soft);word-break:break-all}
#tip{background:#000;border:1px solid var(--edge);color:var(--ink);padding:7px 10px;font-size:13px;border-radius:6px;max-width:300px}
code{background:#111;border:1px solid var(--rule);padding:1px 5px;border-radius:5px;font-size:13.5px}
.count{color:var(--faint);font-size:13px;font-family:ui-monospace,monospace}
footer{max-width:960px;margin:0 auto;padding:18px 24px 44px;color:var(--faint);font-size:13.5px;border-top:1px solid var(--rule)}
footer a{color:var(--accent-soft)}
.navlink{margin-left:auto;font-family:ui-monospace,monospace;font-size:13.5px;color:var(--accent);text-decoration:none;border:1px solid var(--edge);padding:9px 14px;border-radius:8px;white-space:nowrap;align-self:center}
.navlink:hover{border-color:var(--accent)}
"""

DEPOSIT_CSS = """
.section{background:var(--surface);border:1px solid var(--rule);border-radius:12px;padding:20px 24px;margin:14px 0}
.section>h2{font-family:ui-monospace,monospace;font-size:12.5px;letter-spacing:2px;text-transform:uppercase;color:var(--accent-soft);margin:0 0 14px;font-weight:600}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:640px){.grid{grid-template-columns:1fr}}
.field{margin:0 0 12px}
.field label{display:block;font-family:ui-monospace,monospace;font-size:11px;text-transform:uppercase;letter-spacing:1.5px;color:var(--faint);margin-bottom:5px}
.field .hint{color:var(--faint);font-size:12.5px;margin-top:4px}
input[type=text],input[type=email],textarea,select.f{width:100%;font-family:ui-monospace,'SF Mono',Menlo,monospace;font-size:14px;padding:10px 12px;border:1px solid var(--edge);border-radius:8px;background:var(--page);color:var(--ink);outline:none}
input[type=text]:focus,input[type=email]:focus,textarea:focus,select.f:focus{border-color:var(--accent)}
textarea{min-height:64px;resize:vertical;line-height:1.5}
#f_body{min-height:230px}
input[type=file]{color:var(--muted);font-family:ui-monospace,monospace;font-size:13px}
.req::after{content:" *";color:var(--accent)}
.err,.warn,.ok{font-family:ui-monospace,monospace;font-size:13px;margin:4px 0}
.err{color:#e58f8f}.warn{color:#e5c98f}.ok{color:#8fe5a3}
#out{white-space:pre-wrap;font-family:ui-monospace,'SF Mono',Menlo,monospace;font-size:12.5px;background:var(--page);border:1px solid var(--rule);border-radius:8px;padding:14px 16px;max-height:420px;overflow:auto;margin:12px 0 0}
.actions{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0 4px}
button.act{font-family:ui-monospace,monospace;font-size:13.5px;padding:11px 16px;border-radius:8px;border:1px solid var(--edge);background:var(--surface);color:var(--ink);cursor:pointer}
button.act:hover:not(:disabled){border-color:var(--accent)}
button.act:disabled{opacity:.4;cursor:not-allowed}
button.act.primary{background:var(--accent);border-color:var(--accent);color:#fff}
#flash{font-family:ui-monospace,monospace;font-size:13px;color:var(--accent-soft);margin:6px 0;min-height:18px}
#rendered{border-top:1px dashed var(--rule);margin-top:14px;padding-top:6px}
.note{color:var(--faint);font-size:13.5px}
"""

JS = r"""
const DATA = JSON.parse(document.getElementById('bugbank-data').textContent);
const byId = Object.fromEntries(DATA.entries.map(e => [e.id, e]));
const $ = id => document.getElementById(id);
const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
function score(e, terms) {
  if (!terms.length) return 1;
  const ref = e.refutes.toLowerCase(), ti = e.title.toLowerCase(),
        rest = (e.statement+' '+e.true_theorem+' '+e.tags.join(' ')+' '+e.subdomain+' '+e.body).toLowerCase();
  let s = 0;
  for (const t of terms) {
    if (ref.includes(t)) s += 5; else if (ti.includes(t)) s += 3;
    else if (rest.includes(t)) s += 1; else return 0;
  }
  return s;
}
function hits() {
  const terms = $('q').value.toLowerCase().split(/\s+/).filter(Boolean);
  const dom = $('domain').value, typ = $('type').value;
  return DATA.entries.map(e => [score(e, terms), e])
    .filter(([s,e]) => s > 0 && (!dom || e.domain === dom) && (!typ || e.type === typ))
    .sort((a,b) => b[0]-a[0]).map(([s,e]) => e);
}
function typeset(el){ if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([el]).catch(()=>{}); }
function tip(html, x, y) {
  const t = $('tip'); t.style.display='block'; t.innerHTML = html;
  const w = t.offsetWidth; t.style.left = Math.min(x+14, window.innerWidth-w-10)+'px'; t.style.top = (y+14)+'px';
}
function untip(){ $('tip').style.display='none'; }
function show(id) {
  const e = byId[id];
  $('results').style.display='none'; $('viz').style.display='none';
  const d = $('detail'); d.style.display='';
  const src = e.source_book ? (DATA.sources[e.source_book]||e.source_book)+(e.source_chapter?' — '+e.source_chapter:'') : '';
  d.innerHTML = `<button class="back" onclick="back()">&larr; all entries</button>
    <h2>${esc(e.title)}</h2>
    <div class="meta">${e.domain}/${e.subdomain} &middot; ${e.type} &middot; ${e.status} &middot; difficulty ${e.difficulty}/5</div>
    <div class="refutesbox"><div class="label">Refutes</div>${esc(e.refutes)}</div>
    ${e.statement ? `<div class="fieldbox"><div class="label">Statement</div>${esc(e.statement)}</div>` : ''}
    ${e.true_theorem ? `<div class="truebox"><div class="label">True theorem nearby</div>${esc(e.true_theorem)}</div>` : ''}
    ${e.hypothesis_violated ? `<div class="truebox"><div class="label">Hypothesis violated</div>${esc(e.hypothesis_violated)}</div>` : ''}
    <div class="body">${marked.parse(e.body)}</div>
    ${e.formalized.length ? `<div class="fieldbox links"><div class="label">Formalized</div>`+e.formalized.map(f=>/^(https?:\/\/|bank\/)/.test(f)?`<a href="${esc(f).replace(/"/g,'&quot;')}" target="_blank" rel="noopener">${esc(f)}</a>`:`<code>${esc(f)}</code>`).join('<br>')+`</div>`:''}
    ${e.related.length ? `<div class="fieldbox"><div class="label">Related</div>`+e.related.map(r=>`<span class="rel" onclick="show('${r}')">${r}</span>`).join(' &middot; ')+`</div>`:''}
    ${src ? `<div class="fieldbox"><div class="label">Source</div>${esc(src)}</div>` : ''}`;
  window.scrollTo(0,0); typeset(d);
}
function back(){ $('detail').style.display='none'; $('results').style.display=''; $('viz').style.display=''; render(); }

let NODE = {};   // id -> circle element, for highlighting search hits
function drawConstellation() {
  const svg = $('constellation');
  const W=900, H=580, SP=8.5, PAD=36;
  const doms = [...new Set(DATA.entries.map(e=>e.domain))].sort();
  const groups = doms.map(d => ({d, es: DATA.entries.filter(e=>e.domain===d)}))
    .map(g => ({...g, r: SP*Math.sqrt(g.es.length)+10})).sort((a,b)=>b.r-a.r);
  // greedy circle packing: place the largest cluster at the centre, then each
  // next cluster at the candidate spot (tangent to a placed one) nearest the centre
  const placed = [];
  const ok = (x,y,r) => placed.every(p => Math.hypot(p.x-x,p.y-y) >= p.r+r+PAD-0.01);
  groups.forEach((g,i) => {
    if (i===0) { g.x=0; g.y=0; placed.push(g); return; }
    let best=null;
    placed.forEach(p => { for (let k=0;k<72;k++) {
      const a=k*Math.PI/36, dd=p.r+g.r+PAD, x=p.x+dd*Math.cos(a), y=p.y+dd*Math.sin(a);
      if (!ok(x,y,g.r)) continue;
      const cost=Math.hypot(x/1.7,y);   // favour a landscape arrangement (canvas is ~1.6:1)
      if (!best || cost<best.cost) best={x,y,cost};
    }});
    g.x=best.x; g.y=best.y; placed.push(g);
  });
  // fit the packing into the canvas
  const minX=Math.min(...placed.map(g=>g.x-g.r)), maxX=Math.max(...placed.map(g=>g.x+g.r));
  const minY=Math.min(...placed.map(g=>g.y-g.r-16)), maxY=Math.max(...placed.map(g=>g.y+g.r));
  const sc=Math.min(1,(W-24)/(maxX-minX),(H-24)/(maxY-minY));
  const ox=W/2-sc*(minX+maxX)/2, oy=H/2-sc*(minY+maxY)/2;
  const pos = {};
  placed.forEach(g => {
    g.cx=ox+sc*g.x; g.cy=oy+sc*g.y; g.R=sc*g.r;
    g.es.forEach((e,i) => {          // sunflower spiral inside the cluster
      const rr=sc*SP*Math.sqrt(i+0.5), aa=i*2.39996;
      pos[e.id]=[g.cx+rr*Math.cos(aa), g.cy+rr*Math.sin(aa)];
    });
  });
  const deg = {};
  DATA.entries.forEach(e => e.related.forEach(r => { if (pos[r]) { deg[e.id]=(deg[e.id]||0)+1; deg[r]=(deg[r]||0)+1; }}));
  let halos = '';
  placed.forEach(g => {
    halos += `<circle cx="${g.cx}" cy="${g.cy}" r="${g.R}" fill="#3987e5" fill-opacity="0.045" stroke="#2c2c2a" stroke-width="1"/>`;
  });
  let edges = '';
  DATA.entries.forEach(e => e.related.forEach(r => {
    if (byId[r] && e.id < r) {
      const [x1,y1]=pos[e.id],[x2,y2]=pos[r];
      edges += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#8fb8e8" stroke-opacity="0.35" stroke-width="1"/>`;
    }
  }));
  let nodes = '';
  DATA.entries.forEach(e => {
    const [x,y]=pos[e.id]; const r = sc*(2.6 + Math.min(2.4,(deg[e.id]||0)*0.8));
    nodes += `<circle class="node" data-id="${e.id}" cx="${x}" cy="${y}" r="${r}" fill="#3987e5"
      onmouseenter="tip('<b>${esc(e.title).replace(/'/g,'&#39;')}</b><br><span style=color:#898781>${e.domain}/${e.subdomain}</span>',event.clientX,event.clientY)"
      onmouseleave="untip()" onclick="show('${e.id}')"/>`;
  });
  let labels = '';
  placed.forEach(g => {
    labels += `<text class="domlabel" x="${g.cx}" y="${g.cy-g.R-5}" text-anchor="middle" fill="#c3c2b7"
      font-family="ui-monospace,monospace" font-size="11" letter-spacing="1.2"
      onclick="pickDomain('${g.d}')">${g.d.toUpperCase()} <tspan fill="#898781">${g.es.length}</tspan></text>`;
  });
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('height', H);
  svg.innerHTML = halos + edges + nodes + labels;
  NODE = {}; svg.querySelectorAll('.node').forEach(c => NODE[c.dataset.id]=c);
}
function pickDomain(d){ $('domain').value = ($('domain').value===d) ? '' : d; render(); }
function highlight(h) {
  const on = new Set(h.map(e=>e.id)); const all = h.length===DATA.entries.length;
  for (const id in NODE) NODE[id].setAttribute('opacity', all||on.has(id) ? 1 : 0.12);
}
function render() {
  const h = hits();
  $('count').textContent = h.length + '/' + DATA.entries.length + ' entries';
  highlight(h);
  $('results').innerHTML = h.map(e => `<div class="card" onclick="show('${e.id}')">
      <h3>${esc(e.title)}</h3>
      <div class="kills"><b>refutes</b> ${esc(e.refutes)}</div>
      <div class="sub">${e.domain}/${e.subdomain} &middot; ${e.type} &middot; ${e.status} &middot; d${e.difficulty}${e.formalized.length?' &middot; lean&#10003;':''}</div>
    </div>`).join('');
  typeset($('results'));
}
$('q').addEventListener('input', render);
$('domain').addEventListener('change', render);
$('type').addEventListener('change', render);
drawConstellation();
render();
"""

# JavaScript for the deposit page. The validation here mirrors, rule for rule,
# what scripts/build_db.py enforces — keep the two in sync.
DEPOSIT_JS = r"""
const META = JSON.parse(document.getElementById('bugbank-meta').textContent);
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const SLUG = /^[a-z0-9][a-z0-9-]*$/;               // same as build_db.py
const TYPES = ['counterexample','example','pathology','sharpness'];
let idEdited = false;

const slugify = s => s.toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g,'')
  .replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'');

function collect() {
  const v = id => $(id).value.trim();
  return {
    id: v('f_id'), title: v('f_title'), type: v('f_type'),
    domain: v('f_domain'), subdomain: v('f_subdomain'),
    tags: v('f_tags').split(',').map(s=>s.trim()).filter(Boolean),
    refutes: v('f_refutes'), statement: v('f_statement'),
    true_theorem: v('f_true'), hypothesis_violated: v('f_hyp'),
    difficulty: parseInt(v('f_difficulty'), 10),
    book: v('f_book'), chapter: v('f_chapter'), item: v('f_item'), pages: v('f_pages'),
    related: v('f_related').split(',').map(s=>s.trim()).filter(Boolean),
    formalized: v('f_formalized').split(/\n+/).map(s=>s.trim()).filter(Boolean),
    body: $('f_body').value.replace(/\s+$/,''),
    depositor: v('f_depositor'), contact: v('f_contact'),
  };
}

function validate(o) {
  const errors = [], warns = [];
  if (!o.title) errors.push("missing required field 'title'");
  if (!o.id) errors.push("missing required field 'id'");
  else if (!SLUG.test(o.id)) errors.push(`id '${o.id}' is not a valid slug (lowercase letters, digits, hyphens)`);
  else if (META.ids.includes(o.id)) errors.push(`id '${o.id}' already exists in the bank — pick another, or relate your entry to it`);
  if (!TYPES.includes(o.type)) errors.push('choose a type');
  if (!o.domain) errors.push("missing required field 'domain'");
  else if (!SLUG.test(o.domain)) errors.push(`domain '${o.domain}' is not a valid slug`);
  if (!o.subdomain) errors.push("missing required field 'subdomain'");
  else if (!SLUG.test(o.subdomain)) errors.push(`subdomain '${o.subdomain}' is not a valid slug`);
  if (!o.tags.length) errors.push('at least one tag is required');
  o.tags.forEach(t => { if (!SLUG.test(t)) errors.push(`tag '${t}' is not a valid slug`); });
  if (!o.statement) errors.push("missing required field 'statement'");
  if ((o.type === 'counterexample' || o.type === 'sharpness') && !o.refutes)
    errors.push(`type '${o.type}' requires the refuted claim`);
  if (!(o.difficulty >= 1 && o.difficulty <= 5)) errors.push('difficulty must be 1-5');
  o.related.forEach(r => {
    if (!SLUG.test(r)) errors.push(`related id '${r}' is not a valid slug`);
    else if (!META.ids.includes(r)) warns.push(`related id '${r}' is not in the bank (yet) — the build will reject it unless that entry lands first`);
  });
  if (o.book && !(o.book in META.sources))
    warns.push(`source book '${o.book}' is not in sources.yaml — the maintainer will add the citation, or move the reference into a ## References section`);
  if (o.domain && SLUG.test(o.domain) && !META.domains.includes(o.domain))
    warns.push(`'${o.domain}' would be a new domain — fine if intentional`);
  return {errors, warns};
}

// --- YAML emission (subset used by the entry template) ---
const yplain = s => /^[A-Za-z0-9][^:#"'\n\\]*$/.test(s) && !/\s$/.test(s);
const yline = (k, s) => k + ': ' + (yplain(s) ? s : JSON.stringify(s));
function yfold(k, s) {                       // one-paragraph fields, folded style
  const words = s.replace(/\s+/g,' ').trim().split(' ');
  const lines = []; let cur = '';
  for (const w of words) {
    if (cur && (cur + ' ' + w).length > 76) { lines.push(cur); cur = w; }
    else cur = cur ? cur + ' ' + w : w;
  }
  if (cur) lines.push(cur);
  return k + ': >-\n  ' + lines.join('\n  ');
}

function genMarkdown(o) {
  const L = ['---',
    'id: ' + o.id,
    yline('title', o.title),
    'type: ' + o.type,
    'domain: ' + o.domain,
    'subdomain: ' + o.subdomain,
    'tags: [' + o.tags.join(', ') + ']'];
  if (o.refutes) L.push(yfold('refutes', o.refutes));
  if (o.statement) L.push(yfold('statement', o.statement));
  if (o.true_theorem) L.push(yfold('true_theorem', o.true_theorem));
  if (o.hypothesis_violated) L.push(yfold('hypothesis_violated', o.hypothesis_violated));
  if (o.book || o.chapter || o.item || o.pages) {
    L.push('source:');
    if (o.book) L.push('  book: ' + o.book);
    if (o.chapter) L.push('  chapter: ' + JSON.stringify(o.chapter));
    if (o.item) L.push('  item: ' + JSON.stringify(o.item));
    if (o.pages) L.push('  pages: ' + JSON.stringify(o.pages));
  }
  L.push('difficulty: ' + o.difficulty, 'status: draft');
  if (o.related.length) L.push('related: [' + o.related.join(', ') + ']');
  if (o.formalized.length) {
    L.push('formalized:');
    o.formalized.forEach(f => L.push('  - ' + JSON.stringify(f)));
  }
  L.push('---', '', o.body, '');
  return L.join('\n');
}

function render() {
  const o = collect();
  const {errors, warns} = validate(o);
  const md = genMarkdown(o);
  $('out').textContent = md;
  $('path').textContent = 'entries/' + (o.domain || '<domain>') + '/' + (o.id || '<id>') + '.md';
  $('problems').innerHTML =
    errors.map(e => `<div class="err">&#10007; ${esc(e)}</div>`).join('') +
    warns.map(w => `<div class="warn">&#9651; ${esc(w)}</div>`).join('') +
    (errors.length ? '' : '<div class="ok">&#10003; passes the schema checks that scripts/build_db.py enforces</div>');
  ['b_dl','b_cp','b_em','b_gh'].forEach(b => $(b).disabled = !!errors.length);
  return {o, md, errors};
}

function flash(msg) {
  $('flash').textContent = msg;
  clearTimeout(flash.t); flash.t = setTimeout(() => $('flash').textContent = '', 4000);
}

function download() {
  const {o, md, errors} = render(); if (errors.length) return;
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([md], {type: 'text/markdown'}));
  a.download = o.id + '.md'; a.click();
  URL.revokeObjectURL(a.href);
  flash('downloaded ' + o.id + '.md — email it to the maintainer or attach it to a GitHub issue');
}
function copyMd() {
  const {md, errors} = render(); if (errors.length) return;
  navigator.clipboard.writeText(md).then(() => flash('entry copied to clipboard'),
                                         () => flash('copy failed — select the text below instead'));
}
function emailMd() {
  const {o, md, errors} = render(); if (errors.length) return;
  const meta = (o.depositor ? 'Deposited by: ' + o.depositor + '\n' : '')
             + (o.contact ? 'Contact: ' + o.contact + '\n' : '');
  let body = meta + '\n' + md;
  if (body.length > 1500) {   // mailto URLs get truncated; fall back to clipboard
    navigator.clipboard.writeText(md).catch(() => {});
    body = meta + '\nDeposit: ' + o.id + '\n\n'
         + '(The entry was too long for a mailto link. It has been copied to the\n'
         + 'clipboard — paste it here, or attach the downloaded ' + o.id + '.md.)';
    flash('entry copied — paste it into the email body');
  }
  location.href = 'mailto:' + META.email
    + '?subject=' + encodeURIComponent('[BugBank deposit] ' + o.id)
    + '&body=' + encodeURIComponent(body);
}
function ghIssue() {
  const {o, md, errors} = render(); if (errors.length) return;
  const base = 'https://github.com/' + META.repo + '/issues/new';
  const who = [o.depositor, o.contact].filter(Boolean).join(' — ');
  let url = base + '?template=deposit.yml&title=' + encodeURIComponent('[deposit] ' + o.id)
    + '&entry=' + encodeURIComponent(md)
    + (who ? '&depositor=' + encodeURIComponent(who) : '');
  if (url.length > 7500) {   // GitHub rejects very long URLs; fall back to clipboard
    navigator.clipboard.writeText(md).catch(() => {});
    url = base + '?template=deposit.yml' + (who ? '&depositor=' + encodeURIComponent(who) : '');
    flash('entry copied — paste it into the issue form');
  }
  window.open(url, '_blank', 'noopener');
}

function preview() {
  const o = collect();
  const d = $('rendered');
  d.style.display = '';
  d.innerHTML = `<h2 style="font-weight:650">${esc(o.title || '(untitled)')}</h2>
    <div class="meta">${esc(o.domain||'?')}/${esc(o.subdomain||'?')} &middot; ${esc(o.type)} &middot; draft &middot; difficulty ${o.difficulty}/5</div>
    ${o.refutes ? `<div class="refutesbox"><div class="label">Refutes</div>${esc(o.refutes)}</div>` : ''}
    ${o.statement ? `<div class="fieldbox"><div class="label">Statement</div>${esc(o.statement)}</div>` : ''}
    ${o.true_theorem ? `<div class="truebox"><div class="label">True theorem nearby</div>${esc(o.true_theorem)}</div>` : ''}
    <div class="body">${marked.parse(o.body)}</div>`;
  if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([d]).catch(() => {});
}

// --- upload an existing entry file into the form ---
$('f_upload').addEventListener('change', ev => {
  const file = ev.target.files[0]; if (!file) return;
  file.text().then(text => {
    const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
    if (!m) { flash('no YAML frontmatter block found in ' + file.name); return; }
    let meta;
    try { meta = jsyaml.load(m[1]); } catch (e) { flash('YAML parse error: ' + e.message); return; }
    if (!meta || typeof meta !== 'object') { flash('frontmatter is not a YAML mapping'); return; }
    fill(meta, m[2].trim());
    flash('loaded ' + file.name + ' — review the checks below');
  });
});
function fill(meta, body) {
  const set = (id, val) => $(id).value = val == null ? '' : String(val);
  idEdited = true;
  set('f_id', meta.id); set('f_title', meta.title);
  $('f_type').value = TYPES.includes(meta.type) ? meta.type : 'counterexample';
  set('f_domain', meta.domain); set('f_subdomain', meta.subdomain);
  set('f_tags', (meta.tags || []).join(', '));
  set('f_refutes', meta.refutes); set('f_statement', meta.statement);
  set('f_true', meta.true_theorem); set('f_hyp', meta.hypothesis_violated);
  $('f_difficulty').value = (meta.difficulty >= 1 && meta.difficulty <= 5) ? meta.difficulty : 2;
  const src = meta.source || {};
  set('f_book', src.book); set('f_chapter', src.chapter);
  set('f_item', src.item); set('f_pages', src.pages);
  set('f_related', (meta.related || []).join(', '));
  set('f_formalized', (meta.formalized || []).join('\n'));
  $('f_body').value = body;
  render();
}

// --- wiring ---
document.querySelectorAll('input[type=text],input[type=email],textarea,select.f')
  .forEach(el => el.addEventListener('input', render));
$('f_title').addEventListener('input', () => {
  if (!idEdited) { $('f_id').value = slugify($('f_title').value); render(); }
});
$('f_id').addEventListener('input', () => { idEdited = $('f_id').value !== ''; });
$('b_dl').addEventListener('click', download);
$('b_cp').addEventListener('click', copyMd);
$('b_em').addEventListener('click', emailMd);
$('b_gh').addEventListener('click', ghIssue);
$('b_pv').addEventListener('click', preview);
render();
"""


def project_entries(root):
    root = Path(root)
    authority_path = root / active_release.NAME
    authority = json.loads(authority_path.read_text()) if authority_path.exists() else {}
    corrected = authority.get('schema') == active_release.CORRECTED_SCHEMA
    projector = site_assets.Projector(root) if corrected else None
    entries = []
    for path in active_release.active_paths(root):
        entry = parse_entry(path)
        entries.append(projector.entry(entry, path) if projector else entry)
    entries = sorted(active_release.prune_relations(entries, active_release.load(root)),
                     key=lambda e: (e['domain'], e['id']))
    if projector:
        projector.active_authority(authority)
    return entries, projector


def main():
    entries, projector = project_entries(ROOT)
    sources = yaml.safe_load((ROOT / "sources.yaml").read_text(encoding="utf-8")) or {}
    sources = {k: v.strip() for k, v in sources.items()}
    domains = sorted({e["domain"] for e in entries})

    data = json.dumps({"entries": entries, "sources": sources}, ensure_ascii=False)
    data = data.replace("</", "<\\/")  # keep </script> inside strings inert

    domain_options = "\n".join(
        f'<option value="{d}">{d} ({sum(1 for e in entries if e["domain"] == d)})</option>'
        for d in domains
    )
    header_fly = FLY_SVG.replace('viewBox="0 0 120 120"', 'viewBox="0 0 120 120" width="84" height="84"', 1)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BugBank — counterexamples for debugging proofs and algorithms</title>
<link rel="icon" href="fly.svg" type="image/svg+xml">
<script>
MathJax = {{ tex: {{ inlineMath: [['$', '$']], displayMath: [['$$', '$$']] }},
            options: {{ skipHtmlTags: ['script','noscript','style','textarea','pre','code'] }} }};
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<header>
  {header_fly}
  <div>
    <h1>bugbank<span class="cursor">_</span></h1>
    <p class="tagline">counterexamples, machine-checked where possible &mdash; indexed by the claim they refute</p>
  </div>
  <a class="navlink" href="deposit.html">+ make a deposit</a>
</header>
<main>
  <div id="viz">
    <svg id="constellation" width="100%" height="580" viewBox="0 0 900 580" role="img"
         aria-label="Map of entries; nodes are entries, edges are related links"></svg>
    <div class="vizcap">the collection as a graph &mdash; each node an entry, each edge a recorded relation;
      clusters are domains (click a label to filter), hover a node to identify, click to open; searching dims the rest</div>
  </div>
  <div class="searchrow">
    <input id="q" type="search" placeholder="grep the claim you suspect is false&hellip;" autocomplete="off" autofocus>
    <select id="domain"><option value="">all domains</option>
{domain_options}
    </select>
    <select id="type"><option value="">all types</option>
      <option>counterexample</option><option>sharpness</option>
      <option>pathology</option><option>example</option>
    </select>
  </div>
  <div class="count" id="count"></div>
  <div id="results"></div>
  <div id="detail" style="display:none"></div>
</main>
<footer>
  BugBank is maintained by the project team. Verified entries are checked against their cited source
  or carry a machine-checked Lean&nbsp;4 formalization; seeded entries await verification against a
  physical copy of the source. To contribute an entry, <a href="deposit.html">make a deposit</a>.
</footer>
<div id="tip" style="display:none;position:fixed;z-index:50"></div>
<script id="bugbank-data" type="application/json">{data}</script>
<script>{JS}</script>
</body>
</html>
"""
    deposit = deposit_page(entries, sources, header_fly)

    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    (OUT / "deposit.html").write_text(deposit, encoding="utf-8")
    (OUT / "fly.svg").write_text(FLY_SVG, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    if projector:
        projector.write(OUT)
    print(f"OK: wrote site/index.html ({len(entries)} entries) and site/deposit.html.")


MAINTAINER_EMAIL = "maintainer@example.invalid"
REPO = "example/research-source"

DIFFICULTY_LABELS = {
    1: "1 — one-liner every student should know",
    2: "2 — standard, worth having at your fingertips",
    3: "3 — a real construction with something to check",
    4: "4 — delicate estimates or a clever trick",
    5: "5 — AC / transfinite construction / genuinely hard",
}


def deposit_page(entries, sources, header_fly):
    meta = json.dumps({
        "ids": [e["id"] for e in entries],
        "domains": sorted({e["domain"] for e in entries}),
        "sources": sources,
        "email": MAINTAINER_EMAIL,
        "repo": REPO,
    }, ensure_ascii=False).replace("</", "<\\/")

    domain_list = "".join(f'<option value="{e}">' for e in sorted({x["domain"] for x in entries}))
    subdomain_list = "".join(f'<option value="{e}">' for e in sorted({x["subdomain"] for x in entries if x["subdomain"]}))
    book_list = "".join(f'<option value="{k}" label="{v}">' for k, v in sorted(sources.items()))
    difficulty_options = "".join(f'<option value="{k}"{" selected" if k == 2 else ""}>{v}</option>'
                                 for k, v in DIFFICULTY_LABELS.items())

    body_skeleton = "## Object\n\n\n## What it kills\n\n\n## Why it works\n\n\n## Debugging uses\n\n\n## Remarks\n"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BugBank — make a deposit</title>
<link rel="icon" href="fly.svg" type="image/svg+xml">
<script>
MathJax = {{ tex: {{ inlineMath: [['$', '$']], displayMath: [['$$', '$$']] }},
            options: {{ skipHtmlTags: ['script','noscript','style','textarea','pre','code'] }} }};
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/js-yaml@4/dist/js-yaml.min.js"></script>
<style>{CSS}{DEPOSIT_CSS}</style>
</head>
<body>
<header>
  {header_fly}
  <div>
    <h1>bugbank<span class="cursor">_</span></h1>
    <p class="tagline">make a deposit &mdash; one counterexample, precisely labeled</p>
  </div>
  <a class="navlink" href="index.html">&larr; the collection</a>
</header>
<main>
  <p class="note">A deposit is a single Markdown file, <code>entries/&lt;domain&gt;/&lt;id&gt;.md</code>,
  indexed by the false claim it refutes. Fill in the form (LaTeX welcome: <code>$...$</code> and
  <code>$$...$$</code>), or upload a file you already wrote against the
  <a href="https://github.com/{REPO}" style="color:var(--accent-soft)">repository template</a>.
  Everything is checked in your browser against the same schema the build enforces; nothing is sent
  anywhere until you choose how to submit.</p>

  <div class="section">
    <h2>0 &middot; already have an entry file?</h2>
    <div class="field"><label for="f_upload">upload it to validate and edit</label>
      <input type="file" id="f_upload" accept=".md,.markdown,text/markdown">
    </div>
  </div>

  <div class="section">
    <h2>1 &middot; classification</h2>
    <div class="grid">
      <div class="field"><label class="req" for="f_type">type</label>
        <select class="f" id="f_type">
          <option value="counterexample">counterexample — kills a false claim</option>
          <option value="sharpness">sharpness — shows a hypothesis can't be dropped</option>
          <option value="pathology">pathology — stranger than it has any right to be</option>
          <option value="example">example — a witness worth keeping</option>
        </select>
      </div>
      <div class="field"><label class="req" for="f_difficulty">difficulty</label>
        <select class="f" id="f_difficulty">{difficulty_options}</select>
      </div>
    </div>
    <p class="note">Deposits enter the bank with <code>status: draft</code>; the maintainer verifies
    them against a cited source (or a Lean formalization) before they are marked
    <code>verified</code>.</p>
  </div>

  <div class="section">
    <h2>2 &middot; identity</h2>
    <div class="field"><label class="req" for="f_title">title</label>
      <input type="text" id="f_title" placeholder="The Dirichlet function" autocomplete="off">
    </div>
    <div class="grid">
      <div class="field"><label class="req" for="f_id">id (slug &mdash; becomes the filename)</label>
        <input type="text" id="f_id" placeholder="dirichlet-function" autocomplete="off">
      </div>
      <div class="field"><label class="req" for="f_tags">tags (comma-separated slugs)</label>
        <input type="text" id="f_tags" placeholder="continuity, dense-sets" autocomplete="off">
      </div>
      <div class="field"><label class="req" for="f_domain">domain</label>
        <input type="text" id="f_domain" list="dl_domains" placeholder="analysis" autocomplete="off">
        <datalist id="dl_domains">{domain_list}</datalist>
      </div>
      <div class="field"><label class="req" for="f_subdomain">subdomain</label>
        <input type="text" id="f_subdomain" list="dl_subdomains" placeholder="functions-and-limits" autocomplete="off">
        <datalist id="dl_subdomains">{subdomain_list}</datalist>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>3 &middot; the mathematics</h2>
    <div class="field"><label for="f_refutes">refutes &mdash; the plausible-but-false claim this kills
        (required for counterexample and sharpness)</label>
      <textarea id="f_refutes" placeholder="Every function that is a pointwise limit of continuous functions is continuous somewhere on every interval."></textarea>
    </div>
    <div class="field"><label class="req" for="f_statement">statement &mdash; one paragraph: the object and which
        properties it has/lacks</label>
      <textarea id="f_statement"></textarea>
    </div>
    <div class="field"><label for="f_true">true theorem nearby (optional) &mdash; what you must assume instead</label>
      <textarea id="f_true"></textarea>
    </div>
    <div class="field"><label for="f_hyp">hypothesis violated (for sharpness entries) &mdash; exactly which
        hypothesis of the true theorem fails</label>
      <textarea id="f_hyp"></textarea>
    </div>
  </div>

  <div class="section">
    <h2>4 &middot; provenance &amp; connections</h2>
    <div class="grid">
      <div class="field"><label for="f_book">source book (slug from sources.yaml)</label>
        <input type="text" id="f_book" list="dl_books" placeholder="gelbaum-olmsted" autocomplete="off">
        <datalist id="dl_books">{book_list}</datalist>
      </div>
      <div class="field"><label for="f_chapter">chapter</label>
        <input type="text" id="f_chapter" placeholder="Functions and Limits" autocomplete="off">
      </div>
      <div class="field"><label for="f_item">item (only if verified against a physical copy)</label>
        <input type="text" id="f_item" autocomplete="off">
      </div>
      <div class="field"><label for="f_pages">pages</label>
        <input type="text" id="f_pages" autocomplete="off">
      </div>
    </div>
    <div class="field"><label for="f_related">related entry ids (comma-separated &mdash; browse
        <a href="index.html" style="color:var(--accent-soft)">the collection</a> for ids)</label>
      <input type="text" id="f_related" placeholder="cantor-set, thomae-function" autocomplete="off">
    </div>
    <div class="field"><label for="f_formalized">formalized (Lean/Isabelle/Coq links, one per line)</label>
      <textarea id="f_formalized" style="min-height:44px"></textarea>
    </div>
    <div class="grid">
      <div class="field"><label for="f_depositor">your name (for attribution &mdash; goes in the email/issue, not the file)</label>
        <input type="text" id="f_depositor" autocomplete="name">
      </div>
      <div class="field"><label for="f_contact">contact (email or homepage)</label>
        <input type="text" id="f_contact" autocomplete="email">
      </div>
    </div>
  </div>

  <div class="section">
    <h2>5 &middot; body</h2>
    <div class="field"><label for="f_body">the entry itself &mdash; keep the section headers, delete any you
        don't need. <i>Debugging uses</i> is the one that makes an entry earn its keep.</label>
      <textarea id="f_body">{body_skeleton}</textarea>
    </div>
    <div class="actions"><button class="act" id="b_pv" type="button">render preview</button></div>
    <div id="rendered" class="detail" style="display:none"></div>
  </div>

  <div class="section">
    <h2>the deposit slip</h2>
    <div class="count" id="path"></div>
    <div id="problems"></div>
    <pre id="out"></pre>
    <div class="actions">
      <button class="act primary" id="b_dl" type="button">download .md</button>
      <button class="act" id="b_cp" type="button">copy</button>
      <button class="act" id="b_em" type="button">email the maintainer</button>
      <button class="act" id="b_gh" type="button">open a GitHub issue</button>
    </div>
    <div id="flash"></div>
    <p class="note">The GitHub route requires the repository to be public (soon); a workflow then
    validates the deposit and opens a pull request automatically. Until then, email works: the
    maintainer runs <code>scripts/ingest_deposit.py</code> on your file and it enters the bank as a
    draft, credited to you.</p>
  </div>
</main>
<footer>
  BugBank is maintained by the project team. Deposits are reviewed before they are marked verified;
  the bank optimizes for precision of the <i>refutes</i> field, not volume.
</footer>
<script id="bugbank-meta" type="application/json">{meta}</script>
<script>{DEPOSIT_JS}</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
