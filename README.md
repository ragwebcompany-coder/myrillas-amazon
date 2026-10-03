# kmyrillas.gr · Prime Video theme

Αναδόμηση του [kmyrillas.gr](https://kmyrillas.gr) (WordPress) σε στατικό site με τη σχεδιαστική
γλώσσα του **Amazon Prime Video**: navy φόντο, ένα μπλε accent, κάρτες 16:9 που «ανοίγουν» panel
στο hover, περιστρεφόμενο hero, X-Ray, watchlist, προφίλ, επεισόδια.

Στατικό HTML/CSS/JS. **Καμία εξάρτηση** πέρα από Python 3 (και προαιρετικά Pillow για webp).
Το CSS είναι 44 KB, το JS 39 KB, χωρίς frameworks.

```
build.py                ← τρέξτε αυτό
lib/content.py          ταξινόμηση, κατηγορίες, Top 10, βίντεο, μαρτυρίες, βιογραφικό, χρονολόγιο
lib/ui.py               head, topbar, footer, overlays, κάρτες, σειρές, hero, επεισόδια
content/legacy.json     το κείμενο κάθε σελίδας, όπως τραβήχτηκε από το ζωντανό site (Σεπτ. 2026)
content/pages-extra.json  βιογραφικό, επικοινωνία, μαρτυρίες
content/yt-titles.json  τίτλοι βίντεο από το YouTube oEmbed
content/imgmap.json     URL εικόνας στο παλιό site → τοπικό αρχείο
content/img-src/        190 πρωτότυπες εικόνες του ιατρείου
src/assets/css/prime.css · src/assets/js/prime.js · src/assets/docs/ (τα δύο PDF)
site/                   ← ΤΟ ΠΑΡΑΔΟΤΕΟ. Ανεβάζετε αυτόν τον φάκελο.
```

## Χτίσιμο & προεπισκόπηση

```bash
python3 build.py                     # ~10 δευτερόλεπτα, 111 σελίδες (η πρώτη φορά φτιάχνει και webp)
cd site && python3 -m http.server 8877
```

## Τι περιέχει (όλα από το kmyrillas.gr)

| Τι | Πόσα | Πού |
|---|---|---|
| Υπηρεσίες / παθήσεις | 36, σε 10 κατηγορίες (όπως το μενού του ιατρείου) | `/services/<slug>/`, `/katigoria/<slug>/` |
| Άρθρα | 53 | `/<slug>/` (ίδιο URL με το WordPress), `/blog/` |
| Βίντεο | 36 από το κανάλι YouTube, σε 6 ομάδες | `/video-gallery/` |
| Μαρτυρίες | 2 | αρχική, `/testimonials/<slug>/` |
| Βιογραφικό | πλήρες κείμενο, μελέτες, χρονολόγιο, 8 δημοσιεύσεις | `/gynaikologos-dr-k-myrillas/` |
| Επικοινωνία | διεύθυνση, τηλέφωνα, ωράριο, χάρτης | `/epikinonia/` |
| Gallery | Τύπος, στιγμιότυπα βίντεο, πορτρέτα | `/photo-gallery/` |
| PDF | «Χειρουργική ελάχιστης παρέμβασης» (2) | `/assets/docs/` |

**Τα URL μένουν ίδια με το παλιό site** (services/, τα slugs των άρθρων, blog/, video-gallery/,
photo-gallery/, epikinonia/, gynaikologos-dr-k-myrillas/). Ό,τι άλλαξε έχει 301 σε `_redirects`,
`.htaccess` και `vercel.json`.

Οι 10 φωτογραφίες της παλιάς photo gallery (`kmyrillas-1…10.jpg`) **δεν υπάρχουν πια στον server**
(404 σε όλα τα μεγέθη). Αν τις έχει ο γιατρός, μπαίνουν στο `content/img-src/` και προστίθενται
στη `build_photos()`.

## Το theme, με λέξεις του Prime Video

| Prime Video | Εδώ |
|---|---|
| Ποιος παρακολουθεί; | 5 προφίλ (Εγκυμοσύνη, Γυναικολογία, Εμμηνόπαυση, Γονιμότητα, Χειρουργείο). Οι κατηγορίες του προφίλ έρχονται πρώτες στην αρχική. |
| Hero carousel | 5 διαφάνειες (οι 3 του παλιού slider + HPV + κρυοσυντήρηση), 8″ ανά διαφάνεια, παύση στο hover. |
| Included with Prime ✓ | «Στο ιατρείο ✓» |
| Top 10 | Top 10 στο ιατρείο, με τα μεγάλα νούμερα |
| Κάρτες 16:9, hover panel | κάθε θέμα: play, +λίστα, X-Ray, ενότητες, λεπτά, περίληψη |
| Επεισόδια | κάθε `<h2>` του κειμένου είναι επεισόδιο (`<details>`), με διάρκεια ανάγνωσης και ✓ όταν διαβαστεί |
| Continue watching | «Συνεχίστε την ανάγνωση»: από την πρόοδο των επεισοδίων, στη συσκευή |
| Trailer | το βίντεο του ιατρείου για το θέμα (YouTube facade, τίποτα δεν φορτώνει πριν το πάτημα) |
| X-Ray | πλαϊνό panel: είδος, κατηγορία, ενότητες, βίντεο, σχετικά, ο γιατρός, ραντεβού |
| Watchlist | «Η λίστα μου», localStorage, σελίδα `/i-lista-mou/` |
| Search | ⌘K / Ctrl+K palette σε θέματα, άρθρα, βίντεο, εντολές· ελληνικά χωρίς τόνους |
| Channels | «Δείτε επίσης»: LVRI Athens, Forever Skin Laser |
| Reviews | «Είπαν για εμάς» με αστέρια |
| Recommended for you | «Τι με αφορά;» οδηγός δύο βημάτων (`/odigos/`), πλοήγηση όχι διάγνωση |

Γραμματοσειρά **Manrope** (Google Fonts, με ελληνικά), non-blocking. Χρώματα στο `:root` του CSS.

## Τι μένει στη συσκευή

Προφίλ, λίστα, πρόοδος ανάγνωσης, διακόπτης κίνησης, το «Εντάξει» του σημειώματος. Όλα σε
`localStorage`, τίποτα δεν αποστέλλεται. Διαγράφονται από το εικονίδιο προφίλ.

Η φόρμα ραντεβού **συνθέτει email** προς `web@kmyrillas.gr`: δεν υπάρχει server. Αν θέλετε
φόρμα που στέλνεται απευθείας, χρειάζεται endpoint (π.χ. Formspree) στο `booking()` του JS.

## SEO

- Ίδια URL με το WordPress, canonical, sitemap.xml, robots.txt, 404.
- JSON-LD: `Physician` + `MedicalBusiness` (ωράριο, geo, μέλος εταιρειών, υπηρεσίες), `MedicalWebPage`
  με `MedicalCondition`/`MedicalProcedure` και `VideoObject` ανά θέμα, `Article`, `BreadcrumbList`,
  `ContactPage`, `Review`, `ItemList` βίντεο.
- Τα meta descriptions του παλιού site διατηρούνται (καθαρισμένα από «Κλείστε ραντεβού»).
- Open Graph εικόνα ανά σελίδα, geo meta, `og-default.jpg`.
- Αρχική: ένα `<h1>` με «Γυναικολόγος – Μαιευτήρας Χειρουργός στην Αθήνα» και τοπικό κείμενο (Βύρωνας και γύρω περιοχές)·
  οι τίτλοι του carousel είναι `<h2>`.
- `FAQPage` σε 33 υπηρεσίες από το `content/faq.json` (οι ερωτήσεις του schema του παλιού site, 149 συνολικά).
- Τα 4 άρθρα-δίδυμα (`ARTICLE_TWIN`) έχουν canonical στη σελίδα υπηρεσίας και δεν μπαίνουν στο sitemap.
- `Physician`: `areaServed`, `contactPoint`, `alumniOf`, `hasCredential`· `ProfilePage` στο βιογραφικό· εικόνες στο sitemap.
- Διορθώσεις τίτλων/περιγραφών: `SEO_TITLE`, `SEO_META`, `ARTICLE_SEO_TITLE` στο `lib/content.py`.

## Ποιότητα

- 111 σελίδες, 0 σπασμένοι εσωτερικοί σύνδεσμοι, 0 αναφορές σε εικόνες του παλιού server, 0 σφάλματα JS.
- Χωρίς JavaScript: όλο το κείμενο, οι σύνδεσμοι, τα επεισόδια (`<details>`) και οι σειρές λειτουργούν.
- Skip link, focus trap στα modals, ARIA στα tabs/carousel, `prefers-reduced-motion` + διακόπτης κίνησης.
- Οι εικόνες σερβίρονται webp με fallback και `loading="lazy"`.

## Πριν τη δημοσίευση

1. Ελέγξτε ωράριο και τηλέφωνα στο `lib/content.py` → `SITE`.
2. Το ωράριο Δευ/Τετ/Πεμ 17:00–21:30 προέρχεται από τα sidebar των παλιών σελίδων.
3. Αν υπάρχουν οι φωτογραφίες της gallery, προσθέστε τις (βλ. πάνω).
4. Ανεβάστε το `site/`, επιβεβαιώστε τα 301, δηλώστε ξανά το sitemap στο Search Console.
