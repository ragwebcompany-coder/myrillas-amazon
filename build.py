# -*- coding: utf-8 -*-
"""Χτίζει το kmyrillas.gr (Prime Video theme) μέσα στο site/.

    python3 build.py

Χρειάζεται μόνο Python 3. Αν υπάρχει Pillow, παράγει και webp / μικρότερες εικόνες.
Τα URL μένουν ίδια με το παλιό WordPress site (services/<slug>/, <slug>/ για άρθρα,
blog/, video-gallery/, photo-gallery/, epikinonia/, gynaikologos-dr-k-myrillas/),
ώστε να μη χαθεί τίποτα από το SEO.
"""
import os, re, sys, json, html, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import content as C
import ui as U
from content import (SITE, CATEGORIES, CAT, SERVICES, SVC, ARTICLES, VIDEOS, VID, VIDEO_GROUPS, HOME_VIDEOS,
                     TESTIMONIALS, TIMELINE, MEMBERSHIPS, STUDIES, PRESS, HERO, TOP10, IMGMAP,
                     rel, read_minutes, pretty_date, plain, shorten, related_articles, article_rec,
                     ARTICLE_TWIN, TODAY)

OUT = os.path.join(HERE, "site")
SRC = os.path.join(HERE, "src")
IMG_SRC = os.path.join(HERE, "content", "img-src")
PAGES, SEARCH = [], []


def write(path, markup):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(markup)


def register(url, prio="0.6", freq="monthly"):
    PAGES.append((url, prio, freq))


def index(url, *, title, desc, kind, img=None, kw="", video=None, xray=None):
    row = {"t": title, "d": desc, "u": url, "k": kind, "kw": kw}
    if img:
        row["img"] = img
    if video:
        row["v"] = video
    if xray:
        row["x"] = xray
    SEARCH.append(row)


# ── JSON-LD ──────────────────────────────────────────────────────────────────
def address_ld():
    return {"@type": "PostalAddress", "streetAddress": SITE["address"], "addressLocality": SITE["locality"],
            "postalCode": SITE["postcode"], "addressRegion": SITE["region"], "addressCountry": "GR"}


def physician_ld():
    return {"@type": ["Physician", "MedicalBusiness"], "@id": SITE["domain"] + "/#physician",
            "name": SITE["doctor"], "alternateName": "Dr. Κ. Μυρίλλας",
            "description": "Μαιευτήρας Χειρουργός Γυναικολόγος M.R.C.O.G. Λαπαροσκοπική και ρομποτική χειρουργική, ιατρείο στον Βύρωνα, χειρουργεία στο Μαιευτήριο ΡΕΑ.",
            "url": SITE["domain"] + "/", "image": SITE["domain"] + "/assets/img/2023-02-dr.-myrillas.jpg",
            "telephone": SITE["phone_href"], "email": SITE["email"], "address": address_ld(),
            "geo": {"@type": "GeoCoordinates", "latitude": SITE["lat"], "longitude": SITE["lng"]},
            "hasMap": SITE["map_url"], "medicalSpecialty": ["Obstetric", "Gynecologic"],
            "knowsLanguage": ["el", "en"], "priceRange": "€€",
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                           "dayOfWeek": ["Monday", "Wednesday", "Thursday"],
                                           "opens": "17:00", "closes": "21:30"}],
            "hospitalAffiliation": {"@type": "Hospital", "name": SITE["hospital"]},
            "memberOf": [{"@type": "Organization", "name": m} for m in MEMBERSHIPS],
            "sameAs": list(SITE["social"].values()),
            "availableService": [{"@type": "MedicalProcedure", "name": s["title"],
                                  "url": f"{SITE['domain']}/services/{s['slug']}/"} for s in SERVICES]}


def site_ld():
    return {"@type": "WebSite", "@id": SITE["domain"] + "/#website", "url": SITE["domain"] + "/",
            "name": "kmyrillas.gr", "inLanguage": "el", "publisher": {"@id": SITE["domain"] + "/#physician"}}


def base_graph():
    return {"@context": "https://schema.org", "@graph": [physician_ld(), site_ld()]}


# ── shell ────────────────────────────────────────────────────────────────────
def shell(*, path, title, desc, depth, body, active="", jsonld=None, body_class="", og_image=None,
          page_meta=None, kind="website"):
    ld = [base_graph()] + list(jsonld or [])
    extra = ""
    if page_meta:
        extra = f'<script>window.__PAGE={json.dumps(page_meta, ensure_ascii=False, separators=(",", ":"))}</script>'
    return (U.head(title=title, desc=desc, depth=depth, canonical=path, jsonld=ld, body_class=body_class,
                   og_image=og_image, kind=kind)
            + U.topbar(depth, active) + body + U.footer(depth) + U.tail(depth, extra_js=extra))


def hero_img(s):
    return s["image"]


def service_xray(s, eps):
    cat = CAT[s["cat"]]
    sib = [x for x in SERVICES if x["cat"] == s["cat"] and x["slug"] != s["slug"]][:4]
    arts = related_articles(s["slug"], 3)
    return {"facts": [["Είδος", s["kind"]], ["Κατηγορία", cat["title"]],
                      ["Ενότητες", str(len(eps))], ["Ανάγνωση", f"{read_minutes(s['words'])} λεπτά"],
                      ["Ιατρός", SITE["doctor"]], ["Χειρουργεία", SITE["hospital"]],
                      ["Ιατρείο", f"{SITE['address']}, {SITE['locality']}"],
                      ["Ενημερώθηκε", pretty_date(s["mod"] or s["pub"])]],
            "eps": [t for t, _ in eps][:12],
            "videos": [[v, VID[v]["title"]] for v in s["videos"] if v in VID][:5],
            "rel": [[f"services/{x['slug']}/", x["title"]] for x in sib] + [[f"{a['slug']}/", a["title"]] for a in arts]}


# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
def build_home():
    d = 0
    top = [U.card(SVC[s], d, n=i + 1) for i, s in enumerate(TOP10)]
    cat_rows = ""
    for c in CATEGORIES:
        cards = [U.card(SVC[s], d) for s in c["services"]]
        if len(cards) < 2:
            continue
        cat_rows += U.row(rid=f"r-{c['slug']}", title=c["title"], sub=c["blurb"], cards=cards,
                          all_href=f"katigoria/{c['slug']}/", attrs=f'data-row-cat="{c["slug"]}"')
    singles = [U.card(SVC[s], d) for c in CATEGORIES if len(c["services"]) == 1 for s in c["services"]]
    singles += [U.card(SVC[s], d) for s in ("ksirotita-atrofia-kolpou-emminopafsi", "kolposkopisi", "loop-traxilou")]
    v_cards = [U.video_card(VID[i], d) for i in HOME_VIDEOS if i in VID]
    a_cards = [U.card(article_rec(a["slug"]), d, kind="article") for a in ARTICLES[:12]]
    revs = "".join(U.review(t, d) for t in TESTIMONIALS)
    chans = "".join(f'''<a class="chan__i" href="{p['url'] or 'photo-gallery/'}"{' rel="noopener" target="_blank"' if p['url'] else ''}>
      <span class="chan__logo">{U.pic(p['logo'], p['name'], d)}</span>
      <span><h3>{html.escape(p['name'])}</h3><p>{html.escape(p['text'])}</p>
      <span class="ext">{'Επίσκεψη στο site' if p['url'] else 'Περισσότερα'} {U.I['ext'] if p['url'] else ''}</span></span></a>''' for p in SITE["partners"])
    body = U.hero(d, HERO) + f'''
<main id="main" data-home-rows>
  <p class="wrap row__sub" data-profile-hello hidden style="margin-top:1.4rem">Προφίλ: <b data-profile-name></b>. Οι κατηγορίες που σας αφορούν ήρθαν πρώτες.</p>
  <div data-rows-anchor></div>
  <section class="row" data-continue hidden></section>
  {U.row(rid="r-top", title="Top 10 στο ιατρείο", sub="Τα θέματα με το περισσότερο υλικό: κείμενα, βίντεο, χειρουργεία.", cards=top, kind="row--top", all_href="services/")}
  {U.row(rid="r-vid", title="Από το χειρουργείο και την τηλεόραση", sub="Βίντεο του ιατρείου, με ένα πάτημα.", cards=v_cards, all_href="video-gallery/", all_label="Όλα τα βίντεο")}
  {cat_rows}
  {U.row(rid="r-more", title="Ακόμη", cards=singles, all_href="services/")}
  {U.row(rid="r-art", title="Άρθρα", sub="Κείμενα του ιατρείου για την εγκυμοσύνη, τη γυναικολογία και τις εξετάσεις.", cards=a_cards, all_href="blog/", all_label="Όλα τα άρθρα")}

  <section class="sec rv"><div class="wrap">
    <div class="cast">
      <div class="cast__ph">{U.pic('2023-02-dr.-myrillas.jpg', SITE['doctor'], d)}</div>
      <div>
        <p class="cast__k">Ο γιατρός</p>
        <h2>{SITE['doctor']}</h2>
        <p>Μαιευτήρας – Χειρουργός Γυναικολόγος, M.R.C.O.G. Ειδικεύεται στη χειρουργική ελάχιστης παρέμβασης
          και εκτέλεσε το πρώτο χειρουργείο στην Ελλάδα με το ρομπότ Da Vinci High Definition τον Οκτώβριο του 2007.
          Ιδρυτικό στέλεχος του Μαιευτηρίου ΡΕΑ, όπου διευθύνει από το 2013 το τμήμα πλαστικής κόλπου και
          επανορθωτικής χειρουργικής πυέλου με laser.</p>
        <ul class="cast__facts">
          <li><b>2001</b><span>ιδιωτεύει στην Αθήνα</span></li>
          <li><b>2007</b><span>πρώτο ρομποτικό χειρουργείο στην Ελλάδα</span></li>
          <li><b>65</b><span>περιστατικά second look laparoscopy</span></li>
          <li><b>{len(VIDEOS)}</b><span>βίντεο από χειρουργεία και ΜΜΕ</span></li>
        </ul>
        <div style="display:flex;gap:.6rem;flex-wrap:wrap">
          <a class="btn btn--blue" href="gynaikologos-dr-k-myrillas/">Βιογραφικό</a>
          <button class="btn btn--ghost" type="button" data-video="WrXrhO9063c" data-vtitle="Κωνσταντίνος Μυρίλλας, βιογραφικό">{U.I['play']}Δείτε το βίντεο</button>
        </div>
      </div>
    </div>
  </div></section>

  <section class="sec sec--tight rv"><div class="wrap">
    <div class="sec__head"><h2>Είπαν για εμάς</h2><p>Μαρτυρίες όπως δημοσιεύονται στο site του ιατρείου.</p></div>
    <div class="revs">{revs}</div>
  </div></section>

  <section class="sec sec--tight rv"><div class="wrap">
    <div class="guide" data-guide>
      <h2>Τι με αφορά;</h2>
      <p class="lede">Δύο βήματα, χωρίς ερωτηματολόγιο: διαλέξτε τι σας φέρνει εδώ και ποιο θέμα σας μοιάζει
        περισσότερο. Ό,τι διαλέξετε μένει στη συσκευή σας.</p>
      <div data-guide-stage></div>
      <div class="guide__res" data-guide-res></div>
    </div>
  </div></section>

  <section class="sec sec--tight rv"><div class="wrap">
    <div class="sec__head"><h2>Δείτε επίσης</h2><p>Δύο συνεργαζόμενοι χώροι του γιατρού.</p></div>
    <div class="chan">{chans}</div>
  </div></section>

  <section class="sec sec--tight rv"><div class="wrap">
    <div class="sec__head"><h2>Χειρουργική ελάχιστης παρέμβασης</h2>
      <p>Το έντυπο του ιατρείου για τη λαπαροσκοπική και ρομποτική χειρουργική, σε PDF.</p></div>
    <a class="btn btn--ghost" href="assets/docs/2021-11-sel-2-compressed.pdf" target="_blank" rel="noopener">Διαβάστε το PDF</a>
  </div></section>
  {U.cta_band(d)}
</main>
{guide_data()}'''
    desc = ("Γυναικολόγος - Μαιευτήρας Χειρουργός Κωνσταντίνος Μυρίλλας με ιατρείο στην Αθήνα, εξειδικεύεται "
            "στη ρομποτική, λαπαροσκοπική και αισθητική χειρουργική.")
    write("index.html", shell(path="", title="Γυναικολόγος - Μαιευτήρας Χειρουργός Αθήνα Κων/νος Μυρίλλας",
                              desc=desc, depth=d, body=body, active="home", body_class="is-home",
                              og_image="2021-11-myr.jpg"))
    register("", "1.0", "weekly")
    index("", title="Αρχική", desc="Όλα τα θέματα, τα βίντεο και ο γιατρός", kind="page", kw="αρχικη home")


def guide_data():
    cats = []
    for c in CATEGORIES:
        cats.append({"slug": c["slug"], "title": c["title"], "blurb": c["blurb"],
                     "items": [{"u": f"services/{s}/", "t": SVC[s]["title"], "d": shorten(SVC[s]["lead"], 120)}
                               for s in c["services"]]})
    return f'<script id="guide-data" type="application/json">{json.dumps({"cats": cats}, ensure_ascii=False, separators=(",", ":"))}</script>'


# ══════════════════════════════════════════════════════════════════════════════
# SERVICES
# ══════════════════════════════════════════════════════════════════════════════
def service_ld(s, eps):
    cat = CAT[s["cat"]]
    typ = "MedicalProcedure" if s["kind"] in ("Επέμβαση", "Επεμβάσεις", "Εξέταση", "Εξετάσεις", "Διαδικασία") else "MedicalCondition"
    ld = {"@context": "https://schema.org", "@type": "MedicalWebPage", "@id": f"{SITE['domain']}/services/{s['slug']}/",
          "url": f"{SITE['domain']}/services/{s['slug']}/", "name": s["seo_title"] or s["title"],
          "description": s["lead"], "inLanguage": "el", "datePublished": s["pub"], "dateModified": s["mod"],
          "author": {"@id": SITE["domain"] + "/#physician"}, "reviewedBy": {"@id": SITE["domain"] + "/#physician"},
          "about": {"@type": typ, "name": s["title"], "alternateName": cat["title"]},
          "hasPart": [{"@type": "WebPageElement", "name": t, "position": i + 1} for i, (t, _) in enumerate(eps)]}
    if s["image"]:
        ld["primaryImageOfPage"] = f"{SITE['domain']}/assets/img/{s['image']}"
    vids = [{"@type": "VideoObject", "name": VID[v]["title"], "thumbnailUrl": f"https://i.ytimg.com/vi/{v}/hqdefault.jpg",
             "embedUrl": f"https://www.youtube-nocookie.com/embed/{v}", "uploadDate": s["pub"] or "2022-01-01",
             "description": VID[v]["title"]} for v in s["videos"] if v in VID]
    if vids:
        ld["video"] = vids
    return {k: v for k, v in ld.items() if v}


def build_service(s):
    d, slug = 2, s["slug"]
    cat = CAT[s["cat"]]
    eps_html, n = U.episodes(s["body"], d, slug=f"services/{slug}/")
    eps = U.episodes_of(s["body"])
    crumb, crumb_ld = U.crumbs([("Αρχική", ""), (cat["title"], f"katigoria/{cat['slug']}/"), (s["title"], None)], d)
    sib = [U.card(x, d) for x in SERVICES if x["cat"] == s["cat"] and x["slug"] != slug]
    if len(sib) < 3:
        sib += [U.card(SVC[x], d) for x in TOP10 if x != slug and SVC[x]["cat"] != s["cat"]][:4 - len(sib)]
    arts = [U.card(article_rec(a["slug"]), d, kind="article") for a in related_articles(slug, 8)]
    vids = [U.video_card(VID[v], d, wide=False) for v in s["videos"] if v in VID]
    if not vids:
        vids = [U.video_card(VID[v], d, wide=False) for v in HOME_VIDEOS[:6]]
    trailer = next((v for v in s["videos"] if v in VID), None)
    meta = [(s["kind"], ""), (cat.get("short", cat["title"]), ""), (f"{n} ενότητες" if n > 1 else "1 ενότητα", ""),
            (f"{read_minutes(s['words'])} λεπτά", ""), ("Βίντεο", "blue") if s["videos"] else ("", "")]
    details = U.details_dl([
        ("Ιατρός", f'<a href="../../gynaikologos-dr-k-myrillas/">{SITE["doctor"]}</a>, {SITE["tagline"]}'),
        ("Κατηγορία", f'<a href="../../katigoria/{cat["slug"]}/">{cat["title"]}</a>'),
        ("Είδος", s["kind"]), ("Ενότητες", str(n)), ("Ανάγνωση", f"{read_minutes(s['words'])} λεπτά, {s['words']} λέξεις"),
        ("Βίντεο", str(len([v for v in s['videos'] if v in VID])) if s["videos"] else ""),
        ("Πρώτη δημοσίευση", pretty_date(s["pub"])), ("Ενημερώθηκε", pretty_date(s["mod"])),
        ("Ιατρείο", f"{SITE['address']}, {SITE['locality']} · {SITE['hours_short']}"),
        ("Χειρουργεία", SITE["hospital"]), ("Γλώσσα", "Ελληνικά"),
    ])
    aside = f'''<div class="panel"><h3>Ραντεβού</h3><p>{SITE['hours_short']}. Για άλλες ημέρες, κατόπιν συνεννόησης.</p>
  <button class="btn btn--blue" type="button" data-open="book" data-topic="{html.escape(s['title'], quote=True)}">Ζητήστε ραντεβού</button></div>
<div class="panel"><h3>Στην ίδια κατηγορία</h3><ul>{"".join(f'<li><a href="../{x["slug"]}/">{html.escape(x["title"])}</a></li>' for x in SERVICES if x["cat"] == s["cat"] and x["slug"] != slug) or "<li>Μόνο αυτό το θέμα.</li>"}</ul></div>
<div class="panel"><h3>Εργαλεία</h3><ul>
  <li><button class="linky" type="button" data-share>{U.I['share']} Κοινοποίηση</button></li>
  <li><button class="linky" type="button" data-print>{U.I['print']} Εκτύπωση όλου του κειμένου</button></li>
  <li><button class="linky" type="button" data-xray="services/{slug}/">{U.I['xray']} X-Ray</button></li>
</ul></div>'''
    panels = [
        ("episodes", "Επεισόδια", f'<div class="wrap doc"><div class="doc__main">{eps_html}</div><aside class="doc__aside">{aside}</aside></div>'),
        ("related", "Σχετικά", U.row(rid="r-sib", title="Στην ίδια κατηγορία", cards=sib, all_href=f"../../katigoria/{cat['slug']}/")
                                + U.row(rid="r-vid", title="Βίντεο", cards=vids, all_href="../../video-gallery/", all_label="Όλα τα βίντεο")
                                + (U.row(rid="r-art", title="Σχετικά άρθρα", cards=arts, all_href="../../blog/") if arts else "")),
        ("details", "Λεπτομέρειες", f'<div class="wrap wrap--narrow">{details}</div>'),
    ]
    body = U.title_hero(d, crumb=crumb, kicker=f"{s['kind']} · {cat['title']}", title=s["title"], lead=s["lead"],
                        meta_pills=meta, image=s["image"], url=f"services/{slug}/", kind="service",
                        trailer_id=trailer, eps=n)
    body += f'<main id="main">{U.tabs(panels, d)}{U.cta_band(d, title="Μια ερώτηση δεν κοστίζει τίποτα")}</main>'
    meta_desc = (s["meta"] or s["lead"])[:158]
    xray = service_xray(s, eps)
    write(f"services/{slug}/index.html",
          shell(path=f"services/{slug}/", title=s["seo_title"] or C.seo_title(s["title"]), desc=meta_desc, depth=d,
                body=body, active=cat["slug"] if cat["slug"] in ("maieftiki", "gynaikologia", "xeirourgiki") else "services",
                jsonld=[service_ld(s, eps), crumb_ld], og_image=s["image"], kind="article",
                page_meta={"t": s["title"], "u": f"services/{slug}/", "img": s["image"], "k": f"{s['kind']} · {cat['title']}"}))
    register(f"services/{slug}/", "0.9")
    index(f"services/{slug}/", title=s["title"], desc=f"{s['kind']} · {cat['title']}", kind="service", img=s["image"],
          kw=s["lead"] + " " + " ".join(t for t, _ in eps), xray=xray)


def build_services_hub():
    d = 1
    crumb, crumb_ld = U.crumbs([("Αρχική", ""), ("Όλα τα θέματα", None)], d)
    rows = "".join(U.row(rid=f"r-{c['slug']}", title=c["title"], sub=c["blurb"],
                         cards=[U.card(SVC[s], d) for s in c["services"]], all_href=f"../katigoria/{c['slug']}/")
                   for c in CATEGORIES)
    chips = "".join(f'<a class="chip" href="../katigoria/{c["slug"]}/">{c["title"]}</a>' for c in CATEGORIES)
    body = f'''<section class="th"><div class="wrap th__in"><div class="th__text">{crumb}
  <p class="th__kicker">{len(SERVICES)} θέματα σε {len(CATEGORIES)} κατηγορίες</p>
  <h1 class="th__title">Όλα τα θέματα</h1>
  <p class="th__lead">Παθήσεις, επεμβάσεις, εξετάσεις και ενημέρωση, όπως τα οργανώνει το ίδιο το ιατρείο.
    Κάθε θέμα ανοίγει σε επεισόδια, με βίντεο όπου υπάρχει.</p>
  <div class="chips">{chips}</div></div></div></section>
<main id="main">{rows}{U.cta_band(d)}</main>'''
    write("services/index.html", shell(path="services/", title="Όλα τα θέματα | Κ. Μυρίλλας",
          desc="Μαιευτική, γυναικολογία, ενδομήτριο, τράχηλος, εμμηνόπαυση, αποβολή, ωοθήκες, HPV, γονιμότητα και χειρουργική ελάχιστης παρέμβασης: 36 θέματα από το ιατρείο του Κ. Μυρίλλα.",
          depth=d, body=body, active="services", jsonld=[crumb_ld]))
    register("services/", "0.8", "weekly")
    index("services/", title="Όλα τα θέματα", desc=f"{len(SERVICES)} θέματα", kind="page", kw="υπηρεσιες θεματα κατηγοριες")


def build_category(c):
    d = 2
    crumb, crumb_ld = U.crumbs([("Αρχική", ""), ("Όλα τα θέματα", "services/"), (c["title"], None)], d)
    items = [SVC[s] for s in c["services"]]
    grid = "".join(U.card(s, d) for s in items)
    vids_ids = []
    for s in items:
        for v in s["videos"]:
            if v in VID and v not in vids_ids:
                vids_ids.append(v)
    vids = [U.video_card(VID[v], d, wide=False) for v in vids_ids[:10]]
    arts = []
    for s in items:
        for a in related_articles(s["slug"], 4):
            if a["slug"] not in [x["slug"] for x in arts]:
                arts.append(a)
    a_cards = [U.card(article_rec(a["slug"]), d, kind="article") for a in arts[:10]]
    others = "".join(f'<a class="chip{" is-on" if x["slug"] == c["slug"] else ""}" href="../{x["slug"]}/">{x["title"]}</a>' for x in CATEGORIES)
    body = f'''<section class="th"><div class="wrap th__in"><div class="th__text">{crumb}
  <p class="th__kicker">Κατηγορία · {len(items)} {"θέματα" if len(items) > 1 else "θέμα"}</p>
  <h1 class="th__title">{html.escape(c['title'])}</h1>
  <p class="th__lead">{html.escape(c['blurb'])}</p>
  <div class="chips">{others}</div></div></div></section>
<main id="main">
  <section class="sec sec--tight"><div class="wrap"><div class="grid">{grid}</div></div></section>
  {U.row(rid="r-vid", title="Βίντεο", cards=vids, all_href="../../video-gallery/", all_label="Όλα τα βίντεο") if vids else ""}
  {U.row(rid="r-art", title="Σχετικά άρθρα", cards=a_cards, all_href="../../blog/") if a_cards else ""}
  {U.cta_band(d)}
</main>'''
    write(f"katigoria/{c['slug']}/index.html", shell(path=f"katigoria/{c['slug']}/", title=f"{c['title']} | Κ. Μυρίλλας",
          desc=f"{c['title']}: {c['blurb']} Θέματα, βίντεο και άρθρα από τον μαιευτήρα χειρουργό γυναικολόγο Κ. Μυρίλλα.",
          depth=d, body=body, active=c["slug"], jsonld=[crumb_ld]))
    register(f"katigoria/{c['slug']}/", "0.7", "weekly")
    index(f"katigoria/{c['slug']}/", title=c["title"], desc=c["blurb"], kind="page", kw=" ".join(SVC[s]["title"] for s in c["services"]))


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLES
# ══════════════════════════════════════════════════════════════════════════════
def build_article(a):
    d, slug = 1, a["slug"]
    r = article_rec(slug)
    twin = ARTICLE_TWIN.get(slug)
    eps_html, n = U.episodes(r["body"], d, slug=f"{slug}/", single_title="Το άρθρο")
    eps = U.episodes_of(r["body"])
    crumb, crumb_ld = U.crumbs([("Αρχική", ""), ("Άρθρα", "blog/"), (a["title"], None)], d)
    same = [x for x in ARTICLES if x["tag"] == a["tag"] and x["slug"] != slug][:8]
    if len(same) < 4:
        same += [x for x in ARTICLES if x["slug"] != slug and x not in same][:8 - len(same)]
    rel_cards = [U.card(article_rec(x["slug"]), d, kind="article") for x in same]
    svc_hits = [s for s in SERVICES if any(k in (a["title"] + slug).lower() for k in C.RELATED_KEYS.get(s["slug"], []))][:6]
    if twin and SVC.get(twin) and SVC[twin] not in svc_hits:
        svc_hits.insert(0, SVC[twin])
    s_cards = [U.card(s, d) for s in svc_hits]
    trailer = next((v for v in r["videos"] if v in VID), None)
    meta = [("Άρθρο", ""), (a["tag"], ""), (f"{n} ενότητες" if n > 1 else "", ""), (f"{read_minutes(r['words'])} λεπτά", ""),
            (pretty_date(r["pub"]), "")]
    twin_note = (f'<div class="panel"><h3>Το πλήρες θέμα</h3><p>Το άρθρο έχει και δική του σελίδα θέματος με βίντεο και σχετικά.</p>'
                 f'<a class="btn btn--blue" href="../services/{twin}/">{html.escape(SVC[twin]["title"])}</a></div>') if twin and twin in SVC else ""
    aside = f'''{twin_note}<div class="panel"><h3>Ρωτήστε τον γιατρό</h3><p>Ό,τι διαβάσατε αφορά τη γενική εικόνα. Το δικό σας περιστατικό θέλει εξέταση.</p>
  <button class="btn btn--blue" type="button" data-open="book">Ζητήστε ραντεβού</button></div>
<div class="panel"><h3>Εργαλεία</h3><ul>
  <li><button class="linky" type="button" data-share>{U.I['share']} Κοινοποίηση</button></li>
  <li><button class="linky" type="button" data-print>{U.I['print']} Εκτύπωση</button></li></ul></div>'''
    panels = [("episodes", "Επεισόδια" if n > 1 else "Το άρθρο",
               f'<div class="wrap doc"><div class="doc__main">{eps_html}</div><aside class="doc__aside">{aside}</aside></div>'),
              ("related", "Σχετικά", (U.row(rid="r-svc", title="Σχετικά θέματα", cards=s_cards, all_href="../services/") if s_cards else "")
                                     + U.row(rid="r-art", title="Περισσότερα άρθρα", cards=rel_cards, all_href="../blog/")),
              ("details", "Λεπτομέρειες", '<div class="wrap wrap--narrow">' + U.details_dl([
                  ("Συγγραφέας", f'<a href="../gynaikologos-dr-k-myrillas/">{SITE["doctor"]}</a>'), ("Κατηγορία", a["tag"]),
                  ("Δημοσίευση", pretty_date(r["pub"])), ("Ενημέρωση", pretty_date(r["mod"])),
                  ("Ανάγνωση", f"{read_minutes(r['words'])} λεπτά, {r['words']} λέξεις"), ("Γλώσσα", "Ελληνικά")]) + "</div>")]
    body = U.title_hero(d, crumb=crumb, kicker=f"Άρθρο · {a['tag']}", title=a["title"], lead=r["lead"], meta_pills=meta,
                        image=r["image"], url=f"{slug}/", kind="article", trailer_id=trailer, eps=n)
    body += f'<main id="main">{U.tabs(panels, d)}{U.cta_band(d)}</main>'
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"][:110], "inLanguage": "el",
          "datePublished": r["pub"] or None, "dateModified": r["mod"] or None, "url": f"{SITE['domain']}/{slug}/",
          "author": {"@id": SITE["domain"] + "/#physician"}, "publisher": {"@id": SITE["domain"] + "/#physician"},
          "mainEntityOfPage": f"{SITE['domain']}/{slug}/",
          "image": f"{SITE['domain']}/assets/img/{r['image']}" if r["image"] else None}
    ld = {k: v for k, v in ld.items() if v}
    xray = {"facts": [["Είδος", "Άρθρο"], ["Κατηγορία", a["tag"]], ["Ανάγνωση", f"{read_minutes(r['words'])} λεπτά"],
                      ["Δημοσίευση", pretty_date(r["pub"])], ["Συγγραφέας", SITE["doctor"]]],
            "eps": [t for t, _ in eps][:12], "videos": [[v, VID[v]["title"]] for v in r["videos"] if v in VID][:5],
            "rel": [[f"services/{s['slug']}/", s["title"]] for s in svc_hits[:4]]}
    write(f"{slug}/index.html", shell(path=f"{slug}/", title=r["seo_title"] or C.seo_title(a["title"]),
          desc=(r["meta"] or r["lead"])[:158], depth=d, body=body, active="blog", jsonld=[ld, crumb_ld],
          og_image=r["image"], kind="article",
          page_meta={"t": a["title"], "u": f"{slug}/", "img": r["image"], "k": f"Άρθρο · {a['tag']}"}))
    register(f"{slug}/", "0.6")
    index(f"{slug}/", title=a["title"], desc=f"Άρθρο · {a['tag']}", kind="article", img=r["image"],
          kw=plain(r["body"])[:400], xray=xray)


def build_blog():
    d = 1
    crumb, crumb_ld = U.crumbs([("Αρχική", ""), ("Άρθρα", None)], d)
    tags = []
    for a in ARTICLES:
        if a["tag"] not in tags:
            tags.append(a["tag"])
    chips = '<button class="chip is-on" type="button" data-filter-tag="all">Όλα</button>' + "".join(
        f'<button class="chip" type="button" data-filter-tag="{html.escape(t)}">{html.escape(t)}</button>' for t in tags)
    items = "".join(f'<div data-item data-tag="{html.escape(a["tag"])}" data-text="{html.escape(a["title"] + " " + article_rec(a["slug"])["lead"], quote=True)}">'
                    f'{U.card(article_rec(a["slug"]), d, kind="article")}</div>' for a in ARTICLES)
    body = f'''<section class="th"><div class="wrap th__in"><div class="th__text">{crumb}
  <p class="th__kicker">{len(ARTICLES)} άρθρα του ιατρείου</p>
  <h1 class="th__title">Άρθρα</h1>
  <p class="th__lead">Κείμενα για την εγκυμοσύνη, τη γυναικολογία, τις εξετάσεις και τη γονιμότητα, από το 2013 έως σήμερα.</p>
  </div></div></section>
<main id="main"><section class="sec sec--tight"><div class="wrap" data-filter>
  <div class="fld" style="max-width:440px"><label for="blog-q">Αναζήτηση στα άρθρα</label>
    <input id="blog-q" type="search" placeholder="π.χ. θηλασμός" autocomplete="off" data-filter-q></div>
  <div class="chips" style="margin:0 0 1.4rem">{chips}</div>
  <div class="grid" data-filter-grid>{items}</div>
  <p data-filter-empty hidden style="color:var(--dim);margin-top:2rem">Καμία αντιστοιχία.</p>
</div></section>{U.cta_band(d)}</main>'''
    write("blog/index.html", shell(path="blog/", title="Άρθρα | Κ. Μυρίλλας",
          desc="53 άρθρα του μαιευτήρα χειρουργού γυναικολόγου Κωνσταντίνου Μυρίλλα για την εγκυμοσύνη, τη γυναικολογία, τις εξετάσεις και τη γονιμότητα.",
          depth=d, body=body, active="blog", jsonld=[crumb_ld]))
    register("blog/", "0.7", "weekly")
    index("blog/", title="Άρθρα", desc=f"{len(ARTICLES)} άρθρα", kind="page", kw="blog αρθρα")


# ══════════════════════════════════════════════════════════════════════════════
# VIDEO / PHOTO
# ══════════════════════════════════════════════════════════════════════════════
def build_videos():
    d = 1
    crumb, crumb_ld = U.crumbs([("Αρχική", ""), ("Βίντεο", None)], d)
    groups = ""
    for gt, gk, ids in VIDEO_GROUPS:
        cards = "".join(f'<div data-item data-tag="{html.escape(gt)}" data-text="{html.escape(VID[v]["title"], quote=True)}">{U.video_card(VID[v], d, wide=False)}</div>' for v in ids if v in VID)
        groups += f'<section class="sec sec--tight" data-group><div class="wrap"><div class="sec__head"><h2>{html.escape(gt)}</h2><p>{html.escape(gk)}</p></div><div class="grid">{cards}</div></div></section>'
    chips = '<button class="chip is-on" type="button" data-filter-tag="all">Όλα</button>' + "".join(
        f'<button class="chip" type="button" data-filter-tag="{html.escape(gt)}">{html.escape(gt)}</button>' for gt, _, _ in VIDEO_GROUPS)
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "Βίντεο του ιατρείου",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {
              "@type": "VideoObject", "name": v["title"], "description": v["title"] + " · " + v["group"],
              "thumbnailUrl": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg",
              "embedUrl": f"https://www.youtube-nocookie.com/embed/{v['id']}", "uploadDate": "2022-01-01"}}
              for i, v in enumerate(VIDEOS)]}
    body = f'''<section class="th"><div class="wrap th__in"><div class="th__text">{crumb}
  <p class="th__kicker">{len(VIDEOS)} βίντεο από το κανάλι του ιατρείου</p>
  <h1 class="th__title">Βίντεο</h1>
  <p class="th__lead">Χειρουργεία λαπαροσκόπησης και υστεροσκόπησης, ρομποτική χειρουργική, τηλεοπτικές συνεντεύξεις.
    Τίποτα δεν φορτώνει από το YouTube πριν πατήσετε.</p>
  <a class="btn btn--ghost" href="{SITE['social']['youtube']}" rel="noopener" target="_blank">{U.I['yt']}Το κανάλι στο YouTube</a>
  </div></div></section>
<main id="main"><div data-filter>
  <div class="wrap" style="margin-top:1.5rem"><div class="fld" style="max-width:440px"><label for="vid-q">Αναζήτηση στα βίντεο</label>
    <input id="vid-q" type="search" placeholder="π.χ. ινομύωμα" autocomplete="off" data-filter-q></div>
  <div class="chips">{chips}</div></div>
  <div data-filter-grid>{groups}</div>
  <p class="wrap" data-filter-empty hidden style="color:var(--dim);margin-top:2rem">Καμία αντιστοιχία.</p>
</div>{U.cta_band(d)}</main>'''
    write("video-gallery/index.html", shell(path="video-gallery/", title="Βίντεο: χειρουργεία και συνεντεύξεις | Κ. Μυρίλλας",
          desc="36 βίντεο του μαιευτήρα χειρουργού γυναικολόγου Κ. Μυρίλλα: λαπαροσκοπικές επεμβάσεις, υστεροσκόπηση, ρομποτική χειρουργική και τηλεοπτικές συνεντεύξεις.",
          depth=d, body=body, active="video", jsonld=[crumb_ld, ld]))
    register("video-gallery/", "0.7")
    index("video-gallery/", title="Βίντεο", desc=f"{len(VIDEOS)} βίντεο", kind="page", kw="video βιντεο youtube")
    for v in VIDEOS:
        index("video-gallery/", title=v["title"], desc=v["group"], kind="video", video=v["id"], kw=v["group"])


def build_photos():
    d = 1
    crumb, crumb_ld = U.crumbs([("Αρχική", ""), ("Gallery", None)], d)

    def tile(img, cap, wide=False):
        return (f'<button class="gal__i" type="button" data-lb="../assets/img/{img}" data-alt="{html.escape(cap, quote=True)}" '
                f'data-cap="{html.escape(cap, quote=True)}">{U.pic(img, cap, d)}</button>')
    press = "".join(tile(p, "Δημοσίευση στον Τύπο") for p in PRESS)
    surg = "".join(tile(VID[v]["thumb"], VID[v]["title"]) for v in ["XXaY2SgYyNM", "uu_zQdoOfP8", "r0bjdoeFty4", "DG7sv_O_szQ", "iGFBuU3COOY", "msSCFVDZcxc", "RGLafhTXWwo", "EPHbT_-9GkI"] if VID[v].get("thumb"))
    doc = "".join(tile(p, SITE["doctor"]) for p in ["2023-02-dr.-myrillas.jpg", "2021-11-dr-myrilas-1.jpg", "2022-03-myrillas.jpg"])
    body = f'''<section class="th"><div class="wrap th__in"><div class="th__text">{crumb}
  <p class="th__kicker">Backstage</p>
  <h1 class="th__title">Gallery</h1>
  <p class="th__lead">Δημοσιεύσεις στον Τύπο, στιγμιότυπα από τα βίντεο του ιατρείου και ο γιατρός.</p>
  </div></div></section>
<main id="main">
  <section class="sec sec--tight"><div class="wrap"><div class="sec__head"><h2>Στον Τύπο</h2><p>Εξώφυλλα και συνεντεύξεις σε περιοδικά.</p></div><div class="gal">{press}</div></div></section>
  <section class="sec sec--tight"><div class="wrap"><div class="sec__head"><h2>Από τα βίντεο</h2><p>Τα στιγμιότυπα που ανέβασε το ίδιο το ιατρείο. Δείτε τα ολόκληρα στη σελίδα <a class="linky" href="../video-gallery/">Βίντεο</a>.</p></div><div class="gal gal--wide">{surg}</div></div></section>
  <section class="sec sec--tight"><div class="wrap"><div class="sec__head"><h2>Ο γιατρός</h2></div><div class="gal">{doc}</div></div></section>
  {U.cta_band(d)}
</main>'''
    write("photo-gallery/index.html", shell(path="photo-gallery/", title="Gallery | Κ. Μυρίλλας",
          desc="Δημοσιεύσεις στον Τύπο, στιγμιότυπα από χειρουργεία και ο μαιευτήρας χειρουργός γυναικολόγος Κωνσταντίνος Μυρίλλας.",
          depth=d, body=body, active="", jsonld=[crumb_ld]))
    register("photo-gallery/", "0.4")
    index("photo-gallery/", title="Gallery", desc="Τύπος και στιγμιότυπα", kind="page", kw="gallery φωτογραφιες")


# ══════════════════════════════════════════════════════════════════════════════
# DOCTOR / CONTACT / TESTIMONIALS / TOOLS
# ══════════════════════════════════════════════════════════════════════════════
def build_doctor():
    d = 1
    crumb, crumb_ld = U.crumbs([("Αρχική", ""), (SITE["doctor"], None)], d)
    body_html = C.DOCTOR_BODY
    body_html = body_html.split("Μελέτες")[0]
    body_html = re.sub(r'^.*?</p>\s*', "", body_html, count=1, flags=re.S)  # crumbs + φωτογραφία
    body_html = U._fix_body(body_html, d)
    tl = "".join(f"<li><b>{html.escape(y)}</b><p>{html.escape(t)}</p></li>" for y, t in TIMELINE)
    mem = "".join(f"<li>{html.escape(m)}</li>" for m in MEMBERSHIPS)
    st = "".join(f"<li>{html.escape(m)}</li>" for m in STUDIES)
    press = "".join(f'<button class="gal__i" type="button" data-lb="../assets/img/{p}" data-cap="Δημοσίευση στον Τύπο">{U.pic(p, "Δημοσίευση στον Τύπο", d)}</button>' for p in PRESS)
    vids = [U.video_card(VID[v], d, wide=False) for v in ["WrXrhO9063c", "cAh-5sH2lV0", "EPHbT_-9GkI", "RGLafhTXWwo", "iGFBuU3COOY", "msSCFVDZcxc"]]
    body = f'''<section class="th th--img"><div class="th__bg" aria-hidden="true">{U.pic('2021-11-myr.jpg', '', d, eager=True)}</div>
<div class="wrap th__in"><div class="th__text">{crumb}
  <p class="th__kicker">Ο γιατρός</p>
  <h1 class="th__title">{SITE['doctor']}</h1>
  <div class="th__meta">{U.prime_badge('Ιατρείο στον Βύρωνα')}{U.pills([("Μαιευτήρας", ""), ("Χειρουργός Γυναικολόγος", ""), ("M.R.C.O.G.", "blue"), ("Ρομποτική", ""), ("Λαπαροσκόπηση", "")])}</div>
  <p class="th__lead">Γεννήθηκε το 1967 στην Αθήνα, σπούδασε ιατρική στην Αθήνα, ειδικεύτηκε στο Λονδίνο και το Cambridge,
    και από το 2001 ιδιωτεύει στην Αθήνα. Το 2007 εκτέλεσε το πρώτο ρομποτικό χειρουργείο στην Ελλάδα.</p>
  <div class="th__acts">
    <button class="btn btn--blue btn--lg" type="button" data-video="WrXrhO9063c" data-vtitle="Κωνσταντίνος Μυρίλλας, βιογραφικό">{U.I['play']}Βίντεο βιογραφικό</button>
    <button class="btn btn--ghost btn--lg" type="button" data-open="book">Ραντεβού</button>
  </div></div>
  <div class="th__poster" style="aspect-ratio:2/3;max-width:320px;justify-self:end">{U.pic('2023-02-dr.-myrillas.jpg', SITE['doctor'], d, eager=True)}</div>
</div></section>
<main id="main">
  <div class="wrap doc" style="margin-top:2.5rem">
    <div class="doc__main">
      <div class="prose">{body_html}</div>
      <h2 style="margin-top:2.5rem">Μελέτες</h2><ul class="prose" style="list-style:none;padding:0">{st}</ul>
      <h2 style="margin-top:2.5rem">Μέλος</h2><ul class="prose" style="list-style:none;padding:0">{mem}</ul>
    </div>
    <aside class="doc__aside">
      <div class="panel"><h3>Χρονολόγιο</h3><ol class="tl">{tl}</ol></div>
    </aside>
  </div>
  <section class="sec sec--tight"><div class="wrap"><div class="sec__head"><h2>Δημοσιεύσεις</h2><p>Συνεντεύξεις και άρθρα σε περιοδικά.</p></div><div class="gal">{press}</div></div></section>
  {U.row(rid="r-vid", title="Ο γιατρός στην τηλεόραση", cards=vids, all_href="../video-gallery/", all_label="Όλα τα βίντεο")}
  {U.cta_band(d)}
</main>'''
    write("gynaikologos-dr-k-myrillas/index.html", shell(path="gynaikologos-dr-k-myrillas/",
          title="Γυναικολόγος Dr. Κ. Μυρίλλας: βιογραφικό | Μαιευτήρας Χειρουργός Αθήνα",
          desc="Ο μαιευτήρας χειρουργός γυναικολόγος Κωνσταντίνος Μυρίλλας, M.R.C.O.G.: σπουδές σε Αθήνα, Λονδίνο και Cambridge, λαπαροσκοπική και ρομποτική χειρουργική, Μαιευτήριο ΡΕΑ.",
          depth=d, body=body, active="doctor", jsonld=[crumb_ld], og_image="2023-02-dr.-myrillas.jpg", kind="profile"))
    register("gynaikologos-dr-k-myrillas/", "0.8")
    index("gynaikologos-dr-k-myrillas/", title=SITE["doctor"], desc="Βιογραφικό, μελέτες, χρονολόγιο", kind="page",
          img="2023-02-dr.-myrillas.jpg", kw="γιατρος βιογραφικο μυριλλας doctor cv")


def build_contact():
    d = 1
    crumb, crumb_ld = U.crumbs([("Αρχική", ""), ("Επικοινωνία", None)], d)
    days = [("Δευτέρα", "17:00 – 21:30", 1), ("Τρίτη", "κατόπιν ραντεβού", 2), ("Τετάρτη", "17:00 – 21:30", 3),
            ("Πέμπτη", "17:00 – 21:30", 4), ("Παρασκευή", "κατόπιν ραντεβού", 5), ("Σάββατο", "κλειστά", 6), ("Κυριακή", "κλειστά", 0)]
    hours = "".join(f'<li data-day="{n}"><span>{dd}</span><b>{t}</b></li>' for dd, t, n in days)
    ld = {"@context": "https://schema.org", "@type": "ContactPage", "url": f"{SITE['domain']}/epikinonia/",
          "mainEntity": {"@id": SITE["domain"] + "/#physician"}}
    body = f'''<section class="th"><div class="wrap th__in"><div class="th__text">{crumb}
  <p class="th__kicker">Ιατρείο στον Βύρωνα</p>
  <h1 class="th__title">Επικοινωνία</h1>
  <p class="th__lead">{SITE['address']}, {SITE['locality']}. Δεχόμαστε {SITE['hours_short']}. Για άλλες ημέρες, κατόπιν συνεννόησης.</p>
  <div class="th__acts">
    <a class="btn btn--blue btn--lg" href="tel:{SITE['phone_href']}">{U.I['phone']}{SITE['phone']}</a>
    <a class="btn btn--ghost btn--lg" href="tel:{SITE['mobile_href']}">{U.I['phone']}{SITE['mobile']}</a>
    <button class="btn btn--ghost btn--lg" type="button" data-open="book">Φόρμα ραντεβού</button>
  </div></div></div></section>
<main id="main"><section class="sec sec--tight"><div class="wrap contact">
  <div>
    <div class="panel" style="margin-bottom:1rem"><h3>Στοιχεία</h3>
      <dl class="dl">
        <div><dt>Διεύθυνση</dt><dd>{SITE['address']}, {SITE['locality']} {SITE['postcode']}</dd></div>
        <div><dt>Τηλέφωνο</dt><dd><a href="tel:{SITE['phone_href']}">{SITE['phone']}</a></dd></div>
        <div><dt>Κινητό</dt><dd><a href="tel:{SITE['mobile_href']}">{SITE['mobile']}</a></dd></div>
        <div><dt>Fax</dt><dd>{SITE['fax']}</dd></div>
        <div><dt>Email</dt><dd><a href="mailto:{SITE['email']}">{SITE['email']}</a></dd></div>
        <div><dt>Χειρουργεία</dt><dd>{SITE['hospital']}</dd></div>
      </dl></div>
    <div class="panel"><h3>Ώρες ιατρείου</h3><ul class="hours">{hours}</ul></div>
  </div>
  <div>
    <a class="contact__map" href="{SITE['map_url']}" rel="noopener" target="_blank">{U.pic('2023-04-screenshot-19.webp', 'Χάρτης: ' + SITE['address'] + ', ' + SITE['locality'], d)}<span>Άνοιγμα στους Χάρτες Google</span></a>
    <div class="panel" style="margin-top:1rem"><h3>Φόρμα</h3><p>Η φόρμα ραντεβού ετοιμάζει ένα email προς {SITE['email']} που ελέγχετε πριν φύγει. Τίποτα δεν αποθηκεύεται στον ιστότοπο.</p>
      <button class="btn btn--blue" type="button" data-open="book">Ζητήστε ραντεβού</button></div>
  </div>
</div></section></main>'''
    write("epikinonia/index.html", shell(path="epikinonia/", title="Επικοινωνία | Γυναικολόγος Κ. Μυρίλλας, Βύρωνας",
          desc=f"Ιατρείο: {SITE['address']}, {SITE['locality']}. Τηλέφωνο {SITE['phone']}, κινητό {SITE['mobile']}. Δευτέρα, Τετάρτη και Πέμπτη 17:00 – 21:30.",
          depth=d, body=body, active="", jsonld=[crumb_ld, ld]))
    register("epikinonia/", "0.8")
    index("epikinonia/", title="Επικοινωνία", desc=f"{SITE['address']}, {SITE['locality']} · {SITE['phone']}", kind="page",
          kw="επικοινωνια τηλεφωνο διευθυνση ωραριο ραντεβου χαρτης")


def build_testimonials():
    for t in TESTIMONIALS:
        d = 2
        title = f"{t['name']} από {t['place']}"
        crumb, crumb_ld = U.crumbs([("Αρχική", ""), ("Είπαν για εμάς", "#"), (title, None)], d)
        svc = SVC[t["topic"]]
        others = [U.card(svc, d)] + [U.card(SVC[s], d) for s in TOP10 if s != t["topic"]][:5]
        ld = {"@context": "https://schema.org", "@type": "Review", "reviewBody": t["text"],
              "author": {"@type": "Person", "name": title}, "itemReviewed": {"@id": SITE["domain"] + "/#physician"},
              "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"}}
        body = f'''<section class="th"><div class="wrap th__in"><div class="th__text">{crumb}
  <p class="th__kicker">Είπαν για εμάς</p>
  <h1 class="th__title">{html.escape(title)}</h1>
  <div class="revs" style="margin-top:1rem;max-width:720px">{U.review(t, d)}</div>
  </div></div></section>
<main id="main">{U.row(rid="r-rel", title="Σχετικά θέματα", cards=others, all_href="../../services/")}{U.cta_band(d)}</main>'''
        write(f"testimonials/{t['slug']}/index.html", shell(path=f"testimonials/{t['slug']}/", title=f"{title} | Κ. Μυρίλλας",
              desc=shorten(t["text"], 155), depth=d, body=body, jsonld=[crumb_ld, ld]))
        register(f"testimonials/{t['slug']}/", "0.3")


def build_guide_page():
    d = 1
    crumb, crumb_ld = U.crumbs([("Αρχική", ""), ("Τι με αφορά;", None)], d)
    body = f'''<section class="th"><div class="wrap th__in"><div class="th__text">{crumb}
  <p class="th__kicker">Οδηγός σε δύο βήματα</p>
  <h1 class="th__title">Τι με αφορά;</h1>
  <p class="th__lead">Διαλέξτε τι σας φέρνει εδώ και ποιο θέμα σας μοιάζει περισσότερο. Είναι πλοήγηση στο υλικό του ιατρείου, όχι διάγνωση.</p>
  </div></div></section>
<main id="main"><section class="sec sec--tight"><div class="wrap"><div class="guide" data-guide>
  <div data-guide-stage></div><div class="guide__res" data-guide-res></div></div></div></section>{U.cta_band(d)}</main>{guide_data()}'''
    write("odigos/index.html", shell(path="odigos/", title="Τι με αφορά; Οδηγός θεμάτων | Κ. Μυρίλλας",
          desc="Δύο βήματα για να βρείτε ποιο θέμα του ιατρείου σας αφορά: κατηγορία και το πιο κοντινό θέμα. Χωρίς αποστολή δεδομένων.",
          depth=d, body=body, jsonld=[crumb_ld]))
    register("odigos/", "0.5")
    index("odigos/", title="Τι με αφορά;", desc="Οδηγός σε δύο βήματα", kind="page", kw="οδηγος συμπτωματα")


def build_mylist():
    d = 1
    crumb, crumb_ld = U.crumbs([("Αρχική", ""), ("Η λίστα μου", None)], d)
    body = f'''<section class="th"><div class="wrap th__in"><div class="th__text">{crumb}
  <p class="th__kicker">Στη συσκευή σας</p><h1 class="th__title">Η λίστα μου</h1>
  <p class="th__lead">Ό,τι κρατήσατε με το <b>+</b>. Μένει μόνο σε αυτόν τον browser, δεν συνδέεται με λογαριασμό.</p>
  </div></div></section>
<main id="main"><section class="sec sec--tight"><div class="wrap"><div data-mylist></div></div></section>{U.cta_band(d)}</main>'''
    write("i-lista-mou/index.html", shell(path="i-lista-mou/", title="Η λίστα μου | Κ. Μυρίλλας",
          desc="Τα θέματα και τα άρθρα που κρατήσατε. Αποθηκεύονται τοπικά στη συσκευή σας.", depth=d, body=body, jsonld=[crumb_ld]))
    register("i-lista-mou/", "0.2")


def build_terms():
    d = 1
    crumb, crumb_ld = U.crumbs([("Αρχική", ""), ("Όροι χρήσης", None)], d)
    body = f'''<section class="th"><div class="wrap th__in"><div class="th__text">{crumb}
  <h1 class="th__title">Όροι χρήσης & απόρρητο</h1></div></div></section>
<main id="main"><section class="sec sec--tight"><div class="wrap wrap--narrow prose">
  <h3>Περιεχόμενο</h3>
  <p>Ο ιστότοπος kmyrillas.gr ανήκει στον μαιευτήρα χειρουργό γυναικολόγο Κωνσταντίνο Μυρίλλα ({SITE['address']}, {SITE['locality']}).
    Το περιεχόμενο είναι ενημερωτικό, δεν υποκαθιστά την ιατρική εξέταση και δεν αποτελεί ιατρική συμβουλή για συγκεκριμένο περιστατικό.</p>
  <h3>Προσωπικά δεδομένα</h3>
  <p>Ο ιστότοπος δεν διαθέτει server-side φόρμες και δεν αποθηκεύει προσωπικά δεδομένα. Η φόρμα ραντεβού συνθέτει ένα email στο
    πρόγραμμα αλληλογραφίας σας, το οποίο ελέγχετε και στέλνετε εσείς προς {SITE['email']}. Τα στοιχεία που μας στέλνετε χρησιμοποιούνται
    μόνο για την επικοινωνία μαζί σας.</p>
  <h3>Τοπικά δεδομένα</h3>
  <p>Το προφίλ, η λίστα σας και η πρόοδος ανάγνωσης αποθηκεύονται μόνο στον browser σας (localStorage) και δεν αποστέλλονται πουθενά.
    Μπορείτε να τα διαγράψετε από το εικονίδιο προφίλ.</p>
  <h3>Τρίτοι</h3>
  <p>Τα βίντεο φορτώνουν από το YouTube (youtube-nocookie.com) μόνο όταν πατήσετε αναπαραγωγή. Οι γραμματοσειρές φορτώνουν από το Google Fonts.
    Ο χάρτης ανοίγει στους Χάρτες Google σε νέα καρτέλα.</p>
</div></section></main>'''
    write("oroi-chrisis/index.html", shell(path="oroi-chrisis/", title="Όροι χρήσης & απόρρητο | Κ. Μυρίλλας",
          desc="Όροι χρήσης και πολιτική απορρήτου του kmyrillas.gr.", depth=d, body=body, jsonld=[crumb_ld]))
    register("oroi-chrisis/", "0.1")


def build_404():
    d = 0
    body = f'''<section class="th"><div class="wrap th__in"><div class="th__text">
  <p class="th__kicker">404</p><h1 class="th__title">Αυτή η σελίδα δεν υπάρχει</h1>
  <p class="th__lead">Ίσως άλλαξε διεύθυνση. Δοκιμάστε την αναζήτηση ή ξεκινήστε από τα θέματα.</p>
  <div class="th__acts"><button class="btn btn--blue btn--lg" type="button" data-open="palette">{U.I['search']}Αναζήτηση</button>
    <a class="btn btn--ghost btn--lg" href="/services/">Όλα τα θέματα</a><a class="btn btn--ghost btn--lg" href="/">Αρχική</a></div>
  </div></div></section><main id="main"></main>'''
    write("404.html", shell(path="404.html", title="Η σελίδα δεν βρέθηκε | Κ. Μυρίλλας", desc="Η σελίδα δεν βρέθηκε.",
                            depth=d, body=body).replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/'))


# ══════════════════════════════════════════════════════════════════════════════
# ASSETS
# ══════════════════════════════════════════════════════════════════════════════
FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0F171E"/><text x="32" y="40" text-anchor="middle" font-family="Manrope,Arial,sans-serif" font-weight="800" font-size="34" fill="#fff">m</text><path d="M14 46c10 8 28 8 38 2" fill="none" stroke="#1399FF" stroke-width="5" stroke-linecap="round"/><path d="M48 44l5 3-2 5" fill="none" stroke="#1399FF" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>'''


def images():
    dst = os.path.join(OUT, "assets", "img")
    os.makedirs(dst, exist_ok=True)
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        Image = None
    n = 0
    for f in sorted(os.listdir(IMG_SRC)):
        src, out = os.path.join(IMG_SRC, f), os.path.join(dst, f)
        if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
            shutil.copy(src, out)
        stem = f.rsplit(".", 1)[0]
        webp = os.path.join(dst, stem + ".webp")
        if Image and (not os.path.exists(webp) or os.path.getmtime(webp) < os.path.getmtime(src)):
            try:
                im = Image.open(src)
                im = im.convert("RGBA") if im.mode in ("P", "LA") else im.convert("RGB") if im.mode != "RGBA" else im
                if im.width > 1800:
                    im = im.resize((1800, round(im.height * 1800 / im.width)), Image.LANCZOS)
                im.save(webp, "WEBP", quality=82, method=6)
                n += 1
            except Exception as e:
                print("  webp skipped", f, e)
    with open(os.path.join(dst, "favicon.svg"), "w", encoding="utf-8") as fh:
        fh.write(FAVICON)
    if Image:
        ic = Image.new("RGB", (180, 180), "#0F171E")
        dr = ImageDraw.Draw(ic)
        dr.rounded_rectangle((0, 0, 179, 179), radius=36, fill="#0F171E")
        dr.arc((36, 60, 144, 168), 200, 340, fill="#1399FF", width=12)
        dr.ellipse((70, 60, 110, 100), fill="#FFFFFF")
        ic.save(os.path.join(dst, "apple-touch-icon.png"))
        og = Image.open(os.path.join(IMG_SRC, "2021-11-myr.jpg")).convert("RGB")
        w, h = og.size
        target = 1200 / 630
        if w / h > target:
            nw = round(h * target); og = og.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        og = og.resize((1200, 630), Image.LANCZOS)
        og.save(os.path.join(dst, "og-default.jpg"), quality=85)
    print(f"  images: {len(os.listdir(IMG_SRC))} files, {n} new webp")


def assets():
    for sub in ("css", "js", "docs"):
        s, d = os.path.join(SRC, "assets", sub), os.path.join(OUT, "assets", sub)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
    images()


def redirects():
    old = [("/dr-k-myrillas/", "/gynaikologos-dr-k-myrillas/"), ("/newsletter/", "/"), ("/robotiki-xeirourgiki/", "/services/robotiki-xeirourgiki/"),
           ("/testimonials/", "/"), ("/blog/page/:n/", "/blog/")]
    with open(os.path.join(OUT, "_redirects"), "w") as f:
        for a, b in old:
            f.write(f"{a.replace(':n', '*')}  {b}  301\n")
    with open(os.path.join(OUT, ".htaccess"), "w") as f:
        f.write("RewriteEngine On\n")
        for a, b in old:
            if ":n" in a:
                f.write(f"RewriteRule ^blog/page/[0-9]+/?$ /blog/ [R=301,L]\n")
            else:
                f.write(f"Redirect 301 {a.rstrip('/')} {b}\n")
        f.write("ErrorDocument 404 /404.html\n")
    vercel = {"$schema": "https://openapi.vercel.sh/vercel.json", "trailingSlash": True, "cleanUrls": False,
              "redirects": [{"source": a, "destination": b, "permanent": True} for a, b in old],
              "headers": [{"source": "/assets/(img|docs)/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
                          {"source": "/assets/(css|js)/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=86400, must-revalidate"}]},
                          {"source": "/(.*)", "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"},
                                                          {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}]}]}
    with open(os.path.join(OUT, "vercel.json"), "w", encoding="utf-8") as f:
        json.dump(vercel, f, ensure_ascii=False, indent=2)


def sitemap():
    rows = "".join(f"<url><loc>{SITE['domain']}/{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{fr}</changefreq><priority>{p}</priority></url>\n"
                   for u, p, fr in PAGES)
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /i-lista-mou/\nSitemap: {SITE['domain']}/sitemap.xml\n")
    write("search-index.json", json.dumps(SEARCH, ensure_ascii=False, separators=(",", ":")))


def main():
    if os.path.isdir(OUT):
        for f in os.listdir(OUT):
            p = os.path.join(OUT, f)
            if f == "assets":
                continue
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(OUT, exist_ok=True)
    print("assets…"); assets()
    print("pages…")
    build_home()
    for s in SERVICES:
        build_service(s)
    build_services_hub()
    for c in CATEGORIES:
        build_category(c)
    for a in ARTICLES:
        build_article(a)
    build_blog(); build_videos(); build_photos(); build_doctor(); build_contact(); build_testimonials()
    build_guide_page(); build_mylist(); build_terms(); build_404()
    redirects(); sitemap()
    print(f"  {len(PAGES)} pages, {len(SEARCH)} search rows → {OUT}")


if __name__ == "__main__":
    main()
