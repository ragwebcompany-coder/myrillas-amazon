# -*- coding: utf-8 -*-
"""Περιοχές γύρω από το ιατρείο (Βύρωνας) για τις τοπικές σελίδες «Γυναικολόγος <περιοχή>».

Μόνο περιοχές σε λογική απόσταση (έως ~6 χλμ): η Google τιμωρεί δεκάδες σχεδόν ίδιες σελίδες
(doorway pages), γι' αυτό κάθε σελίδα έχει τη δική της απόσταση, γειτονιές, θέματα και ερωτήσεις.
Οι συντεταγμένες είναι το κέντρο κάθε περιοχής (κατά προσέγγιση)· η απόσταση γράφεται στρογγυλεμένη.
"""
import math

# slug, ονομαστική, αιτιατική με άρθρο (για «από …» / «σ…»), lat, lng
AREAS = [
    ("vyronas", "Βύρωνας", "τον Βύρωνα", 37.9608, 23.7536),
    ("kaisariani", "Καισαριανή", "την Καισαριανή", 37.9660, 23.7640),
    ("pagkrati", "Παγκράτι", "το Παγκράτι", 37.9675, 23.7445),
    ("ymittos", "Υμηττός", "τον Υμηττό", 37.9495, 23.7455),
    ("dafni", "Δάφνη", "τη Δάφνη", 37.9460, 23.7350),
    ("zografou", "Ζωγράφου", "το Ζωγράφου", 37.9770, 23.7700),
    ("ilioupoli", "Ηλιούπολη", "την Ηλιούπολη", 37.9320, 23.7550),
    ("mets", "Μετς", "το Μετς", 37.9665, 23.7390),
    ("ilisia", "Ιλίσια", "τα Ιλίσια", 37.9775, 23.7560),
    ("neos-kosmos", "Νέος Κόσμος", "τον Νέο Κόσμο", 37.9575, 23.7285),
    ("agios-dimitrios", "Άγιος Δημήτριος", "τον Άγιο Δημήτριο", 37.9330, 23.7300),
    ("ampelokipoi", "Αμπελόκηποι", "τους Αμπελόκηπους", 37.9870, 23.7580),
    ("nea-smyrni", "Νέα Σμύρνη", "τη Νέα Σμύρνη", 37.9445, 23.7145),
    ("papagou", "Παπάγου", "το Παπάγου", 37.9880, 23.7930),
    ("cholargos", "Χολαργός", "τον Χολαργό", 38.0010, 23.7970),
    ("argyroupoli", "Αργυρούπολη", "την Αργυρούπολη", 37.9060, 23.7500),
]

CLINIC = (37.956885, 23.761704)

# Δήμος κάθε περιοχής (οι γειτονιές της Αθήνας ανήκουν στον Δήμο Αθηναίων)
MUNICIPALITY = {
    "vyronas": "Δήμος Βύρωνα", "kaisariani": "Δήμος Καισαριανής", "pagkrati": "Δήμος Αθηναίων",
    "ymittos": "Δήμος Δάφνης – Υμηττού", "dafni": "Δήμος Δάφνης – Υμηττού", "zografou": "Δήμος Ζωγράφου",
    "ilioupoli": "Δήμος Ηλιούπολης", "mets": "Δήμος Αθηναίων", "ilisia": "Δήμος Αθηναίων",
    "neos-kosmos": "Δήμος Αθηναίων", "agios-dimitrios": "Δήμος Αγίου Δημητρίου", "ampelokipoi": "Δήμος Αθηναίων",
    "nea-smyrni": "Δήμος Νέας Σμύρνης", "papagou": "Δήμος Παπάγου – Χολαργού", "cholargos": "Δήμος Παπάγου – Χολαργού",
    "argyroupoli": "Δήμος Ελληνικού – Αργυρούπολης",
}
COMPASS = ["βόρεια", "βορειοανατολικά", "ανατολικά", "νοτιοανατολικά", "νότια", "νοτιοδυτικά", "δυτικά", "βορειοδυτικά"]


def bearing(frm, to):
    """Κατεύθυνση (8 σημεία) από το frm προς το to."""
    la1, lo1, la2, lo2 = map(math.radians, (*frm, *to))
    y = math.sin(lo2 - lo1) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(lo2 - lo1)
    deg = (math.degrees(math.atan2(y, x)) + 360) % 360
    return COMPASS[round(deg / 45) % 8]


def km(a, b):
    """Απόσταση σε ευθεία (χλμ) ανάμεσα σε δύο (lat, lng)."""
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def sto(acc):
    """«το Παγκράτι» → «στο Παγκράτι», «την Ηλιούπολη» → «στην Ηλιούπολη»."""
    return "σ" + acc


def build():
    out = []
    for slug, name, acc, lat, lng in AREAS:
        d = km((lat, lng), CLINIC)
        out.append(dict(slug=slug, url=f"gynaikologos-{slug}/", name=name, acc=acc, lat=lat, lng=lng,
                        municipality=MUNICIPALITY[slug], direction=bearing(CLINIC, (lat, lng)),
                        km=d, km_text="λιγότερο από 1 χλμ" if d < 1 else f"περίπου {round(d * 2) / 2:g} χλμ".replace(".", ",")))
    for a in out:
        a["near"] = sorted((b for b in out if b is not a), key=lambda b: km((a["lat"], a["lng"]), (b["lat"], b["lng"])))[:5]
    return sorted(out, key=lambda a: a["km"])


AREA_PAGES = build()
