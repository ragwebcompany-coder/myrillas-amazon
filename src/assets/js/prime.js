/* =============================================================
   KMYRILLAS.GR · Prime Video theme runtime
   Vanilla JS, no dependencies. Everything stays on the device.
   ============================================================= */
(function () {
"use strict";
var D = document, W = window, root = D.documentElement;
var $ = function (s, c) { return (c || D).querySelector(s); };
var $$ = function (s, c) { return Array.prototype.slice.call((c || D).querySelectorAll(s)); };
var depth = +(D.body.dataset.depth || 0);
var base = D.body.dataset.base || (depth ? new Array(depth + 1).join("../") : "");
var reduced = W.matchMedia("(prefers-reduced-motion: reduce)").matches;

var K = { list: "prime:list", prog: "prime:progress", profile: "prime:profile", motion: "prime:motion",
          ck: "prime:ck", who: "prime:whoSeen" };
function get(k, fb) { try { var v = localStorage.getItem(k); return v == null ? fb : JSON.parse(v); } catch (e) { return fb; } }
function set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
function del(k) { try { localStorage.removeItem(k); } catch (e) {} }
function esc(s) { var d = D.createElement("div"); d.textContent = s == null ? "" : s; return d.innerHTML; }
function norm(s) {
  return (s || "").toString().toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "")
    .replace(/ς/g, "σ").replace(/[^\p{L}\p{N} ]/gu, " ").replace(/\s+/g, " ").trim();
}

/* ── toast ───────────────────────────────────────────────── */
var toastBox = $("#toast");
function toast(msg) {
  if (!toastBox) return;
  var el = D.createElement("div"); el.className = "toast__i"; el.textContent = msg; toastBox.appendChild(el);
  setTimeout(function () { el.style.transition = "opacity .35s"; el.style.opacity = "0"; setTimeout(function () { el.remove(); }, 380); }, 2400);
}

/* ── index (search + xray + continue) ─────────────────────── */
var IDX = null, idxWait = [];
function withIndex(fn) {
  if (IDX) return fn(IDX);
  idxWait.push(fn);
  if (idxWait.length > 1) return;
  fetch(base + "search-index.json").then(function (r) { return r.json(); }).then(function (j) {
    IDX = j; idxWait.forEach(function (f) { f(IDX); }); idxWait = [];
  }).catch(function () { IDX = []; idxWait.forEach(function (f) { f(IDX); }); idxWait = []; });
}
function byUrl(u) { return (IDX || []).filter(function (x) { return x.u === u; })[0]; }

/* ── prefs / motion ──────────────────────────────────────── */
var motion = get(K.motion, "on") !== "off";
function applyMotion() { if (motion) delete root.dataset.motion; else root.dataset.motion = "off"; set(K.motion, motion ? "on" : "off"); }
applyMotion();
$$("[data-pref=motion]").forEach(function (inp) {
  inp.checked = motion;
  inp.addEventListener("change", function () { motion = inp.checked; applyMotion(); toast(motion ? "Κίνηση: ναι" : "Κίνηση: όχι"); });
});
var wipe = $("[data-wipe]");
if (wipe) wipe.addEventListener("click", function () {
  Object.keys(K).forEach(function (k) { del(K[k]); }); toast("Τα τοπικά δεδομένα διαγράφηκαν");
  setTimeout(function () { location.reload(); }, 600);
});

/* ── overlays ────────────────────────────────────────────── */
var openStack = [], lastFocus = null;
function openOv(id, ctx) {
  var ov = D.getElementById(id); if (!ov) return;
  lastFocus = D.activeElement; ov.hidden = false; D.body.style.overflow = "hidden"; openStack.push(ov);
  if (id === "palette") palOpen();
  if (id === "book" && ctx && ctx.dataset.topic) { var sel = $("#bk-topic"); if (sel) sel.value = ctx.dataset.topic; }
  if (id === "who") whoMark();
  var f = ov.querySelector("input:not([type=checkbox]),select,textarea,button:not([data-close]),a[href]");
  if (f) setTimeout(function () { f.focus(); }, 60);
}
function closeOv(ov) {
  ov = ov || openStack[openStack.length - 1]; if (!ov) return;
  ov.hidden = true; openStack = openStack.filter(function (x) { return x !== ov; });
  if (!openStack.length) D.body.style.overflow = "";
  if (ov.id === "player") { var fr = $(".pl__frame", ov); if (fr) fr.innerHTML = ""; }
  if (lastFocus && lastFocus.focus) lastFocus.focus();
}
D.addEventListener("click", function (e) {
  var op = e.target.closest("[data-open]");
  if (op) { e.preventDefault(); if (op.dataset.open === "drawer") return; openOv(op.dataset.open, op); return; }
  if (e.target.closest("[data-close]") || e.target.classList.contains("ov__scrim")) { e.preventDefault(); closeOv(); }
});
D.addEventListener("keydown", function (e) {
  if (e.key === "Escape" && openStack.length) { e.preventDefault(); closeOv(); }
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
    e.preventDefault(); var pal = $("#palette"); if (pal && !pal.hidden) closeOv(pal); else openOv("palette");
  }
  if (openStack.length && e.key === "Tab") {
    var ov = openStack[openStack.length - 1];
    var f = $$('a[href],button:not([disabled]),input,select,textarea,[tabindex]:not([tabindex="-1"])', ov)
      .filter(function (el) { return el.offsetParent !== null; });
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && D.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && D.activeElement === last) { e.preventDefault(); first.focus(); }
  }
});
var drawer = $("#drawer");
if (drawer) {
  $$("[data-open='drawer']").forEach(function (b) { b.addEventListener("click", function () { drawer.hidden = false; D.body.style.overflow = "hidden"; }); });
  drawer.addEventListener("click", function (e) {
    if (e.target === drawer || e.target.closest("[data-close]") || e.target.closest("a")) { drawer.hidden = true; if (!openStack.length) D.body.style.overflow = ""; }
  });
}

/* ── topbar / progress / reveal ──────────────────────────── */
var tb = $("#topbar"), prog = $(".progress"), totop = $(".totop"), ticking = false;
function onScroll() {
  var y = W.scrollY || 0;
  if (tb) tb.dataset.atTop = y > 24 ? "0" : "1";
  var h = root.scrollHeight - W.innerHeight, p = h > 0 ? Math.min(1, y / h) : 0;
  if (prog) prog.style.setProperty("--p", p.toFixed(4));
  if (totop) totop.hidden = y < 800;
  ticking = false;
}
W.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
onScroll();
if (totop) totop.addEventListener("click", function () { W.scrollTo({ top: 0, behavior: reduced ? "auto" : "smooth" }); });
var rvs = $$(".rv");
if ("IntersectionObserver" in W && rvs.length) {
  var io = new IntersectionObserver(function (en) { en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add("is-in"); io.unobserve(x.target); } }); },
    { rootMargin: "0px 0px -6% 0px", threshold: .05 });
  rvs.forEach(function (t) { io.observe(t); });
} else rvs.forEach(function (t) { t.classList.add("is-in"); });

/* ── rows ────────────────────────────────────────────────── */
function initRow(row) {
  var track = $(".row__track", row), L = $(".row__nav--l", row), R = $(".row__nav--r", row);
  if (!track || track.dataset.ready) return;
  track.dataset.ready = "1";
  function page() { return Math.max(240, track.clientWidth * .8); }
  function sync() {
    var max = track.scrollWidth - track.clientWidth;
    if (L) L.disabled = track.scrollLeft < 8;
    if (R) R.disabled = track.scrollLeft > max - 8;
  }
  if (L) L.addEventListener("click", function () { track.scrollBy({ left: -page(), behavior: "smooth" }); });
  if (R) R.addEventListener("click", function () { track.scrollBy({ left: page(), behavior: "smooth" }); });
  track.addEventListener("scroll", function () { requestAnimationFrame(sync); }, { passive: true });
  track.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight") { e.preventDefault(); track.scrollBy({ left: page(), behavior: "smooth" }); }
    if (e.key === "ArrowLeft") { e.preventDefault(); track.scrollBy({ left: -page(), behavior: "smooth" }); }
  });
  var down = false, sx = 0, sl = 0, moved = 0;
  track.addEventListener("pointerdown", function (e) {
    if (e.pointerType === "touch" || e.target.closest(".card__hover,.ic")) return;
    down = true; moved = 0; sx = e.clientX; sl = track.scrollLeft;
  });
  W.addEventListener("pointermove", function (e) {
    if (!down) return; var dx = e.clientX - sx; moved = Math.abs(dx);
    if (moved > 4) { track.style.scrollBehavior = "auto"; track.scrollLeft = sl - dx; }
  });
  W.addEventListener("pointerup", function () {
    if (down && moved > 6) track.addEventListener("click", function k(ev) { ev.preventDefault(); ev.stopPropagation(); track.removeEventListener("click", k, true); }, true);
    down = false; track.style.scrollBehavior = "";
  });
  new ResizeObserver(sync).observe(track); sync();
}
$$("[data-row]").forEach(initRow);

/* ── watchlist ───────────────────────────────────────────── */
function listGet() { var l = get(K.list, []); return Array.isArray(l) ? l : []; }
function listHas(id) { return listGet().some(function (x) { return x.id === id; }); }
function listCount() { var n = listGet().length; $$("[data-mylist-count]").forEach(function (b) { b.textContent = n; b.hidden = !n; }); }
function syncSaves() {
  $$("[data-save]").forEach(function (b) {
    var it; try { it = JSON.parse(b.dataset.save); } catch (e) { return; }
    var on = listHas(it.id);
    b.setAttribute("aria-pressed", on ? "true" : "false");
    b.setAttribute("aria-label", (on ? "Αφαίρεση από τη λίστα μου: " : "Προσθήκη στη λίστα μου: ") + it.t);
    var lab = b.querySelector("span"); if (lab && b.classList.contains("save-inline")) lab.textContent = on ? "Στη λίστα" : "Η λίστα μου";
  });
}
D.addEventListener("click", function (e) {
  var b = e.target.closest("[data-save]"); if (!b) return;
  e.preventDefault(); e.stopPropagation();
  var item; try { item = JSON.parse(b.dataset.save); } catch (err) { return; }
  var l = listGet(), i = l.findIndex(function (x) { return x.id === item.id; });
  if (i > -1) { l.splice(i, 1); set(K.list, l); toast("Αφαιρέθηκε από τη λίστα"); }
  else { l.unshift(Object.assign({ ts: Date.now() }, item)); set(K.list, l); toast("Προστέθηκε στη λίστα σας"); }
  syncSaves(); listCount();
});
syncSaves(); listCount();

/* ── profiles: who's watching ────────────────────────────── */
var profile = get(K.profile, null);
function whoMark() { $$(".who__p").forEach(function (p) { p.classList.toggle("is-on", !!profile && p.dataset.profile === profile.id || !profile && p.dataset.profile === ""); }); }
function applyProfile() {
  var av = $("[data-profile-avatar]");
  if (av) { av.textContent = profile ? profile.name[0] : "Ε"; av.style.setProperty("--pc", profile ? profile.color : "var(--bg-4)"); }
  if (profile) root.dataset.profile = profile.id; else delete root.dataset.profile;
  var home = $("[data-home-rows]");
  if (home && profile && profile.cats) {
    var anchor = $("[data-rows-anchor]", home);
    profile.cats.slice().reverse().forEach(function (c) {
      var r = home.querySelector('[data-row-cat="' + c + '"]');
      if (r && anchor) anchor.after(r);
    });
    var hi = $("[data-profile-name]"); if (hi) hi.textContent = profile.name;
    var hiBox = $("[data-profile-hello]"); if (hiBox) hiBox.hidden = false;
  }
}
$$(".who__p").forEach(function (p) {
  p.addEventListener("click", function () {
    profile = p.dataset.profile ? { id: p.dataset.profile, name: p.dataset.name, color: p.dataset.color, cats: p.dataset.cats.split(",").filter(Boolean) } : null;
    if (profile) set(K.profile, profile); else del(K.profile);
    set(K.who, 1); applyProfile(); closeOv(); toast(profile ? "Προφίλ: " + profile.name : "Χωρίς προφίλ");
    if (profile && !D.body.classList.contains("is-home")) location.href = base;
    else W.scrollTo({ top: 0, behavior: "auto" });
  });
});
applyProfile();

/* ── hero carousel ───────────────────────────────────────── */
(function hero() {
  var h = $("[data-hero]"); if (!h) return;
  var slides = $$(".hero__slide", h), dots = $$("[data-dot]", h), cur = 0, timer = null, T = 8000;
  h.style.setProperty("--hero-t", T + "ms");
  function show(i) {
    cur = (i + slides.length) % slides.length;
    slides.forEach(function (s, j) { s.classList.toggle("is-on", j === cur); s.setAttribute("aria-hidden", j === cur ? "false" : "true"); });
    dots.forEach(function (d, j) { if (j === cur) d.setAttribute("aria-current", "true"); else d.removeAttribute("aria-current"); });
  }
  function arm() { clearTimeout(timer); if (!motion || reduced) return; timer = setTimeout(function () { show(cur + 1); arm(); }, T); }
  dots.forEach(function (d) { d.addEventListener("click", function () { show(+d.dataset.dot); arm(); }); });
  var prev = $("[data-hero-prev]", h), next = $("[data-hero-next]", h);
  if (prev) prev.addEventListener("click", function () { show(cur - 1); arm(); });
  if (next) next.addEventListener("click", function () { show(cur + 1); arm(); });
  h.addEventListener("mouseenter", function () { h.dataset.paused = "1"; clearTimeout(timer); });
  h.addEventListener("mouseleave", function () { delete h.dataset.paused; arm(); });
  h.addEventListener("focusin", function () { clearTimeout(timer); });
  var tx = 0;
  h.addEventListener("touchstart", function (e) { tx = e.touches[0].clientX; }, { passive: true });
  h.addEventListener("touchend", function (e) { var dx = e.changedTouches[0].clientX - tx; if (Math.abs(dx) > 50) { show(dx < 0 ? cur + 1 : cur - 1); arm(); } });
  D.addEventListener("visibilitychange", function () { if (D.hidden) clearTimeout(timer); else arm(); });
  show(0); arm();
})();

/* ── reading progress: episodes ──────────────────────────── */
function progGet() { var p = get(K.prog, {}); return p && typeof p === "object" ? p : {}; }
(function episodes() {
  var rootEl = $("[data-eps-root]"); if (!rootEl) return;
  var slug = rootEl.dataset.epsRoot, total = +rootEl.dataset.total || 1;
  var eps = $$(".ep", rootEl), meta = W.__PAGE || {};
  var st = progGet()[slug] || { seen: [] };
  function save() {
    var p = progGet();
    p[slug] = { seen: st.seen, total: total, t: meta.t, u: meta.u, img: meta.img, k: meta.k, ts: Date.now() };
    set(K.prog, p);
  }
  function mark(n) {
    if (st.seen.indexOf(n) > -1) return;
    st.seen.push(n); save();
    var ep = eps[n - 1]; if (ep) ep.classList.add("is-done");
    if (st.seen.length === total) toast("Το διαβάσατε ολόκληρο");
  }
  st.seen.forEach(function (n) { var ep = eps[n - 1]; if (ep) ep.classList.add("is-done"); });
  if ("IntersectionObserver" in W) {
    var seenIO = new IntersectionObserver(function (en) {
      en.forEach(function (x) {
        if (!x.isIntersecting) return;
        var ep = x.target.closest(".ep"); if (ep && ep.open) mark(+ep.dataset.ep);
      });
    }, { rootMargin: "0px 0px -20% 0px", threshold: 0 });
    eps.forEach(function (ep) {
      var b = $(".ep__body", ep); if (!b) return;
      var sentinel = D.createElement("i"); sentinel.style.cssText = "display:block;height:1px"; b.appendChild(sentinel); seenIO.observe(sentinel);
    });
  }
  $$("[data-eps]").forEach(function (b) {
    b.addEventListener("click", function () { eps.forEach(function (ep) { ep.open = b.dataset.eps === "open"; }); });
  });
  var play = $("[data-play-ep]");
  if (play) play.addEventListener("click", function (e) {
    e.preventDefault();
    var next = eps.filter(function (ep) { return st.seen.indexOf(+ep.dataset.ep) < 0; })[0] || eps[0];
    next.open = true; next.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" });
  });
  if (location.hash && /^#ep-\d+$/.test(location.hash)) { var t = $(location.hash); if (t) t.open = true; }
  save();
})();

/* progress bars on cards + continue reading row */
function paintProgress() {
  var p = progGet();
  $$("[data-card]").forEach(function (c) {
    var st = p[c.dataset.card]; var bar = $("[data-prog]", c); if (!bar) return;
    if (st && st.seen && st.seen.length && st.total) { bar.hidden = false; bar.style.setProperty("--p", (st.seen.length / st.total).toFixed(3)); }
  });
}
paintProgress();
(function continueRow() {
  var mount = $("[data-continue]"); if (!mount) return;
  var p = progGet();
  var items = Object.keys(p).map(function (k) { return Object.assign({ id: k }, p[k]); })
    .filter(function (x) { return x.seen && x.seen.length && x.seen.length < x.total && x.t; })
    .sort(function (a, b) { return b.ts - a.ts; }).slice(0, 12);
  if (!items.length) return;
  var cards = items.map(function (x) {
    var pct = x.seen.length / x.total;
    return '<article class="card" data-card="' + esc(x.u) + '"><a class="card__link" href="' + base + esc(x.u) + '">' +
      '<span class="card__img">' + (x.img ? '<img src="' + base + 'assets/img/' + esc(x.img) + '" alt="" loading="lazy">' : '<span class="poster" style="--pc:#1399FF"></span>') +
      '<span class="card__shade"></span><span class="card__cap"><span class="card__k">' + esc(x.k || "") + ' · ' + x.seen.length + ' από ' + x.total + '</span>' +
      '<span class="card__t">' + esc(x.t) + '</span></span><i class="card__prog" data-prog style="--p:' + pct.toFixed(3) + '"><b></b></i></span></a></article>';
  }).join("");
  mount.innerHTML = '<div class="wrap row__head"><div><h2 class="row__title">Συνεχίστε την ανάγνωση</h2><p class="row__sub">Από εκεί που σταματήσατε, σε αυτή τη συσκευή.</p></div>' +
    '<div class="row__nav"><button class="row__btn row__nav--l" type="button" aria-label="Προηγούμενα" tabindex="-1"><svg viewBox="0 0 24 24" width="22" height="22" fill="none"><path d="M14.5 5 8 12l6.5 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>' +
    '<button class="row__btn row__nav--r" type="button" aria-label="Επόμενα"><svg viewBox="0 0 24 24" width="22" height="22" fill="none"><path d="M9.5 5 16 12l-6.5 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button></div></div>' +
    '<div class="row__vp row__track" tabindex="0" role="list"><div class="row__track-in">' + cards + '</div></div>';
  mount.hidden = false; initRow(mount);
})();

/* ── my list page ────────────────────────────────────────── */
(function myListPage() {
  var mount = $("[data-mylist]"); if (!mount) return;
  function draw() {
    var l = listGet();
    if (!l.length) {
      mount.innerHTML = '<div class="panel"><h3>Η λίστα σας είναι άδεια</h3><p>Πατήστε το <b>+</b> σε οποιαδήποτε κάρτα και θα βρίσκεται εδώ. Μένει μόνο σε αυτή τη συσκευή.</p>' +
        '<a class="btn btn--blue" href="' + base + 'services/">Δείτε όλα τα θέματα</a></div>';
      return;
    }
    withIndex(function (idx) {
      mount.innerHTML = '<div class="grid">' + l.map(function (x) {
        var it = idx.filter(function (i) { return i.u === x.u; })[0] || {};
        return '<article class="card" data-card="' + esc(x.u) + '"><a class="card__link" href="' + base + esc(x.u) + '"><span class="card__img">' +
          (it.img ? '<img src="' + base + 'assets/img/' + esc(it.img) + '" alt="" loading="lazy">' : '<span class="poster" style="--pc:#1399FF"></span>') +
          '<span class="card__shade"></span><span class="card__cap"><span class="card__k">' + esc(it.k || "") + '</span><span class="card__t">' + esc(x.t) + '</span></span>' +
          '<i class="card__prog" data-prog hidden><b></b></i></span></a>' +
          '<p style="margin:.5rem 0 0;font-size:.85rem"><button class="linky" type="button" data-drop="' + esc(x.id) + '">Αφαίρεση</button></p></article>';
      }).join("") + "</div>";
      paintProgress();
    });
  }
  mount.addEventListener("click", function (e) {
    var d = e.target.closest("[data-drop]"); if (!d) return;
    set(K.list, listGet().filter(function (x) { return x.id !== d.dataset.drop; })); listCount(); syncSaves(); draw(); toast("Αφαιρέθηκε από τη λίστα");
  });
  draw();
})();

/* ── command palette ─────────────────────────────────────── */
var palSel = 0, palRows = [];
var ACTIONS = [
  { t: "Ζητήστε ραντεβού", s: "Άνοιγμα φόρμας", ic: "ΡΑ", act: function () { closeOv(); openOv("book"); } },
  { t: "Κλήση στο ιατρείο", s: "210 76 09 109", ic: "ΤΗ", act: function () { location.href = "tel:+302107609109"; } },
  { t: "Τι με αφορά;", s: "Οδηγός σε δύο βήματα", ic: "ΟΔ", act: function () { location.href = base + "odigos/"; } },
  { t: "Η λίστα μου", s: "Αποθηκευμένα", ic: "ΛΙ", act: function () { location.href = base + "i-lista-mou/"; } },
  { t: "Αλλαγή προφίλ", s: "Ποιος παρακολουθεί;", ic: "ΠΡ", act: function () { closeOv(); openOv("who"); } }
];
var LABEL = { service: "Θέματα", article: "Άρθρα", video: "Βίντεο", page: "Σελίδες" };
function palOpen() {
  var inp = $(".pal__in"); if (inp) { inp.value = ""; setTimeout(function () { inp.focus(); }, 40); }
  palRender(""); withIndex(function () { palRender($(".pal__in") ? $(".pal__in").value : ""); });
}
function score(q, it) {
  var t = it._t || (it._t = norm(it.t)), k = it._k || (it._k = norm((it.kw || "") + " " + (it.d || "")));
  if (t === q) return 100; if (t.indexOf(q) === 0) return 80; if (t.indexOf(q) > -1) return 60; if (k.indexOf(q) > -1) return 30;
  var parts = q.split(" ").filter(Boolean);
  if (parts.length > 1 && parts.every(function (p) { return (t + " " + k).indexOf(p) > -1; })) return 24;
  return 0;
}
function hi(text, q) {
  if (!q) return esc(text); var n = norm(text), i = n.indexOf(q); if (i < 0) return esc(text);
  return esc(text.slice(0, i)) + "<mark>" + esc(text.slice(i, i + q.length)) + "</mark>" + esc(text.slice(i + q.length));
}
function palRender(raw) {
  var box = $("#pal-res"); if (!box) return;
  var q = norm(raw), out = "", n = 0; palRows = [];
  var acts = ACTIONS.filter(function (a) { return !q || norm(a.t).indexOf(q) > -1 || norm(a.s).indexOf(q) > -1; });
  if (acts.length) {
    out += '<p class="pal__group">Εντολές</p>';
    acts.slice(0, q ? 4 : 3).forEach(function (a) {
      out += '<button class="pal__item" data-act="' + ACTIONS.indexOf(a) + '"><span class="pal__ic">' + a.ic + '</span><span class="pal__txt"><b>' + hi(a.t, q) + '</b><span>' + esc(a.s) + '</span></span></button>';
      palRows.push({ act: a }); n++;
    });
  }
  if (q && q.length > 1 && IDX && IDX.length) {
    var hits = IDX.map(function (it) { return { it: it, s: score(q, it) }; }).filter(function (x) { return x.s > 0; })
      .sort(function (a, b) { return b.s - a.s || a.it.t.length - b.it.t.length; }).slice(0, 24);
    var groups = {}, best = {};
    hits.forEach(function (x) { (groups[x.it.k] = groups[x.it.k] || []).push(x.it); best[x.it.k] = Math.max(best[x.it.k] || 0, x.s); });
    Object.keys(groups).sort(function (a, b) { return best[b] - best[a]; }).forEach(function (k) {
      out += '<p class="pal__group">' + (LABEL[k] || k) + "</p>";
      groups[k].forEach(function (it) {
        var ic = it.img ? '<img src="' + base + "assets/img/" + esc(it.img) + '" alt="" loading="lazy">' : (it.v ? '<img src="https://i.ytimg.com/vi/' + it.v + '/default.jpg" alt="">' : esc((it.t || "?").slice(0, 2).toUpperCase()));
        if (it.v) { out += '<button class="pal__item" data-video="' + it.v + '" data-vtitle="' + esc(it.t) + '"><span class="pal__ic">' + ic + '</span><span class="pal__txt"><b>' + hi(it.t, q) + '</b><span>' + esc(it.d || "") + '</span></span></button>'; palRows.push({ video: it.v, t: it.t }); }
        else { out += '<a class="pal__item" href="' + base + it.u + '"><span class="pal__ic">' + ic + '</span><span class="pal__txt"><b>' + hi(it.t, q) + '</b><span>' + esc(it.d || "") + "</span></span></a>"; palRows.push({ href: base + it.u }); }
        n++;
      });
    });
  }
  if (!n) out += '<p class="pal__empty">' + (q.length > 1 ? "Καμία αντιστοιχία." : "Γράψτε τουλάχιστον 2 χαρακτήρες ή διαλέξτε μια εντολή.") + "</p>";
  box.innerHTML = out; palSel = 0; palMark();
}
function palMark() {
  var items = $$(".pal__item", $("#pal-res"));
  items.forEach(function (el, i) { el.classList.toggle("is-sel", i === palSel); });
  if (items[palSel]) items[palSel].scrollIntoView({ block: "nearest" });
}
var palIn = $(".pal__in");
if (palIn) {
  palIn.addEventListener("input", function () { palRender(palIn.value); });
  palIn.addEventListener("keydown", function (e) {
    var items = $$(".pal__item", $("#pal-res"));
    if (e.key === "ArrowDown") { e.preventDefault(); palSel = Math.min(items.length - 1, palSel + 1); palMark(); }
    if (e.key === "ArrowUp") { e.preventDefault(); palSel = Math.max(0, palSel - 1); palMark(); }
    if (e.key === "Enter") {
      e.preventDefault(); var r = palRows[palSel]; if (!r) return;
      if (r.act) r.act.act(); else if (r.video) { closeOv(); playVideo(r.video, r.t); } else location.href = r.href;
    }
  });
}
var palRes = $("#pal-res");
if (palRes) palRes.addEventListener("click", function (e) {
  var b = e.target.closest("[data-act]"); if (b) { e.preventDefault(); ACTIONS[+b.dataset.act].act(); }
});

/* ── video player (facade) ───────────────────────────────── */
function playVideo(id, title) {
  var frame = $(".pl__frame"); if (!frame) return;
  frame.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0&hl=el" title="' + esc(title || "Βίντεο") +
    '" allow="accelerometer;autoplay;encrypted-media;gyroscope;picture-in-picture" allowfullscreen></iframe>';
  var t = $(".pl__t"); if (t) t.textContent = title || "";
  var pl = $("#player"); if (pl && pl.hidden) openOv("player");
}
D.addEventListener("click", function (e) {
  var b = e.target.closest("[data-video]"); if (!b) return;
  e.preventDefault(); e.stopPropagation(); playVideo(b.dataset.video, b.dataset.vtitle);
});

/* ── X-Ray ───────────────────────────────────────────────── */
D.addEventListener("click", function (e) {
  var b = e.target.closest("[data-xray]"); if (!b) return;
  e.preventDefault(); e.stopPropagation();
  var u = b.dataset.xray;
  withIndex(function (idx) {
    var it = idx.filter(function (i) { return i.u === u; })[0];
    var title = $(".xr__t"), body = $(".xr__body");
    if (!title || !body) return;
    if (!it) { title.textContent = "X-Ray"; body.innerHTML = "<p>Δεν βρέθηκαν στοιχεία.</p>"; openOv("xray"); return; }
    var x = it.x || {};
    var h = "";
    if (it.img) h += '<img src="' + base + "assets/img/" + esc(it.img) + '" alt="">';
    h += "<p>" + esc(it.d || "") + "</p>";
    var facts = (x.facts || []).map(function (f) { return "<li><span style=\"color:var(--dim);display:inline-block;min-width:9.5em\">" + esc(f[0]) + "</span> " + esc(f[1]) + "</li>"; }).join("");
    if (facts) h += "<h3>Με μια ματιά</h3><ul>" + facts + "</ul>";
    if (x.eps && x.eps.length) h += "<h3>Επεισόδια</h3><ul>" + x.eps.map(function (t, i) { return '<li><a href="' + base + it.u + "#ep-" + (i + 1) + '">' + (i + 1) + ". " + esc(t) + "</a></li>"; }).join("") + "</ul>";
    if (x.videos && x.videos.length) h += "<h3>Βίντεο</h3><ul>" + x.videos.map(function (v) { return '<li><a href="#" data-video="' + v[0] + '" data-vtitle="' + esc(v[1]) + '">▶ ' + esc(v[1]) + "</a></li>"; }).join("") + "</ul>";
    if (x.rel && x.rel.length) h += "<h3>Σχετικά</h3><ul>" + x.rel.map(function (r) { return '<li><a href="' + base + r[0] + '">' + esc(r[1]) + "</a></li>"; }).join("") + "</ul>";
    title.textContent = it.t; body.innerHTML = h;
    var xr = $("#xray"); if (xr && xr.hidden) openOv("xray");
  });
});

/* ── tabs ────────────────────────────────────────────────── */
$$("[data-tabs]").forEach(function (t) {
  var btns = $$(".tabs__b", t), panels = $$(".tabs__p", t);
  btns.forEach(function (b) {
    b.addEventListener("click", function () {
      btns.forEach(function (x) { x.classList.toggle("is-on", x === b); x.setAttribute("aria-selected", x === b ? "true" : "false"); });
      panels.forEach(function (p) { p.classList.toggle("is-on", p.id === b.getAttribute("aria-controls")); });
      $$("[data-row]", t).forEach(initRow);
    });
  });
});

/* ── booking (mailto composer) ───────────────────────────── */
(function booking() {
  var form = $(".bk__form"); if (!form) return;
  var dateI = $("#bk-date"), timeI = $("#bk-time"), closed = $("[data-closed]");
  var today = new Date(); today.setHours(0, 0, 0, 0);
  if (dateI) dateI.min = today.toISOString().slice(0, 10);
  function slots() {
    if (!dateI || !timeI) return;
    var v = dateI.value; timeI.innerHTML = '<option value="">Επιλέξτε ώρα</option>'; if (!v) return;
    var day = new Date(v + "T00:00:00").getDay(), open = day === 1 || day === 3 || day === 4;
    if (closed) closed.classList.toggle("is-on", !open);
    for (var t = 17; t <= 21; t += .5) {
      var hh = Math.floor(t), mm = t % 1 ? "30" : "00", o = D.createElement("option");
      o.value = o.textContent = hh + ":" + mm; timeI.appendChild(o);
    }
  }
  if (dateI) dateI.addEventListener("change", slots);
  form.addEventListener("submit", function (e) {
    e.preventDefault(); var ok = true;
    ["name", "phone"].forEach(function (n) { var el = form.elements[n], bad = !el.value.trim(); el.parentElement.classList.toggle("is-bad", bad); if (bad) ok = false; });
    var consent = form.elements.consent; $(".err--consent").classList.toggle("is-on", !consent.checked); if (!consent.checked) ok = false;
    if (!ok) { toast("Ελέγξτε τα σημειωμένα πεδία"); return; }
    var f = form.elements, lines = ["Ονοματεπώνυμο: " + f.name.value.trim(), "Τηλέφωνο: " + f.phone.value.trim(),
      f.email.value.trim() ? "Email: " + f.email.value.trim() : "", "Θέμα: " + (f.topic.value || "δεν είμαι σίγουρη"),
      f.date.value ? "Προτίμηση: " + f.date.value + (f.time.value ? " " + f.time.value : "") : "", "", f.note.value.trim()].filter(Boolean).join("\n");
    location.href = "mailto:web@kmyrillas.gr?subject=" + encodeURIComponent("Αίτημα ραντεβού: " + f.name.value.trim()) + "&body=" + encodeURIComponent(lines);
    toast("Ανοίγει το πρόγραμμα email σας");
  });
})();

/* ── guide: τι με αφορά ──────────────────────────────────── */
(function guide() {
  var g = $("[data-guide]"); if (!g) return;
  var data; try { data = JSON.parse($("#guide-data").textContent); } catch (e) { return; }
  var stage = $("[data-guide-stage]", g), res = $("[data-guide-res]", g);
  function step1() {
    res.innerHTML = "";
    stage.innerHTML = '<p class="row__sub">Βήμα 1 από 2. Τι σας φέρνει εδώ;</p><div class="guide__steps">' + data.cats.map(function (c) {
      return '<button class="guide__opt" type="button" data-c="' + c.slug + '"><b>' + esc(c.title) + "</b><span>" + esc(c.blurb) + "</span></button>";
    }).join("") + "</div>";
  }
  function step2(slug) {
    var c = data.cats.filter(function (x) { return x.slug === slug; })[0]; if (!c) return;
    stage.innerHTML = '<p class="row__sub">Βήμα 2 από 2. ' + esc(c.title) + ': ποιο σας μοιάζει πιο πολύ; <button class="linky" type="button" data-back>Πίσω</button></p><div class="guide__steps">' +
      c.items.map(function (s) { return '<button class="guide__opt" type="button" data-s="' + s.u + '"><b>' + esc(s.t) + "</b><span>" + esc(s.d) + "</span></button>"; }).join("") + "</div>";
  }
  function result(u, slug) {
    var c = data.cats.filter(function (x) { return x.slug === slug; })[0]; var it = c.items.filter(function (s) { return s.u === u; })[0];
    stage.innerHTML = '<p class="row__sub">Αυτό σας ταιριάζει περισσότερο. <button class="linky" type="button" data-restart>Από την αρχή</button></p>';
    res.innerHTML = '<div class="panel"><h3>Προτείνεται</h3><h2 style="margin-bottom:.4em"><a href="' + base + it.u + '">' + esc(it.t) + "</a></h2><p>" + esc(it.d) + '</p>' +
      '<div style="display:flex;gap:.5rem;flex-wrap:wrap"><a class="btn btn--blue" href="' + base + it.u + '">Δείτε</a><button class="btn btn--ghost" type="button" data-open="book" data-topic="' + esc(it.t) + '">Ραντεβού</button></div></div>' +
      (c.items.length > 1 ? '<h3 style="margin-top:1.4rem">Στην ίδια κατηγορία</h3><ul class="chips">' + c.items.filter(function (s) { return s.u !== u; }).map(function (s) { return '<li><a class="chip" href="' + base + s.u + '">' + esc(s.t) + "</a></li>"; }).join("") + "</ul>" : "") +
      '<p class="row__sub" style="margin-top:1.2rem">Αυτό είναι πλοήγηση, όχι διάγνωση. Ο υπολογισμός έγινε στη συσκευή σας.</p>';
  }
  var curCat = null;
  g.addEventListener("click", function (e) {
    var b = e.target.closest("[data-c],[data-s],[data-back],[data-restart]"); if (!b) return;
    if (b.dataset.c) { curCat = b.dataset.c; step2(curCat); }
    else if (b.dataset.s) { result(b.dataset.s, curCat); }
    else step1();
  });
  step1();
})();

/* ── filters: blog / videos / hub grids ──────────────────── */
(function filters() {
  var box = $("[data-filter]"); if (!box) return;
  var q = $("[data-filter-q]", box), chips = $$("[data-filter-tag]", box), grid = $("[data-filter-grid]", box), empty = $("[data-filter-empty]", box), tag = "all";
  function run() {
    var v = norm(q ? q.value : ""), shown = 0;
    $$("[data-item]", grid).forEach(function (c) {
      var okT = tag === "all" || c.dataset.tag === tag, okQ = !v || norm(c.dataset.text || c.textContent).indexOf(v) > -1;
      c.hidden = !(okT && okQ); if (!c.hidden) shown++;
    });
    $$("[data-group]", grid).forEach(function (g) { g.hidden = !$$("[data-item]:not([hidden])", g).length; });
    if (empty) empty.hidden = shown > 0;
  }
  if (q) q.addEventListener("input", run);
  chips.forEach(function (c) { c.addEventListener("click", function () { chips.forEach(function (x) { x.classList.toggle("is-on", x === c); }); tag = c.dataset.filterTag; run(); }); });
})();

/* ── lightbox ────────────────────────────────────────────── */
(function lightbox() {
  var items = $$("[data-lb]"); if (!items.length) return;
  var ov = D.createElement("div"); ov.className = "ov ov--full"; ov.id = "lightbox"; ov.hidden = true;
  ov.innerHTML = '<div class="ov__scrim" data-close></div><figure class="lb" role="dialog" aria-modal="true" aria-label="Φωτογραφία"><button class="ov__x" type="button" data-close aria-label="Κλείσιμο"><svg viewBox="0 0 24 24" width="18" height="18" fill="none"><path d="m6 6 12 12M18 6 6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button><img alt=""><figcaption></figcaption></figure>';
  D.body.appendChild(ov);
  var img = $("img", ov), cap = $("figcaption", ov), cur = 0;
  function open(i) { cur = (i + items.length) % items.length; img.src = items[cur].dataset.lb; img.alt = items[cur].dataset.alt || ""; cap.textContent = (cur + 1) + " / " + items.length + (items[cur].dataset.cap ? " · " + items[cur].dataset.cap : ""); if (ov.hidden) openOv("lightbox"); }
  items.forEach(function (b, i) { b.addEventListener("click", function () { open(i); }); });
  D.addEventListener("keydown", function (e) { if (ov.hidden) return; if (e.key === "ArrowLeft") open(cur - 1); if (e.key === "ArrowRight") open(cur + 1); });
})();

/* ── opening hours: today ────────────────────────────────── */
(function hours() {
  var rows = $$("[data-day]"); if (!rows.length) return;
  var d = new Date().getDay();
  rows.forEach(function (r) { if (+r.dataset.day === d) r.classList.add("is-open"); });
})();

/* ── cookie note ─────────────────────────────────────────── */
(function cookie() {
  var bar = $("#cookie"); if (!bar || get(K.ck, null)) return;
  setTimeout(function () { bar.hidden = false; }, 1600);
  $$("[data-ck]", bar).forEach(function (b) { b.addEventListener("click", function () { set(K.ck, 1); bar.hidden = true; }); });
})();

/* ── share / print ───────────────────────────────────────── */
D.addEventListener("click", function (e) {
  var s = e.target.closest("[data-share]"); if (s) {
    e.preventDefault(); var data = { title: D.title, url: location.href };
    if (navigator.share) navigator.share(data).catch(function () {});
    else if (navigator.clipboard) navigator.clipboard.writeText(location.href).then(function () { toast("Ο σύνδεσμος αντιγράφηκε"); });
  }
  var p = e.target.closest("[data-print]"); if (p) { e.preventDefault(); $$(".ep").forEach(function (ep) { ep.open = true; }); W.print(); }
});

/* ── view transitions ────────────────────────────────────── */
if (D.startViewTransition && !reduced && motion) {
  D.addEventListener("click", function (e) {
    var a = e.target.closest("a[href]");
    if (!a || a.target || a.hasAttribute("download") || e.metaKey || e.ctrlKey || e.shiftKey || a.closest("[data-video],[data-xray]")) return;
    var u = new URL(a.href, location.href);
    if (u.origin !== location.origin || u.pathname === location.pathname || u.hash) return;
    e.preventDefault(); D.startViewTransition(function () { location.href = a.href; });
  });
}
})();
