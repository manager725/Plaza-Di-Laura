"""Generates the Plaza Di Laura prototype pages from _build/content/*.json.

Run from anywhere:  python -I _build/build.py
Swedish is rendered into the HTML; English goes into data-en attributes that
assets/js/site.js swaps in when the visitor picks EN.
"""
import hashlib
import html
import json
import os
import re
import sys

BUILD = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BUILD)
CONTENT = os.path.join(BUILD, "content")
SITE = "https://bylaura.se"


def load(name, default):
    p = os.path.join(CONTENT, name)
    if not os.path.exists(p):
        print(f"  (missing {name}, using fallback)")
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


TREATMENTS = load("treatments.json", [])
COURSES = load("courses.json", [])
ACADEMY = load("academy.json", {})
ABOUT = load("about.json", {})
REVIEWS = load("reviews.json", [])
IMGS = load("images.json", {"images": {}, "pages": {}, "results": [], "logos": {}})
IMAGES = IMGS.get("images", {})
RESULTS = IMGS.get("results", [])
TBY = {t["slug"]: t for t in TREATMENTS}
CBY = {c["slug"]: c for c in COURSES}

# Image choices, picked from the client's own photos (see the contact sheet in QA notes).
CHOICE_T = {
    "puderbryn": "result-powder-brows-strokes-front", "strokes": "result-microblading-before-after",
    "lappar": "lip-blush-freckled-selfie", "fraknar": "faux-freckles-curly-hair-closeup",
    "lashliner": "lash-liner-eye-closeup", "microneedling": "serum-bottles-gold-banner",
    "smp": "smp-practitioner-scalp", "lift": "lift-solution-bottle", "fettfrysning": "fat-freezing-proshock-ice",
}
CHOICE_C = {
    "signature-pmu": "academy-supervised-treatment-overhead", "signature-microblading": "academy-students-practising-lamp",
    "freckle": "academy-training-kit-table", "smp": "academy-student-practice-skin",
    "microneedling": "laura-demo-ring-light-students", "ink-removal": "lift-solution-bottle",
}
SLOT = {
    "heroMain": "laura-portrait-laughing-profile", "heroInset": "result-ombre-lips-fresh-portrait",
    "pathTreat": "treatment-brows-lips-closeup", "pathAcademy": "academy-supervised-treatment-overhead",
    "nt": "laura-portrait-arms-crossed", "meet": "laura-portrait-seated-stool",
    "aband1": "academy-students-sketching-table", "aband2": "academy-graduates-certificates-trio",
    "academyHero": "academy-graduates-certificates-trio", "teacher": "laura-portrait-pointing-up",
    "aboutHero": "laura-portrait-seated-stool", "aboutAside": "laura-studio-ring-light-seated",
    "megaBeh": "result-powder-brows-strokes-front", "megaAka": "academy-students-sketching-table",
}
RESULT_ORDER = [
    "result-powder-brows-strokes-front", "result-ombre-lips-fresh-portrait", "result-faux-freckles-before-after-1",
    "result-powder-brows-before-after-1", "result-soft-lips-before-after", "result-microblading-before-after",
    "result-faux-freckles-before-after-2", "result-ombre-lips-before-fresh-healed", "result-powder-brows-before-after-2",
    "result-ombre-lips-fresh-inset", "result-powder-brows-healed-before-after", "result-ombre-lips-fresh-face",
    "result-soft-lips-before-healed", "result-powder-brows-healed-client-selfie", "result-faux-freckles-healed-selfie",
    "result-ombre-brows-healed-collage",
]
RESULTS.sort(key=lambda r: RESULT_ORDER.index(r["slug"]) if r["slug"] in RESULT_ORDER else 99)
for _t in TREATMENTS:
    _t["_img"] = CHOICE_T.get(_t["slug"])
for _c in COURSES:
    _c["_img"] = CHOICE_C.get(_c["slug"])


def minify_assets():
    """Readable CSS/JS live in _build/src (never deployed); the site gets minified copies in assets/.
    Uses the pinned esbuild in _build/node_modules (npm install inside _build). Without it, copies unminified and warns."""
    import shutil
    import subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    exe = os.path.join(here, "node_modules", ".bin", "esbuild.cmd" if os.name == "nt" else "esbuild")
    pairs = [("css/site.css", "assets/css/site.css"), ("css/app.css", "assets/css/app.css"),
             ("js/site.js", "assets/js/site.js"), ("js/kundkort.js", "assets/js/kundkort.js")]
    have = os.path.exists(exe)
    if not have:
        print("WARNING: esbuild not found in _build/node_modules, assets copied unminified (run: npm install, inside _build)")
    for src, dst in pairs:
        s, d = os.path.join(here, "src", src), os.path.join(ROOT, dst)
        if not have:
            shutil.copyfile(s, d)
            continue
        r = subprocess.run([exe, s, "--minify", "--legal-comments=none", "--charset=utf8", "--log-level=warning", "--outfile=" + d],
                           capture_output=True, text=True, shell=os.name == "nt")
        if r.returncode != 0:
            raise SystemExit("minify failed for " + src + ":\n" + r.stderr)


minify_assets()


def ver(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return "0"
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


CSS_V = ver("assets/css/site.css")
APP_CSS_V = ver("assets/css/app.css")
APP_JS_V = ver("assets/js/kundkort.js")
JS_V = ver("assets/js/site.js")

# ---------------------------------------------------------------- helpers
def esc(s):
    return html.escape(s or "", quote=False)


def att(s):
    return html.escape(s or "", quote=True)


def L(sv, en=None):
    return {"sv": sv, "en": sv if en is None else en}


def sv(o):
    return o["sv"] if isinstance(o, dict) else (o or "")


def en(o):
    if isinstance(o, dict):
        return o.get("en") or o.get("sv") or ""
    return o or ""


def tx(o, tag="span", cls=None, raw=False, extra=""):
    """Element with Swedish content and English in data-en."""
    if o is None:
        return ""
    if isinstance(o, str):
        o = L(o)
    s = sv(o) if raw else esc(sv(o))
    e = en(o) if raw else esc(en(o))
    da = f' data-en="{att(e)}"' if e != s else ""
    c = f' class="{cls}"' if cls else ""
    return f"<{tag}{c}{extra}{da}>{s}</{tag}>"


def ia(o, name):
    """Attribute pair: name="sv" data-en-name="en"."""
    if isinstance(o, str):
        o = L(o)
    short = {"placeholder": "ph", "aria-label": "aria", "alt": "alt", "title": "title", "content": "content", "href": "href"}[name]
    s, e = sv(o), en(o)
    out = f' {name}="{att(s)}"'
    if e != s:
        out += f' data-en-{short}="{att(e)}"'
    return out


def split_words(o, em=None):
    def sp(text, mark):
        out = []
        for i, w in enumerate(text.split()):
            inner = f'<span class="wi" style="--i:{i}">{esc(w)}</span>'
            if mark and w.strip(".,!?") == mark:
                inner = f"<em>{inner}</em>"
            out.append(f'<span class="w">{inner}</span>')
        return " ".join(out)
    return {"sv": sp(sv(o), sv(em) if em else None), "en": sp(en(o), en(em) if em else None)}


BROW = '<svg class="brow" viewBox="0 0 64 22" aria-hidden="true"><path d="M3 18 C 16 6, 34 2, 48 5 S 61 13, 62 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
PAUSE_BTN_ICONS = ('<svg class="i-pause" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="7" y="5" width="3.2" height="14" rx="1"/><rect x="13.8" y="5" width="3.2" height="14" rx="1"/></svg>'
                   '<svg class="i-play" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.5v13l10.5-6.5z"/></svg>')


def marquee(items_html, label, cls="", speed=60):
    one = "".join(items_html)
    dup = one.replace("<a ", '<a tabindex="-1" ')
    return (f'<div class="marquee {cls}" data-marquee style="--dur:{speed}s" role="region"{ia(label, "aria-label")}>'
            f'<div class="marquee__track"><ul>{one}</ul><ul aria-hidden="true">{dup}</ul></div></div>')


def para_list(items, tag="p", cls=None):
    return "".join(tx(p, tag, cls) for p in (items or []))


def bullets(items, cls="bul"):
    if not items:
        return ""
    return f'<ul class="{cls}">' + "".join(tx(i, "li") for i in items) + "</ul>"


ICON = {
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>',
    "chev": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
    "plus": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
    "close": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 8h16M4 16h16"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 21s-6.5-5.6-6.5-11A6.5 6.5 0 0 1 18.5 10c0 5.4-6.5 11-6.5 11Z"/><circle cx="12" cy="10" r="2.3"/></svg>',
    "cal": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15.5" rx="1.5"/><path d="M3.5 9.5h17M8 3v4M16 3v4"/></svg>',
    "video": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="3" y="6" width="13" height="12" rx="1.5"/><path d="m16 10 5-3v10l-5-3"/></svg>',
    "star": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 3.5 14.6 9l5.9.6-4.4 4 1.3 5.9L12 16.5 6.6 19.5 7.9 13.6l-4.4-4L9.4 9 12 3.5Z"/></svg>',
    "moon": '<svg class="i-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5Z"/></svg>',
    "sun": '<svg class="i-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/></svg>',
    "chat": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 5.5h16v10H9l-5 4v-14Z"/><path d="M8 9.5h8M8 12.5h5"/></svg>',
    "send": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 12 20 4l-6 16-2.5-6.5L4 12Z"/></svg>',
    "up": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M12 19V5m-6 6 6-6 6 6"/></svg>',
    "left": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M19 12H5m6-6-6 6 6 6"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>',
    "user": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="8.5" r="3.5"/><path d="M5 20c1.2-3.6 3.8-5.5 7-5.5s5.8 1.9 7 5.5"/></svg>',
    "doc": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M7 3.5h7l4 4v13H7z"/><path d="M14 3.5v4h4M12 11v6m-3-3 3 3 3-3"/></svg>',
    "ig": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r=".8" fill="currentColor"/></svg>',
    "fb": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M14 8.5h2.5V5H14a3.5 3.5 0 0 0-3.5 3.5V11H8v3.5h2.5V21H14v-6.5h2.5L17 11h-3V9a.5.5 0 0 1 .5-.5Z"/></svg>',
    "tt": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M14 3.5v11.2a3.8 3.8 0 1 1-3.8-3.8"/><path d="M14 3.5c.4 2.6 2.2 4.4 5 4.6"/></svg>',
}

SOCIAL = [
    ("https://www.instagram.com/plazadilaura/", "ig", "Instagram"),
    ("https://www.facebook.com/plazadilaura/", "fb", "Facebook"),
    ("https://www.tiktok.com/@plazadilauraacademy", "tt", "TikTok"),
]
DIRECTIONS = "https://www.google.com/maps/dir/?api=1&destination=Kungsgatan+11%2C+G%C3%B6teborg"

# ---------------------------------------------------------------- images
def img_meta(slug):
    return IMAGES.get(slug) if slug else None


def pic(slug, sizes="100vw", cls=None, alt=None, eager=False, decorative=False, extra="", lazy=True):
    m = img_meta(slug)
    if not m:
        return ""
    widths = sorted(m.get("widths") or [])
    if not widths:
        return ""
    big = widths[-1]
    ratio = float(m.get("ratio") or (m["w"] / m["h"]))
    h = round(big / ratio)
    srcset = ", ".join(f"assets/img/{slug}-{w}.webp {w}w" for w in widths)
    mid = 1080 if 1080 in widths else big
    if decorative:
        alt_attr = ' alt=""'
    else:
        alt_attr = ia(alt or m.get("alt") or L(""), "alt")
    c = f' class="{cls}"' if cls else ""
    load = ' fetchpriority="high"' if eager else (' loading="lazy"' if lazy else '')
    jpg = m.get("jpg")
    fallback = f"assets/img/{jpg}" if jpg else f"assets/img/{slug}-{mid}.webp"
    return (f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes}">'
            f'<img{c} src="{fallback}" width="{big}" height="{h}"{alt_attr} decoding="async"{load}{extra}></picture>')


def img_src(slug, w=1080):
    m = img_meta(slug)
    if not m:
        return ""
    widths = m.get("widths") or []
    use = w if w in widths else (widths[-1] if widths else w)
    return f"assets/img/{slug}-{use}.webp"


def first_image(*keys, kinds=("treatment", "result", "portrait", "course", "clinic", "other")):
    pages = IMGS.get("pages", {})
    for k in keys:
        for s in pages.get(k, []):
            m = IMAGES.get(s)
            if m and m.get("kind") in kinds and m.get("widths"):
                return s
    return None


def find_image(pattern, kinds=None):
    rx = re.compile(pattern, re.I)
    for s, m in IMAGES.items():
        if not m.get("widths"):
            continue
        if kinds and m.get("kind") not in kinds:
            continue
        if rx.search(s) or rx.search(m.get("source", "")):
            return s
    return None


def treatment_image(t):
    return t.get("_img") or first_image("products/" + t.get("handle", ""), kinds=("treatment", "result", "portrait", "clinic", "other"))


def course_image(c):
    return c.get("_img") or first_image("products/" + c.get("handle", ""), kinds=("course", "result", "treatment", "portrait", "clinic", "other"))


PORTRAITS = [s for s, m in IMAGES.items() if m.get("kind") == "portrait" and m.get("widths")]


def portrait(i):
    if not PORTRAITS:
        return None
    return PORTRAITS[i % len(PORTRAITS)]


# ---------------------------------------------------------------- shared UI strings
U = {
    "book": L("Boka tid", "Book now"),
    "consult": L("Kostnadsfri konsultation", "Free consultation"),
    "consultLong": L("Kostnadsfri konsultation på plats, per telefon eller via Zoom", "Free consultation in person, by phone or on Zoom"),
    "courseAdvice": L("Boka kostnadsfri kursrådgivning", "Book free course advice"),
    "readMore": L("Läs mer", "Read more"),
    "treatments": L("Behandlingar", "Treatments"),
    "allTreatments": L("Alla behandlingar", "All treatments"),
    "academy": L("Akademi", "Academy"),
    "results": L("Resultat", "Results"),
    "about": L("Om Laura", "About Laura"),
    "contact": L("Kontakt", "Contact"),
    "home": L("Hem", "Home"),
    "address": L("Kungsgatan 11, Göteborg", "Kungsgatan 11, Gothenburg"),
    "days": L("dagar", "days"),
    "skip": L("Hoppa till innehållet", "Skip to content"),
    "menu": L("Meny", "Menu"),
    "close": L("Stäng", "Close"),
    "theme": L("Byt mellan ljust och mörkt läge", "Switch between light and dark mode"),
    "langLabel": L("Välj språk", "Choose language"),
    "since": L("Sedan 2006", "Since 2006"),
}
GROUPS = {
    "pmu": L("Kosmetisk tatuering", "Cosmetic tattooing"),
    "skin": L("Hudvård", "Skin"),
    "scalp": L("Hårbotten", "Scalp"),
    "removal": L("Borttagning", "Removal"),
    "body": L("Kropp", "Body"),
}
FILTERS = [("all", L("Alla", "All")), ("bryn", L("Bryn", "Brows")), ("lappar", L("Läppar", "Lips")), ("fraknar", L("Fräknar", "Freckles"))]


def tfile(slug):
    return f"behandling-{slug}.html"


def cfile(slug):
    return f"utbildning-{slug}.html"


def days_label(c):
    d = c.get("days")
    return L(f"{d} dagar", f"{d} days") if d else None


# ---------------------------------------------------------------- partials
BOOT = """(function(d){var r=d.documentElement,t=null,l=null,i=null;try{t=localStorage.getItem('pdl-theme');l=localStorage.getItem('pdl-lang');i=sessionStorage.getItem('pdl-intro')}catch(e){}
if(t==='dark')r.setAttribute('data-theme','dark');if(l==='en'){r.setAttribute('data-lang','en');r.classList.add('i18n-pending')}
var m=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;if(!m&&'IntersectionObserver'in window)r.classList.add('reveal-on');
if(/[?&]intro(?:[=&]|$)/.test(location.search))i=null;if(!m&&!i)r.classList.add('has-loader','loader-hold');setTimeout(function(){if(!window.__pdlReady){r.classList.remove('reveal-on','i18n-pending','has-loader','loader-hold')}},2500)})(document);"""


def head(title, desc, path, jsonld=None):
    canon = SITE + "/" + ("" if path == "index.html" else path.replace(".html", ""))
    og = SITE + "/assets/img/og-image.jpg"
    ld = ""
    for block in (jsonld or []):
        ld += '<script type="application/ld+json">' + json.dumps(block, ensure_ascii=False, separators=(",", ":")) + "</script>\n"
    return f"""<!doctype html>
<html lang="sv" data-lang="sv" data-theme="light" data-title-sv="{att(sv(title))}" data-title-en="{att(en(title))}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(sv(title))}</title>
<meta name="description"{ia(desc, "content")}>
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Plaza Di Laura">
<meta property="og:locale" content="sv_SE">
<meta property="og:title"{ia(title, "content")}>
<meta property="og:description"{ia(desc, "content")}>
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f7f3ef" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#171413" media="(prefers-color-scheme: dark)">
<link rel="icon" href="assets/img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="assets/img/favicon-192.png" sizes="192x192" type="image/png">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="preload" href="assets/fonts/jost-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/cormorant-garamond-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/site.css?v={CSS_V}">
<script>{BOOT}</script>
<script defer src="assets/js/site.js?v={JS_V}"></script>
<!-- Analytics: add GA4 or GTM here in production, loaded only after cookie consent. -->
{ld}</head>
"""


def logo(cls_extra=""):
    logos = IMGS.get("logos", {})
    dark = logos.get("wordmarkDark") or "logo-wordmark-dark.png"
    light = logos.get("wordmarkLight") or "logo-wordmark-light.png"
    w, h = logo_size(dark)
    return (f'<img class="logo-dark{cls_extra}" src="assets/img/{dark}" width="{w}" height="{h}" alt="Plaza Di Laura">'
            f'<img class="logo-light{cls_extra}" src="assets/img/{light}" width="{w}" height="{h}" alt="Plaza Di Laura">')


def logo_size(name):
    p = os.path.join(ROOT, "assets", "img", name)
    try:
        with open(p, "rb") as f:
            b = f.read(32)
        if b[:8] == b"\x89PNG\r\n\x1a\n":
            import struct
            w, h = struct.unpack(">II", b[16:24])
            return w, h
    except OSError:
        pass
    return 1000, 90


def mega_treatments():
    pmu = [t for t in TREATMENTS if t["group"] == "pmu"]
    other = [t for t in TREATMENTS if t["group"] in ("skin", "scalp", "body")]
    rem = [t for t in TREATMENTS if t["group"] == "removal"]
    li = lambda t: f'<li><a href="{tfile(t["slug"])}">{tx(t["name"])}</a></li>'
    guide_img = SLOT["megaBeh"]
    return f"""<div class="mega" id="mega-beh">
  <div class="container mega__inner">
    <div class="mega__col">{tx(GROUPS["pmu"], "h3")}<ul>{"".join(li(t) for t in pmu)}</ul></div>
    <div class="mega__col">{tx(L("Hud, hår och kropp", "Skin, scalp and body"), "h3")}<ul>{"".join(li(t) for t in other)}</ul></div>
    <div class="mega__col">{tx(L("Korrigering och rådgivning", "Corrections and advice"), "h3")}<ul>{"".join(li(t) for t in rem)}
      <li><a href="boka.html?t=konsultation">{tx(U["consult"])}</a></li>
      <li><a href="behandlingar.html">{tx(U["allTreatments"])}</a></li></ul></div>
    <a class="mega__feature" href="index.html#brynguiden">{pic(guide_img, "160px", decorative=True)}<div>
      {tx(L("Puder eller strokes?", "Powder or strokes?"), "strong")}
      {tx(L("Svara på fyra frågor så rekommenderar Brynguiden rätt brynmetod för dig.", "Answer four questions and the brow guide recommends the right method for you."))}
      <em>{tx(L("Testa Brynguiden", "Try the brow guide"))} {ICON["arrow"]}</em></div></a>
  </div>
</div>"""


def mega_academy():
    pmu = [c for c in COURSES if c["slug"] in ("signature-pmu", "signature-microblading", "freckle")]
    rest = [c for c in COURSES if c not in pmu]

    def li(c):
        d = days_label(c)
        small = tx(d, "small") if d else ""
        return f'<li><a href="{cfile(c["slug"])}">{tx(c["name"])}{small}</a></li>'
    feat = SLOT["megaAka"]
    sig = CBY.get("signature-pmu", {})
    pdf = sig.get("pdf")
    pdf_li = f'<li><a href="{att(pdf)}" target="_blank" rel="noopener">{tx(L("Kursinformation (PDF)", "Course information (PDF)"))}</a></li>' if pdf else ""
    return f"""<div class="mega" id="mega-aka">
  <div class="container mega__inner">
    <div class="mega__col">{tx(L("PMU-program", "PMU programmes"), "h3")}<ul>{"".join(li(c) for c in pmu)}</ul></div>
    <div class="mega__col">{tx(L("Fler grundkurser", "More foundation courses"), "h3")}<ul>{"".join(li(c) for c in rest)}</ul></div>
    <div class="mega__col">{tx(L("Akademin", "The academy"), "h3")}<ul>
      <li><a href="akademi.html">{tx(L("Om Plaza Di Laura Academy", "About the academy"))}</a></li>
      <li><a href="boka.html?t=kursradgivning">{tx(U["courseAdvice"])}</a></li>{pdf_li}</ul></div>
    <a class="mega__feature" href="akademi.html">{pic(feat, "160px", decorative=True)}<div>
      {tx(L("Max 2 elever per kurstillfälle", "Max 2 students per course"), "strong")}
      {tx(L("Praktisk träning på modeller, livstid support och möjlighet till praktik på skolan.", "Hands-on training on models, lifetime support and the option of practice at the school."))}
      <em>{tx(L("Se utbildningar", "See courses"))} {ICON["arrow"]}</em></div></a>
  </div>
</div>"""


LOADER_BROW = "M18 60 C 12 56, 12 46, 22 41 C 50 28, 110 12, 168 10 C 196 9, 220 22, 236 40 C 214 30, 192 26, 170 27 C 120 30, 70 44, 40 55 C 32 58, 24 62, 18 60 Z"
LOADER_HAIRS = ['M23.3 58.7 Q 23.8 50.0 27.7 40.6', 'M27.6 50.4 Q 27.3 44.9 30.4 38.6', 'M30.3 55.8 Q 32.3 47.1 37.6 37.2', 'M33.8 49.3 Q 34.5 43.8 38.6 36.9', 'M37.4 54.5 Q 39.2 44.8 44.5 33.9', 'M41.0 45.3 Q 41.9 38.1 46.3 29.7', 'M42.1 51.6 Q 45.8 41.9 52.8 30.5', 'M45.7 44.1 Q 47.7 37.9 52.9 30.0', 'M48.5 48.7 Q 51.6 39.9 57.9 29.6', 'M53.3 41.5 Q 54.9 35.8 59.7 28.4', 'M56.1 48.0 Q 60.5 38.6 68.0 27.4', 'M59.5 39.6 Q 61.8 33.7 67.3 26.0', 'M63.7 45.9 Q 67.7 37.4 74.8 27.1', 'M67.5 37.6 Q 69.6 32.3 74.9 25.1', 'M71.7 43.4 Q 78.1 35.4 87.2 25.2', 'M75.6 34.7 Q 79.7 29.4 86.5 21.9', 'M78.8 41.5 Q 85.3 32.5 94.6 21.3', 'M82.4 33.4 Q 85.4 28.8 91.3 22.0', 'M87.8 39.2 Q 93.8 31.7 102.6 21.7', 'M90.1 31.4 Q 93.3 27.1 99.3 20.5', 'M93.7 35.9 Q 101.8 28.8 112.4 19.0', 'M97.2 28.8 Q 101.9 24.8 109.1 18.1', 'M102.8 34.9 Q 111.8 28.4 123.0 19.1', 'M107.0 28.1 Q 112.0 24.8 119.3 18.6', 'M111.6 34.0 Q 119.5 28.4 129.7 19.9', 'M113.6 25.3 Q 118.7 22.0 125.9 15.8', 'M118.5 30.5 Q 126.9 24.6 137.6 15.9', 'M122.2 24.5 Q 128.4 20.3 136.8 13.4', 'M127.9 30.3 Q 136.4 25.5 146.9 17.7', 'M132.0 23.4 Q 138.5 19.9 147.1 13.4', 'M136.5 27.7 Q 146.6 23.2 158.4 15.5', 'M144.2 26.7 Q 154.5 23.6 166.2 17.3', 'M152.3 25.7 Q 163.0 23.2 175.0 17.4', 'M161.5 25.0 Q 171.4 21.4 182.9 14.5']


def loader():
    """Intro shown once per tab session (BOOT adds has-loader). Brow: powder fill wipes in under drawn hair strokes."""
    hairs = "".join(f'<path class="loader__hair" style="--i:{i}" pathLength="1" d="{d}"/>' for i, d in enumerate(LOADER_HAIRS))
    return f"""<div class="loader" aria-hidden="true">
  <div class="loader__veil"></div>
  <div class="loader__panel">
    <div class="loader__center">
      <svg class="loader__brow" viewBox="8 4 234 62"><defs><linearGradient id="ld-grad" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="currentColor" stop-opacity="0.14"/><stop offset="0.42" stop-color="currentColor" stop-opacity="0.48"/><stop offset="1" stop-color="currentColor" stop-opacity="0.95"/></linearGradient><mask id="ld-mask"><rect class="loader__wipe" x="0" y="0" width="248" height="70" fill="#fff"/></mask><clipPath id="ld-clip"><path d="{LOADER_BROW}"/></clipPath></defs><path class="loader__fill" mask="url(#ld-mask)" d="{LOADER_BROW}"/><g clip-path="url(#ld-clip)">{hairs}</g></svg>
      <div class="loader__mark">{logo()}</div>
      {tx(L("Kosmetisk tatuering och akademi", "Cosmetic tattooing and academy"), "p", "loader__tag")}
    </div>
    <div class="loader__foot">
      {tx(L("Kungsgatan 11, Göteborg", "Kungsgatan 11, Gothenburg"), "span", "loader__place")}
      <span class="loader__count"><span data-loader-count>0</span><small>%</small></span>
    </div>
    <div class="loader__bar"><i></i></div>
  </div>
</div>"""


def header(current):
    def cur(key):
        return ' aria-current="page"' if key == current else ""

    def cls(key):
        return " is-current" if key == current else ""
    pmu = [t for t in TREATMENTS if t["group"] == "pmu"]
    oth = [t for t in TREATMENTS if t["group"] != "pmu"]
    dsub = lambda items, f: "".join(f'<li><a href="{f(x["slug"])}">{tx(x["name"])}</a></li>' for x in items)
    lang_sw = f"""<div class="lang-switch" role="group"{ia(U["langLabel"], "aria-label")}><button type="button" value="sv" aria-pressed="true" lang="sv">SV</button><button type="button" value="en" aria-pressed="false" lang="en">EN</button></div>"""
    theme = f'<button type="button" class="icon-btn theme-btn"{ia(U["theme"], "aria-label")} aria-pressed="false">{ICON["moon"]}{ICON["sun"]}</button>'
    return f"""<a class="skip" href="#main">{tx(U["skip"])}</a>
{loader()}
<header class="site-header">
  <div class="util"><div class="container util__inner">
    <div class="util__info">
      <a href="kontakt.html">{ICON["pin"]}{tx(U["address"])}</a>
      <span>{ICON["video"]}{tx(U["consultLong"])}</span>
    </div>
    <div class="util__tools">{lang_sw}{theme}</div>
  </div></div>
  <div class="container nav">
    <a class="brand-link" href="index.html"{ia(L("Plaza Di Laura, till startsidan", "Plaza Di Laura, home"), "aria-label")}>{logo()}</a>
    <nav{ia(L("Huvudmeny", "Main menu"), "aria-label")}>
      <ul class="menu">
        <li><button type="button" class="menu__link{cls('beh')}" data-mega aria-expanded="false" aria-controls="mega-beh">{tx(U["treatments"])}{ICON["chev"]}</button></li>
        <li><button type="button" class="menu__link{cls('aka')}" data-mega aria-expanded="false" aria-controls="mega-aka">{tx(U["academy"])}{ICON["chev"]}</button></li>
        <li><a class="menu__link" href="resultat.html"{cur('res')}>{tx(U["results"])}</a></li>
        <li><a class="menu__link" href="om-laura.html"{cur('om')}>{tx(U["about"])}</a></li>
        <li><a class="menu__link" href="kontakt.html"{cur('kon')}>{tx(U["contact"])}</a></li>
      </ul>
    </nav>
    <div class="nav__actions">
      <a class="btn btn--primary btn--sm nav__book" href="boka.html">{tx(U["book"])}</a>
      <button type="button" class="icon-btn nav__burger" aria-expanded="false" aria-controls="drawer"{ia(U["menu"], "aria-label")}>{ICON["menu"]}</button>
    </div>
  </div>
  {mega_treatments()}
  {mega_academy()}
  <div class="progress" aria-hidden="true"></div>
</header>
<div class="drawer" id="drawer" role="dialog" aria-modal="true"{ia(U["menu"], "aria-label")} aria-hidden="true">
  <div class="drawer__top"><a class="brand-link" href="index.html">{logo()}</a>
    <button type="button" class="icon-btn drawer__close"{ia(U["close"], "aria-label")}>{ICON["close"]}</button></div>
  <div class="drawer__body"><ul class="drawer__list">
    <li><details class="drawer__acc"><summary>{tx(U["treatments"])}{ICON["plus"]}</summary><ul class="drawer__sub">
      {tx(GROUPS["pmu"], "h3")}{dsub(pmu, tfile)}
      {tx(L("Hud, hår, kropp och korrigering", "Skin, scalp, body and corrections"), "h3")}{dsub(oth, tfile)}
      <li><a href="behandlingar.html">{tx(U["allTreatments"])}</a></li></ul></details></li>
    <li><details class="drawer__acc"><summary>{tx(U["academy"])}{ICON["plus"]}</summary><ul class="drawer__sub">
      {dsub(COURSES, cfile)}<li><a href="akademi.html">{tx(L("Om akademin", "About the academy"))}</a></li></ul></details></li>
    <li><a href="resultat.html">{tx(U["results"])}</a></li>
    <li><a href="om-laura.html">{tx(U["about"])}</a></li>
    <li><a href="kontakt.html">{tx(U["contact"])}</a></li>
  </ul></div>
  <div class="drawer__foot">
    <a class="btn btn--primary btn--block" href="boka.html">{tx(U["book"])}</a>
    <div class="drawer__tools">{lang_sw}{theme}</div>
    {tx(L("Kungsgatan 11, Göteborg · Kostnadsfri konsultation", "Kungsgatan 11, Gothenburg · Free consultation"), "p", "drawer__info")}
  </div>
</div>"""


FOOT_LOGO = IMGS.get("logos", {}).get("wordmarkLight", "logo-wordmark-light.png")


def _foot_mark(word="PLAZA DI LAURA"):
    """Giant footer wordmark as live text (vector sharp at any width), one span per letter for the rise and hover wave."""
    out, i = [], 0
    for ch in word:
        if ch == " ":
            out.append('<span class="fmark__sp"></span>')
        else:
            out.append(f'<span class="fmark__c" style="--i:{i}">{ch}</span>')
            i += 1
    return "".join(out)


FOOT_MARK = _foot_mark()


JOURNEY = [
    (L("Konsultation", "Consultation"), L("Kostnadsfri, på plats, per telefon eller via Zoom, om du är osäker eller har frågor.", "Free, in person, by phone or on Zoom, if you are unsure or have questions."), "laura-portrait-pointing-up"),
    (L("Form och färg", "Shape and colour"), L("Laura mäter och målar en form efter dina ansiktsmått. Ni väljer färg efter hudtyp och underton.", "Laura measures and draws a shape to your proportions. Together you choose a colour for your skin type and undertone."), "laura-studio-ring-light-seated"),
    (L("Behandling", "Treatment"), L("Pigmentet läggs in i lager med en premiummaskin. Bedövning före och under.", "Pigment is built up in layers with a premium machine. Numbing before and during."), "pmu-machine-pink-pen"),
    (L("Återbesök", "Touch-up"), L("Efter ca 4 till 6 veckor för ett färdigt resultat. Eftervård ingår.", "After about 4 to 6 weeks for the finished result. Aftercare included."), "result-ombre-brows-healed-collage"),
    (L("Refill", "Refill"), L("Inom 12 månader. Annars kan du låta tatueringen läka bort.", "Within 12 months. Otherwise you can let the tattoo fade."), "result-powder-brows-healed-client-selfie"),
]


def journey_section():
    """How it works: step cards that stack like a deck as you scroll, beside a sticky index of the steps."""
    cards, index = [], []
    for i, (title, text, img) in enumerate(JOURNEY):
        n = f"{i + 1:02d}"
        cards.append(f"""<li class="jcard rv" id="steg-{i + 1}" style="--i:{i}">
        <div class="jcard__text"><span class="jcard__num" aria-hidden="true">{n}</span>{tx(title, "h3", "jcard__title")}{tx(text, "p")}</div>
        <div class="jcard__media">{pic(img, "(min-width: 1024px) 24vw, (min-width: 768px) 42vw, 92vw")}</div>
      </li>""")
        index.append(f'<li><a href="#steg-{i + 1}" data-jindex="{i}"><span class="jindex__n">{n}</span>{tx(title)}</a></li>')
    return f"""<section class="section journey" aria-labelledby="steps-h">
  <div class="container journey__grid">
    <div class="journey__intro rv">
      {tx(L("Så går det till", "How it works"), "span", "label")}
      {tx(L("Från konsultation till <em>färdigt resultat</em>", "From consultation to <em>finished result</em>"), "h2", "h-2", raw=True, extra=' id="steps-h"')}
      {tx(L("Gäller kosmetisk tatuering, till exempel puderbryn.", "Applies to cosmetic tattooing, for example powder brows."), "p", "journey__lead")}
      <ol class="jindex"{ia(L("Stegen", "The steps"), "aria-label")}>{"".join(index)}</ol>
      <a class="btn btn--primary" href="boka.html?t=konsultation">{tx(U["consult"])}{ICON["arrow"]}</a>
    </div>
    <ol class="jdeck" data-jdeck>
      {"".join(cards)}
    </ol>
  </div>
</section>"""


def footer(gallery=False):
    pmu = [t for t in TREATMENTS if t["group"] == "pmu"]
    oth = [t for t in TREATMENTS if t["group"] != "pmu"]
    lis = lambda items, f: "".join(f'<li><a href="{f(x["slug"])}">{tx(x["name"])}</a></li>' for x in items)
    social = "".join(f'<a href="{u}" target="_blank" rel="noopener" aria-label="{n}">{ICON[i]}</a>' for u, i, n in SOCIAL)
    lb = ""
    if gallery:
        lb = f"""<div class="lb" role="dialog" aria-modal="true"{ia(L("Bildvisning", "Image viewer"), "aria-label")} hidden>
  <div class="lb__top"><span class="lb__count tnum" aria-live="polite"></span><button type="button" class="icon-btn lb__close"{ia(U["close"], "aria-label")}>{ICON["close"]}</button></div>
  <div class="lb__stage"><img src="data:," alt=""><button type="button" class="icon-btn lb__side lb__side--prev"{ia(L("Föregående bild", "Previous image"), "aria-label")}>{ICON["left"]}</button><button type="button" class="icon-btn lb__side lb__side--next"{ia(L("Nästa bild", "Next image"), "aria-label")}>{ICON["arrow"]}</button></div>
  <p class="lb__cap"></p>
</div>"""
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer__top">
      <div class="footer__brand">
        <img src="assets/img/{IMGS.get("logos", {}).get("wordmarkLight", "logo-wordmark-light.png")}" width="{logo_size(IMGS.get("logos", {}).get("wordmarkLight", "logo-wordmark-light.png"))[0]}" height="{logo_size(IMGS.get("logos", {}).get("wordmarkLight", "logo-wordmark-light.png"))[1]}" alt="Plaza Di Laura">
        {tx(L("Klinik och skola för kosmetisk tatuering, avancerad hudvård och SMP på Kungsgatan 11 i centrala Göteborg. Sedan 2006.", "Clinic and school for cosmetic tattooing, advanced skin care and SMP at Kungsgatan 11 in central Gothenburg. Since 2006."), "p")}
        <div class="footer__social">{social}</div>
      </div>
      <div class="footer__cols">
        <div>{tx(GROUPS["pmu"], "h2")}<ul>{lis(pmu, tfile)}</ul></div>
        <div>{tx(L("Fler behandlingar", "More treatments"), "h2")}<ul>{lis(oth, tfile)}<li><a href="behandlingar.html">{tx(U["allTreatments"])}</a></li></ul></div>
        <div>{tx(U["academy"], "h2")}<ul>{lis(COURSES, cfile)}</ul></div>
        <div>{tx(L("Plaza Di Laura", "Plaza Di Laura"), "h2")}<ul>
          <li><a href="om-laura.html">{tx(U["about"])}</a></li>
          <li><a href="resultat.html">{tx(U["results"])}</a></li>
          <li><a href="kontakt.html">{tx(U["contact"])}</a></li>
          <li><a href="boka.html">{tx(U["book"])}</a></li>
          <li><a href="kundkort.html">{tx(L("Kundkort för personal", "Client records for staff"))}</a></li>
          <li><a href="https://bylaura.se/policies/privacy-policy" target="_blank" rel="noopener">{tx(L("Integritetspolicy", "Privacy policy"))}</a></li>
        </ul></div>
      </div>
    </div>
    <div class="footer__bottom">
      <span>© 2026 Plaza Di Laura · Kungsgatan 11, Göteborg</span>
      {tx(L("Avbokning av kosmetisk tatuering senast 24 timmar innan.", "Cosmetic tattoo appointments can be cancelled up to 24 hours before."))}
    </div>
    <div class="footer__mark rv rv-clip" aria-hidden="true"><div class="fmark">{FOOT_MARK}</div></div>
  </div>
</footer>
<div class="cursor" aria-hidden="true"><span class="cursor__label"></span></div>
<figure class="cpreview" aria-hidden="true"><img src="data:," alt=""></figure>
<button type="button" class="chat-launch" data-chat-open aria-expanded="false" aria-controls="chat">{ICON["chat"]}{tx(L("Frågor?", "Questions?"))}</button>
<div class="mbar"><a class="btn btn--primary" href="boka.html">{tx(U["book"])}</a><button type="button" class="icon-btn" data-chat-open aria-expanded="false" aria-controls="chat"{ia(L("Öppna frågor och svar", "Open questions and answers"), "aria-label")}>{ICON["chat"]}</button></div>
<button type="button" class="totop"{ia(L("Till toppen", "Back to top"), "aria-label")}>{ICON["up"]}</button>
<section class="chat" id="chat" role="dialog"{ia(L("Frågor och svar", "Questions and answers"), "aria-label")} aria-hidden="true">
  <div class="chat__head"><div>{tx(L("Frågor och svar", "Questions and answers"), "strong")}{tx(L("Snabba svar om behandlingar och utbildningar", "Quick answers about treatments and courses"))}</div>
    <button type="button" class="icon-btn chat__close"{ia(U["close"], "aria-label")}>{ICON["close"]}</button></div>
  <div class="chat__log" aria-live="polite"></div>
  <div class="chat__chips"></div>
  <form class="chat__form" autocomplete="off"><label class="sr-only" for="chat-q">{tx(L("Skriv din fråga", "Type your question"))}</label>
    <input id="chat-q" type="text"{ia(L("Skriv din fråga", "Type your question"), "placeholder")}>
    <button type="submit"{ia(L("Skicka", "Send"), "aria-label")}>{ICON["send"]}</button></form>
</section>
{lb}
</body>
</html>
"""


def crumbs(items):
    lis = []
    for i, (label, href) in enumerate(items):
        if href and i < len(items) - 1:
            lis.append(f'<li><a href="{href}">{tx(label)}</a></li>')
        else:
            lis.append(f'<li aria-current="page">{tx(label)}</li>')
    return f'<nav class="crumbs container"{ia(L("Brödsmulor", "Breadcrumbs"), "aria-label")}><ol>{"".join(lis)}</ol></nav>'


def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": sv(label), "item": SITE + "/" + (href or "").replace(".html", "").replace("index", "")}
        for i, (label, href) in enumerate(items)]}


ORG_LD = {
    "@context": "https://schema.org", "@type": "HealthAndBeautyBusiness", "name": "Plaza Di Laura",
    "url": SITE + "/", "image": SITE + "/assets/img/og-image.jpg", "foundingDate": "2006",
    "address": {"@type": "PostalAddress", "streetAddress": "Kungsgatan 11", "addressLocality": "Göteborg", "addressCountry": "SE"},
    "founder": {"@type": "Person", "name": "Laura Lindqvist", "jobTitle": "PMU-artist och utbildare"},
    "sameAs": [u for u, _, _ in SOCIAL],
}


def write(path, content):
    if "—" in content:
        raise SystemExit(f"em dash found in {path}")
    with open(os.path.join(ROOT, path), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("  wrote", path, f"{len(content) // 1024} KB")


# ---------------------------------------------------------------- sections
def result_cards(items, track=True):
    out = []
    for r in items:
        slug = r["slug"]
        m = img_meta(slug)
        if not m:
            continue
        cat = r.get("filter", "")
        cat_label = dict(FILTERS).get(cat, L(""))
        full = img_src(slug, 1600)
        size = "(min-width: 1200px) 330px, (min-width: 700px) 30vw, 70vw" if track else "(min-width: 1200px) 300px, (min-width: 900px) 30vw, 50vw"
        out.append(f"""<figure class="rcard" data-cat="{cat}"><button type="button" data-full="{full}" data-cap-sv="{att(sv(r["caption"]))}" data-cap-en="{att(en(r["caption"]))}"{ia(L("Visa större: " + sv(r["caption"]), "View larger: " + en(r["caption"])), "aria-label")}>{pic(slug, size)}</button>
  <figcaption>{tx(cat_label)}{tx(r["caption"])}</figcaption></figure>""")
    return "".join(out)


def filter_bar(target):
    btns = "".join(f'<button type="button" class="filter" value="{k}" aria-pressed="{"true" if k == "all" else "false"}">{tx(v)}</button>' for k, v in FILTERS)
    return f'<div class="filters" role="group" data-filter-group="{target}"{ia(L("Filtrera resultat", "Filter results"), "aria-label")}>{btns}</div>'


def guide_section(compact=False):
    def step(n, name, legend, opts):
        o = "".join(f'<label class="opt"><input type="radio" name="{name}" value="{v}">{tx(lbl)}</label>' for v, lbl in opts)
        return f"""<fieldset class="guide__step"{' hidden' if n > 1 else ''}>
  {tx(L(f"Fråga {n} av 4", f"Question {n} of 4"), "span", "guide__count")}
  {tx(legend, "legend")}
  <div class="guide__opts">{o}</div></fieldset>"""
    steps = [
        step(1, "g-tattoo", L("Har du en tidigare tatuering i brynen?", "Do you have an existing tattoo in your brows?"),
             [("none", L("Nej", "No")), ("ok", L("Ja, den är jämn och har fin färg", "Yes, it is even and the colour is good")), ("bad", L("Ja, den är missfärgad, ojämn eller för mörk", "Yes, it is discoloured, uneven or too dark"))]),
        step(2, "g-skin", L("Hur är din hy vid brynen?", "What is your skin like around the brows?"),
             [("normal", L("Normal eller torr", "Normal or dry")), ("oily", L("Fet, eller med förstorade porer", "Oily, or with enlarged pores"))]),
        step(3, "g-hair", L("Hur mycket egna brynhår har du?", "How many brow hairs of your own do you have?"),
             [("some", L("Jag har strån men vill fylla ut eller jämna till formen", "I have hairs but want to fill in or even out the shape")), ("few", L("Väldigt lite strån", "Very few hairs"))]),
        step(4, "g-look", L("Vilket resultat tycker du om?", "Which result do you like?"),
             [("powder", L("Mjukt pudrat, som ett lätt ifyllt bryn med smink", "Soft and powdered, like a lightly filled-in brow with makeup")), ("strokes", L("Hårstrån som ser ut som egna strån", "Hair strokes that look like natural hairs"))]),
    ]

    def result(key, title):
        t = TBY.get(key)
        if not t:
            return ""
        img = treatment_image(t)
        name = t["name"]
        return f"""<div data-result="{key}" hidden>
  <div class="guide__result-top">{pic(img, "110px", decorative=True)}<div>{tx(L("Vår rekommendation", "Our recommendation"), "span", "label")}{tx(title or name, "h3")}</div></div>
  <ul class="guide__why"></ul>
  <div class="btn-row"><a class="btn btn--primary" href="boka.html?t={key}">{tx(L("Boka " + sv(name).lower(), "Book " + en(name).lower()))}{ICON["arrow"]}</a>
  <a class="btn btn--ghost" href="{tfile(key)}">{tx(L("Läs om " + sv(name).lower(), "About " + en(name).lower()))}</a></div>
  <p class="note">{tx(L("Osäker? ", "Unsure? "))}<a href="boka.html?t=konsultation">{tx(L("Boka en kostnadsfri konsultation", "Book a free consultation"))}</a>{tx(L(" eller ", " or "))}<button type="button" class="link-arrow" data-guide-restart style="border:0;background:none;padding:0;font-size:inherit">{tx(L("gör om testet", "start again"))}</button></p>
</div>"""
    res = result("puderbryn", None) + result("strokes", None) + result("lift", None)
    return f"""<section class="section section--tint" id="brynguiden" aria-labelledby="guide-h">
  <div class="container guide">
    <div class="guide__intro rv">
      {tx(L("Brynguiden", "Brow guide"), "span", "label")}
      {tx(L("Puder eller strokes? Hitta <em>rätt</em> brynmetod", "Powder or strokes? Find the <em>right</em> brow method"), "h2", "h-2", raw=True, extra=' id="guide-h"')}
      {tx(L("Microblading passar inte alla. Svara på fyra frågor så får du en rekommendation byggd på Lauras egna riktlinjer för fet hy, porer, egna strån och gamla tatueringar.", "Microblading does not suit everyone. Answer four questions and get a recommendation based on Laura's own guidelines on oily skin, pores, natural hairs and old tattoos."), "p")}
      {tx(L("Rekommendationen ersätter inte en bedömning. Laura går alltid igenom form och färg med dig innan behandlingen.", "The recommendation does not replace an assessment. Laura always goes through shape and colour with you before the treatment."), "p", "guide__note")}
    </div>
    <div class="guide__card rv" data-guide>
      <div class="guide__progress" aria-hidden="true"><span></span><span></span><span></span><span></span></div>
      {"".join(steps)}
      <div class="guide__nav"><button type="button" class="btn btn--ghost" data-guide-back>{tx(L("Tillbaka", "Back"))}</button><button type="button" class="btn btn--ink" data-guide-next disabled>{tx(L("Nästa", "Next"))}</button></div>
      <div class="guide__result" hidden aria-live="polite">{res}</div>
    </div>
  </div>
</section>"""


def review_feature(r):
    return f"""<figure class="review-feature rv">{tx(r["text"], "blockquote")}<figcaption><strong>{esc(r["name"])}</strong> · {tx(L("Kund hos Plaza Di Laura", "Plaza Di Laura client"))}</figcaption></figure>"""


def review_card(r):
    return f"""<figure class="review rv">{tx(r["text"], "blockquote")}<cite><strong>{esc(r["name"])}</strong></cite></figure>"""


def reviews_section(title=None, topic=None, limit=9, tint=False):
    if not REVIEWS:
        return ""
    revs = list(REVIEWS)
    if topic:
        revs.sort(key=lambda r: 0 if r.get("topic") == topic else 1)
    feat = max(revs[:4], key=lambda r: len(sv(r["text"]))) if not topic else revs[0]
    rest = [r for r in revs if r is not feat][: limit - 1]
    return f"""<section class="section{' section--tint' if tint else ''}" aria-labelledby="rev-h">
  <div class="container">
    <div class="section-head rv"><div>{tx(L("Omdömen", "Reviews"), "span", "label")}{tx(title or L("Vad kunderna <em>säger</em>", "What clients <em>say</em>"), "h2", "h-2", raw=True, extra=' id="rev-h"')}</div></div>
    <div class="reviews">{review_feature(feat)}<div class="review-cols">{"".join(review_card(r) for r in rest)}</div></div>
  </div>
</section>"""


def cta_band(title, text, primary, secondary=None, tint=True):
    p_href, p_label = primary
    sec = f'<a class="btn btn--ghost" href="{secondary[0]}">{tx(secondary[1])}</a>' if secondary else ""
    return f"""<section class="section{' section--tint' if tint else ''}">
  <div class="container cta-band rv"><div>{tx(title, "h2", "h-2")}{tx(text, "p")}</div>
  <div class="btn-row"><a class="btn btn--primary" href="{p_href}">{tx(p_label)}{ICON["arrow"]}</a>{sec}</div></div>
</section>"""


def visit_section():
    social = " · ".join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for u, _, n in SOCIAL)
    return f"""<section class="section" id="besok" aria-labelledby="visit-h">
  <div class="container visit">
    <div class="visit__info rv">
      {tx(L("Besök oss", "Visit us"), "span", "label")}
      {tx(L("Klinik och skola mitt i <em>Göteborg</em>", "Clinic and school in central <em>Gothenburg</em>"), "h2", "h-2", raw=True, extra=' id="visit-h"')}
      <dl>
        <div>{tx(L("Adress", "Address"), "dt")}{tx(L("Kungsgatan 11, Göteborg", "Kungsgatan 11, Gothenburg"), "dd")}</div>
        <div>{tx(L("Konsultation", "Consultation"), "dt")}{tx(L("Kostnadsfri, på plats, per telefon eller via Zoom", "Free, in person, by phone or on Zoom"), "dd")}</div>
        <div>{tx(L("Följ oss", "Follow us"), "dt")}<dd>{social}</dd></div>
      </dl>
      <div class="btn-row"><a class="btn btn--primary" href="boka.html">{tx(U["book"])}{ICON["arrow"]}</a><a class="btn btn--ghost" href="kontakt.html">{tx(L("Kontakta oss", "Contact us"))}</a></div>
    </div>
    <div class="map rv">
      <div class="map__placeholder">{ICON["pin"].replace("<svg", '<svg class="map__pin"')}
        <strong>Kungsgatan 11</strong>
        {tx(L("Kartan laddas från Google Maps först när du väljer att visa den.", "The map loads from Google Maps only when you choose to show it."), "p")}
        <div class="btn-row" style="justify-content:center"><button type="button" class="btn btn--ink btn--sm" data-map-load>{tx(L("Visa karta", "Show map"))}</button>
        <a class="btn btn--ghost btn--sm" href="{DIRECTIONS}" target="_blank" rel="noopener">{tx(L("Vägbeskrivning", "Directions"))}</a></div>
      </div>
    </div>
  </div>
</section>"""


def ba_section():
    items = [("bryn", "puderbryn", "result-powder-brows-before-after-1"), ("lappar", "lappar", "result-soft-lips-before-after"), ("fraknar", "fraknar", "result-faux-freckles-before-after-1")]
    rby = {r["slug"]: r for r in RESULTS}
    items = [(k, t, s_) for k, t, s_ in items if img_meta(f"ba-{k}-before") and TBY.get(t)]
    if not items:
        return ""
    panes, tabs = "", ""
    for i, (k, tslug, rslug) in enumerate(items):
        t = TBY[tslug]
        cap = (rby.get(rslug) or {}).get("caption") or t["fullName"]
        hidden = "" if i == 0 else " hidden"
        panes += f"""<div class="ba" data-ba data-key="{k}" data-book="boka.html?t={tslug}"{hidden}>
  {pic(f"ba-{k}-after", "(min-width: 960px) 46vw, 92vw", cls="ba__after")}
  <div class="ba__before">{pic(f"ba-{k}-before", "(min-width: 960px) 46vw, 92vw")}</div>
  {tx(L("Före", "Before"), "span", "ba__tag ba__tag--before")}{tx(L("Efter", "After"), "span", "ba__tag ba__tag--after")}
  <div class="ba__handle" aria-hidden="true"><span>{ICON["left"]}{ICON["arrow"]}</span></div>
  <input class="ba__range" type="range" min="0" max="100" value="50"{ia(L("Dra för att jämföra före och efter: " + sv(t["name"]), "Drag to compare before and after: " + en(t["name"])), "aria-label")}>
</div>"""
        tabs += f"""<button type="button" class="ba__tab" data-ba-tab="{k}" aria-pressed="{"true" if i == 0 else "false"}">{tx(t["name"], "strong")}{tx(cap, "span")}</button>"""
    return f"""<section class="section ba-section" aria-labelledby="ba-h">
  <div class="container ba-grid">
    <div class="ba-stage rv rv-clip">{panes}</div>
    <div class="ba-info rv">
      {tx(L("Före och efter", "Before and after"), "span", "label")}
      {tx(L("Dra och se <em>skillnaden</em>", "Drag to see the <em>difference</em>"), "h2", "h-2", raw=True, extra=' id="ba-h"')}
      {tx(L("Kunder fotograferade i kliniken före och efter behandlingen. Dra i reglaget för att jämföra.", "Clients photographed in the clinic before and after treatment. Drag the handle to compare."), "p")}
      <div class="ba__tabs" role="group"{ia(L("Välj behandling", "Choose treatment"), "aria-label")}>{tabs}</div>
      <div class="btn-row"><a class="btn btn--primary" href="boka.html?t={items[0][1]}" data-ba-book>{tx(U["book"])}{ICON["arrow"]}</a><a class="btn btn--ghost" href="resultat.html">{tx(L("Alla resultat", "All results"))}</a></div>
    </div>
  </div>
</section>"""


REVIEW_ORDER = ["Susanna A.", "Linda L.", "Anneli W.", "Frida A.", "Alexandra Ö.", "Tommy B.", "Paula K.", "Linda E.", "Agneta L.", "My K.", "Andela J.", "Jasmine Z."]


def reviews_featured():
    """One large featured quote at a time, a row of client names as tabs (the active one fills as it auto-advances)."""
    if not REVIEWS:
        return ""
    rs = sorted(REVIEWS, key=lambda r: REVIEW_ORDER.index(r["name"]) if r["name"] in REVIEW_ORDER else 99)
    quotes, tabs = [], []
    for i, r in enumerate(rs):
        cls = "rvw__q" + (" is-long" if len(sv(r["text"])) > 150 else "") + (" is-active" if i == 0 else "")
        quotes.append(f'<figure class="{cls}" id="rvw-{i}" role="tabpanel" aria-labelledby="rvw-t{i}">{tx(r["text"], "blockquote")}<figcaption>{esc(r["name"])}</figcaption></figure>')
        tabs.append(f'<button type="button" class="rvw__tab" role="tab" id="rvw-t{i}" aria-controls="rvw-{i}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}">{esc(r["name"])}</button>')
    n = len(rs)
    return f"""<section class="section section--tint rvw-sec" aria-labelledby="rev-h">
  <div class="container rvw" data-rvw>
    <div class="rvw__head rv">
      {tx(L("Omdömen", "Reviews"), "span", "label")}
      {tx(L("Vad kunderna <em>säger</em>", "What clients <em>say</em>"), "h2", "h-2", raw=True, extra=' id="rev-h"')}
    </div>
    <div class="rvw__main rv">
      <button type="button" class="rvw__arrow" data-rvw-prev{ia(L("Föregående omdöme", "Previous review"), "aria-label")}>{ICON["left"]}</button>
      <div class="rvw__stage" aria-live="off">{"".join(quotes)}</div>
      <button type="button" class="rvw__arrow" data-rvw-next{ia(L("Nästa omdöme", "Next review"), "aria-label")}>{ICON["arrow"]}</button>
    </div>
    <div class="rvw__tabs rv" role="tablist"{ia(L("Välj omdöme", "Choose a review"), "aria-label")}>{"".join(tabs)}</div>
    <div class="rvw__meta rv">
      <span class="rvw__count" data-rvw-count aria-hidden="true">01 / {n:02d}</span>
      {tx(L("Ordagrant från kunder hos Plaza Di Laura", "Word for word from Plaza Di Laura clients"), "span", "rvw__note")}
      <button type="button" class="rvw__play" data-rvw-play aria-pressed="false"{ia(L("Pausa bytet av omdömen", "Pause rotating reviews"), "aria-label")}>{PAUSE_BTN_ICONS}</button>
    </div>
  </div>
</section>"""


def meet_section(meet_img, meet_p):
    """Meet Laura: portrait collage with a slowly turning title badge, her own headline as a pull quote and three facts."""
    head = ABOUT.get("headline")
    facts = [("2006", L("Etablerat", "Established")),
             ("15+", L("År med kosmetisk tatuering", "Years in cosmetic tattooing")),
             ("20+", L("År i skönhetsbranschen", "Years in the beauty industry"))]
    facts_html = "".join(f'<li><strong>{a}</strong>{tx(b)}</li>' for a, b in facts)
    inset = pic("laura-portrait-black-white-denim", "(min-width: 960px) 15vw, 36vw", decorative=True)
    return f"""<section class="section meet-sec" aria-labelledby="meet-h">
  <div class="container meet meet--home">
    <div class="meet__visual">
      <div class="rv rv-clip meet__media">{pic(meet_img, "(min-width: 960px) 36vw, 84vw")}</div>
      {f'<div class="rv rv-clip meet__inset">{inset}</div>' if inset else ''}
      <div class="meet__badge" aria-hidden="true">
        <svg viewBox="0 0 200 200"><defs><path id="meet-ring" d="M100,100 m-74,0 a74,74 0 1,1 148,0 a74,74 0 1,1 -148,0"/></defs><text><textPath href="#meet-ring" textLength="456" lengthAdjust="spacing"{' data-en="Founder · PMU artist · Educator · Gothenburg ·"'}>Grundare · PMU-artist · Utbildare · Göteborg ·</textPath></text></svg>
        {BROW}
      </div>
    </div>
    <div class="meet__text rv">
      {tx(L("Möt Laura", "Meet Laura"), "span", "label")}
      <h2 class="meet__name" id="meet-h">Laura <em>Lindqvist</em></h2>
      {tx(L("Grundare, PMU-artist och utbildare", "Founder, PMU artist and educator"), "p", "meet__role")}
      {tx(head, "blockquote", "meet__quote") if head else ""}
      {meet_p}
      <ul class="meet__facts">{facts_html}</ul>
      <a class="link-arrow" href="om-laura.html">{tx(L("Läs mer om Laura", "More about Laura"))}{ICON["arrow"]}</a>
    </div>
  </div>
</section>"""


# ---------------------------------------------------------------- pages
def page_home():
    portraits = PORTRAITS
    hero_main = SLOT["heroMain"]
    rby = {r["slug"]: r for r in RESULTS}
    slides = [(SLOT["heroInset"], (rby.get(SLOT["heroInset"]) or {}).get("caption")),
              ("result-powder-brows-strokes-front", (rby.get("result-powder-brows-strokes-front") or {}).get("caption")),
              ("faux-freckles-curly-hair-closeup", L("Faux freckles, fräknar.", "Faux freckles."))]
    slides = [(s_, c_) for s_, c_ in slides if img_meta(s_) and c_]
    inset_html = ""
    if slides:
        imgs = "".join(f'<div class="hero__slide{" is-active" if i == 0 else ""}">{pic(s_, "250px", lazy=False, decorative=i > 0)}</div>' for i, (s_, c_) in enumerate(slides))
        caps = "".join(tx(c_, "span", "hero__cap" + (" is-active" if i == 0 else "")) for i, (s_, c_) in enumerate(slides))
        dots = "".join(f'<button type="button" aria-pressed="{"true" if i == 0 else "false"}"{ia(L(f"Visa resultat {i + 1}", f"Show result {i + 1}"), "aria-label")}></button>' for i in range(len(slides)))
        inset_html = (f'<figure class="hero__inset" data-slides><div class="hero__slides">{imgs}</div>'
                      f'<figcaption>{caps}</figcaption><div class="hero__dots" role="group"{ia(L("Välj resultat", "Choose result"), "aria-label")}>{dots}</div></figure>')
    pmu = [t for t in TREATMENTS if t["group"] == "pmu"]
    other = [t for t in TREATMENTS if t["group"] != "pmu"]
    other.sort(key=lambda t: ["smp", "microneedling", "lift", "fettfrysning"].index(t["slug"]) if t["slug"] in ("smp", "microneedling", "lift", "fettfrysning") else 9)
    rows = "".join(f"""<li class="tlist__row rv"><a href="{tfile(t['slug'])}">{pic(treatment_image(t), "76px", decorative=True)}<span>{tx(t["name"], "span", "tlist__name")}{tx(t["short"], "span", "tlist__short")}</span>{ICON["arrow"].replace("<svg", '<svg class="tlist__arrow"')}</a></li>""" for t in pmu)
    previews = "".join(f'<figure class="{"is-active" if i == 0 else ""}">{pic(treatment_image(t), "(min-width: 1024px) 40vw, 1px", decorative=True)}{tx(t["fullName"], "figcaption")}</figure>' for i, t in enumerate(pmu))
    cards = "".join(f"""<a class="tcard rv" href="{tfile(t['slug'])}">{pic(treatment_image(t), "(min-width: 1024px) 40vw, (min-width: 720px) 50vw, 100vw", decorative=True)}<div class="tcard__body">{tx(GROUPS[t["group"]], "span", "label")}{tx(t["name"], "h3")}<div class="tcard__reveal">{tx(t["short"], "p")}<span class="path__go">{tx(U["readMore"])}{ICON["arrow"]}</span></div></div></a>""" for t in other)
    res_items = RESULTS[:12]
    # paths
    brow_img = SLOT["pathTreat"]
    stud_img = SLOT["pathAcademy"]
    # no trauma
    nt_img = SLOT["nt"]
    sus = next((r for r in REVIEWS if r["name"].startswith("Susanna")), None)
    nt_quote = ""
    if sus:
        nt_quote = f'<blockquote class="nt__quote">{tx(L("Jag tycker inte om nålar, men Laura trollar bort detta med sin proffsighet och humor.", "I don&#39;t like needles, but Laura makes that disappear with her professionalism and humour."), raw=True)}<cite>Susanna A.</cite></blockquote>'
    # academy band
    career = ACADEMY.get("careerBlock", {})
    courses_list = "".join(f'<li><a href="{cfile(c["slug"])}" data-preview="{img_src(course_image(c), 640)}">{tx(c["name"])}{tx(days_label(c)) if c.get("days") else ""}</a></li>' for c in COURSES)
    ticks = "".join(tx(i, "li") for i in career.get("items", []))
    aband_imgs = [s for s, m in IMAGES.items() if m.get("kind") == "course" and m.get("widths")]
    a1, a2 = SLOT["aband1"], SLOT["aband2"]
    # meet
    meet_img = SLOT["meet"]
    story = ABOUT.get("story", [])
    meet_p = "".join(tx(p, "p") for p in (story[0]["paragraphs"][:1] if story else []))

    title = L("Kosmetisk tatuering i Göteborg | Plaza Di Laura", "Cosmetic tattooing in Gothenburg | Plaza Di Laura")
    desc = L("Kosmetisk tatuering, microneedling och SMP på Kungsgatan 11 i Göteborg. Laura Lindqvist har 20 års erfarenhet och utbildar PMU-artister. Boka konsultation.",
             "Cosmetic tattooing, microneedling and SMP at Kungsgatan 11, Gothenburg. Laura Lindqvist has 20 years of experience and trains PMU artists. Book a consultation.")
    body = f"""<body>
{header('home')}
<main id="main">
<section class="hero">
  <div class="hero__grid">
    <div class="hero__text">
      <div class="hero__copy">
        {tx(L("Kosmetisk tatuering · Hudvård · Akademi", "Cosmetic tattooing · Skin · Academy"), "span", "label")}
        {tx(split_words(L("Kosmetisk tatuering i Göteborg med naturliga resultat", "Cosmetic tattooing in Gothenburg with natural results"), em=L("naturliga", "natural")), "h1", "h-display hero__title is-split", raw=True)}
        {tx(L("Laura Lindqvist har arbetat i skönhetsbranschen i över 20 år, varav de senaste 15 med kosmetisk tatuering. Hennes filosofi är resultat som ser ut som dina egna, även utan smink.", "Laura Lindqvist has worked in the beauty industry for more than 20 years, the last 15 specialising in cosmetic tattooing. Her philosophy: results that look like your own, even without makeup."), "p", "lead")}
        <div class="btn-row"><a class="btn btn--primary" href="boka.html">{tx(U["book"])}{ICON["arrow"]}</a><a class="btn btn--ghost" href="boka.html?t=konsultation">{tx(U["consult"])}</a></div>
      </div>
      <div class="hero__foot">
        <ul class="hero__meta">
          <li>{tx(U["since"])}</li>
          <li>{tx(U["address"])}</li>
        </ul>
        <span class="hero__scroll" aria-hidden="true"><i></i>{tx(L("Scrolla", "Scroll"))}</span>
      </div>
    </div>
    <div class="hero__media">
      <div class="hero__frame">{pic(hero_main, "(min-width: 960px) 50vw, 100vw", cls="hero__main", eager=True)}</div>
      <p class="hero__sign"><span>Laura Lindqvist</span>{tx(L("Grundare, PMU-artist och utbildare", "Founder, PMU artist and educator"))}</p>
      {inset_html}
    </div>
  </div>
</section>

<section class="proof" aria-label="{att('Plaza Di Laura i korthet')}" data-en-aria="Plaza Di Laura at a glance">
  <div class="container"><ul class="proof__list">
    <li>{tx(U["since"], "strong")}{tx(L("Klinik och skola på Kungsgatan i centrala Göteborg", "Clinic and school on Kungsgatan in central Gothenburg"))}</li>
    <li>{tx(L("20+ år", "20+ years"), "strong", extra=" data-count")}{tx(L("i skönhetsbranschen, 15 av dem med kosmetisk tatuering", "in the beauty industry, 15 of them in cosmetic tattooing"))}</li>
    <li>{tx(L("No Trauma-teknik", "No Trauma technique"), "strong")}{tx(L("Lauras egen metod, utvecklad efter flera års tester", "Laura's own method, developed over years of testing"))}</li>
    <li>{tx(L("Premiumverktyg", "Premium tools"), "strong")}{tx(L("Biomaser, Kwadron, Permablend, LI Pigments, MAST och Cheyenne", "Biomaser, Kwadron, Permablend, LI Pigments, MAST and Cheyenne"))}</li>
  </ul></div>
</section>

<section class="ticker band"{ia(L("Våra behandlingar", "Our treatments"), "aria-label")}>
  {marquee([f'<li><a href="{tfile(t["slug"])}">{tx(t["name"])}</a></li><li class="ticker__sep" aria-hidden="true">{BROW}</li>' for t in TREATMENTS], L("Behandlingar som rullar förbi", "Scrolling list of treatments"), "ticker__mq", 55)}
  <button type="button" class="marquee__toggle" aria-pressed="false"{ia(L("Pausa rörelsen", "Pause motion"), "aria-label")}>{PAUSE_BTN_ICONS}</button>
</section>

<section class="section section--tight">
  <div class="container paths">
    <a class="path rv" href="behandlingar.html">{pic(brow_img, "(min-width: 800px) 54vw, 100vw", decorative=True)}<div class="path__body">
      {tx(L("För dig som kund", "For clients"), "span", "label")}{tx(U["treatments"], "h2")}
      {tx(L("Kosmetisk tatuering, microneedling, SMP, LIFT Ink Removal och fettfrysning.", "Cosmetic tattooing, microneedling, SMP, LIFT Ink Removal and fat freezing."), "p")}
      <span class="path__go">{tx(U["allTreatments"])}{ICON["arrow"]}</span>
      <span class="path__more">{"".join(tx(t["name"], "span", extra=f' style="--i:{i}"') for i, t in enumerate(TREATMENTS))}</span></div></a>
    <a class="path rv" href="akademi.html">{pic(stud_img, "(min-width: 800px) 46vw, 100vw", decorative=True)}<div class="path__body">
      {tx(L("För dig som vill utbilda dig", "For future artists"), "span", "label")}{tx(L("Plaza Di Laura Academy", "Plaza Di Laura Academy"), "h2")}
      {tx(L("Lär dig kosmetisk tatuering av Laura. Max 2 elever per kurstillfälle.", "Learn cosmetic tattooing from Laura. Max 2 students per course."), "p")}
      <span class="path__go">{tx(L("Se utbildningar", "See courses"))}{ICON["arrow"]}</span>
      <span class="path__more">{"".join(tx(c["name"], "span", extra=f' style="--i:{i}"') for i, c in enumerate(COURSES))}</span></div></a>
  </div>
</section>

<section class="section" id="behandlingar" aria-labelledby="pmu-h">
  <div class="container">
    <div class="section-head rv"><div>{tx(GROUPS["pmu"], "span", "label")}{tx(L("Kosmetisk tatuering som ser ut som <em>din egen</em>", "Cosmetic tattooing that looks like <em>your own</em>"), "h2", "h-2", raw=True, extra=' id="pmu-h"')}
      {tx(L("Laura är emot kosmetisk tatuering som trendar. Form och färg anpassas efter din hudtyp, underton, hårfärg och dina ansiktsmått.", "Laura is against trend-driven cosmetic tattooing. Shape and colour are matched to your skin type, undertone, hair colour and facial proportions."), "p")}</div>
      <a class="link-arrow" href="behandlingar.html">{tx(U["allTreatments"])}{ICON["arrow"]}</a></div>
    <div class="tlist"><ul class="tlist__rows">{rows}</ul><div class="tlist__preview" aria-hidden="true">{previews}</div></div>
  </div>
</section>

<section class="section section--surface" aria-labelledby="oth-h">
  <div class="container">
    <div class="section-head rv"><div>{tx(L("Fler behandlingar", "More treatments"), "span", "label")}{tx(L("Hud, hårbotten och <em>korrigering</em>", "Skin, scalp and <em>corrections</em>"), "h2", "h-2", raw=True, extra=' id="oth-h"')}</div></div>
    <div class="tgrid">{cards}</div>
  </div>
</section>

{ba_section()}

{guide_section()}

<section class="section" id="resultat" aria-labelledby="res-h" data-gallery>
  <div class="container">
    <div class="section-head rv"><div>{tx(U["results"], "span", "label")}{tx(L("Före, direkt efter och <em>läkt</em>", "Before, right after and <em>healed</em>"), "h2", "h-2", raw=True, extra=' id="res-h"')}
      {tx(L("Resultat från kliniken på bryn, läppar och fräknar, med Lauras egna bildtexter.", "Results from the clinic on brows, lips and freckles, with Laura's own captions."), "p")}</div>
      <div class="rtrack__nav"><button type="button" class="round-btn" data-track-prev="home-track"{ia(L("Föregående", "Previous"), "aria-label")}>{ICON["left"]}</button><button type="button" class="round-btn" data-track-next="home-track"{ia(L("Nästa", "Next"), "aria-label")}>{ICON["arrow"]}</button></div></div>
    <div class="rv" style="margin-bottom:20px">{filter_bar("home-track")}</div>
    <div class="rtrack" id="home-track" tabindex="0"{ia(L("Resultatgalleri", "Results gallery"), "aria-label")}>{result_cards(res_items)}</div>
    <p style="margin-top:20px"><a class="link-arrow" href="resultat.html">{tx(L("Se alla resultat", "See all results"))}{ICON["arrow"]}</a></p>
  </div>
</section>

<section class="section section--surface" aria-labelledby="nt-h">
  <div class="container nt">
    <div class="rv nt__text">
      <svg class="nt__stroke" viewBox="0 0 600 170" aria-hidden="true"><path pathLength="1" d="M12 150 C 150 52, 330 6, 470 30 S 588 96, 594 118"/></svg>
      {tx(L("No Trauma Technique", "No Trauma Technique"), "span", "label")}
      {tx(L("Utvecklad av Laura, för en <em>fin läkning</em>", "Developed by Laura, for <em>clean healing</em>"), "h2", "h-2", raw=True, extra=' id="nt-h"')}
      {tx(L("Efter flera års praktiska tester av maskiner, nålar, pigment, hastighet, teknik och eftervård har Laura utvecklat sin egen metod. På grund av minimalt vävnadstrauma blir resultaten naturliga med en fin läkning.", "After years of hands-on testing of machines, needles, pigments, speed, technique and aftercare, Laura developed her own method. With minimal tissue trauma, results look natural and heal well."), "p", "lead")}
      <ul class="nt__list">
        <li>{tx(L("Ingen smärta", "No pain"), "strong")}{tx(L("Bedövningssalva före och under behandlingen", "Numbing cream before and during treatment"))}</li>
        <li>{tx(L("Minimal svullnad", "Minimal swelling"), "strong")}{tx(L("Och inga blåmärken", "And no bruising"))}</li>
        <li>{tx(L("Ingen blödning", "No bleeding"), "strong")}{tx(L("Tack vare minimalt vävnadstrauma", "Thanks to minimal tissue trauma"))}</li>
        <li>{tx(L("Inga skorpor", "No scabs"), "strong")}{tx(L("Under läkningen", "While it heals"))}</li>
      </ul>
    </div>
    <div class="nt__media rv rv-clip">{pic(nt_img, "(min-width: 960px) 40vw, 92vw")}{nt_quote}</div>
  </div>
</section>

{journey_section()}

{reviews_featured()}

<section class="section band" aria-labelledby="aca-h">
  <div class="container aband">
    <div class="aband__media rv rv-clip">{pic(a1, "(min-width: 1024px) 44vw, 92vw")}{pic(a2, "(min-width: 1024px) 20vw, 40vw")}</div>
    <div class="rv">
      {tx(L("Plaza Di Laura Academy", "Plaza Di Laura Academy"), "span", "label")}
      {tx(career.get("title") or L("Starta din karriär inom kosmetisk tatuering", "Start your career in cosmetic tattooing"), "h2", "h-2", extra=' id="aca-h"')}
      {tx(career.get("paragraph"), "p") if career.get("paragraph") else ""}
      <ul class="aband__courses">{courses_list}</ul>
      <ul class="ticks">{ticks}</ul>
      <div class="btn-row"><a class="btn btn--light" href="boka.html?t=kursradgivning">{tx(U["courseAdvice"])}{ICON["arrow"]}</a><a class="btn btn--outline-light" href="akademi.html">{tx(L("Om akademin", "About the academy"))}</a></div>
    </div>
  </div>
</section>

{meet_section(meet_img, meet_p)}

{visit_section()}
</main>
"""
    return head(title, desc, "index.html", [ORG_LD]) + body + footer(gallery=True)


def treatment_cards(items):
    out = []
    for t in items:
        facts = t.get("facts") or []
        meta = sv(facts[0]["value"]) if facts else ""
        meta_html = tx(L(sv(facts[0]["label"]) + ": " + sv(facts[0]["value"]), en(facts[0]["label"]) + ": " + en(facts[0]["value"])), "span", "card__meta") if facts else ""
        out.append(f"""<a class="card rv" href="{tfile(t['slug'])}"><div class="card__img">{pic(treatment_image(t), "(min-width: 1024px) 30vw, (min-width: 640px) 45vw, 92vw", decorative=True)}<span class="card__go" aria-hidden="true">{ICON["arrow"]}</span></div>
  {tx(t["name"], "h3")}{tx(t["short"], "p")}{meta_html}</a>""")
    return "".join(out)


def page_treatments():
    groups = [("pmu", [t for t in TREATMENTS if t["group"] == "pmu"]),
              ("other", [t for t in TREATMENTS if t["group"] != "pmu"])]
    labels = {"pmu": GROUPS["pmu"], "other": L("Hud, hårbotten, kropp och korrigering", "Skin, scalp, body and corrections")}
    blocks = ""
    for key, items in groups:
        blocks += f"""<div class="group"><div class="group-head rv">{tx(labels[key], "h2")}{tx(L(f"{len(items)} behandlingar", f"{len(items)} treatments"))}</div><div class="cards">{treatment_cards(items)}</div></div>"""
    intro = ABOUT.get("philosophy")
    cr = [(U["home"], "index.html"), (U["treatments"], "behandlingar.html")]
    title = L("Behandlingar i Göteborg: PMU, SMP, microneedling | Plaza Di Laura", "Treatments in Gothenburg: PMU, SMP, microneedling | Plaza Di Laura")
    desc = L("Kosmetisk tatuering av bryn, läppar, fräknar och lashliner, microneedling, SMP, LIFT Ink Removal och fettfrysning på Kungsgatan 11 i Göteborg.",
             "Cosmetic tattooing of brows, lips, freckles and lash line, microneedling, SMP, LIFT Ink Removal and fat freezing at Kungsgatan 11 in Gothenburg.")
    body = f"""<body>
{header('beh')}
<main id="main">
{crumbs(cr)}
<section class="phero phero--simple"><div class="container"><div class="phero__text">
  {tx(L("Plaza Di Laura Klinik", "Plaza Di Laura Clinic"), "span", "label")}
  {tx(L("Behandlingar i Göteborg", "Treatments in Gothenburg"), "h1", "h-1")}
  {tx(intro, "p", "lead") if intro else ""}
  <div class="btn-row"><a class="btn btn--primary" href="boka.html">{tx(U["book"])}{ICON["arrow"]}</a><a class="btn btn--ghost" href="boka.html?t=konsultation">{tx(U["consult"])}</a></div>
</div></div></section>
<section class="section" style="padding-top:0"><div class="container">{blocks}</div></section>
{guide_section()}
{cta_band(L("Osäker på vad som passar dig?", "Not sure what suits you?"), L("Boka en kostnadsfri konsultation på plats, per telefon eller via Zoom.", "Book a free consultation in person, by phone or on Zoom."), ("boka.html?t=konsultation", U["consult"]), ("kontakt.html", L("Skicka en fråga", "Send a question")), tint=False)}
</main>
"""
    return head(title, desc, "behandlingar.html", [crumbs_ld(cr)]) + body + footer()


def results_for(t):
    m = {"puderbryn": "bryn", "strokes": "bryn", "lappar": "lappar", "fraknar": "fraknar"}
    f = m.get(t["slug"])
    return [r for r in RESULTS if r.get("filter") == f] if f else []


def page_treatment(t):
    slug = t["slug"]
    img = treatment_image(t)
    facts = t.get("facts") or []
    facts_html = ""
    short_facts = [f for f in facts if len(sv(f["value"])) <= 40][:4]
    if short_facts:
        facts_html = '<dl class="facts">' + "".join(f'<div>{tx(f["label"], "dt")}{tx(f["value"], "dd")}</div>' for f in short_facts) + "</dl>"
    intro = t.get("intro") or []
    sections, nav = [], []

    def add(sid, label, html_):
        nav.append((sid, label))
        sections.append(f'<section id="{sid}" class="rv">{html_}</section>')

    about = "".join(tx(p, "p") for p in intro[1:])
    if t.get("benefits"):
        about += tx(t["benefits"]["title"], "h3") + bullets(t["benefits"]["items"])
    for ex in t.get("extra") or []:
        about += (tx(ex["title"], "h3") if ex.get("title") else "") + para_list(ex.get("paragraphs")) + bullets(ex.get("items"))
    if t.get("people"):
        for p in t["people"]:
            about += f'<div class="panel panel--tint person" style="margin-top:24px"><span class="person__mark">{ICON["user"]}</span><div><h3 class="h-4">{esc(p["name"])}</h3>{tx(p.get("role"), "p", "small muted")}{para_list(p.get("bio"))}</div></div>'
    if about:
        add("om", L("Om behandlingen", "About"), tx(L("Om behandlingen", "About the treatment"), "h2") + about)

    if t.get("process") or t.get("noTrauma"):
        h = ""
        if t.get("process"):
            h += tx(t["process"]["title"], "h2") + para_list(t["process"]["paragraphs"])
        if t.get("noTrauma"):
            h += tx(L("Lauras No Trauma-teknik innebär att:", "Laura's No Trauma technique means that:"), "h3") + bullets(t["noTrauma"])
        add("sa-gar-det-till", L("Så går det till", "How it works"), h)

    if t.get("notFor"):
        nf = t["notFor"]
        add("passar-inte", L("Passar inte alla", "Not for everyone"), f'<div class="panel panel--brand">{tx(nf["title"], "h2")}{bullets(nf.get("items"))}{tx(nf.get("note"), "p", "note") if nf.get("note") else ""}</div>')

    prep = ""
    if t.get("before"):
        b = t["before"]
        inner = "".join(tx(g["when"], "h3") + bullets(g["items"]) for g in b.get("groups", []))
        prep += f'<div class="panel">{tx(b["title"], "h3")}{inner}{tx(b.get("note"), "p", "note") if b.get("note") else ""}</div>'
    if t.get("contraindications"):
        c = t["contraindications"]
        prep += f'<div class="panel">{tx(c["title"], "h3")}{bullets(c.get("items"))}{tx(c.get("note"), "p", "note") if c.get("note") else ""}</div>'
    if prep:
        add("infor", L("Inför behandlingen", "Before your visit"), tx(L("Inför behandlingen", "Before your treatment"), "h2") + f'<div class="split2">{prep}</div>')

    cons = ""
    if t.get("consultation") or t.get("cancellation"):
        if t.get("consultation"):
            cons += tx(L("Kostnadsfri konsultation", "Free consultation"), "h2") + tx(L("Är du osäker och har frågor är du välkommen att boka en kostnadsfri konsultation på plats, per telefon eller via Zoom.", "If you are unsure or have questions, you are welcome to book a free consultation in person, by phone or on Zoom."), "p")
            cons += f'<p><a class="btn btn--ghost" href="boka.html?t=konsultation">{tx(L("Boka konsultation", "Book a consultation"))}</a></p>'
        if t.get("cancellation"):
            cons += tx(L("Avbokning", "Cancellation"), "h3") + tx(t["cancellation"], "p")
        add("konsultation", L("Konsultation", "Consultation") if t.get("consultation") else L("Avbokning", "Cancellation"), cons)

    res = results_for(t)
    res_html = ""
    if res:
        res_html = f"""<section class="section section--surface" id="resultat" aria-labelledby="tres-h" data-gallery><div class="container">
  <div class="section-head rv"><div>{tx(U["results"], "span", "label")}{tx(L("Resultat: " + sv(t["name"]).lower(), "Results: " + en(t["name"]).lower()), "h2", "h-2", extra=' id="tres-h"')}</div>
  <div class="rtrack__nav"><button type="button" class="round-btn" data-track-prev="t-track"{ia(L("Föregående", "Previous"), "aria-label")}>{ICON["left"]}</button><button type="button" class="round-btn" data-track-next="t-track"{ia(L("Nästa", "Next"), "aria-label")}>{ICON["arrow"]}</button></div></div>
  <div class="rtrack" id="t-track" tabindex="0"{ia(L("Resultatgalleri", "Results gallery"), "aria-label")}>{result_cards(res)}</div>
</div></section>"""
        nav.append(("resultat", U["results"]))

    subnav = '<nav class="subnav"' + ia(L("På den här sidan", "On this page"), "aria-label") + '><div class="container"><ul>' + "".join(f'<li><a href="#{sid}">{tx(lbl)}</a></li>' for sid, lbl in nav) + "</ul></div></nav>"
    aside_rows = "".join(f'<div>{tx(f["label"], "dt")}{tx(f["value"], "dd")}</div>' for f in facts)
    aside = f"""<aside class="aside-card"><div class="panel">
  {tx(GROUPS[t["group"]], "span", "label")}{tx(t["fullName"], "h2")}
  {f'<dl style="margin-top:16px">{aside_rows}</dl>' if aside_rows else ''}
  <div style="display:grid;gap:10px;margin-top:20px"><a class="btn btn--primary btn--block" href="boka.html?t={slug}">{tx(L("Boka " + sv(t["name"]).lower(), "Book " + en(t["name"]).lower()))}</a>
  {f'<a class="btn btn--ghost btn--block" href="boka.html?t=konsultation">{tx(U["consult"])}</a>' if t.get("consultation") else ''}</div>
  {tx(L("Kungsgatan 11, Göteborg", "Kungsgatan 11, Gothenburg"), "p", "note")}
</div></aside>"""

    related = [x for x in TREATMENTS if x["slug"] != slug and x["group"] == t["group"]][:3]
    if len(related) < 3:
        related += [x for x in TREATMENTS if x["slug"] != slug and x not in related][: 3 - len(related)]
    guide = guide_section() if slug in ("puderbryn", "strokes") else ""
    topic = "microneedling" if slug == "microneedling" else "pmu"
    cr = [(U["home"], "index.html"), (U["treatments"], "behandlingar.html"), (t["name"], tfile(slug))]
    seo = t.get("seo") or {}
    service_ld = {"@context": "https://schema.org", "@type": "Service", "name": sv(t["fullName"]), "serviceType": sv(GROUPS[t["group"]]),
                  "provider": {"@type": "HealthAndBeautyBusiness", "name": "Plaza Di Laura", "address": ORG_LD["address"]}, "areaServed": "Göteborg",
                  "description": sv(t["short"])}
    body = f"""<body>
{header('beh')}
<main id="main">
{crumbs(cr)}
<section class="phero"><div class="container phero__grid">
  <div class="phero__text">
    {tx(GROUPS[t["group"]], "span", "label")}
    {tx(t["h1"], "h1", "h-1")}
    {tx(intro[0], "p", "lead") if intro else tx(t["short"], "p", "lead")}
    <div class="btn-row"><a class="btn btn--primary" href="boka.html?t={slug}">{tx(L("Boka " + sv(t["name"]).lower(), "Book " + en(t["name"]).lower()))}{ICON["arrow"]}</a>
    {f'<a class="btn btn--ghost" href="boka.html?t=konsultation">{tx(U["consult"])}</a>' if t.get("consultation") else ''}</div>
    {facts_html}
  </div>
  <div class="phero__media">{pic(img, "(min-width: 960px) 38vw, 92vw", eager=True)}</div>
</div></section>
{subnav}
<section class="section"><div class="container article"><div class="prose">{"".join(sections)}</div>{aside}</div></section>
{res_html}
{guide}
{reviews_section(title=L("Kunderna om Laura", "Clients on Laura"), topic=topic, limit=5)}
<section class="section section--surface" aria-labelledby="rel-h"><div class="container">
  <div class="section-head rv"><div>{tx(L("Fler behandlingar", "More treatments"), "h2", "h-2", extra=' id="rel-h"')}</div><a class="link-arrow" href="behandlingar.html">{tx(U["allTreatments"])}{ICON["arrow"]}</a></div>
  <div class="cards">{treatment_cards(related)}</div>
</div></section>
</main>
"""
    title = seo.get("title") or L(sv(t["name"]) + " i Göteborg | Plaza Di Laura", en(t["name"]) + " in Gothenburg | Plaza Di Laura")
    desc = seo.get("description") or t["short"]
    return head(title, desc, tfile(slug), [service_ld, crumbs_ld(cr)]) + body + footer(gallery=bool(res))


def course_cards(items):
    out = []
    for c in items:
        d = days_label(c)
        meta = []
        if d:
            meta.append(d)
        if c.get("price"):
            meta.append(c["price"])
        meta_html = ""
        if meta:
            meta_html = tx(L(" · ".join(sv(m) for m in meta), " · ".join(en(m) for m in meta)), "span", "card__meta")
        out.append(f"""<a class="card rv" href="{cfile(c['slug'])}"><div class="card__img">{pic(course_image(c), "(min-width: 1024px) 30vw, (min-width: 640px) 45vw, 92vw", decorative=True)}<span class="card__go" aria-hidden="true">{ICON["arrow"]}</span></div>
  {meta_html}{tx(c["name"], "h3")}{tx(c["short"], "p")}</a>""")
    return "".join(out)


def page_academy():
    A = ACADEMY
    hub = A.get("hubIntro", {})
    teacher = A.get("teacher", {})
    sup = A.get("suppliers", {})
    pr = A.get("practice", {})
    why = A.get("whyStudents", [])
    q = A.get("studentQuote")
    yh = A.get("yhProgramme")
    career = A.get("careerBlock", {})
    stud = SLOT["academyHero"]
    t_img = SLOT["teacher"]
    pmu_c = [c for c in COURSES if c["slug"] in ("signature-pmu", "signature-microblading", "freckle")]
    other_c = [c for c in COURSES if c not in pmu_c]
    cr = [(U["home"], "index.html"), (U["academy"], "akademi.html")]
    title = L("PMU-utbildning i Göteborg | Plaza Di Laura Academy", "PMU training in Gothenburg | Plaza Di Laura Academy")
    desc = L("Utbildningar i kosmetisk tatuering, microblading, fräknar, SMP, microneedling och Ink Removal med Laura Lindqvist i Göteborg. Max 2 elever per kurstillfälle.",
             "Courses in cosmetic tattooing, microblading, freckles, SMP, microneedling and ink removal with Laura Lindqvist in Gothenburg. Max 2 students per course.")
    yh_html = ""
    if yh:
        yh_html = f"""<section class="section section--tint" aria-labelledby="yh-h"><div class="container article"><div class="prose rv">
  {tx(L("På gång", "In development"), "span", "label")}{tx(L("En CSN-berättigad YH-utbildning", "A state-funded vocational programme"), "h2", extra=' id="yh-h"')}
  {tx(yh.get("paragraph"), "p")}{bullets(yh.get("items"))}
  {tx(L("Utbildningen fokuserar bland annat på:", "The programme focuses on, among other things:"), "h3") if yh.get("focus") else ""}{bullets(yh.get("focus"))}
</div></div></section>"""
    body = f"""<body>
{header('aka')}
<main id="main">
{crumbs(cr)}
<section class="phero"><div class="container phero__grid">
  <div class="phero__text">
    {tx(L("Plaza Di Laura Academy", "Plaza Di Laura Academy"), "span", "label")}
    {tx(L("Utbildningar i kosmetisk tatuering i Göteborg", "Cosmetic tattooing courses in Gothenburg"), "h1", "h-1")}
    {tx(hub["paragraphs"][0], "p", "lead") if hub.get("paragraphs") else ""}
    <div class="btn-row"><a class="btn btn--primary" href="boka.html?t=kursradgivning">{tx(U["courseAdvice"])}{ICON["arrow"]}</a><a class="btn btn--ghost" href="#utbildningar">{tx(L("Se utbildningar", "See courses"))}</a></div>
    <dl class="facts">
      <div>{tx(L("Elever", "Students"), "dt")}{tx(L("Max 2 per kurstillfälle", "Max 2 per course"), "dd")}</div>
      <div>{tx(L("Betalning", "Payment"), "dt")}{tx(L("Avbetalning med Qliro", "Instalments with Qliro"), "dd")}</div>
      <div>{tx(L("Certifikat", "Certificate"), "dt")}{tx(L("Internationellt certifikat", "International certificate"), "dd")}</div>
    </dl>
  </div>
  <div class="phero__media">{pic(stud, "(min-width: 960px) 38vw, 92vw", eager=True)}</div>
</div></section>

<section class="section" id="utbildningar" style="padding-top:0"><div class="container">
  <div class="group"><div class="group-head rv">{tx(L("PMU-program", "PMU programmes"), "h2")}{tx(L("Kosmetisk tatuering", "Cosmetic tattooing"))}</div><div class="cards">{course_cards(pmu_c)}</div></div>
  <div class="group"><div class="group-head rv">{tx(L("Fler grundkurser", "More foundation courses"), "h2")}{tx(L("Hårbotten, hud och borttagning", "Scalp, skin and removal"))}</div><div class="cards">{course_cards(other_c)}</div></div>
</div></section>

<section class="section band" aria-labelledby="why-h"><div class="container aband">
  <div class="rv">
    {tx(L("Därför väljer elever vår skola", "Why students choose us"), "span", "label")}
    {tx(career.get("title") or L("Starta din karriär", "Start your career"), "h2", "h-2", extra=' id="why-h"')}
    {tx(career.get("paragraph"), "p") if career.get("paragraph") else ""}
    <ul class="ticks" style="margin-top:28px">{"".join(tx(w, "li") for w in why)}{"".join(tx(i, "li") for i in career.get("items", []))}</ul>
  </div>
  <div class="rv">
    {tx(pr.get("title"), "h3", "h-3") if pr.get("title") else ""}
    {tx(pr.get("paragraph"), "p") if pr.get("paragraph") else ""}
    <hr class="rule" style="margin:28px 0">
    {tx(L("Leverantörer", "Suppliers"), "span", "label")}
    {tx(sup.get("paragraph"), "p") if sup.get("paragraph") else ""}
    <ul class="brands" style="margin-top:16px">{"".join(f"<li>{esc(b)}</li>" for b in sup.get("brands", []))}</ul>
  </div>
</div></section>

<section class="section" aria-labelledby="teach-h"><div class="container meet">
  <div class="rv">{pic(t_img, "(min-width: 960px) 38vw, 92vw")}</div>
  <div class="rv">
    {tx(teacher.get("title") or L("Vem är din lärare?", "Who is your teacher?"), "span", "label")}
    <h2 class="meet__name" id="teach-h">Laura <em>Lindqvist</em></h2>
    {tx(L("PMU-artist och lärare", "PMU artist and teacher"), "p", "meet__role")}
    {para_list(teacher.get("paragraphs"))}
    {f'<figure class="quote-block" style="margin-top:32px">{tx(q["text"], "blockquote")}<figcaption>{esc(q["name"])}, {tx(L("elev", "student"))}</figcaption></figure>' if q else ''}
  </div>
</div></section>
{yh_html}
{cta_band(L("Vilken utbildning passar dig?", "Which course is right for you?"), L("Boka en kostnadsfri kursrådgivning så hjälper Laura dig att hitta rätt utbildning.", "Book free course advice and Laura will help you find the right course."), ("boka.html?t=kursradgivning", U["courseAdvice"]), ("kontakt.html", L("Skicka en fråga", "Send a question")), tint=False)}
</main>
"""
    return head(title, desc, "akademi.html", [crumbs_ld(cr)]) + body + footer()


def page_course(c):
    slug = c["slug"]
    img = course_image(c)
    intro = c.get("intro") or []
    facts = []
    if c.get("days"):
        facts.append((L("Längd", "Length"), days_label(c)))
    facts.append((L("Elever", "Students"), L("Max 2 per kurstillfälle", "Max 2 per course")))
    if c.get("price"):
        facts.append((L("Pris", "Price"), c["price"]))
    facts.append((L("Betalning", "Payment"), L("Avbetalning med Qliro", "Instalments with Qliro")))
    facts_html = '<dl class="facts">' + "".join(f'<div>{tx(a, "dt")}{tx(b, "dd")}</div>' for a, b in facts) + "</dl>"
    pdf_btn = f'<a class="btn btn--ghost" href="{att(c["pdf"])}" target="_blank" rel="noopener">{ICON["doc"]}{tx(L("Kursinformation (PDF)", "Course information (PDF)"))}</a>' if c.get("pdf") else ""
    sections = []
    s = tx(L("Om utbildningen", "About the course"), "h2") + "".join(tx(p, "p") for p in intro[1:])
    if c.get("methods"):
        s += tx(L("Metoder du lär dig", "Methods you learn"), "h3") + '<ul class="chips">' + "".join(f"<li>{esc(m)}</li>" for m in c["methods"]) + "</ul>"
    if c.get("learn"):
        s += tx(c["learn"]["title"], "h3") + bullets(c["learn"]["items"])
    if c.get("signatureTechnique"):
        s += f'<div class="panel panel--tint" style="margin-top:24px">{tx(L("Lauras egenutvecklade teknik", "Laura&#39;s own technique"), "h3", raw=True)}{tx(c["signatureTechnique"], "p")}</div>'
    sections.append(s)
    if c.get("format") or c.get("included"):
        blk = ""
        if c.get("format"):
            blk += f'<div class="panel">{tx(c["format"]["title"], "h3")}{bullets(c["format"]["items"])}</div>'
        if c.get("included"):
            blk += f'<div class="panel">{tx(c["included"]["title"], "h3")}{bullets(c["included"]["items"])}</div>'
        sections.append(tx(L("Upplägg och vad som ingår", "Format and what is included"), "h2") + f'<div class="split2">{blk}</div>')
    if c.get("career"):
        sections.append(tx(c["career"]["title"], "h2") + para_list(c["career"]["paragraphs"]))
    for ex in c.get("extra") or []:
        sections.append((tx(ex["title"], "h2") if ex.get("title") else "") + para_list(ex.get("paragraphs")) + bullets(ex.get("items")))
    if c.get("people"):
        for p in c["people"]:
            sections.append(f'<div class="panel panel--tint person"><span class="person__mark">{ICON["user"]}</span><div><h3 class="h-4">{esc(p["name"])}</h3>{tx(p.get("role"), "p", "small muted")}{para_list(p.get("bio"))}</div></div>')
    prose = "".join(f'<section class="rv">{x}</section>' for x in sections)
    hl = c.get("highlights") or []
    price_html = ""
    if c.get("price"):
        price_html = f'<div class="price-panel">{tx(L("Pris", "Price"), "span", "label")}{tx(c["price"], "span", "price", extra=" data-count")}{tx(c.get("priceNote"), "p", "note") if c.get("priceNote") else ""}</div>'
    elif c.get("days"):
        price_html = f'<div class="price-panel">{tx(L("Längd", "Length"), "span", "label")}{tx(days_label(c), "span", "days", extra=" data-count")}</div>'
    aside = f"""<aside class="aside-card"><div class="panel">
  {price_html}
  <ul class="ticks" style="margin:18px 0">{"".join(tx(h, "li") for h in hl)}</ul>
  <div style="display:grid;gap:10px"><a class="btn btn--primary btn--block" href="boka.html?t=kursradgivning&amp;kurs={slug}">{tx(U["courseAdvice"])}</a>
  <a class="btn btn--ghost btn--block" href="kontakt.html">{tx(L("Kontakta oss", "Contact us"))}</a></div>
</div></aside>"""
    others = [x for x in COURSES if x["slug"] != slug][:3]
    q = ACADEMY.get("studentQuote")
    teacher = ACADEMY.get("teacher", {})
    cr = [(U["home"], "index.html"), (U["academy"], "akademi.html"), (c["name"], cfile(slug))]
    seo = c.get("seo") or {}
    course_ld = {"@context": "https://schema.org", "@type": "Course", "name": sv(c["name"]), "description": sv(c["short"]),
                 "provider": {"@type": "Organization", "name": "Plaza Di Laura Academy", "sameAs": SITE}, "inLanguage": "sv"}
    if c.get("price"):
        num = re.sub(r"\D", "", sv(c["price"]))
        course_ld["offers"] = {"@type": "Offer", "price": num, "priceCurrency": "SEK", "category": "Paid"}
    body = f"""<body>
{header('aka')}
<main id="main">
{crumbs(cr)}
<section class="phero"><div class="container phero__grid">
  <div class="phero__text">
    {tx(L("Plaza Di Laura Academy", "Plaza Di Laura Academy"), "span", "label")}
    {tx(c["h1"], "h1", "h-1")}
    {tx(intro[0], "p", "lead") if intro else tx(c["short"], "p", "lead")}
    <div class="btn-row"><a class="btn btn--primary" href="boka.html?t=kursradgivning&amp;kurs={slug}">{tx(U["courseAdvice"])}{ICON["arrow"]}</a>{pdf_btn}</div>
    {facts_html}
  </div>
  <div class="phero__media">{pic(img, "(min-width: 960px) 38vw, 92vw", eager=True)}</div>
</div></section>
<section class="section"><div class="container article"><div class="prose">{prose}</div>{aside}</div></section>
<section class="section section--tint" aria-labelledby="t-h"><div class="container article"><div class="rv">
  {tx(teacher.get("title") or L("Vem är din lärare?", "Who is your teacher?"), "span", "label")}
  <h2 class="h-2" id="t-h">Laura Lindqvist</h2>
  {"".join(tx(p, "p", "lead") for p in (teacher.get("paragraphs") or [])[:1])}
  {f'<figure class="quote-block" style="margin-top:28px">{tx(q["text"], "blockquote")}<figcaption>{esc(q["name"])}, {tx(L("elev", "student"))}</figcaption></figure>' if q else ''}
</div></div></section>
<section class="section" aria-labelledby="oc-h"><div class="container">
  <div class="section-head rv"><div>{tx(L("Fler utbildningar", "More courses"), "h2", "h-2", extra=' id="oc-h"')}</div><a class="link-arrow" href="akademi.html">{tx(L("Alla utbildningar", "All courses"))}{ICON["arrow"]}</a></div>
  <div class="cards">{course_cards(others)}</div>
</div></section>
</main>
"""
    title = seo.get("title") or L(sv(c["name"]) + " | Plaza Di Laura Academy", en(c["name"]) + " | Plaza Di Laura Academy")
    desc = seo.get("description") or c["short"]
    return head(title, desc, cfile(slug), [course_ld, crumbs_ld(cr)]) + body + footer()


def page_results():
    cr = [(U["home"], "index.html"), (U["results"], "resultat.html")]
    title = L("Resultat: puderbryn, läppar och fräknar | Plaza Di Laura", "Results: powder brows, lips and freckles | Plaza Di Laura")
    desc = L("Före- och efterbilder på kosmetisk tatuering från Plaza Di Laura i Göteborg: puderbryn, strokes, läppar och fräknar, nygjorda och läkta.",
             "Before and after photos of cosmetic tattooing from Plaza Di Laura in Gothenburg: powder brows, strokes, lips and freckles, fresh and healed.")
    body = f"""<body>
{header('res')}
<main id="main">
{crumbs(cr)}
<section class="phero phero--simple"><div class="container"><div class="phero__text">
  {tx(GROUPS["pmu"], "span", "label")}
  {tx(L("Resultat från kliniken", "Results from the clinic"), "h1", "h-1")}
  {tx(L("Före- och efterbilder på bryn, läppar och fräknar. Nygjorda resultat ser mörkare ut och mjuknar under läkningen, därför visar vi både direkt efter och läkt.", "Before and after photos of brows, lips and freckles. Fresh results look darker and soften as they heal, which is why we show both right after and healed."), "p", "lead")}
</div></div></section>
<section class="section" style="padding-top:0" data-gallery><div class="container">
  <div class="section-head" style="margin-bottom:28px">{filter_bar("res-grid")}<span class="filter-count small muted" aria-live="polite"></span></div>
  <div class="rgrid" id="res-grid">{result_cards(RESULTS, track=False)}</div>
</div></section>
{cta_band(L("Vill du ha ett lika naturligt resultat?", "Would you like a result this natural?"), L("Boka tid direkt eller börja med en kostnadsfri konsultation.", "Book directly or start with a free consultation."), ("boka.html", U["book"]), ("boka.html?t=konsultation", U["consult"]))}
</main>
"""
    return head(title, desc, "resultat.html", [crumbs_ld(cr)]) + body + footer(gallery=True)


def page_about():
    A = ABOUT
    story = A.get("story", [])
    p_img = SLOT["aboutHero"]
    p2 = SLOT["aboutAside"]
    blocks = ""
    for i, s in enumerate(story[1:] if story else []):
        blocks += f'<section class="rv">{tx(s.get("title"), "h2") if s.get("title") else ""}{para_list(s.get("paragraphs"))}{bullets(s.get("items"))}</section>'
    trio = "".join(f'<li>{tx(v["title"], "strong")}{tx(v["text"])}</li>' for v in A.get("valueTrio", []))
    clinic = A.get("clinic", {})
    cr = [(U["home"], "index.html"), (U["about"], "om-laura.html")]
    title = L("Om Laura Lindqvist, PMU-artist i Göteborg | Plaza Di Laura", "About Laura Lindqvist, PMU artist in Gothenburg | Plaza Di Laura")
    desc = L("Laura Lindqvist har arbetat i skönhetsbranschen i över 20 år och specialiserat sig på kosmetisk tatuering. Hon har utvecklat No Trauma-tekniken och utbildar behandlare.",
             "Laura Lindqvist has worked in beauty for over 20 years, specialising in cosmetic tattooing. She developed the No Trauma technique and trains practitioners.")
    intro = story[0] if story else {}
    person_ld = {"@context": "https://schema.org", "@type": "Person", "name": "Laura Lindqvist", "jobTitle": "PMU-artist och utbildare",
                 "worksFor": {"@type": "HealthAndBeautyBusiness", "name": "Plaza Di Laura"}}
    body = f"""<body>
{header('om')}
<main id="main">
{crumbs(cr)}
<section class="phero"><div class="container phero__grid">
  <div class="phero__text">
    {tx(L("Om Laura", "About Laura"), "span", "label")}
    {tx(A.get("headline") or L("Laura Lindqvist", "Laura Lindqvist"), "h1", "h-1")}
    {"".join(tx(p, "p", "lead") for p in intro.get("paragraphs", [])[:1])}
    <div class="btn-row"><a class="btn btn--primary" href="boka.html">{tx(U["book"])}{ICON["arrow"]}</a><a class="btn btn--ghost" href="boka.html?t=kursradgivning">{tx(U["courseAdvice"])}</a></div>
  </div>
  <div class="phero__media">{pic(p_img, "(min-width: 960px) 38vw, 92vw", eager=True)}</div>
</div></section>
<section class="proof"><div class="container"><ul class="proof__list">
  <li>{tx(U["since"], "strong")}{tx(L("Klinik och skola i Göteborg", "Clinic and school in Gothenburg"))}</li>
  <li>{tx(L("20+ år", "20+ years"), "strong", extra=" data-count")}{tx(L("i skönhetsbranschen", "in the beauty industry"))}</li>
  <li>{tx(L("15 år", "15 years"), "strong", extra=" data-count")}{tx(L("specialiserad på kosmetisk tatuering", "specialising in cosmetic tattooing"))}</li>
  <li>{tx(L("Hundratals elever", "Hundreds of students"), "strong")}{tx(L("från hela Sverige och internationellt", "from across Sweden and abroad"))}</li>
</ul></div></section>
<section class="section"><div class="container article"><div class="prose">{blocks}</div>
  <aside class="aside-card">{pic(p2, "(min-width: 1024px) 30vw, 92vw")}
  {f'<div class="panel">{tx(L("Filosofi", "Philosophy"), "span", "label")}{tx(A["philosophy"], "p")}</div>' if A.get("philosophy") else ""}</aside>
</div></section>
<section class="section section--tint"><div class="container"><ul class="nt__list" style="grid-template-columns:repeat(auto-fit,minmax(220px,1fr));margin:0">{trio}</ul></div></section>
{f'''<section class="section"><div class="container article"><div class="prose rv">{tx(L("Plaza Di Laura", "Plaza Di Laura"), "span", "label")}{tx(L("Klinik och utbildningscenter inom PMU och SMP", "Clinic and training centre for PMU and SMP"), "h2")}{para_list(clinic.get("paragraphs"))}{bullets(clinic.get("items"))}</div></div></section>''' if clinic else ""}
{reviews_section(title=L("Förtroende byggs över tid", "Trust is built over time"), limit=7, tint=True)}
{cta_band(L("Träffa Laura", "Meet Laura"), L("Boka en behandling eller en kostnadsfri konsultation på Kungsgatan 11.", "Book a treatment or a free consultation at Kungsgatan 11."), ("boka.html", U["book"]), ("boka.html?t=konsultation", U["consult"]), tint=False)}
</main>
"""
    return head(title, desc, "om-laura.html", [person_ld, crumbs_ld(cr)]) + body + footer()


def page_contact():
    cr = [(U["home"], "index.html"), (U["contact"], "kontakt.html")]
    title = L("Kontakt: Kungsgatan 11, Göteborg | Plaza Di Laura", "Contact: Kungsgatan 11, Gothenburg | Plaza Di Laura")
    desc = L("Kontakta Plaza Di Laura på Kungsgatan 11 i Göteborg. Frågor om kosmetisk tatuering, hudvård, SMP eller utbildningar. Kostnadsfri konsultation.",
             "Contact Plaza Di Laura at Kungsgatan 11 in Gothenburg. Questions about cosmetic tattooing, skin care, SMP or courses. Free consultation.")
    topics = [("behandling", L("En behandling", "A treatment")), ("utbildning", L("En utbildning", "A course")), ("ovrigt", L("Något annat", "Something else"))]
    opts = "".join(f'<option value="{v}"{ia(lbl, "label") if False else ""} data-en="{att(en(lbl))}">{esc(sv(lbl))}</option>' for v, lbl in topics)
    body = f"""<body>
{header('kon')}
<main id="main">
{crumbs(cr)}
<section class="phero phero--simple"><div class="container"><div class="phero__text">
  {tx(U["contact"], "span", "label")}
  {tx(L("Kontakta Plaza Di Laura", "Contact Plaza Di Laura"), "h1", "h-1")}
  {tx(L("Har du frågor om en behandling eller en utbildning? Skriv till oss, eller boka en kostnadsfri konsultation på plats, per telefon eller via Zoom.", "Questions about a treatment or a course? Write to us, or book a free consultation in person, by phone or on Zoom."), "p", "lead")}
</div></div></section>
<section class="section" style="padding-top:0"><div class="container article">
  <div>
    <form class="form panel" data-contact data-success="contact-ok" novalidate>
      {tx(L("Skicka en fråga", "Send a question"), "h2", "h-3")}
      <div class="form__row form__row--2">
        <div class="field"><label for="c-name">{tx(L("Namn", "Name"))}<span class="req" aria-hidden="true">*</span></label><input id="c-name" name="name" type="text" autocomplete="name" required><span class="field__err" aria-live="polite"></span></div>
        <div class="field"><label for="c-email">{tx(L("E-post", "Email"))}<span class="req" aria-hidden="true">*</span></label><input id="c-email" name="email" type="email" autocomplete="email" required><span class="field__err" aria-live="polite"></span></div>
      </div>
      <div class="form__row form__row--2">
        <div class="field"><label for="c-phone">{tx(L("Telefon", "Phone"))}</label><input id="c-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel"><span class="field__hint">{tx(L("Valfritt, om du vill att vi ringer upp", "Optional, if you would like a call back"))}</span><span class="field__err" aria-live="polite"></span></div>
        <div class="field"><label for="c-topic">{tx(L("Jag har en fråga om", "My question is about"))}</label><select id="c-topic" name="topic">{opts}</select></div>
      </div>
      <div class="field"><label for="c-msg">{tx(L("Meddelande", "Message"))}<span class="req" aria-hidden="true">*</span></label><textarea id="c-msg" name="message" required></textarea><span class="field__err" aria-live="polite"></span></div>
      <div class="hp" aria-hidden="true"><label for="c-web">Webbplats</label><input id="c-web" name="website" type="text" tabindex="-1" autocomplete="off"></div>
      <div><button type="submit" class="btn btn--primary">{tx(L("Skicka", "Send"))}{ICON["send"]}</button></div>
    </form>
    <div class="form-success" id="contact-ok" hidden role="status">
      <h3>{ICON["check"]}{tx(L("Tack, ", "Thank you, "))}<span data-name></span>!</h3>
      {tx(L("Din fråga är skickad. Vi återkommer till dig via e-post.", "Your question has been sent. We will get back to you by email."), "p")}
      <p><a class="link-arrow" href="index.html">{tx(L("Till startsidan", "Back to home"))}{ICON["arrow"]}</a></p>
    </div>
  </div>
  <aside class="aside-card"><div class="panel">
    {tx(L("Besök oss", "Visit us"), "span", "label")}
    <dl>
      <div>{tx(L("Adress", "Address"), "dt")}{tx(L("Kungsgatan 11, Göteborg", "Kungsgatan 11, Gothenburg"), "dd")}</div>
      <div>{tx(L("Konsultation", "Consultation"), "dt")}{tx(L("Kostnadsfri", "Free"), "dd")}</div>
      <div>{tx(L("Form", "Format"), "dt")}{tx(L("På plats, telefon, Zoom", "In person, phone, Zoom"), "dd")}</div>
    </dl>
    <div style="display:grid;gap:10px;margin-top:20px"><a class="btn btn--primary btn--block" href="boka.html">{tx(U["book"])}</a><a class="btn btn--ghost btn--block" href="{DIRECTIONS}" target="_blank" rel="noopener">{tx(L("Vägbeskrivning", "Directions"))}</a></div>
    <div class="footer__social" style="margin-top:18px">{"".join(f'<a href="{u}" target="_blank" rel="noopener" aria-label="{n}" style="border-color:var(--line)">{ICON[i]}</a>' for u, i, n in SOCIAL)}</div>
  </div></aside>
</div></section>
{visit_section()}
</main>
"""
    return head(title, desc, "kontakt.html", [ORG_LD, crumbs_ld(cr)]) + body + footer()


def page_booking():
    pmu = [t for t in TREATMENTS if t["group"] == "pmu"]
    oth = [t for t in TREATMENTS if t["group"] != "pmu"]
    CHIP = {"puderbryn": L("Inkl. återbesök", "Incl. touch-up"), "strokes": L("Inkl. återbesök", "Incl. touch-up"), "lappar": L("Inkl. återbesök", "Incl. touch-up")}
    check = ICON["check"]

    def card(value, title, short=None, img=None, chip=None):
        media = f'<span class="bk-card__media">{pic(img, "(min-width: 1024px) 220px, 45vw", decorative=True)}</span>' if img else ""
        cls = "bk-card" + ("" if img else " bk-card--plain")
        return (f'<label class="{cls}"><input type="radio" name="b-what" value="{value}">{media}'
                f'<span class="bk-card__body">{tx(title, "strong")}{tx(short, "small") if short else ""}{tx(chip, "em", "bk-card__chip") if chip else ""}</span>'
                f'<span class="bk-card__check" aria-hidden="true">{check}</span></label>')
    cards_pmu = "".join(card(t["slug"], t["fullName"], t.get("short"), treatment_image(t), CHIP.get(t["slug"])) for t in pmu)
    cards_oth = "".join(card(t["slug"], t["fullName"], t.get("short"), treatment_image(t)) for t in oth)
    cards_free = (card("konsultation", L("Kostnadsfri konsultation", "Free consultation"), L("Osäker på vad som passar dig? Laura går igenom form, färg och metod med dig.", "Not sure what suits you? Laura goes through shape, colour and method with you."), SLOT.get("aboutAside"), L("Kostnadsfritt", "Free of charge"))
                  + card("kursradgivning", L("Kostnadsfri kursrådgivning", "Free course advice"), L("Hitta rätt utbildning tillsammans med Laura.", "Find the right course together with Laura."), SLOT.get("aband2"), L("Kostnadsfritt", "Free of charge")))
    contra = (TBY.get("puderbryn") or {}).get("contraindications") or {}
    keys = ["pregnant", "thinners", "skin", "blood", "under18"]
    qs = ""
    for i, item in enumerate(contra.get("items", [])[:5]):
        k = keys[i] if i < len(keys) else f"q{i}"
        qs += (f'<li class="bk-q"><span class="bk-q__text">{tx(item)}</span><span class="seg" role="radiogroup"{ia(item, "aria-label")}>'
               f'<label><input type="radio" name="hq-{k}" value="no"><span>{tx(L("Nej", "No"))}</span></label>'
               f'<label><input type="radio" name="hq-{k}" value="yes"><span>{tx(L("Ja", "Yes"))}</span></label></span></li>')
    contra_note = contra.get("note")
    prep = (TBY.get("puderbryn") or {}).get("before") or {}
    prep_html = "".join(f'<div class="bk-prep__g">{tx(g["when"], "strong")}{bullets(g["items"])}</div>' for g in prep.get("groups", []))
    canc = (TBY.get("puderbryn") or {}).get("cancellation") or L("Avbokning senast 24 timmar innan behandlingen.", "Cancellation at least 24 hours before the treatment.")

    def tinfo(t):
        img = treatment_image(t)
        b = t.get("before") or {}
        return {"name": t["name"], "fullName": t["fullName"], "group": t["group"], "url": tfile(t["slug"]),
                "img": img_src(img, 640), "alt": (img_meta(img) or {}).get("alt", L("")),
                "prep": [{"when": g["when"], "items": g["items"]} for g in b.get("groups", [])], "prepNote": b.get("note")}
    data = {"treatments": {t["slug"]: tinfo(t) for t in TREATMENTS},
            "free": {"konsultation": {"img": img_src(SLOT.get("aboutAside"), 640)}, "kursradgivning": {"img": img_src(SLOT.get("aband2"), 640)}},
            "courses": {c["slug"]: c["name"] for c in COURSES}}
    course_opts = f'<option value="" data-en="Not sure yet">{esc("Jag vet inte än")}</option>' + "".join(f'<option value="{c["slug"]}" data-en="{att(en(c["name"]))}">{esc(sv(c["name"]))}</option>' for c in COURSES)
    sun = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="14" r="4"/><path d="M12 4v3M4.9 8.9l2.1 2.1M19.1 8.9 17 11M3 19h18"/></svg>'
    noon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8"/></svg>'
    anyt = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>'
    cr = [(U["home"], "index.html"), (U["book"], "boka.html")]
    title = L("Boka tid eller konsultation | Plaza Di Laura Göteborg", "Book a treatment or consultation | Plaza Di Laura Gothenburg")
    desc = L("Skicka en bokningsförfrågan för kosmetisk tatuering, microneedling, SMP eller fettfrysning, eller boka kostnadsfri konsultation och kursrådgivning.",
             "Send a booking request for cosmetic tattooing, microneedling, SMP or fat freezing, or book a free consultation or course advice.")
    nav = lambda back=True, label=L("Fortsätt", "Continue"): (f'<div class="bnav">' + (f'<button type="button" class="btn btn--ghost" data-prev>{ICON["left"]}{tx(L("Tillbaka", "Back"))}</button>' if back else "<span></span>")
                                                           + f'<button type="button" class="btn btn--primary" data-next>{tx(label)}{ICON["arrow"]}</button></div>')
    body = f"""<body class="page-book">
{header('book')}
<main id="main">
{crumbs(cr)}
<section class="bk-hero"><div class="container">
  {tx(L("Bokning", "Booking"), "span", "label")}
  {tx(L("Boka din <em>tid</em>", "Book your <em>visit</em>"), "h1", "h-1", raw=True)}
  {tx(L("Välj behandling och vilka dagar som passar dig, så bekräftar vi en tid. Det tar ungefär en minut.", "Choose a treatment and the days that suit you, and we will confirm a time. It takes about a minute."), "p", "lead")}
  <ul class="bk-trust">
    <li>{check}{tx(L("Kostnadsfri konsultation", "Free consultation"))}</li>
    <li>{check}{tx(L("Avbokning senast 24 timmar innan", "Cancel up to 24 hours before"))}</li>
    <li>{ICON["pin"]}{tx(U["address"])}</li>
  </ul>
</div></section>
<section class="section bk-section"><div class="container bk" data-booking>
  <div class="bk-main">
    <ol class="bk-steps"{ia(L("Steg i bokningen", "Booking steps"), "aria-label")}></ol>

    <div class="bstep" data-step="0">
      <div class="bstep__head"><span class="bstep__num" data-stepnum></span>{tx(L("Vad vill du boka?", "What would you like to book?"), "h2")}{tx(L("Välj en behandling. Är du osäker, välj en kostnadsfri konsultation.", "Choose a treatment. If you are unsure, choose a free consultation."), "p")}</div>
      <div class="bk-tabs" role="tablist"{ia(L("Kategorier", "Categories"), "aria-label")}>
        <button type="button" role="tab" data-tab="pmu" aria-selected="true">{tx(GROUPS["pmu"])}</button>
        <button type="button" role="tab" data-tab="other" aria-selected="false">{tx(L("Hud, hår och kropp", "Skin, scalp and body"))}</button>
        <button type="button" role="tab" data-tab="free" aria-selected="false">{tx(L("Kostnadsfritt", "Free of charge"))}</button>
        <span class="bk-tabs__ink" aria-hidden="true"></span>
      </div>
      <p class="alert alert--step" role="alert" tabindex="-1" hidden></p>
      <div class="bk-panel" data-panel="pmu"><div class="bk-cards">{cards_pmu}</div></div>
      <div class="bk-panel" data-panel="other" hidden><div class="bk-cards">{cards_oth}</div></div>
      <div class="bk-panel" data-panel="free" hidden><div class="bk-cards bk-cards--2">{cards_free}</div>
        <div class="bk-sub" data-modes hidden>{tx(L("Hur vill du ha konsultationen?", "How would you like the consultation?"), "h3")}
          <div class="chips-select">
            <label><input type="radio" name="b-mode" value="plats" checked><span>{tx(L("På plats", "In person"))}</span></label>
            <label><input type="radio" name="b-mode" value="telefon"><span>{tx(L("Per telefon", "By phone"))}</span></label>
            <label><input type="radio" name="b-mode" value="zoom"><span>{tx(L("Via Zoom", "On Zoom"))}</span></label>
          </div></div>
        <div class="bk-sub field" data-courserow hidden><label for="b-course">{tx(L("Vilken utbildning är du intresserad av?", "Which course are you interested in?"))}</label><select id="b-course" name="b-course">{course_opts}</select></div>
      </div>
      {nav(back=False)}
    </div>

    <div class="bstep" data-step="1" hidden>
      <div class="bstep__head"><span class="bstep__num" data-stepnum></span>{tx(L("Vilka dagar passar dig?", "Which days suit you?"), "h2")}{tx(L("Välj upp till tre dagar, så bekräftar vi en tid som passar.", "Choose up to three days and we will confirm a time that suits you."), "p")}</div>
      <p class="alert alert--step" role="alert" tabindex="-1" hidden></p>
      <div class="bk-when">
        <div class="cal"><div class="cal__head"><button type="button" class="icon-btn" data-cal-prev>{ICON["left"]}</button><strong aria-live="polite"></strong><button type="button" class="icon-btn" data-cal-next>{ICON["arrow"]}</button></div><div class="cal__grid"></div></div>
        <div class="bk-when__side">
          {tx(L("Valda dagar", "Chosen days"), "h3")}
          <ul class="picked" aria-live="polite"></ul>
          {tx(L("Tid på dagen", "Time of day"), "h3")}
          <div class="tod">
            <label><input type="radio" name="b-tod" value="fm"><span>{sun}{tx(L("Förmiddag", "Morning"))}</span></label>
            <label><input type="radio" name="b-tod" value="em"><span>{noon}{tx(L("Eftermiddag", "Afternoon"))}</span></label>
            <label><input type="radio" name="b-tod" value="any" checked><span>{anyt}{tx(L("Spelar ingen roll", "No preference"))}</span></label>
          </div>
          <label class="switch"><input type="checkbox" name="b-flex"><span class="switch__ui" aria-hidden="true"></span><span>{tx(L("Jag är flexibel, första lediga tid passar", "I am flexible, the first available time suits me"))}</span></label>
        </div>
      </div>
      {nav()}
    </div>

    <div class="bstep" data-step="2" hidden>
      <div class="bstep__head"><span class="bstep__num" data-stepnum></span>{tx(L("Några frågor om din hälsa", "A few health questions"), "h2")}<p>{tx(L("Inför ", "Before "))}<strong data-health-name></strong>{tx(L(" får du inte:", " you must not:"))}</p></div>
      <p class="alert alert--step" role="alert" tabindex="-1" hidden></p>
      <div class="bk-health">
        <ul class="bk-qs">{qs}</ul>
        <aside class="bk-prep">{tx(L("Bra att veta inför besöket", "Good to know before your visit"), "h3")}{prep_html}</aside>
      </div>
      <div class="alert" data-health-alert hidden>
        {tx(L("Då kan vi tyvärr inte utföra behandlingen just nu. Boka gärna en kostnadsfri konsultation så hjälper vi dig vidare.", "Then we cannot carry out the treatment right now. Please book a free consultation and we will help you further."), "p")}
        <button type="button" class="btn btn--ink btn--sm" data-switch-consult>{tx(L("Byt till kostnadsfri konsultation", "Switch to a free consultation"))}</button>
      </div>
      {tx(contra_note, "p", "note") if contra_note else ""}
      {nav()}
    </div>

    <div class="bstep" data-step="3" hidden>
      <div class="bstep__head"><span class="bstep__num" data-stepnum></span>{tx(L("Dina uppgifter", "Your details"), "h2")}{tx(L("Vi använder uppgifterna bara för att bekräfta din bokning.", "We only use your details to confirm your booking."), "p")}</div>
      <form class="form bk-form" novalidate>
        <div class="form__row form__row--2">
          <div class="field ff"><input id="b-fname" name="fname" autocomplete="given-name" required placeholder=" "><label for="b-fname">{tx(L("Förnamn", "First name"))}</label><span class="field__err" aria-live="polite"></span></div>
          <div class="field ff"><input id="b-lname" name="lname" autocomplete="family-name" required placeholder=" "><label for="b-lname">{tx(L("Efternamn", "Last name"))}</label><span class="field__err" aria-live="polite"></span></div>
        </div>
        <div class="form__row form__row--2">
          <div class="field ff"><input id="b-email" name="email" type="email" autocomplete="email" required placeholder=" "><label for="b-email">{tx(L("E-post", "Email"))}</label><span class="field__err" aria-live="polite"></span></div>
          <div class="field ff ff--phone"><div class="phone"><select name="cc"{ia(L("Landsnummer", "Country code"), "aria-label")}><option value="+46">SE +46</option><option value="+47">NO +47</option><option value="+45">DK +45</option><option value="+358">FI +358</option><option value="+44">UK +44</option><option value="+49">DE +49</option></select>
            <span class="ff__wrap"><input id="b-phone" name="phone" type="tel" autocomplete="tel-national" inputmode="tel" required placeholder=" "><label for="b-phone">{tx(L("Mobilnummer", "Mobile number"))}</label></span></div><span class="field__err" aria-live="polite"></span></div>
        </div>
        <div class="bk-sub">{tx(L("Påminnelse före besöket", "Reminder before the visit"), "h3")}
          <div class="chips-select">
            <label><input type="radio" name="b-remind" value="sms" checked><span>{tx(L("Sms", "Text message"))}</span></label>
            <label><input type="radio" name="b-remind" value="email"><span>{tx(L("E-post", "Email"))}</span></label>
            <label><input type="radio" name="b-remind" value="both"><span>{tx(L("Båda", "Both"))}</span></label>
          </div></div>
        <div class="field ff"><textarea id="b-msg" name="message" placeholder=" "></textarea><label for="b-msg">{tx(L("Meddelande (valfritt), till exempel önskad form eller färg", "Message (optional), for example the shape or colour you have in mind"))}</label></div>
        <label class="check" data-terms><input type="checkbox" name="terms"><span>{tx(canc)}</span><span class="field__err" aria-live="polite" style="grid-column:2"></span></label>
        <div class="hp" aria-hidden="true"><label for="b-web">Webbplats</label><input id="b-web" name="website" tabindex="-1" autocomplete="off"></div>
        <div class="bnav"><button type="button" class="btn btn--ghost" data-prev>{ICON["left"]}{tx(L("Tillbaka", "Back"))}</button><button type="submit" class="btn btn--primary">{tx(L("Skicka bokningsförfrågan", "Send booking request"))}{ICON["send"]}</button></div>
      </form>
    </div>

    <div class="bstep confirm" data-step="4" hidden role="status">
      <svg class="confirm__check" viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="29" pathLength="1"/><path d="m19 33 9 9 18-19" pathLength="1"/></svg>
      <h2>{tx(L("Tack, ", "Thank you, "))}<span data-confirm-name></span>!</h2>
      {tx(L("Din bokningsförfrågan är skickad. Vi bekräftar tiden via e-post och sms.", "Your booking request has been sent. We will confirm the time by email and text message."), "p", "lead")}
      <div class="confirm__ticket">
        <div>{tx(L("Referens", "Reference"), "span")}<strong data-confirm-ref></strong></div>
        <div>{tx(L("Bokning", "Booking"), "span")}<strong data-confirm-what></strong></div>
        <div>{tx(L("Önskade dagar", "Preferred days"), "span")}<strong data-confirm-when></strong></div>
      </div>
      <div class="confirm__prep" data-confirm-prep hidden>{tx(L("Förbered dig inför besöket", "Prepare for your visit"), "h3")}<div data-prep-list></div></div>
      <div class="btn-row"><a class="btn btn--ink" href="behandlingar.html" data-confirm-read hidden>{tx(L("Läs om behandlingen", "Read about the treatment"))}</a><a class="btn btn--ghost" href="{DIRECTIONS}" target="_blank" rel="noopener">{tx(L("Vägbeskrivning", "Directions"))}</a><a class="btn btn--ghost" href="index.html">{tx(L("Till startsidan", "Back to home"))}</a></div>
      <a class="demo-link" href="kundkort.html#ny">{ICON["user"]}{tx(L("Prototyp: se hur bokningen hamnar i Lauras kundkort", "Prototype: see how the booking lands in Laura's client records"))}</a>
    </div>
  </div>

  <aside class="bk-aside"><div class="summary" aria-live="polite">
    <div class="summary__media"><img class="summary__img" alt="" width="640" height="420" hidden></div>
    {tx(L("Din bokning", "Your booking"), "h2")}
    <dl></dl>
    <ul class="summary__trust">
      <li>{check}{tx(L("Bekräftelse via e-post och sms", "Confirmation by email and text"))}</li>
      <li>{check}{tx(L("Avbokning senast 24 timmar innan", "Cancel up to 24 hours before"))}</li>
    </ul>
  </div></aside>

  <div class="bk-bar"><div class="bk-bar__info">{tx(L("Din bokning", "Your booking"), "small")}<strong data-bar-what></strong></div><button type="button" class="btn btn--primary" data-bar-next>{tx(L("Fortsätt", "Continue"))}</button></div>
</div></section>
<script type="application/json" id="booking-data">{json.dumps(data, ensure_ascii=False)}</script>
</main>
"""
    return head(title, desc, "boka.html", [crumbs_ld(cr)]) + body + footer()


def page_kundkort():
    lang_sw = f"""<div class="lang-switch" role="group"{ia(U["langLabel"], "aria-label")}><button type="button" value="sv" aria-pressed="true" lang="sv">SV</button><button type="button" value="en" aria-pressed="false" lang="en">EN</button></div>"""
    theme = f'<button type="button" class="icon-btn theme-btn"{ia(U["theme"], "aria-label")} aria-pressed="false">{ICON["moon"]}{ICON["sun"]}</button>'

    def half(k, side):
        return img_src(f"ba-{k}-{side}", 640)
    data = {
        "treatments": {t["slug"]: {"name": t["name"], "group": t["group"]} for t in TREATMENTS},
        "img": {k: {"before": half(k, "before"), "after": half(k, "after")} for k in ("bryn", "lappar", "fraknar") if img_meta(f"ba-{k}-before")},
        "avatars": {k: img_src(v, 640) for k, v in {"anna": "result-powder-brows-strokes-front", "maria": "ba-lappar-after", "sara": "ba-fraknar-after",
                                                       "johan": "smp-practitioner-scalp", "karin": "result-microblading-before-after", "elin": "academy-training-kit-table"}.items() if img_meta(v)},
        "courseName": (CBY.get("signature-pmu") or {}).get("name", L("Signature PMU Artist Program")),
        "coursePrice": (CBY.get("signature-pmu") or {}).get("price") or L("Enligt prislista", "Per price list"),
    }
    title = L("Kundkort | Plaza Di Laura", "Client records | Plaza Di Laura")
    desc = L("Prototyp av Plaza Di Lauras kundkort för personal: klienthistorik, behandlingar, bokningar, samtycke, betalningar, hälsodeklaration, dokumentationsbilder och kontakt.",
             "Prototype of Plaza Di Laura's staff client records: history, treatments, bookings, consent, payments, health declaration, documentation photos and contact.")
    extra_head = f'<link rel="stylesheet" href="assets/css/app.css?v={APP_CSS_V}">\n<script defer src="assets/js/kundkort.js?v={APP_JS_V}"></script>\n</head>'
    body = f"""<body class="app-body">
<a class="skip" href="#app-main">{tx(U["skip"])}</a>
<header class="app-bar">
  <a class="brand-link" href="index.html"{ia(L("Plaza Di Laura, till startsidan", "Plaza Di Laura, home"), "aria-label")}>{logo()}</a>
  {tx(L("Kundkort", "Client records"), "h1", "app-bar__title")}
  <span class="demo-tag">Demo</span>
  <div class="app-bar__tools"><button type="button" class="app-bar__phone" data-phone-open><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="6.5" y="2.5" width="11" height="19" rx="2.5"/><path d="M10.5 18.5h3"/></svg>{tx(L("Mobilvy", "Phone view"))}</button><a class="app-bar__site" href="index.html">{ICON["left"]}{tx(L("Till webbplatsen", "Back to website"))}</a>{lang_sw}{theme}</div>
</header>
<main>
  <section class="login">
    <div class="login__card">
      {logo()}
      {tx(L("Logga in", "Sign in"), "h2")}
      {tx(L("Kundkort för Plaza Di Laura. Endast personal.", "Client records for Plaza Di Laura. Staff only."), "p")}
      <div class="login__btns">
        <button type="button" class="btn btn--primary" data-login>{tx(L("Logga in med BankID", "Sign in with BankID"))}</button>
        <button type="button" class="btn btn--ghost" data-login>{tx(L("Logga in med e-post", "Sign in with email"))}</button>
      </div>
      <div class="login__wait" hidden role="status"><span class="spinner" aria-hidden="true"></span>{tx(L("Öppna BankID-appen på din telefon", "Open the BankID app on your phone"), "p")}</div>
      {tx(L("Prototyp med påhittade exempelkunder. Inga riktiga kunduppgifter visas.", "Prototype with made-up example clients. No real client data is shown."), "p", "small muted")}
    </div>
  </section>
  <div class="app" hidden>
    <aside class="app-list"{ia(L("Klientlista", "Client list"), "aria-label")}>
      <div class="app-list__head">
        {tx(L("Klienter", "Clients"), "h2")}
        <label class="app-search"><span class="sr-only">{tx(L("Sök klient", "Search clients"))}</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/></svg><input type="search" autocomplete="off"{ia(L("Sök på namn eller e-post", "Search by name or email"), "placeholder")}></label>
        <div class="app-filters" role="group"{ia(L("Filtrera klienter", "Filter clients"), "aria-label")}></div>
      </div>
      <div class="app-stats"></div>
      <ul class="client-list"></ul>
    </aside>
    <div class="app-main" id="app-main" aria-live="polite"></div>
  </div>
</main>
<div class="phone-stage" hidden role="dialog" aria-modal="true"{ia(L("Kundkort i mobilvy", "Client records in phone view"), "aria-label")}>
  <div class="phone-stage__copy">
    {logo()}
    {tx(L("Kundkort", "Client record"), "span", "label")}
    <span class="phone-stage__rule" aria-hidden="true"></span>
    {tx(L("Hela kundkortet i telefonen", "The whole client record on your phone"), "h2")}
    {tx(L("Samma kundkort som på datorn, byggt för mobilen. Klicka runt i telefonen: öppna en klient, gå mellan delarna och jämför före och efter.", "The same client record as on the computer, built for the phone. Click around inside the phone: open a client, move between sections and compare before and after."), "p")}
    <button type="button" class="btn btn--ghost" data-phone-close>{tx(L("Stäng mobilvy", "Close phone view"))}</button>
  </div>
  <div class="device"><iframe title="Kundkort" src="about:blank" loading="lazy"></iframe></div>
</div>
<dialog class="app-modal"><div class="app-modal__head"><h2></h2><button type="button" class="icon-btn app-modal__close"{ia(U["close"], "aria-label")}>{ICON["close"]}</button></div><div class="app-modal__body"></div></dialog>
<div class="toast" role="status" aria-live="polite"></div>
<script type="application/json" id="kk-data">{json.dumps(data, ensure_ascii=False)}</script>
</body>
</html>
"""
    return head(title, desc, "kundkort.html").replace("</head>", extra_head, 1) + body


def page_404():
    title = L("Sidan finns inte | Plaza Di Laura", "Page not found | Plaza Di Laura")
    desc = L("Sidan du letar efter finns inte.", "The page you are looking for does not exist.")
    body = f"""<body>
{header('')}
<main id="main"><div class="container nf">
  <svg viewBox="0 0 220 70" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M8 58 C 46 22, 104 8, 152 16 S 204 36, 212 48"/></svg>
  {tx(L("Sidan finns inte", "Page not found"), "h1", "h-1")}
  {tx(L("Länken kan vara gammal eller felstavad. Här är några bra ställen att börja:", "The link may be old or misspelled. Here are a few good places to start:"), "p", "lead")}
  <div class="btn-row"><a class="btn btn--primary" href="index.html">{tx(L("Till startsidan", "Back to home"))}</a><a class="btn btn--ghost" href="behandlingar.html">{tx(U["treatments"])}</a><a class="btn btn--ghost" href="akademi.html">{tx(U["academy"])}</a></div>
</div></main>
"""
    return head(title, desc, "404.html") + body + footer()


def main():
    if not TREATMENTS or not COURSES:
        print("Content not ready: treatments.json and courses.json are required.")
        sys.exit(1)
    print("Building pages")
    write("index.html", page_home())
    write("behandlingar.html", page_treatments())
    for t in TREATMENTS:
        write(tfile(t["slug"]), page_treatment(t))
    write("akademi.html", page_academy())
    for c in COURSES:
        write(cfile(c["slug"]), page_course(c))
    write("resultat.html", page_results())
    write("om-laura.html", page_about())
    write("kontakt.html", page_contact())
    write("boka.html", page_booking())
    write("kundkort.html", page_kundkort())
    write("404.html", page_404())
    print("Done")


if __name__ == "__main__":
    main()
