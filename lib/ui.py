# -*- coding: utf-8 -*-
"""Markup layer: head, topbar, footer, overlays, cards, rows, hero, episodes.

Η γλώσσα του Prime Video, μεταφρασμένη σε ιατρείο:
  τίτλος            -> μια υπηρεσία / πάθηση
  επεισόδια         -> οι ενότητες του κειμένου (κάθε <h2>)
  trailer           -> το βίντεο του ιατρείου για το θέμα
  X-Ray             -> τα στοιχεία της σελίδας με μια ματιά
  Watchlist         -> «Η λίστα μου», στη συσκευή
  Continue watching -> «Συνεχίστε την ανάγνωση», από την πρόοδο των επεισοδίων
  Profiles          -> «Ποιος παρακολουθεί;» και η αρχική αλλάζει σειρά
"""
import re, os, json, html, struct
from content import (SITE, CATEGORIES, CAT, SERVICES, SVC, SERVICE_CAT, VIDEOS, VID, TESTIMONIALS,
                     rel, read_minutes, pretty_date, plain, shorten, IMGMAP, ROOT)

ASSET_V = "1"
IMG_SRC = os.path.join(ROOT, "content", "img-src")

I = {
 "play": '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>',
 "plus": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
 "check": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 "info": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/><path d="M12 11v6M12 7.5v.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
 "search": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="1.8"/><path d="M16.5 16.5 21 21" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
 "left": '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" aria-hidden="true"><path d="M14.5 5 8 12l6.5 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 "right": '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" aria-hidden="true"><path d="M9.5 5 16 12l-6.5 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 "close": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
 "phone": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true"><path d="M5 3h3.5l1.7 4.2-2.1 1.5a12.5 12.5 0 0 0 6.2 6.2l1.5-2.1L20 14.5V18a2 2 0 0 1-2.2 2A16.8 16.8 0 0 1 3 6.2 2 2 0 0 1 5 3z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>',
 "mail": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2" stroke="currentColor" stroke-width="1.8"/><path d="m4 7 8 5.5L20 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
 "pin": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true"><path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><circle cx="12" cy="10" r="2.4" stroke="currentColor" stroke-width="1.8"/></svg>',
 "clock": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="8.5" stroke="currentColor" stroke-width="1.8"/><path d="M12 7.5V12l3 2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 "list": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" aria-hidden="true"><path d="M4 7h10M4 12h10M4 17h7M17 15l2 2 3-3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 "burger": '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
 "xray": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" stroke-width="1.8"/><path d="M7 9h10M7 13h6M7 17h3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
 "ext": '<svg viewBox="0 0 24 24" width="12" height="12" fill="none" aria-hidden="true"><path d="M8 16 16 8M9 8h7v7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 "fb": '<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M13.5 21v-8h2.7l.4-3.1h-3.1V7.9c0-.9.25-1.5 1.55-1.5h1.65V3.6c-.29-.04-1.27-.12-2.41-.12-2.39 0-4.02 1.46-4.02 4.13v2.3H7.5V13h2.77v8h3.23z"/></svg>',
 "yt": '<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M21.6 7.2a2.5 2.5 0 0 0-1.75-1.77C18.3 5 12 5 12 5s-6.3 0-7.85.43A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.75 1.77C5.7 19 12 19 12 19s6.3 0 7.85-.43a2.5 2.5 0 0 0 1.75-1.77A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8zM10 15V9l5.2 3-5.2 3z"/></svg>',
 "ig": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.8"/><circle cx="17.3" cy="6.7" r="1.1" fill="currentColor"/></svg>',
 "x": '<svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor" aria-hidden="true"><path d="M17.5 3h3l-7.3 8.4L22 21h-6.6l-5-6.4L4.5 21h-3l7.8-9L1.5 3h6.7l4.5 5.9L17.5 3zm-1.1 16.2h1.7L7.2 4.7H5.4l11 14.5z"/></svg>',
 "star": '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true"><path d="m12 2.5 2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4 6.1 20.5l1.2-6.5L2.5 9.4l6.6-.9z"/></svg>',
 "chev": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true"><path d="m6 9 6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 "print": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" aria-hidden="true"><path d="M7 8V4h10v4M7 17H4v-6h16v6h-3M8 14h8v6H8z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>',
 "share": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" aria-hidden="true"><path d="M12 3v12M8 7l4-4 4 4M5 14v5h14v-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}

FONTS = "https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap"

NAV = [("", "Αρχική", "home"), ("katigoria/maieftiki/", "Μαιευτική", "maieftiki"),
       ("katigoria/gynaikologia/", "Γυναικολογία", "gynaikologia"),
       ("katigoria/xeirourgiki/", "Χειρουργική", "xeirourgiki"), ("services/", "Όλα τα θέματα", "services"),
       ("video-gallery/", "Βίντεο", "video"), ("blog/", "Άρθρα", "blog"),
       ("gynaikologos-dr-k-myrillas/", "Ο γιατρός", "doctor")]

PROFILES = [("egkymosyni", "Εγκυμοσύνη", "#1399FF", ["maieftiki", "apovoli"]),
            ("gynaikologia", "Γυναικολογία", "#FF4F8B", ["gynaikologia", "endomitrio", "oothikes", "traxilos", "hpv"]),
            ("emminopafsi", "Εμμηνόπαυση", "#5AD8A6", ["emminopafsi"]),
            ("gonimotita", "Γονιμότητα", "#F2D06B", ["gonimotita", "apovoli", "gynaikologia"]),
            ("xeirourgiki", "Χειρουργείο", "#00D1B2", ["xeirourgiki", "gynaikologia"])]


# ── images ───────────────────────────────────────────────────────────────────
_DIM = {}


def img_size(name):
    if name in _DIM:
        return _DIM[name]
    size = None
    path = os.path.join(IMG_SRC, name)
    try:
        with open(path, "rb") as fh:
            head = fh.read(32)
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                size = struct.unpack(">II", head[16:24])
            elif head[:4] == b"RIFF" and head[8:12] == b"WEBP":
                size = None
            elif head[:2] == b"\xff\xd8":
                fh.seek(2)
                while True:
                    b = fh.read(1)
                    if not b:
                        break
                    if b != b"\xff":
                        continue
                    while b == b"\xff":
                        b = fh.read(1)
                    marker = b[0]
                    if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                        continue
                    seg = fh.read(2)
                    if len(seg) < 2:
                        break
                    ln = struct.unpack(">H", seg)[0]
                    if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                        d = fh.read(5)
                        size = (struct.unpack(">H", d[3:5])[0], struct.unpack(">H", d[1:3])[0])
                        break
                    fh.seek(ln - 2, 1)
    except OSError:
        size = None
    _DIM[name] = size
    return size


def pic(name, alt, depth, *, w=800, h=450, eager=False, cls="", sizes=""):
    """<picture> με webp από το pipeline του build και το πρωτότυπο ως fallback."""
    if not name:
        return ""
    r = rel(depth)
    stem = name.rsplit(".", 1)[0]
    real = img_size(name)
    if real:
        w, h = real
    attrs = (f' width="{w}" height="{h}" alt="{html.escape(alt or "", quote=True)}"'
             f'{" sizes=" + chr(34) + sizes + chr(34) if sizes else ""}'
             f'{" fetchpriority=" + chr(34) + "high" + chr(34) if eager else " loading=" + chr(34) + "lazy" + chr(34)}'
             f' decoding="async"{" class=" + chr(34) + cls + chr(34) if cls else ""}')
    return (f'<picture><source srcset="{r}assets/img/{stem}.webp" type="image/webp">'
            f'<img src="{r}assets/img/{name}"{attrs}></picture>')


def poster(title, kicker="", color="#1399FF"):
    """Τυπογραφική αφίσα για ό,τι δεν έχει φωτογραφία."""
    return (f'<span class="poster" style="--pc:{color}"><span class="poster__k">{html.escape(kicker)}</span>'
            f'<span class="poster__t">{html.escape(title)}</span></span>')


# ── head / chrome ────────────────────────────────────────────────────────────
def head(*, title, desc, depth, canonical, jsonld=None, body_class="", og_image=None, kind="website", noindex=False):
    r = rel(depth)
    ld = "".join('<script type="application/ld+json">' + json.dumps(b, ensure_ascii=False, separators=(",", ":"))
                 + "</script>\n" for b in (jsonld or []))
    img_name = og_image or "og-default.jpg"
    og = f"{SITE['domain']}/assets/img/{img_name}"
    dims = (1200, 630) if not og_image else img_size(og_image)
    og_type = "image/png" if img_name.lower().endswith(".png") else "image/jpeg"
    og_dims = (f'<meta property="og:image:width" content="{dims[0]}">\n<meta property="og:image:height" content="{dims[1]}">\n'
               if dims else "")
    robots = ("noindex, follow" if noindex else
              "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1")
    return f'''<!doctype html>
<html lang="el" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#0F171E">
<meta name="color-scheme" content="dark">
<link rel="canonical" href="{SITE['domain']}/{canonical}">
<link rel="icon" href="{r}assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{r}assets/img/apple-touch-icon.png">
<meta name="geo.region" content="{SITE['region_iso']}">
<meta name="geo.placename" content="{SITE['locality']}">
<meta name="geo.position" content="{SITE['lat']};{SITE['lng']}">
<meta name="ICBM" content="{SITE['lat']}, {SITE['lng']}">
<meta property="og:type" content="{kind}">
<meta property="og:locale" content="el_GR">
<meta property="og:site_name" content="{SITE['name']}, Μαιευτήρας Χειρουργός Γυναικολόγος">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:url" content="{SITE['domain']}/{canonical}">
<meta property="og:image" content="{og}">
{og_dims}<meta property="og:image:type" content="{og_type}">
<meta property="og:image:alt" content="{html.escape(title, quote=True)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@KMyrillas">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="{FONTS}"></noscript>
<link rel="stylesheet" href="{r}assets/css/prime.css?v={ASSET_V}">
<script>document.documentElement.className='js';
try{{var p=localStorage.getItem('prime:profile');if(p)document.documentElement.dataset.profile=JSON.parse(p).id;
if(localStorage.getItem('prime:motion')==='"off"')document.documentElement.dataset.motion='off';}}catch(e){{}}</script>
{ld}</head>
<body class="{body_class}" data-depth="{depth}">
<a class="skip" href="#main">Μετάβαση στο περιεχόμενο</a>
'''


def wordmark(depth, href=""):
    r = rel(depth)
    return (f'<a class="tb__logo" href="{r}{href}" aria-label="{SITE["name"]}, αρχική">'
            f'<span class="wm"><span class="wm__t">myrillas</span>'
            f'<svg class="wm__smile" viewBox="0 0 120 22" aria-hidden="true"><path d="M3 5c26 18 76 18 108 3" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><path d="M104 3l9 4-4 9" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg></span>'
            f'<span class="wm__sub">γυναικολόγος</span></a>')


def topbar(depth, active=""):
    r = rel(depth)
    links = "".join(f'<a class="tb__link{" is-on" if slug == active else ""}" href="{r}{href}">{label}</a>'
                    for href, label, slug in NAV)
    return f'''<header class="tb" id="topbar" data-at-top="1">
  <div class="tb__in">
    {wordmark(depth)}
    <nav class="tb__nav" aria-label="Κύρια πλοήγηση">{links}</nav>
    <div class="tb__right">
      <button class="tb__ic" type="button" data-open="palette" aria-label="Αναζήτηση, Ctrl ή ⌘ και K">{I['search']}</button>
      <a class="tb__ic" href="{r}i-lista-mou/" aria-label="Η λίστα μου">{I['list']}<span class="tb__badge" data-mylist-count hidden>0</span></a>
      <button class="tb__ic tb__avatar" type="button" data-open="who" aria-label="Προφίλ"><span data-profile-avatar>Μ</span></button>
      <button class="btn btn--blue tb__cta" type="button" data-open="book">Ραντεβού</button>
      <button class="tb__ic tb__burger" type="button" data-open="drawer" aria-label="Μενού">{I['burger']}</button>
    </div>
  </div>
</header>
<div class="drawer" id="drawer" hidden>
  <div class="drawer__sheet" role="dialog" aria-modal="true" aria-label="Μενού">
    <button class="drawer__x" type="button" data-close aria-label="Κλείσιμο">{I['close']}</button>
    <nav class="drawer__nav">{links}</nav>
    <div class="drawer__cats">{"".join(f'<a href="{r}katigoria/{c["slug"]}/">{c.get("short", c["title"])}</a>' for c in CATEGORIES)}</div>
    <a class="btn btn--ghost" href="{r}i-lista-mou/">{I['list']}Η λίστα μου</a>
    <button class="btn btn--blue" type="button" data-open="book">Ζητήστε ραντεβού</button>
    <a class="drawer__tel" href="tel:{SITE['phone_href']}">{I['phone']}<span>{SITE['phone']}</span></a>
  </div>
</div>'''


def footer(depth):
    r = rel(depth)
    hours = "".join(f"<li><span>{d}</span><b>{t}</b></li>" for d, t in SITE["hours"])
    cats = "".join(f'<li><a href="{r}katigoria/{c["slug"]}/">{c["title"]}</a></li>' for c in CATEGORIES)
    top = "".join(f'<li><a href="{r}services/{s}/">{SVC[s]["title"]}</a></li>' for s in
                  ["laparoskopikes-epemvaseis", "inomyomata-mitras", "endomitriosi-symptomata-diagnosi-therapeia",
                   "ysteroskopisi", "robotiki-xeirourgiki", "hpv-limoksi", "katapsyksi-kryosyntirisi-oarion"])
    return f'''<footer class="ft">
  <div class="wrap ft__grid">
    <div class="ft__brand">
      {wordmark(depth)}
      <p class="ft__tag">{SITE['doctor']}, {SITE['tagline']}. Ιατρείο στον Βύρωνα, χειρουργεία στο {SITE['hospital']}.</p>
      <div class="ft__soc">
        <a href="{SITE['social']['facebook']}" rel="noopener" target="_blank" aria-label="Facebook">{I['fb']}</a>
        <a href="{SITE['social']['youtube']}" rel="noopener" target="_blank" aria-label="YouTube">{I['yt']}</a>
        <a href="{SITE['social']['instagram']}" rel="noopener" target="_blank" aria-label="Instagram">{I['ig']}</a>
        <a href="{SITE['social']['twitter']}" rel="noopener" target="_blank" aria-label="X">{I['x']}</a>
      </div>
    </div>
    <div><h3>Βασικές υπηρεσίες</h3><ul>{top}</ul></div>
    <div><h3>Κατηγορίες</h3><ul>{cats}</ul></div>
    <div><h3>Το site</h3><ul>
      <li><a href="{r}services/">Όλα τα θέματα</a></li>
      <li><a href="{r}blog/">Άρθρα</a></li>
      <li><a href="{r}video-gallery/">Βίντεο</a></li>
      <li><a href="{r}photo-gallery/">Gallery</a></li>
      <li><a href="{r}gynaikologos-dr-k-myrillas/">Ο γιατρός</a></li>
      <li><a href="{r}odigos/">Τι με αφορά;</a></li>
      <li><a href="{r}i-lista-mou/">Η λίστα μου</a></li>
      <li><a href="{r}epikinonia/">Επικοινωνία</a></li>
    </ul></div>
    <div class="ft__nap"><h3>Ιατρείο</h3>
      <ul class="ft__contact">
        <li>{I['pin']}<span>{SITE['address']}, {SITE['locality']}<br>{SITE['postcode']}, {SITE['region']}</span></li>
        <li>{I['phone']}<span><a href="tel:{SITE['phone_href']}">{SITE['phone']}</a> · <a href="tel:{SITE['mobile_href']}">{SITE['mobile']}</a></span></li>
        <li>{I['mail']}<a href="mailto:{SITE['email']}">{SITE['email']}</a></li>
      </ul>
      <ul class="ft__hours">{hours}</ul>
    </div>
  </div>
  <div class="wrap ft__base">
    <p>© {SITE['domain'][8:]} · {SITE['doctor']}, {SITE['tagline']}</p>
    <p><a href="{r}oroi-chrisis/">Όροι χρήσης & απόρρητο</a></p>
  </div>
  <p class="ft__disclaimer">Το περιεχόμενο είναι ενημερωτικό και δεν υποκαθιστά την ιατρική εξέταση.
    Κάθε περιστατικό αξιολογείται ξεχωριστά στο ιατρείο.</p>
  <p class="ft__credit">Made by <a href="https://clinicbrain.gr" rel="noopener" target="_blank">CLINICBRAIN</a></p>
</footer>'''


# ── badges, pills ────────────────────────────────────────────────────────────
def prime_badge(text="Στο ιατρείο"):
    return f'<span class="pbadge">{I["check"]}<span>{text}</span></span>'


def pills(items):
    return '<span class="pills">' + "".join(f'<span class="pill{" pill--" + c if c else ""}">{html.escape(t)}</span>'
                                             for t, c in items if t) + '</span>'


def save_btn(item_id, title, url, kind, label=None, cls="ic"):
    payload = html.escape(json.dumps({"id": item_id, "t": title, "u": url, "k": kind}, ensure_ascii=False), quote=True)
    if label is None:
        return (f'<button class="ic ic--save" type="button" data-save=\'{payload}\' '
                f'aria-label="Προσθήκη στη λίστα μου">{I["plus"]}{I["check"]}</button>')
    return (f'<button class="btn btn--ghost save-inline" type="button" data-save=\'{payload}\'>'
            f'{I["plus"]}{I["check"]}<span>{label}</span></button>')


# ── cards ────────────────────────────────────────────────────────────────────
def episodes_of(body):
    """Σπάει το κείμενο σε «επεισόδια» στα <h2>. Επιστρέφει [(title, html)]."""
    parts = re.split(r"(<h2>.*?</h2>)", body or "", flags=re.S)
    eps, cur_t, buf = [], None, ""
    for p in parts:
        if p.startswith("<h2>"):
            if buf.strip() or cur_t:
                eps.append((cur_t, buf))
            cur_t, buf = plain(p), ""
        else:
            buf += p
    if buf.strip() or cur_t:
        eps.append((cur_t, buf))
    out = []
    for t, h in eps:
        if not t and len(plain(h).split()) < 25:
            continue
        if t and re.match(r"^(Γυναικολογικά Άρθρα|Άρθρα Σχετικά|Μαιευτικά Άρθρα)", t):
            continue
        if not t:
            t = "Εισαγωγή"
        out.append((t, h))
    return out


def card(item, depth, *, kind="service", n=None, wide=False, progress=True):
    """Κάρτα 16:9 του Prime Video, με το hover panel από κάτω."""
    r = rel(depth)
    if kind == "service":
        url, cat = f"services/{item['slug']}/", CAT[item["cat"]]
        k = f"{item['kind']} · {cat.get('short', cat['title'])}"
        eps = len(episodes_of(item["body"]))
        meta = pills([(f"{eps} ενότητες" if eps > 1 else "1 ενότητα", ""),
                      (f"{read_minutes(item['words'])} λεπτά", ""),
                      ("Βίντεο", "blue") if item["videos"] else ("", "")])
        color = cat["color"]
    else:
        url, k, color = f"{item['slug']}/", f"Άρθρο · {item['tag']}", "#8197A4"
        meta = pills([(f"{read_minutes(item['words'])} λεπτά", ""), (pretty_date(item["pub"]), "")])
    art = pic(item["image"], item["title"], depth, sizes="(max-width:700px) 80vw, 25vw") if item["image"] \
        else poster(item["title"], k, color)
    num = f'<span class="card__n" aria-hidden="true">{n}</span>' if n else ""
    return f'''<article class="card{" card--wide" if wide else ""}{" card--num" if n else ""}" data-card="{html.escape(url)}" data-cat="{item.get('cat', '')}">
  {num}<a class="card__link" href="{r}{url}">
    <span class="card__img">{art}<span class="card__shade"></span>
      <span class="card__cap"><span class="card__k">{html.escape(k)}</span><span class="card__t">{html.escape(item['title'])}</span></span>
      <i class="card__prog" data-prog hidden><b></b></i>
    </span>
  </a>
  <div class="card__hover" aria-hidden="true">
    <div class="card__acts">
      <a class="ic ic--play" href="{r}{url}" tabindex="-1" aria-label="Δείτε">{I['play']}</a>
      {save_btn(url, item['title'], url, kind)}
      <button class="ic" type="button" data-xray="{html.escape(url)}" tabindex="-1" aria-label="X-Ray">{I['xray']}</button>
    </div>
    {prime_badge()}{meta}
    <p class="card__lead">{html.escape(shorten(item['lead'], 130))}</p>
  </div>
</article>'''


def video_card(v, depth, *, wide=True):
    thumb = pic(v["thumb"], v["title"], depth) if v.get("thumb") else \
        f'<img src="https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg" alt="" loading="lazy" decoding="async" width="480" height="360">'
    return f'''<article class="card card--video{" card--wide" if wide else ""}">
  <button class="card__link" type="button" data-video="{v['id']}" data-vtitle="{html.escape(v['title'], quote=True)}" aria-label="Αναπαραγωγή: {html.escape(v['title'], quote=True)}">
    <span class="card__img">{thumb}<span class="card__shade"></span>
      <span class="card__play">{I['play']}</span>
      <span class="card__cap"><span class="card__k">{html.escape(v['kicker'])}</span><span class="card__t">{html.escape(v['title'])}</span></span>
    </span>
  </button>
</article>'''


def row(*, rid, title, cards, sub="", all_href=None, all_label="Δείτε όλα", kind="", attrs=""):
    if not cards:
        return ""
    more = f'<a class="row__all" href="{all_href}">{all_label}{I["right"]}</a>' if all_href else ""
    subh = f'<p class="row__sub">{html.escape(sub)}</p>' if sub else ""
    return f'''<section class="row {kind}" data-row id="{rid}" {attrs}>
  <div class="wrap row__head">
    <div><h2 class="row__title">{title}</h2>{subh}</div>
    <div class="row__nav">{more}
      <button class="row__btn row__nav--l" type="button" aria-label="Προηγούμενα" tabindex="-1">{I['left']}</button>
      <button class="row__btn row__nav--r" type="button" aria-label="Επόμενα">{I['right']}</button>
    </div>
  </div>
  <div class="row__vp row__track" tabindex="0" role="list" aria-label="{html.escape(re.sub(r'<[^>]+>', '', title))}">
    <div class="row__track-in">{''.join(cards)}</div>
  </div>
</section>'''


# ── hero carousel (αρχική) ───────────────────────────────────────────────────
def hero(depth, slides, extra=""):
    r = rel(depth)
    out, dots = [], []
    for i, h in enumerate(slides):
        s = SVC[h["service"]]
        cat = CAT[s["cat"]]
        title = h.get("title") or s["title"]
        lead = h.get("lead") or s["lead"]
        eps = len(episodes_of(s["body"]))
        url = f"services/{s['slug']}/"
        trailer = (f'<button class="btn btn--ghost" type="button" data-video="{h["video"]}" data-vtitle="{html.escape(VID[h["video"]]["title"], quote=True)}">{I["play"]}Trailer</button>'
                   if h.get("video") and h["video"] in VID else "")
        out.append(f'''<div class="hero__slide{" is-on" if i == 0 else ""}" data-slide="{i}" {"aria-hidden=true" if i else ""}>
  <div class="hero__bg" style="object-position:{h['pos']}">{pic(h['image'], '', depth, eager=(i == 0))}</div>
  <div class="wrap hero__body">
    <p class="hero__kicker">{html.escape(h['kicker'])}</p>
    <h{1 if i == 0 else 2} class="hero__title">{html.escape(title)}</h{1 if i == 0 else 2}>
    <div class="hero__meta">{prime_badge()}{pills([(s['kind'], ''), (cat.get('short', cat['title']), ''), (f"{eps} ενότητες", ''), (f"{read_minutes(s['words'])} λεπτά", '')])}</div>
    <p class="hero__lead">{html.escape(lead)}</p>
    <div class="hero__acts">
      <a class="btn btn--blue btn--lg" href="{r}{url}">{I['play']}Δείτε</a>
      {trailer}
      {save_btn(url, s['title'], url, 'service', label='Η λίστα μου')}
      <button class="ic ic--lg" type="button" data-xray="{url}" aria-label="X-Ray">{I['xray']}</button>
    </div>
  </div>
</div>''')
        dots.append(f'<button type="button" data-dot="{i}" aria-label="Διαφάνεια {i + 1}: {html.escape(title, quote=True)}"{" aria-current=true" if i == 0 else ""}><i></i></button>')
    return f'''<section class="hero" id="hero" data-hero aria-roledescription="carousel">
  {extra}
  {''.join(out)}
  <div class="wrap hero__dots">{''.join(dots)}</div>
  <button class="hero__arrow hero__arrow--l" type="button" data-hero-prev aria-label="Προηγούμενο">{I['left']}</button>
  <button class="hero__arrow hero__arrow--r" type="button" data-hero-next aria-label="Επόμενο">{I['right']}</button>
</section>'''


# ── title page pieces ────────────────────────────────────────────────────────
def title_hero(depth, *, crumb, kicker, title, lead, meta_pills, image, url, kind, trailer_id=None,
               eps=0, acts_extra=""):
    r = rel(depth)
    bg = pic(image, "", depth, eager=True) if image else ""
    trailer = (f'<button class="btn btn--ghost btn--lg" type="button" data-video="{trailer_id}" data-vtitle="{html.escape(VID[trailer_id]["title"], quote=True)}">{I["play"]}Trailer</button>'
               if trailer_id and trailer_id in VID else "")
    play = (f'<a class="btn btn--blue btn--lg" href="#ep-1" data-play-ep>{I["play"]}Ξεκινήστε</a>' if eps else "")
    return f'''<section class="th{" th--img" if image else ""}">
  <div class="th__bg" aria-hidden="true">{bg}</div>
  <div class="wrap th__in">
    <div class="th__text">{crumb}
      <p class="th__kicker">{html.escape(kicker)}</p>
      <h1 class="th__title">{html.escape(title)}</h1>
      <div class="th__meta">{prime_badge()}{pills(meta_pills)}</div>
      <p class="th__lead">{html.escape(lead)}</p>
      <div class="th__acts">{play}{trailer}
        {save_btn(url, title, url, kind, label='Η λίστα μου')}
        <button class="btn btn--ghost btn--lg" type="button" data-open="book" data-topic="{html.escape(title, quote=True)}">Ραντεβού</button>
        <button class="ic ic--lg" type="button" data-xray="{url}" aria-label="X-Ray">{I['xray']}</button>{acts_extra}
      </div>
    </div>
    {f'<div class="th__poster">{pic(image, title, depth, eager=True)}</div>' if image else ''}
  </div>
</section>'''


def tabs(panels, depth):
    """panels: [(id, label, html)]. Χωρίς JavaScript εμφανίζονται όλα στη σειρά."""
    btns = "".join(f'<button class="tabs__b{" is-on" if i == 0 else ""}" type="button" role="tab" '
                   f'aria-selected="{"true" if i == 0 else "false"}" aria-controls="tab-{pid}" id="tabb-{pid}">{label}</button>'
                   for i, (pid, label, _) in enumerate(panels))
    body = "".join(f'<div class="tabs__p{" is-on" if i == 0 else ""}" id="tab-{pid}" role="tabpanel" aria-labelledby="tabb-{pid}">{h}</div>'
                   for i, (pid, label, h) in enumerate(panels))
    return f'<div class="tabs" data-tabs><div class="wrap tabs__bar" role="tablist">{btns}</div>{body}</div>'


LINK_ALIAS = {"endomitria-paxynsi": "endomitria-paxinsi", "inomiomata-kindini": "inomyomata-mitras",
              "inomiomata-mitras": "inomyomata-mitras", "endomitriosi": "endomitriosi-symptomata-diagnosi-therapeia",
              "kystes-oothikon": "kystes-oothikon", "ysteroskopisi": "ysteroskopisi"}


def _fix_body(body, depth):
    """Εικόνες και σύνδεσμοι του παλιού site -> τοπικά· βίντεο -> facade."""
    r = rel(depth)

    def img(m):
        src = m.group(1).strip()
        alt = re.search(r'alt="([^"]*)"', m.group(0))
        local = IMGMAP.get(src) or IMGMAP.get(src.replace("https://kmyrillas.gr", ""))
        if not local:
            return ""
        return pic(local, alt.group(1) if alt else "", depth)
    body = re.sub(r'<img[^>]*src="([^"]+)"[^>]*>', img, body)

    def vid(m):
        vid_id, inner = m.group(1), m.group(2)
        v = VID.get(vid_id)
        title = v["title"] if v else "Βίντεο"
        thumb = re.search(r'<picture>.*?</picture>', inner, re.S)
        art = thumb.group(0) if thumb else f'<img src="https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg" alt="" loading="lazy" width="480" height="360">'
        return (f'<button class="vid" type="button" data-video="{vid_id}" data-vtitle="{html.escape(title, quote=True)}">'
                f'<span class="vid__img">{art}</span><span class="vid__play">{I["play"]}</span>'
                f'<span class="vid__t">{html.escape(title)}</span></button>')
    body = re.sub(r'<a[^>]*href="(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([A-Za-z0-9_-]{11})"[^>]*>(.*?)</a>',
                  vid, body, flags=re.S)

    def link(m):
        href = m.group(1)
        if href.startswith(("tel:", "mailto:", "#")):
            return m.group(0)
        if "kmyrillas.gr/wp-content/uploads" in href:
            local = IMGMAP.get(href)
            if local and local.startswith("docs/"):
                return f'href="{r}assets/{local}" target="_blank" rel="noopener"'
            return 'href="#" data-noop'  # σύνδεσμος σε εικόνα: η εικόνα είναι ήδη μέσα στο κείμενο
        m2 = re.match(r"^https?://(?:www\.)?kmyrillas\.gr/(.*?)/?$", href)
        if m2:
            path = m2.group(1)
            if path == "":
                return f'href="{r}"'
            slug = path.split("/")[-1]
            slug = LINK_ALIAS.get(slug, slug)
            if path.startswith("services/") and slug in SVC:
                return f'href="{r}services/{slug}/"'
            if slug in SVC:
                return f'href="{r}services/{slug}/"'
            if path in ("dr-k-myrillas", "gynaikologos-dr-k-myrillas", "robotiki-xeirourgiki"):
                return f'href="{r}gynaikologos-dr-k-myrillas/"' if "myrillas" in path else f'href="{r}services/robotiki-xeirourgiki/"'
            return f'href="{r}{path}/"'
        if href.startswith("/"):
            return f'href="{r}{href.lstrip("/")}"'
        if href.startswith("http"):
            return f'href="{href}" rel="noopener" target="_blank"'
        return m.group(0)
    body = re.sub(r'href="([^"]*)"', link, body)
    body = re.sub(r'<a href="#" data-noop>(.*?)</a>', r"\1", body, flags=re.S)
    body = re.sub(r'<a href="[^"]*"[^>]*>\s*</a>', "", body)
    body = re.sub(r"<p>\s*</p>", "", body)
    body = re.sub(r"<(strong|b)>\s*</\1>", "", body)
    body = body.replace("<h2><strong>", "<h2>").replace("</strong></h2>", "</h2>")
    body = re.sub(r"<h3><strong>(.*?)</strong></h3>", r"<h3>\1</h3>", body)
    # παλιά άρθρα: «επικεφαλίδες» γραμμένες ως έντονη παράγραφος μίας γραμμής
    body = re.sub(r"<p>\s*<strong>([^<]{2,48})</strong>\s*</p>", lambda m: f"<h3>{m.group(1).strip().rstrip(':')}</h3>", body)
    return body


def episodes(body, depth, *, slug, single_title="Το κείμενο"):
    eps = episodes_of(body)
    if not eps:
        return "", 0
    if len(eps) == 1:
        eps = [(single_title if eps[0][0] == "Εισαγωγή" else eps[0][0], eps[0][1])]
    items = []
    total = len(eps)
    for i, (t, h) in enumerate(eps, 1):
        words = len(plain(h).split())
        items.append(f'''<details class="ep" id="ep-{i}" data-ep="{i}"{" open" if i == 1 else ""}>
  <summary class="ep__s">
    <span class="ep__n">{i}</span>
    <span class="ep__t"><b>{html.escape(t)}</b><span class="ep__m">{read_minutes(words)} λεπτά · {words} λέξεις</span></span>
    <span class="ep__done" data-ep-done aria-label="Διαβάστηκε">{I['check']}</span>
    <span class="ep__chev">{I['chev']}</span>
  </summary>
  <div class="ep__body prose">{_fix_body(h, depth)}</div>
</details>''')
    head = "" if total == 1 else f'''<div class="eps__head">
  <p class="eps__count">Σεζόν 1 · {total} {"επεισόδια" if total > 1 else "επεισόδιο"}</p>
  <div class="eps__tools"><button class="linky" type="button" data-eps="open">Άνοιγμα όλων</button>
    <button class="linky" type="button" data-eps="close">Κλείσιμο όλων</button></div>
</div>'''
    return f'<div class="eps" data-eps-root="{html.escape(slug)}" data-total="{total}">{head}{"".join(items)}</div>', total


def crumbs(items, depth):
    r = rel(depth)
    li, ld = "", []
    for i, (label, href) in enumerate(items):
        ld.append({"@type": "ListItem", "position": i + 1, "name": label, "item": f"{SITE['domain']}/{href or ''}"})
        li += (f'<li aria-current="page">{html.escape(label)}</li>' if href is None
               else f'<li><a href="{r}{href}">{html.escape(label)}</a></li>')
    return (f'<nav class="crumbs" aria-label="Διαδρομή"><ol>{li}</ol></nav>',
            {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ld})


def details_dl(rows):
    return '<dl class="dl">' + "".join(f'<div><dt>{html.escape(k)}</dt><dd>{v}</dd></div>' for k, v in rows if v) + '</dl>'


def review(t, depth):
    r = rel(depth)
    svc = SVC.get(t["topic"])
    return f'''<article class="rev">
  <div class="rev__stars" aria-label="5 από 5">{I['star'] * 5}</div>
  <blockquote class="rev__q">«{html.escape(t['text'])}»</blockquote>
  <p class="rev__by"><b>{html.escape(t['name'])}</b> από {html.escape(t['place'])}
    {f'· <a href="{r}services/{svc["slug"]}/">{html.escape(svc["title"])}</a>' if svc else ''}</p>
</article>'''


def cta_band(depth, *, title="Μιλήστε με τον γιατρό",
             text="Μια εκτίμηση δεν δεσμεύει σε τίποτα. Ρωτήστε ό,τι σας απασχολεί."):
    return f'''<section class="band">
  <div class="wrap band__in">
    <div><h2>{html.escape(title)}</h2><p>{html.escape(text)}</p></div>
    <div class="band__acts">
      <button class="btn btn--blue btn--lg" type="button" data-open="book">Ζητήστε ραντεβού</button>
      <a class="btn btn--ghost btn--lg" href="tel:{SITE['phone_href']}">{I['phone']}{SITE['phone']}</a>
    </div>
  </div>
</section>'''


# ── overlays ─────────────────────────────────────────────────────────────────
def overlays(depth):
    r = rel(depth)
    topics = "".join(f'<option value="{html.escape(s["title"])}">{html.escape(s["title"])}</option>' for s in SERVICES)
    hours = "".join(f"<li><span>{d}</span><b>{h}</b></li>" for d, h in SITE["hours"])
    profs = "".join(f'''<button class="who__p" type="button" data-profile="{pid}" data-name="{name}" data-color="{color}" data-cats="{",".join(cats)}">
      <span class="who__av" style="--pc:{color}">{name[0]}</span><span>{name}</span></button>''' for pid, name, color, cats in PROFILES)
    return f'''
<div class="ov ov--who" id="who" hidden>
  <div class="ov__scrim" data-close></div>
  <div class="who" role="dialog" aria-modal="true" aria-labelledby="who-t">
    <button class="ov__x" type="button" data-close aria-label="Κλείσιμο">{I['close']}</button>
    <h2 id="who-t">Ποιος παρακολουθεί;</h2>
    <p>Διαλέξτε τι σας αφορά και η αρχική σελίδα αλλάζει σειρά. Η επιλογή μένει σε αυτή τη συσκευή.</p>
    <div class="who__grid">{profs}
      <button class="who__p" type="button" data-profile="" data-name="Επισκέπτης" data-color="#8197A4" data-cats="">
        <span class="who__av" style="--pc:#8197A4">Ε</span><span>Επισκέπτης</span></button>
    </div>
    <div class="who__foot">
      <label class="sw"><input type="checkbox" data-pref="motion"><span class="sw__t"></span><span>Κίνηση και εφέ</span></label>
      <button class="linky" type="button" data-wipe>Διαγραφή τοπικών δεδομένων</button>
    </div>
  </div>
</div>

<div class="ov ov--pal" id="palette" hidden>
  <div class="ov__scrim" data-close></div>
  <div class="pal" role="dialog" aria-modal="true" aria-label="Αναζήτηση">
    <div class="pal__bar">{I['search']}
      <input class="pal__in" type="search" placeholder="Πάθηση, επέμβαση, άρθρο ή βίντεο…" autocomplete="off" spellcheck="false" aria-label="Αναζήτηση" aria-controls="pal-res">
      <kbd>ESC</kbd></div>
    <div class="pal__res" id="pal-res" role="listbox" aria-label="Αποτελέσματα"></div>
    <div class="pal__foot"><span><kbd>↑</kbd><kbd>↓</kbd> πλοήγηση</span><span><kbd>↵</kbd> άνοιγμα</span><span><kbd>⌘</kbd><kbd>K</kbd> εναλλαγή</span></div>
  </div>
</div>

<div class="ov ov--full" id="player" hidden>
  <div class="ov__scrim" data-close></div>
  <div class="pl" role="dialog" aria-modal="true" aria-label="Βίντεο">
    <button class="ov__x" type="button" data-close aria-label="Κλείσιμο">{I['close']}</button>
    <div class="pl__frame"></div>
    <p class="pl__t"></p>
  </div>
</div>

<div class="ov ov--side" id="xray" hidden>
  <div class="ov__scrim" data-close></div>
  <aside class="xr" role="dialog" aria-modal="true" aria-labelledby="xr-t">
    <button class="ov__x" type="button" data-close aria-label="Κλείσιμο">{I['close']}</button>
    <p class="xr__k">{I['xray']} X-Ray</p>
    <h2 id="xr-t" class="xr__t"></h2>
    <div class="xr__body"></div>
    <div class="xr__doc">
      <img src="{r}assets/img/2021-11-dr-myrilas-1.jpg" alt="" width="60" height="90" loading="lazy">
      <div><b>{SITE['doctor']}</b><span>{SITE['tagline']}</span><a href="{r}gynaikologos-dr-k-myrillas/">Βιογραφικό</a></div>
    </div>
    <div class="xr__acts">
      <button class="btn btn--blue" type="button" data-open="book">Ραντεβού</button>
      <a class="btn btn--ghost" href="tel:{SITE['phone_href']}">{I['phone']}{SITE['phone']}</a>
    </div>
  </aside>
</div>

<div class="ov ov--mid" id="book" hidden>
  <div class="ov__scrim" data-close></div>
  <div class="bk" role="dialog" aria-modal="true" aria-labelledby="bk-title">
    <button class="ov__x" type="button" data-close aria-label="Κλείσιμο">{I['close']}</button>
    <div class="bk__side">
      <p class="th__kicker">Ραντεβού</p>
      <h2 id="bk-title">Ζητήστε ραντεβού</h2>
      <p>Η φόρμα δεν στέλνει τίποτα μόνη της: ετοιμάζει ένα email που ελέγχετε πριν φύγει. Για άμεση εξυπηρέτηση, καλέστε.</p>
      <ul class="bk__hours">{hours}</ul>
      <p class="bk__nap">{I['pin']}<span>{SITE['address']}, {SITE['locality']}</span></p>
      <p class="bk__nap">{I['phone']}<span><a href="tel:{SITE['phone_href']}">{SITE['phone']}</a> · <a href="tel:{SITE['mobile_href']}">{SITE['mobile']}</a></span></p>
    </div>
    <form class="bk__form" novalidate>
      <div class="fld"><label for="bk-name">Ονοματεπώνυμο</label>
        <input id="bk-name" name="name" autocomplete="name" required><p class="err">Συμπληρώστε το όνομά σας.</p></div>
      <div class="fld fld--2">
        <div><label for="bk-phone">Τηλέφωνο</label><input id="bk-phone" name="phone" type="tel" autocomplete="tel" required>
          <p class="err">Χρειαζόμαστε έναν τρόπο να σας βρούμε.</p></div>
        <div><label for="bk-mail">Email <i>προαιρετικό</i></label><input id="bk-mail" name="email" type="email" autocomplete="email"></div>
      </div>
      <div class="fld"><label for="bk-topic">Θέμα</label>
        <select id="bk-topic" name="topic"><option value="">Δεν είμαι σίγουρη</option>{topics}</select></div>
      <div class="fld fld--2">
        <div><label for="bk-date">Προτιμώμενη ημέρα</label><input id="bk-date" name="date" type="date">
          <p class="err" data-closed>Το ιατρείο δέχεται Δευτέρα, Τετάρτη και Πέμπτη 17:00 – 21:30. Άλλες ημέρες κατόπιν συνεννόησης.</p></div>
        <div><label for="bk-time">Ώρα</label><select id="bk-time" name="time"><option value="">Επιλέξτε ώρα</option></select></div>
      </div>
      <div class="fld"><label for="bk-note">Θέλετε να μας πείτε κάτι ακόμη;</label>
        <textarea id="bk-note" name="note" rows="3" placeholder="Ό,τι μας βοηθά να προετοιμαστούμε."></textarea></div>
      <label class="chk"><input type="checkbox" name="consent" required><span></span>
        <em>Επιτρέπω να χρησιμοποιήσετε τα στοιχεία μου για να επικοινωνήσετε μαζί μου. Διάβασα τους <a href="{r}oroi-chrisis/">όρους χρήσης</a>.</em></label>
      <p class="err err--consent">Χρειαζόμαστε τη συγκατάθεσή σας.</p>
      <div class="bk__acts">
        <button class="btn btn--ghost" type="button" data-close>Άκυρο</button>
        <button class="btn btn--blue" type="submit">Ετοιμάστε το email</button>
      </div>
    </form>
  </div>
</div>

<div class="toast" id="toast" role="status" aria-live="polite"></div>
<div class="ck" id="cookie" hidden>
  <div class="ck__in">
    <p><b>Χωρίς cookies παρακολούθησης.</b> Ό,τι επιλέγετε (προφίλ, λίστα, πρόοδος ανάγνωσης) μένει μόνο σε αυτή τη συσκευή.</p>
    <div class="ck__acts"><button class="btn btn--blue btn--sm" type="button" data-ck="ok">Εντάξει</button></div>
  </div>
</div>
<button class="totop" type="button" aria-label="Επιστροφή στην κορυφή" hidden>
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true"><path d="M12 19V6M6 11l6-6 6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
</button>
<div class="progress" aria-hidden="true"><i></i></div>
'''


def tail(depth, *, extra_js=""):
    r = rel(depth)
    return f'''{overlays(depth)}
{extra_js}
<script src="{r}assets/js/prime.js?v={ASSET_V}" defer></script>
</body>
</html>'''
