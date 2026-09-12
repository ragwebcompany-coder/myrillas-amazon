# -*- coding: utf-8 -*-
"""Περιεχόμενο του kmyrillas.gr, όπως τραβήχτηκε από το ζωντανό site (Σεπτ. 2026).

Τίποτα εδώ δεν είναι επινοημένο: κείμενα, τίτλοι, meta descriptions, εικόνες,
βίντεο, μαρτυρίες, ωράριο και στοιχεία επικοινωνίας προέρχονται από τις
δημοσιευμένες σελίδες του ιατρείου. Ό,τι είναι "παρουσίαση" (ετικέτες
κατηγοριών, σειρά εμφάνισης, Top 10) είναι επιμέλεια, όχι ιατρική πληροφορία.

  content/legacy.json       το κυρίως κείμενο κάθε σελίδας (πεδίο body)
  content/pages-extra.json  βιογραφικό, επικοινωνία, gallery, μαρτυρίες
  content/yt-titles.json    τίτλοι των βίντεο από το YouTube (oEmbed)
  content/imgmap.json       URL εικόνας στο παλιό site -> αρχείο στο assets/img/
"""
import os, re, json, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONTENT = os.path.join(ROOT, "content")

LEGACY = json.load(open(os.path.join(CONTENT, "legacy.json"), encoding="utf-8"))
EXTRA = json.load(open(os.path.join(CONTENT, "pages-extra.json"), encoding="utf-8"))
YT = json.load(open(os.path.join(CONTENT, "yt-titles.json"), encoding="utf-8"))
IMGMAP = json.load(open(os.path.join(CONTENT, "imgmap.json"), encoding="utf-8"))
BLOG_ORDER = json.load(open(os.path.join(CONTENT, "blog-order.json"), encoding="utf-8"))
TODAY = datetime.date.today().isoformat()

# ── το ιατρείο ───────────────────────────────────────────────────────────────
SITE = dict(
    domain="https://kmyrillas.gr",
    name="Κωνσταντίνος Μυρίλλας",
    brand="myrillas",
    tagline="Μαιευτήρας – Χειρουργός Γυναικολόγος, M.R.C.O.G.",
    doctor="Κωνσταντίνος Μυρίλλας",
    doctor_short="Dr. Κ. Μυρίλλας",
    address="Καραολή Δημητρίου 41",
    locality="Βύρωνας",
    region="Αττική",
    region_iso="GR-A1",
    postcode="162 32",
    lat="37.956885", lng="23.761704",
    map_url="https://www.google.com/maps?ll=37.956885,23.761704&z=17&t=m&hl=el&cid=428410887001455016",
    phone="210 76 09 109", phone_href="+302107609109",
    mobile="6973 64 30 90", mobile_href="+306973643090",
    fax="210 76 09 109",
    email="web@kmyrillas.gr",
    hours=[("Δευτέρα", "17:00 – 21:30"), ("Τρίτη", "κατόπιν ραντεβού"),
           ("Τετάρτη", "17:00 – 21:30"), ("Πέμπτη", "17:00 – 21:30"),
           ("Παρασκευή", "κατόπιν ραντεβού"), ("Σάββατο – Κυριακή", "κλειστά")],
    hours_short="Δευτέρα, Τετάρτη & Πέμπτη 17:00 – 21:30",
    hospital="Μαιευτήριο ΡΕΑ",
    social=dict(facebook="https://www.facebook.com/KonstantinosMyrillas",
                twitter="https://twitter.com/KMyrillas",
                youtube="https://www.youtube.com/user/KMyrillas",
                instagram="https://www.instagram.com/dr_mirillas/"),
    partners=[
        dict(name="LVRI Athens", url="https://lvriathens.com/", logo="2022-01-lvri-logo.png",
             text="Το τμήμα πλαστικής κόλπου και επανορθωτικής χειρουργικής πυέλου με laser που "
                  "διευθύνει ο Dr. Μυρίλλας από το 2013. Δημιουργήθηκε ως απάντηση στην αναζήτηση "
                  "καθημερινών ανθρώπων να διευρύνουν τους ορίζοντες της σεξουαλικότητάς τους."),
        dict(name="Forever Skin Laser", url="", logo="2022-01-forever-logo.png",
             text="Δερματολογικές και γυναικολογικές παθήσεις και αισθητικές επεμβάσεις, ανώδυνα "
                  "και με εξελιγμένες μεθόδους, με επαγγελματισμό και άρτια κατάρτιση."),
    ],
    pdf="docs/sel-2-compressed.pdf",
    pdf_title="Χειρουργική Ελάχιστης Παρέμβασης",
    credit=dict(name="Απόστολος Πολλάλης", url="https://github.com/apostolospollalis"),
)

# ── κατηγορίες, όπως στο μενού του ιατρείου ─────────────────────────────────
CATEGORIES = [
    dict(slug="maieftiki", title="Μαιευτική", color="#1399FF",
         blurb="Από τον προγεννητικό έλεγχο μέχρι τον τοκετό.",
         services=["progennitikos-elegxos", "poreia-egkymosynis-exetaseis",
                   "fysiologikos-toketos", "kaisariki-tomi"]),
    dict(slug="gynaikologia", title="Γυναικολογία", color="#FF4F8B",
         blurb="Ινομυώματα, ενδομητρίωση, υστεροσκόπηση, υστερεκτομή.",
         services=["inomyomata-mitras", "endomitriosi-symptomata-diagnosi-therapeia",
                   "endomitriosi-egkymosyni", "kystes-endomitriosis", "ysteroskopisi", "ysterektomi"]),
    dict(slug="endomitrio", title="Ενδομήτριο", color="#B57BFF",
         blurb="Πάχυνση, πολύποδες, απόξεση, υπερπλασία, καρκίνος.",
         services=["endomitria-paxinsi", "polypodas-endomitriou", "apoxesi-mitras",
                   "yperplasia-endomitriou", "karkinos-ca-endomitriou"]),
    dict(slug="traxilos", title="Τράχηλος", color="#FFB84D",
         blurb="Loop, κωνοειδής εκτομή, κολποσκόπηση, τραχηλίτιδα.",
         services=["loop-traxilou", "traxilitida-diagnosi-therapeia", "konoeidis-ektomi-traxilou-mitras",
                   "kolposkopisi", "karkinos-traxilou-mitras", "polypodas-traxilou-mitras"]),
    dict(slug="emminopafsi", title="Εμμηνόπαυση", color="#5AD8A6",
         blurb="Κλιμακτήριος, συμπτώματα, ξηρότητα κόλπου.",
         services=["ksirotita-atrofia-kolpou-emminopafsi", "klimaktirios", "emminopafsi-symptomata-therapeia"]),
    dict(slug="apovoli", title="Αποβολή", color="#8EA3FF",
         blurb="Πρώτο και δεύτερο τρίμηνο, βιοχημική, παλίνδρομη κύηση.",
         services=["apovoli-emvryou", "protou-triminou", "deuterou-triminou",
                   "vioximiki-apovoli", "palindromi-kyisi"]),
    dict(slug="oothikes", title="Ωοθήκες", color="#FF7A59",
         blurb="Κύστες, πολυκυστικές ωοθήκες, καρκίνος ωοθηκών.",
         services=["kystes-oothikon", "syndromo-polykystikon-oothikon", "karkinos-oothikon"]),
    dict(slug="hpv", title="HPV", color="#3ED0FF",
         blurb="Ο ιός των κονδυλωμάτων, το τεστ Παπ, το εμβόλιο.",
         services=["hpv-limoksi"]),
    dict(slug="gonimotita", title="Γονιμότητα", color="#F2D06B",
         blurb="Κατάψυξη και κρυοσυντήρηση ωαρίων.",
         services=["katapsyksi-kryosyntirisi-oarion"]),
    dict(slug="xeirourgiki", title="Χειρουργική ελάχιστης παρέμβασης", short="Χειρουργική", color="#00D1B2",
         blurb="Λαπαροσκοπική και ρομποτική χειρουργική με το σύστημα Da Vinci.",
         services=["laparoskopikes-epemvaseis", "robotiki-xeirourgiki"]),
]
CAT = {c["slug"]: c for c in CATEGORIES}
SERVICE_CAT = {s: c["slug"] for c in CATEGORIES for s in c["services"]}

# Ετικέτα "είδους" ανά υπηρεσία: μόνο ό,τι προκύπτει από τον ίδιο τον τίτλο.
KIND = {
    "progennitikos-elegxos": "Εξετάσεις", "poreia-egkymosynis-exetaseis": "Εξετάσεις",
    "fysiologikos-toketos": "Τοκετός", "kaisariki-tomi": "Τοκετός",
    "inomyomata-mitras": "Πάθηση", "endomitriosi-symptomata-diagnosi-therapeia": "Πάθηση",
    "endomitriosi-egkymosyni": "Πάθηση", "kystes-endomitriosis": "Πάθηση",
    "ysteroskopisi": "Επέμβαση", "ysterektomi": "Επέμβαση",
    "endomitria-paxinsi": "Πάθηση", "polypodas-endomitriou": "Πάθηση", "apoxesi-mitras": "Επέμβαση",
    "yperplasia-endomitriou": "Πάθηση", "karkinos-ca-endomitriou": "Πάθηση",
    "loop-traxilou": "Επέμβαση", "traxilitida-diagnosi-therapeia": "Πάθηση",
    "konoeidis-ektomi-traxilou-mitras": "Επέμβαση", "kolposkopisi": "Εξέταση",
    "karkinos-traxilou-mitras": "Πάθηση", "polypodas-traxilou-mitras": "Πάθηση",
    "ksirotita-atrofia-kolpou-emminopafsi": "Πάθηση", "klimaktirios": "Ενημέρωση",
    "emminopafsi-symptomata-therapeia": "Ενημέρωση",
    "apovoli-emvryou": "Ενημέρωση", "protou-triminou": "Ενημέρωση", "deuterou-triminou": "Ενημέρωση",
    "vioximiki-apovoli": "Ενημέρωση", "palindromi-kyisi": "Ενημέρωση",
    "kystes-oothikon": "Πάθηση", "syndromo-polykystikon-oothikon": "Πάθηση", "karkinos-oothikon": "Πάθηση",
    "hpv-limoksi": "Πάθηση", "katapsyksi-kryosyntirisi-oarion": "Διαδικασία",
    "laparoskopikes-epemvaseis": "Επεμβάσεις", "robotiki-xeirourgiki": "Επεμβάσεις",
}

# Τα δέκα που ανοίγουν την αρχική. Επιμέλεια, με βάση το πού δίνει βάρος το ίδιο το site
# (slider, βασικές υπηρεσίες στο footer, πλήθος βίντεο και κειμένου).
TOP10 = ["inomyomata-mitras", "robotiki-xeirourgiki", "endomitriosi-symptomata-diagnosi-therapeia",
         "hpv-limoksi", "laparoskopikes-epemvaseis", "ysteroskopisi", "kystes-oothikon",
         "katapsyksi-kryosyntirisi-oarion", "ysterektomi", "fysiologikos-toketos"]

# Το hero της αρχικής: οι τρεις διαφάνειες του παλιού slider συν οι δύο νεότερες υπηρεσίες.
HERO = [
    dict(service="inomyomata-mitras", image="2021-11-inomiomata-slider.jpg", pos="center 40%",
         kicker="Οι πιο συχνοί καλοήθεις όγκοι της μήτρας",
         video="AxqM0BT6XIE"),
    dict(service="fysiologikos-toketos", image="2021-11-slider-3.jpg", pos="center 35%",
         kicker="Μαιευτική", title="Μαιευτική", video=None,
         lead="Προγεννητικός έλεγχος, παρακολούθηση της εγκυμοσύνης, φυσιολογικός τοκετός και "
              "καισαρική τομή στο Μαιευτήριο ΡΕΑ."),
    dict(service="robotiki-xeirourgiki", image="2021-11-myr.jpg", pos="center 30%",
         kicker="Το πρώτο ρομποτικό χειρουργείο στην Ελλάδα, Οκτώβριος 2007",
         title="Ρομποτική Χειρουργική", video="cAh-5sH2lV0"),
    dict(service="hpv-limoksi", image="2024-03-ti-einai-o-hpv.jpg", pos="center",
         kicker="Ο ιός των ανθρώπινων κονδυλωμάτων", video="NjDBP5ciyq8"),
    dict(service="katapsyksi-kryosyntirisi-oarion", image="2024-03-kryosintirisi-oarion.jpg", pos="center",
         kicker="Γονιμότητα", video="msSCFVDZcxc"),
]

# ── βίντεο: 37 από το κανάλι του ιατρείου, ομαδοποιημένα ─────────────────────
VIDEO_GROUPS = [
    ("Ρομποτική & ΜΜΕ", "Συνεντεύξεις και εκπομπές",
     ["WrXrhO9063c", "cAh-5sH2lV0", "EPHbT_-9GkI", "RGLafhTXWwo", "iGFBuU3COOY", "msSCFVDZcxc",
      "DG7sv_O_szQ", "NjDBP5ciyq8", "Eg1q9phhklk", "AsA3RQ8XmsA", "AxqM0BT6XIE", "M4PzAFDu8ME"]),
    ("Ινομυώματα", "Από το χειρουργείο",
     ["XXaY2SgYyNM", "UlkqdHo8DFI", "SLJnO8Nn44E", "O-j--kculzA", "Y0Au-835oSs", "EFf1Q4_Zmyk"]),
    ("Υστερεκτομή", "Από το χειρουργείο",
     ["OM1c7x3ZwdM", "cgjOsb9lbSA", "NrCe2Q3l4xk", "_n6ecKP7B9A", "uu_zQdoOfP8"]),
    ("Ωοθήκες & κύστες", "Από το χειρουργείο",
     ["r0bjdoeFty4", "0sn-0fyhVPs", "9HSIG18nmf4", "qhP2yhgA_Tc", "_gL-FMSycP8"]),
    ("Υστεροσκόπηση & πολύποδες", "Από το χειρουργείο",
     ["3d_PkwJBlhU", "KHOEu-tmoY4", "kd46q8dMh2o", "YbnCAFXaku8", "NeQGmdk4UzY"]),
    ("Εξωμήτριος & συμφύσεις", "Από το χειρουργείο",
     ["VJz3rSs39kI", "h6kXAEQw4ho", "CTZLYcZCblg"]),
]
VIDEO_THUMBS = {  # thumbnails που ανέβασε το ίδιο το ιατρείο (video gallery)
    "XXaY2SgYyNM": "2022-01-endotraxiliko-inomyoma.jpg", "uu_zQdoOfP8": "2022-02-kmyrillas-ysterektomi.jpg",
    "r0bjdoeFty4": "2022-03-kysti-endomitriosis-oothikis.jpg", "DG7sv_O_szQ": "2022-03-ios-hpv.jpg",
    "iGFBuU3COOY": "2022-03-maieytirio-rea.jpg", "msSCFVDZcxc": "2022-03-provlimata-gonimotitas.jpg",
    "RGLafhTXWwo": "2022-03-rompotiki-gynaikologia-2.jpg",
    "EPHbT_-9GkI": "2022-03-rompotiki-cheiroyrgiki-sti-gynaikologia.jpg",
    "cAh-5sH2lV0": "2022-03-rompotiki-cheiroyrgiki-sti-gynaikologia.jpg",
}


def _clean_title(t):
    t = re.sub(r"\s*[-–]\s*(Dr\.? Mirillas|Μαιευτήρας Χειρουργός Γυναικολόγος Κωνσταντίνος Μυρίλλας)\s*$", "", t)
    t = re.sub(r"^(ΕΔΩ - )", "", t)
    return t.strip()


VIDEOS = []
for _g, (_gt, _gk, _ids) in enumerate(VIDEO_GROUPS):
    for _i in _ids:
        _rec = YT.get(_i) or {}
        _title = _rec.get("title") or "Λαπαροσκοπική υστερεκτομία"
        VIDEOS.append(dict(id=_i, title=_clean_title(_title), group=_gt, kicker=_gk,
                           thumb=VIDEO_THUMBS.get(_i)))
VID = {v["id"]: v for v in VIDEOS}
HOME_VIDEOS = ["cAh-5sH2lV0", "AxqM0BT6XIE", "Eg1q9phhklk", "NjDBP5ciyq8", "UlkqdHo8DFI",
               "AsA3RQ8XmsA", "OM1c7x3ZwdM", "r0bjdoeFty4", "WrXrhO9063c", "iGFBuU3COOY"]

# ── μαρτυρίες, όπως δημοσιεύονται στο site ───────────────────────────────────
TESTIMONIALS = [
    dict(slug="xenia-m-apo-kifisia", name="Ξένια Μ.", place="Κηφισιά", topic="kystes-oothikon",
         text="Ο κ. Μυρίλλας μας εξήγησε σε εξονυχιστικό μάλιστα βαθμό τη διαδικασία του χειρουργείου "
              "μας για μια κύστη ωοθήκης με λαπαροσκόπηση. Όλα πήγαν κατ´ευχήν και τον ευχαριστούμε για όλα."),
    dict(slug="maria-l-apo-aigio", name="Μαρία Λ.", place="Αίγιο", topic="inomyomata-mitras",
         text="Βιώσαμε την ευγένεια και τον πολιτισμό στο μαιευτήριο Ρέα με τη βοήθεια του γιατρού μας "
              "Κ. Μυρίλλα σε ενα χειρουργείο λαπαροσκόπησης λόγω ινομυωμάτων. Το επίπεδο του πόνου ήταν "
              "αυτό που μας είχε υποσχεθεί, δηλαδή σχεδόν καθόλου από την πρώτη μέρα. Μακριά απο σας αλλά "
              "αν χρειαστεί χειρουργείο μη φοβάστε, όλα είναι πια απόλυτα ανεκτά!"),
]

# ── ο γιατρός: ό,τι γράφει το βιογραφικό του, σε χρονολογική σειρά ──────────
TIMELINE = [
    ("1967", "Γεννιέται στην Αθήνα, Κερκυραϊκής καταγωγής."),
    ("1979", "Εισάγεται 8ος στη Βαρβάκειο Πρότυπη Σχολή."),
    ("1985", "Αποφοιτεί από τη Βαρβάκειο· εισάγεται 2ος με πανελλήνιες στην Ιατρική Σχολή Αθηνών, "
             "από όπου αποφοιτεί με άριστα."),
    ("Λονδίνο & Cambridge", "Μεταπτυχιακές σπουδές στην Ηνωμένη Βρετανία: King's College Hospital, Royal Free, "
                            "Rosie Maternity και Queen Elizabeth. Ειδικότητα μαιευτικής γυναικολογίας."),
    ("2001", "Ιδιωτεύει στην Αθήνα, αρχικά στα μαιευτήρια ΙΑΣΩ και ΛΗΤΩ."),
    ("2002–2007", "Μελέτες S.C.A.R. και G.E.N.E.V.A. για τις μετεγχειρητικές συμφύσεις: 65 περιστατικά "
                  "second look laparoscopy, ο μεγαλύτερος αριθμός παγκοσμίως για την ομάδα του."),
    ("2005–2011", "Διδάσκει λαπαροσκοπική χειρουργική σε νέους ιατρούς με την ομάδα A.C.E.T. "
                  "στον Λευκό Σταυρό. Από το 2007 Επίτιμος Καθηγητής της σχολής."),
    ("Οκτώβριος 2007", "Μετά από εκπαίδευση στο Στρασβούργο, εκτελεί το πρώτο χειρουργείο στην Ελλάδα "
                       "με το ρομπότ Da Vinci High Definition, με την ομάδα του Ιατρικού Κέντρου Αθηνών."),
    ("2008", "Τα πρώτα πανελλαδικά ρομποτικά χειρουργεία σε μαιευτήριο (Γαία – Ερρίκος Ντυνάν)."),
    ("2010", "Ιδρυτικό στέλεχος του Μαιευτηρίου ΡΕΑ Νοτίων Προαστίων."),
    ("2013", "Αναλαμβάνει την επιστημονική διεύθυνση του τμήματος πλαστικής κόλπου και επανορθωτικής "
             "χειρουργικής πυέλου με laser στο ΡΕΑ (LVRI Athens)."),
]
MEMBERSHIPS = ["Ελληνική Λαπαροσκοπική Εταιρεία", "Royal College of Obstetricians and Gynaecologists (MRCOG)",
               "Επίτιμο μέλος του Αμερικανικού Κολλεγίου", "Ελληνική & διεθνής ρομποτική εταιρεία (MIRA)",
               "European Society for Gynaecological Endoscopy (ESGE)", "Ευρωπαϊκή εταιρεία γονιμότητας (ESHRE)"]
STUDIES = ["Μελέτη S.C.A.R., 2002–2004", "Μελέτη G.E.N.E.V.A., 2004–2006",
           "Συμφύσεις κατόπιν ινομυωμάτων, 14 περιστατικά 2nd look (Fertility & Sterility)",
           "Ετεροτοπική εγκυμοσύνη κατόπιν I.V.F., 9 περιστατικά (ESGE 2006)",
           "Ρόλος μετεγχειρητικών συμφύσεων (ESGE 2009)",
           "Αναδρομική μελέτη πλαστικής κόλπου, 27 περιστατικά (RCOG)",
           "Παρουσιάσεις case studies σε συνέδρια μαιευτικής γυναικολογίας, 2002–2009"]
PRESS = ["2022-01-paraskinio-mme.jpg", "2022-01-life-style92.jpg", "2022-01-modern-beauty-1-exo.jpg",
         "2022-01-life-style27.jpg", "2022-01-eiatrika69.jpg", "2022-01-eiatrika88.jpg",
         "2022-01-jolie.jpg", "2022-01-eiatrika125.jpg"]
GALLERY = [f"2021-11-kmyrillas-{i}-{s}.jpg" for i, s in
           [(10, "300x200"), (9, "300x200"), (8, "300x200"), (7, "300x200"), (6, "300x200"),
            (5, "241x300"), (4, "241x300"), (3, "241x300"), (2, "241x300"), (1, "241x300")]]

# ── άρθρα: κατηγορία από τον τίτλο, σειρά όπως στο blog ─────────────────────
def article_tag(slug, title):
    t = (title + " " + slug).lower()
    if re.search(r"τοκετ|εγκυμ|εγκιμ|κύηση|κυισ|θηλασμ|λοχεί|μαμά|γέννα|διατροφ|κιλά|πολύδυμ|πολυδιμ|επιπλοκ|πλακούντα|ομφάλ", t):
        return "Εγκυμοσύνη"
    if re.search(r"υπέρηχ|μαστογρ|test pap|4d|υπερηχ", t):
        return "Εξετάσεις"
    if re.search(r"υπογονιμ|ivf|αντισύλληψη|εξωσωματ", t):
        return "Γονιμότητα"
    if re.search(r"λαπαροσκοπ|υστερεκτ|υστεροσκ", t):
        return "Χειρουργική"
    if re.search(r"καλοκαίρι|κρίση", t):
        return "Καθημερινότητα"
    return "Γυναικολογία"


ARTICLES = [dict(slug=s, title=t, tag=article_tag(s, t)) for s, t in BLOG_ORDER]
ART = {a["slug"]: a for a in ARTICLES}

# Άρθρα που έχουν πρακτικά το ίδιο κείμενο με μια υπηρεσία: στέλνουν εκεί.
ARTICLE_TWIN = {"inomyomata-mitras": "inomyomata-mitras", "ysteroskopisi": "ysteroskopisi",
                "kystes-oothikon": "kystes-oothikon", "kolposkopisi": "kolposkopisi"}
# σχετικά άρθρα ανά υπηρεσία (με λέξεις-κλειδιά του τίτλου)
RELATED_KEYS = {
    "inomyomata-mitras": ["ινομυ"], "endomitriosi-symptomata-diagnosi-therapeia": ["ενδομητρ"],
    "endomitriosi-egkymosyni": ["ενδομητρ"], "kystes-endomitriosis": ["ενδομητρ"],
    "ysteroskopisi": ["υστεροσκ", "πολύποδ"], "ysterektomi": ["υστερεκτ"],
    "polypodas-endomitriou": ["πολύποδ"], "polypodas-traxilou-mitras": ["πολύποδ"],
    "kystes-oothikon": ["κύστες", "ωοθηκ"], "syndromo-polykystikon-oothikon": ["πολυκυστ"],
    "karkinos-oothikon": ["ωοθηκ"], "hpv-limoksi": ["hpv", "κονδυλ", "pap"],
    "kolposkopisi": ["κολποσκ", "pap", "hpv"], "loop-traxilou": ["hpv", "pap"],
    "konoeidis-ektomi-traxilou-mitras": ["hpv", "pap"], "karkinos-traxilou-mitras": ["hpv", "pap"],
    "emminopafsi-symptomata-therapeia": ["εμμηνόπαυσ"], "klimaktirios": ["εμμηνόπαυσ"],
    "ksirotita-atrofia-kolpou-emminopafsi": ["εμμηνόπαυσ", "αιδοί"],
    "fysiologikos-toketos": ["τοκετ", "γέννα", "λοχεί"], "kaisariki-tomi": ["καισαρ", "τοκετ"],
    "poreia-egkymosynis-exetaseis": ["εγκυμ", "εγκιμ", "παρακολούθ", "διατροφ", "κιλά"],
    "progennitikos-elegxos": ["σύλληψη", "υπέρηχ", "4d", "μαμά"],
    "apovoli-emvryou": ["αποβολ", "εξωμήτρ"], "protou-triminou": ["αποβολ"], "deuterou-triminou": ["αποβολ"],
    "vioximiki-apovoli": ["αποβολ", "σύλληψη"], "palindromi-kyisi": ["αποβολ"],
    "katapsyksi-kryosyntirisi-oarion": ["υπογονιμ", "ivf", "μαμά"],
    "laparoskopikes-epemvaseis": ["λαπαροσκοπ", "υστερεκτ", "εξωμήτρ", "σαλπίγγ"],
    "robotiki-xeirourgiki": ["λαπαροσκοπ", "υστερεκτ"],
    "endomitria-paxinsi": ["πολύποδ", "περίοδος"], "yperplasia-endomitriou": ["πολύποδ"],
    "karkinos-ca-endomitriou": ["πολύποδ", "υστερεκτ"], "apoxesi-mitras": ["αποβολ", "πολύποδ"],
    "traxilitida-diagnosi-therapeia": ["αιδοί", "hpv", "καλοκαίρι"],
}


def related_articles(service_slug, n=6):
    keys = RELATED_KEYS.get(service_slug, [])
    out = [a for a in ARTICLES if any(k in (a["title"] + a["slug"]).lower() for k in keys)
           and ARTICLE_TWIN.get(a["slug"]) != service_slug]
    return out[:n]


# ── υπηρεσίες ────────────────────────────────────────────────────────────────
def rec(slug, kind="service"):
    return LEGACY.get(("services__" + slug) if kind == "service" else slug) or {}


SPAM = re.compile(r"\s*(Κλείστε( τώρα| σήμερα)? ραντεβού[^.!]*[.!]?|Ο Dr\.? Μυρίλλας απαντά(ει)?( σε όλα)?\.?|"
                  r"Μάθετ[εα] τα πάντα[^.!]*[.!]?|Ενημερωθείτε από[^.!]*[.!]?|Βρείτε όλες τις απαντήσεις\.?|"
                  r"Δώστε άμεση λύση\.?|Κλείνοντας ραντεβού με τον ιατρό\.?)", re.I)


def plain(markup):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", markup or ""))).strip()


def first_paragraph(body, minlen=60):
    for p in re.findall(r"<(?:p|li)>(.*?)</(?:p|li)>", body or "", re.S):
        t = plain(p)
        if len(t) >= minlen:
            return t
    return ""


def shorten(text, limit=160):
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(" ,·;:—–-")
    return cut + "…"


def lead_for(r):
    d = SPAM.sub("", r.get("desc") or "").strip()
    d = re.sub(r"\s+", " ", d).strip(" .") + ("." if d else "")
    if len(d) < 50:
        d = first_paragraph(r.get("body", ""))
    return shorten(d, 190)


def h1_for(slug, r):
    h = (r.get("h1") or "").strip()
    fixes = {"laparoskopikes-epemvaseis": "Λαπαροσκοπικές επεμβάσεις",
             "traxilitida-diagnosi-therapeia": "Τραχηλίτιδα", "robotiki-xeirourgiki": "Ρομποτική χειρουργική",
             "katapsyksi-kryosyntirisi-oarion": "Κατάψυξη ωαρίων", "apovoli-emvryou": "Αποβολή εμβρύου"}
    return fixes.get(slug, h)


SERVICES = []
for _c in CATEGORIES:
    for _s in _c["services"]:
        _r = rec(_s)
        SERVICES.append(dict(slug=_s, cat=_c["slug"], title=h1_for(_s, _r), seo_title=_r.get("title", ""),
                             meta=_r.get("desc") or "", lead=lead_for(_r), image=IMGMAP.get(_r.get("image", "")),
                             body=_r.get("body", ""), videos=_r.get("videos", []), words=_r.get("words", 0),
                             pub=_r.get("pub", ""), mod=_r.get("mod", ""), kind=KIND.get(_s, "Ενημέρωση")))
SVC = {s["slug"]: s for s in SERVICES}


def article_rec(slug):
    r = LEGACY.get(slug) or {}
    a = ART[slug]
    return dict(slug=slug, title=a["title"], tag=a["tag"], seo_title=r.get("title", ""),
                meta=SPAM.sub("", r.get("desc") or ""), lead=lead_for(r),
                image=IMGMAP.get(r.get("image", "")), body=r.get("body", ""),
                videos=r.get("videos", []), words=r.get("words", 0), pub=r.get("pub", ""), mod=r.get("mod", ""))


DOCTOR_BODY = EXTRA["gynaikologos-dr-k-myrillas"]

# ── βοηθητικά ────────────────────────────────────────────────────────────────
def rel(depth):
    return "../" * depth if depth else ""


def read_minutes(words):
    return max(1, round(words / 180))


MONTHS_GEN = ["Ιανουαρίου", "Φεβρουαρίου", "Μαρτίου", "Απριλίου", "Μαΐου", "Ιουνίου", "Ιουλίου",
              "Αυγούστου", "Σεπτεμβρίου", "Οκτωβρίου", "Νοεμβρίου", "Δεκεμβρίου"]


def pretty_date(iso):
    if not iso:
        return ""
    y, m, d = iso.split("-")
    return f"{int(d)} {MONTHS_GEN[int(m) - 1]} {y}"


def seo_title(text, suffix=" | Κ. Μυρίλλας", cap=68):
    text = text.strip()
    return text if len(text) + len(suffix) > cap else text + suffix
