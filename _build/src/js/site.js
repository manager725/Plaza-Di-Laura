/* Plaza Di Laura */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement;
  window.__pdlReady = true;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
    sget: function (k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
    sset: function (k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }
  };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };

  /* ---------- Language ---------- */
  var lang = root.getAttribute("data-lang") === "en" ? "en" : "sv";
  function L(o) { if (o == null) return ""; if (typeof o === "string") return o; return o[lang] != null ? o[lang] : o.sv; }
  var ATTRS = [["data-en-ph", "placeholder"], ["data-en-aria", "aria-label"], ["data-en-alt", "alt"], ["data-en-title", "title"], ["data-en-content", "content"], ["data-en-href", "href"]];
  function applyLang(next, initial) {
    lang = next;
    root.setAttribute("lang", next === "en" ? "en" : "sv");
    root.setAttribute("data-lang", next);
    $$("[data-en]").forEach(function (el) {
      if (!el.hasAttribute("data-sv")) el.setAttribute("data-sv", el.innerHTML);
      el.innerHTML = next === "en" ? el.getAttribute("data-en") : el.getAttribute("data-sv");
    });
    ATTRS.forEach(function (pair) {
      $$("[" + pair[0] + "]").forEach(function (el) {
        var keep = "data-sv-" + pair[1];
        if (!el.hasAttribute(keep)) el.setAttribute(keep, el.getAttribute(pair[1]) || "");
        el.setAttribute(pair[1], next === "en" ? el.getAttribute(pair[0]) : el.getAttribute(keep));
      });
    });
    var t = next === "en" ? root.getAttribute("data-title-en") : root.getAttribute("data-title-sv");
    if (t) doc.title = t;
    $$(".lang-switch button").forEach(function (b) { b.setAttribute("aria-pressed", String(b.value === next)); });
    if (!initial) doc.dispatchEvent(new CustomEvent("pdl:lang"));
  }
  $$("[data-en]").forEach(function (el) { if (!el.hasAttribute("data-sv")) el.setAttribute("data-sv", el.innerHTML); });
  if (!root.getAttribute("data-title-sv")) root.setAttribute("data-title-sv", doc.title);
  if (lang === "en") applyLang("en", true);
  root.classList.remove("i18n-pending");
  $$(".lang-switch button").forEach(function (b) {
    b.setAttribute("aria-pressed", String(b.value === lang));
    b.addEventListener("click", function () { if (b.value === lang) return; store.set("pdl-lang", b.value); applyLang(b.value); });
  });

  /* ---------- Theme ---------- */
  $$(".theme-btn").forEach(function (b) {
    b.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      var apply = function () {
        root.setAttribute("data-theme", next);
        store.set("pdl-theme", next);
        $$(".theme-btn").forEach(function (x) { x.setAttribute("aria-pressed", String(next === "dark")); });
      };
      // Snapshot-based reveal where supported; otherwise switch instantly (never animate every element's colour).
      if (reduce || !doc.startViewTransition) { apply(); return; }
      var r = b.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
      root.style.setProperty("--tx", x + "px");
      root.style.setProperty("--ty", y + "px");
      root.style.setProperty("--tr", Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y)) + "px");
      root.classList.add("theme-vt");
      var vt = doc.startViewTransition(apply);
      vt.finished.finally(function () { root.classList.remove("theme-vt"); });
    });
    b.setAttribute("aria-pressed", String(root.getAttribute("data-theme") === "dark"));
  });

  /* ---------- Loader ----------
     Counts real progress (fonts plus the images the page loads eagerly), never shorter than
     MIN or longer than MAX, then lifts as a two-layer curtain. Entrances wait for it via onIntro. */
  var introWaiters = [];
  var onIntro = function (fn) { if (root.classList.contains("loader-hold")) introWaiters.push(fn); else fn(); };
  (function () {
    if (!root.classList.contains("has-loader")) return;
    var lo = $(".loader");
    var release = function () {
      if (!root.classList.contains("loader-hold")) return;
      root.classList.remove("loader-hold");
      introWaiters.splice(0).forEach(function (fn) { fn(); });
    };
    if (!lo) { root.classList.remove("has-loader"); release(); return; }
    store.sset("pdl-intro", "1");
    var countEl = $("[data-loader-count]", lo), bar = $(".loader__bar", lo);
    var MIN = 1700, MAX = 4200, t0 = performance.now(), shown = 0, leaving = false;
    var imgs = $$("img").filter(function (im) { return im.loading !== "lazy" && !lo.contains(im); });
    var total = imgs.length + 1, got = 0, pageLoaded = false;
    var bump = function () { got = Math.min(total, got + 1); };
    imgs.forEach(function (im) {
      if (im.complete) bump(); else { im.addEventListener("load", bump, { once: true }); im.addEventListener("error", bump, { once: true }); }
    });
    if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(bump, bump); else bump();
    window.addEventListener("load", function () { pageLoaded = true; }, { once: true });
    var leave = function () {
      if (leaving) return;
      leaving = true;
      root.classList.add("loader-exit");
      setTimeout(release, 360);
      setTimeout(function () { root.classList.remove("has-loader", "loader-exit"); }, 1400);
    };
    var tick = function (now) {
      if (leaving) return;
      var el = now - t0;
      var real = pageLoaded ? 1 : got / total;
      var goal = Math.min(el / MIN, el > MAX ? 1 : real);
      shown += (goal - shown) * 0.14;
      if (goal >= 1 && shown > 0.994) shown = 1;
      var pct = Math.round(shown * 100);
      if (countEl) countEl.textContent = pct;
      if (bar) bar.style.setProperty("--lp", shown.toFixed(3));
      if (shown >= 1) setTimeout(leave, 180); else requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    // Any intent to use the page skips straight to the curtain.
    ["pointerdown", "keydown", "wheel", "touchstart"].forEach(function (ev) {
      window.addEventListener(ev, leave, { once: true, passive: true });
    });
  })();

  /* ---------- Images fade-in surface ---------- */
  $$("img").forEach(function (img) {
    var mark = function () { img.classList.add("is-loaded"); };
    if (img.complete && img.naturalWidth) mark(); else img.addEventListener("load", mark, { once: true });
  });

  /* ---------- Header ---------- */
  var header = $(".site-header");
  var mbar = $(".mbar"), totop = $(".totop");
  var onScroll = function () {
    var y = window.scrollY || 0;
    if (header) {
      header.classList.toggle("is-scrolled", y > 8);
      var max = doc.documentElement.scrollHeight - window.innerHeight;
      header.style.setProperty("--p", max > 0 ? Math.min(1, y / max).toFixed(4) : 0);
    }
    if (mbar) mbar.classList.toggle("is-visible", y > window.innerHeight * 0.5);
    if (totop) totop.classList.toggle("is-visible", y > window.innerHeight * 2);
  };
  var ticking = false;
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(function () { onScroll(); ticking = false; }); } }, { passive: true });
  onScroll();
  if (totop) totop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); var b = $(".brand-link"); b && b.focus({ preventScroll: true }); });

  // Mega menus
  var megaTriggers = $$("[data-mega]");
  var openMega = null, megaTimer = null;
  function closeMega(focusBack) {
    if (!openMega) return;
    var t = openMega;
    t.setAttribute("aria-expanded", "false");
    var p = doc.getElementById(t.getAttribute("aria-controls"));
    if (p) p.classList.remove("is-open");
    openMega = null;
    if (focusBack) t.focus();
  }
  function showMega(t) {
    if (openMega === t) return;
    closeMega(false);
    t.setAttribute("aria-expanded", "true");
    var p = doc.getElementById(t.getAttribute("aria-controls"));
    if (p) p.classList.add("is-open");
    openMega = t;
  }
  megaTriggers.forEach(function (t) {
    var panel = doc.getElementById(t.getAttribute("aria-controls"));
    t.addEventListener("click", function (e) { e.preventDefault(); if (openMega === t) closeMega(false); else showMega(t); });
    if (window.matchMedia("(hover: hover)").matches) {
      var enter = function () { clearTimeout(megaTimer); megaTimer = setTimeout(function () { showMega(t); }, 90); };
      var leave = function () { clearTimeout(megaTimer); megaTimer = setTimeout(function () { if (openMega === t) closeMega(false); }, 180); };
      t.parentNode.addEventListener("mouseenter", enter);
      t.parentNode.addEventListener("mouseleave", leave);
      if (panel) { panel.addEventListener("mouseenter", function () { clearTimeout(megaTimer); }); panel.addEventListener("mouseleave", leave); }
    }
    if (panel) panel.addEventListener("focusout", function (e) { if (!panel.contains(e.relatedTarget) && e.relatedTarget !== t) closeMega(false); });
  });
  doc.addEventListener("click", function (e) { if (openMega && !e.target.closest(".mega") && !e.target.closest("[data-mega]")) closeMega(false); });

  // Drawer
  var drawer = $(".drawer"), burger = $(".nav__burger"), lastFocus = null;
  function trap(container, e) {
    var f = $$('a[href], button:not([disabled]), input:not([disabled]), select, textarea, summary, [tabindex]:not([tabindex="-1"])', container).filter(function (x) { return x.offsetParent !== null || x === doc.activeElement; });
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && doc.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && doc.activeElement === last) { e.preventDefault(); first.focus(); }
  }
  function setDrawer(open) {
    if (!drawer) return;
    drawer.classList.toggle("is-open", open);
    drawer.setAttribute("aria-hidden", String(!open));
    if (open) { drawer.removeAttribute("inert"); } else { drawer.setAttribute("inert", ""); }
    burger && burger.setAttribute("aria-expanded", String(open));
    doc.body.classList.toggle("is-locked", open);
    if (open) { lastFocus = doc.activeElement; var c = $(".drawer__close", drawer); c && c.focus(); }
    else if (lastFocus) { lastFocus.focus(); }
  }
  if (drawer) {
    drawer.setAttribute("inert", "");
    burger && burger.addEventListener("click", function () { setDrawer(true); });
    $(".drawer__close", drawer).addEventListener("click", function () { setDrawer(false); });
    drawer.addEventListener("keydown", function (e) { if (e.key === "Tab") trap(drawer, e); });
    $$("a", drawer).forEach(function (a) { a.addEventListener("click", function () { setDrawer(false); }); });
  }
  doc.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (lb && !lb.hidden) return;
    if (drawer && drawer.classList.contains("is-open")) setDrawer(false);
    else if (openMega) closeMega(true);
    else if (chat && chat.classList.contains("is-open")) setChat(false);
  });

  /* ---------- Reveal ---------- */
  if (root.classList.contains("reveal-on") && "IntersectionObserver" in window) {
    var groups = new Map();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        (en.target.__rv || [en.target]).forEach(function (x) { x.classList.add("is-in"); });
        io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.02 });
    $$(".rv").forEach(function (el) {
      var p = el.parentElement, i = groups.get(p) || 0;
      groups.set(p, i + 1);
      if (i > 0 && i < 6) el.style.setProperty("--d", (i * 70) + "ms");
      // Curtain-clipped elements have no visible area, so watch their parent instead.
      var target = el.classList.contains("rv-clip") ? p : el;
      target.__rv = (target.__rv || []).concat(el);
      onIntro(function () { io.observe(target); });
    });
  } else {
    root.classList.remove("reveal-on");
  }

  /* ---------- Treatment list preview ---------- */
  var preview = $(".tlist__preview");
  if (preview) {
    var figs = $$("figure", preview), curFig = 0;
    $$(".tlist__row a").forEach(function (a, i) {
      var act = function () {
        if (i === curFig) return;
        figs.forEach(function (f) { f.classList.remove("is-prev"); });
        figs[curFig].classList.remove("is-active");
        figs[curFig].classList.add("is-prev");
        void figs[i].offsetWidth;
        figs[i].classList.add("is-active");
        curFig = i;
      };
      a.addEventListener("mouseenter", act);
      a.addEventListener("focus", act);
    });
  }

  /* ---------- Results: filters, track, lightbox ---------- */
  $$("[data-filter-group]").forEach(function (group) {
    var scope = doc.getElementById(group.getAttribute("data-filter-group"));
    if (!scope) return;
    $$(".filter", group).forEach(function (btn) {
      btn.addEventListener("click", function () {
        $$(".filter", group).forEach(function (b) { b.setAttribute("aria-pressed", String(b === btn)); });
        var f = btn.value;
        $$(".rcard", scope).forEach(function (c) { c.hidden = !(f === "all" || c.getAttribute("data-cat") === f); });
        if (scope.classList.contains("rtrack")) scope.scrollTo({ left: 0, behavior: reduce ? "auto" : "smooth" });
        var live = group.parentNode.querySelector(".filter-count");
        if (live) {
          var n = $$(".rcard", scope).filter(function (c) { return !c.hidden; }).length;
          live.textContent = lang === "en" ? n + " results shown" : n + " resultat visas";
        }
      });
    });
  });
  $$("[data-track-prev], [data-track-next]").forEach(function (b) {
    b.addEventListener("click", function () {
      var tr = doc.getElementById(b.getAttribute("data-track-prev") || b.getAttribute("data-track-next"));
      if (!tr) return;
      var card = $(".rcard:not([hidden])", tr), step = card ? card.getBoundingClientRect().width + 14 : 300;
      tr.scrollBy({ left: b.hasAttribute("data-track-next") ? step : -step, behavior: reduce ? "auto" : "smooth" });
    });
  });
  var lb = $(".lb"), lbItems = [], lbIndex = 0, lbOpener = null;
  function lbShow(i) {
    lbIndex = (i + lbItems.length) % lbItems.length;
    var it = lbItems[lbIndex], img = $(".lb__stage img", lb);
    img.src = it.getAttribute("data-full");
    img.alt = it.querySelector("img").alt;
    $(".lb__cap", lb).textContent = it.getAttribute(lang === "en" ? "data-cap-en" : "data-cap-sv");
    $(".lb__count", lb).textContent = (lbIndex + 1) + " / " + lbItems.length;
  }
  function lbOpen(btn) {
    var scope = btn.closest("[data-gallery]");
    lbItems = $$(".rcard:not([hidden]) button", scope);
    lbOpener = btn;
    lb.hidden = false;
    doc.body.classList.add("is-locked");
    lbShow(lbItems.indexOf(btn));
    $(".lb__close", lb).focus();
  }
  function lbClose() { lb.hidden = true; doc.body.classList.remove("is-locked"); if (lbOpener) lbOpener.focus(); }
  if (lb) {
    $$("[data-gallery] .rcard button").forEach(function (b) { b.addEventListener("click", function () { lbOpen(b); }); });
    $(".lb__close", lb).addEventListener("click", lbClose);
    $(".lb__side--prev", lb).addEventListener("click", function () { lbShow(lbIndex - 1); });
    $(".lb__side--next", lb).addEventListener("click", function () { lbShow(lbIndex + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb || e.target.classList.contains("lb__stage")) lbClose(); });
    lb.addEventListener("keydown", function (e) {
      if (e.key === "Escape") lbClose();
      else if (e.key === "ArrowLeft") lbShow(lbIndex - 1);
      else if (e.key === "ArrowRight") lbShow(lbIndex + 1);
      else if (e.key === "Tab") trap(lb, e);
    });
    var sx = null;
    lb.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) { if (sx == null) return; var dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 50) lbShow(lbIndex + (dx < 0 ? 1 : -1)); sx = null; });
    doc.addEventListener("pdl:lang", function () { if (!lb.hidden) lbShow(lbIndex); });
  }

  /* ---------- Brynguiden ---------- */
  var guide = $("[data-guide]");
  if (guide) {
    var G = {
      next: { sv: "Nästa", en: "Next" }, back: { sv: "Tillbaka", en: "Back" }, show: { sv: "Visa rekommendation", en: "Show my recommendation" },
      why: {
        bad: { sv: "LIFT Ink Removal är särskilt effektiv för felaktig microblading, missfärgade bryn (grå, blå eller röda toner) och ojämn eller för mörk permanent makeup.", en: "LIFT Ink Removal is especially effective for poor microblading, discoloured brows (grey, blue or red tones) and uneven or too-dark permanent makeup." },
        badNext: { sv: "Är du osäker och har frågor är du välkommen att boka en kostnadsfri konsultation, på plats, per telefon eller via Zoom.", en: "If you are unsure or have questions, you are welcome to book a free consultation, in person, by phone or on Zoom." },
        old: { sv: "Microblading passar inte över en gammal maskintatuering.", en: "Microblading is not suitable over an old machine tattoo." },
        oily: { sv: "På grund av fet hy flyter stråna ut och blir till fläckar.", en: "With oily skin the strokes spread and turn into patches." },
        few: { sv: "Med väldigt lite egna brynhår får de intatuerade stråna inget skydd och nöts bort inom cirka 3 månader.", en: "With very few brow hairs of your own, tattooed strokes have no protection and wear away within about 3 months." },
        recPowder: { sv: "Därför rekommenderar vi hellre skuggade bryn (puderbryn).", en: "That is why we recommend shaded brows (powder brows) instead." },
        nano: { sv: "Vill du ändå ha strålook kan nanostrokes med maskin vara ett alternativ (1 000 kr tillägg).", en: "If you would still like a stroke look, machine nanostrokes can be an alternative (SEK 1,000 extra)." },
        powder: { sv: "Puderbryn ger mjukt markerade, jämna och naturligt skuggade bryn, likt ett lätt ifyllt bryn med smink.", en: "Powder brows give softly defined, even and naturally shaded brows, like a lightly filled-in brow with makeup." },
        powder2: { sv: "Passar alla hudtyper och håller i ca 1,5–3 år.", en: "Suits all skin types and lasts about 1.5–3 years." },
        strokes: { sv: "Strokes skapar realistiska, hårstråliknande bryn som jämnar till formen och fyller ut där det saknas strån.", en: "Strokes create realistic, hair-like brows that even out the shape and fill in where hairs are missing." },
        strokes2: { sv: "Återbesök efter ca 4–5 veckor och refill inom 12 månader.", en: "Touch-up after about 4–5 weeks and a refill within 12 months." }
      }
    };
    var gsteps = $$(".guide__step", guide), gi = 0;
    var gprog = $$(".guide__progress span", guide);
    var gBack = $("[data-guide-back]", guide), gNext = $("[data-guide-next]", guide), gNav = $(".guide__nav", guide);
    var gRes = $(".guide__result", guide);
    function gVal(name) { var c = $('input[name="' + name + '"]:checked', guide); return c ? c.value : null; }
    var gShown = -1;
    function gRender() {
      gsteps.forEach(function (s, i) {
        s.hidden = i !== gi;
        if (i === gi && gShown !== gi && gShown !== -1 && !reduce) { s.classList.remove("is-enter"); void s.offsetWidth; s.classList.add("is-enter"); }
      });
      gShown = gi;
      gprog.forEach(function (p, i) { p.classList.toggle("is-done", i <= gi); });
      gBack.style.visibility = gi === 0 ? "hidden" : "visible";
      gNext.innerHTML = esc(L(gi === gsteps.length - 1 ? G.show : G.next)) + ' <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>';
      var name = $("input", gsteps[gi]).name;
      gNext.disabled = !gVal(name);
    }
    function gResult() {
      var tat = gVal("g-tattoo"), skin = gVal("g-skin"), hair = gVal("g-hair"), look = gVal("g-look");
      var key, why = [];
      if (tat === "bad") { key = "lift"; why = [G.why.bad, G.why.badNext]; }
      else {
        var ex = [];
        if (tat === "ok") ex.push(G.why.old);
        if (skin === "oily") ex.push(G.why.oily);
        if (hair === "few") ex.push(G.why.few);
        if (ex.length) { key = "puderbryn"; why = ex.concat([G.why.recPowder]); if (look === "strokes") why.push(G.why.nano); }
        else if (look === "strokes") { key = "strokes"; why = [G.why.strokes, G.why.strokes2]; }
        else { key = "puderbryn"; why = [G.why.powder, G.why.powder2]; }
      }
      guide.__why = why;
      $$("[data-result]", guide).forEach(function (r) { r.hidden = r.getAttribute("data-result") !== key; });
      var active = $('[data-result="' + key + '"]', guide);
      $(".guide__why", active).innerHTML = why.map(function (w, n) { return '<li style="--i:' + n + '">' + esc(L(w)) + "</li>"; }).join("");
      gsteps.forEach(function (s) { s.hidden = true; });
      gNav.hidden = true;
      gprog.forEach(function (p) { p.classList.add("is-done"); });
      gRes.hidden = false;
      var h = $("h3", active); h && h.setAttribute("tabindex", "-1"); h && h.focus({ preventScroll: true });
      active.scrollIntoView({ block: "nearest", behavior: reduce ? "auto" : "smooth" });
    }
    guide.addEventListener("change", function () { gRender(); });
    gNext.addEventListener("click", function () { if (gi < gsteps.length - 1) { gi++; gRender(); var f = $("input", gsteps[gi]); f && f.focus({ preventScroll: true }); } else gResult(); });
    gBack.addEventListener("click", function () { if (gi > 0) { gi--; gRender(); } });
    $$("[data-guide-restart]", guide).forEach(function (b) {
      b.addEventListener("click", function () { $$("input", guide).forEach(function (i) { i.checked = false; }); gi = 0; gRes.hidden = true; gNav.hidden = false; gRender(); var f = $("input", gsteps[0]); f && f.focus(); });
    });
    doc.addEventListener("pdl:lang", function () { gRender(); if (!gRes.hidden && guide.__why) { var a = $("[data-result]:not([hidden])", guide); $(".guide__why", a).innerHTML = guide.__why.map(function (w) { return "<li>" + esc(L(w)) + "</li>"; }).join(""); } });
    gRender();
  }

  /* ---------- Map ---------- */
  $$("[data-map-load]").forEach(function (b) {
    b.addEventListener("click", function () {
      var box = b.closest(".map");
      var f = doc.createElement("iframe");
      f.src = "https://maps.google.com/maps?q=" + encodeURIComponent("Kungsgatan 11, Göteborg") + "&z=16&output=embed";
      f.title = lang === "en" ? "Map: Kungsgatan 11, Gothenburg" : "Karta: Kungsgatan 11, Göteborg";
      f.loading = "lazy";
      f.referrerPolicy = "no-referrer-when-downgrade";
      box.appendChild(f);
      var ph = $(".map__placeholder", box); ph && ph.remove();
    });
  });

  /* ---------- Forms ---------- */
  var MSG = {
    required: { sv: "Fyll i det här fältet.", en: "Please fill in this field." },
    email: { sv: "Skriv en giltig e-postadress, till exempel namn@exempel.se.", en: "Enter a valid email address, for example name@example.com." },
    phone: { sv: "Skriv ett telefonnummer med minst 7 siffror.", en: "Enter a phone number with at least 7 digits." },
    terms: { sv: "Du behöver godkänna villkoren för att skicka.", en: "Please accept the terms to send." },
    sending: { sv: "Skickar...", en: "Sending..." }
  };
  function validateField(f) {
    var wrap = f.closest(".field") || f.closest(".check");
    var v = (f.value || "").trim(), err = null;
    if (f.type === "checkbox") { if (f.required && !f.checked) err = MSG.terms; }
    else if (f.required && !v) err = MSG.required;
    else if (v && f.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) err = MSG.email;
    else if (v && f.type === "tel" && v.replace(/\D/g, "").length < 7) err = MSG.phone;
    if (wrap) {
      wrap.classList.toggle("is-invalid", !!err);
      var m = $(".field__err", wrap);
      if (m) m.textContent = err ? L(err) : "";
    }
    f.setAttribute("aria-invalid", String(!!err));
    return !err;
  }
  function validateAll(scope) {
    var ok = true, first = null;
    $$("input, select, textarea", scope).forEach(function (f) {
      if (f.closest(".hp") || f.disabled || f.type === "radio") return;
      if (!validateField(f)) { ok = false; first = first || f; }
    });
    if (first) first.focus();
    return ok;
  }
  $$("input, select, textarea").forEach(function (f) {
    f.addEventListener("blur", function () { if (f.closest("form") && (f.value || f.type === "checkbox") && !f.closest(".hp")) validateField(f); });
    f.addEventListener("input", function () { var w = f.closest(".is-invalid"); if (w) validateField(f); });
  });
  $$("form[data-contact]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validateAll(form)) return;
      if ($(".hp input", form) && $(".hp input", form).value) return;
      var btn = $('button[type="submit"]', form);
      btn.disabled = true; btn.setAttribute("data-label", btn.innerHTML); btn.textContent = L(MSG.sending);
      setTimeout(function () {
        form.hidden = true;
        var ok = doc.getElementById(form.getAttribute("data-success"));
        if (ok) {
          var n = $('[name="name"]', form); var span = $("[data-name]", ok);
          if (span && n) span.textContent = n.value.trim().split(" ")[0];
          ok.hidden = false; ok.setAttribute("tabindex", "-1"); ok.focus();
        }
      }, 700);
    });
  });

  /* ---------- Booking ---------- */
  var book = $("[data-booking]");
  if (book) initBooking(book);
  function initBooking(book) {
    var data = JSON.parse($("#booking-data").textContent);
    var T = data.treatments, C = data.courses, F = data.free || {};
    var CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>';
    var S = {
      steps: [{ sv: "Behandling", en: "Treatment" }, { sv: "Datum", en: "Dates" }, { sv: "Hälsa", en: "Health" }, { sv: "Uppgifter", en: "Details" }],
      stepOf: { sv: "Steg {n} av {t}", en: "Step {n} of {t}" },
      consultT: { sv: "Kostnadsfri konsultation", en: "Free consultation" }, courseT: { sv: "Kostnadsfri kursrådgivning", en: "Free course advice" },
      modes: { plats: { sv: "På plats", en: "In person" }, telefon: { sv: "Per telefon", en: "By phone" }, zoom: { sv: "Via Zoom", en: "On Zoom" } },
      tod: { fm: { sv: "Förmiddag", en: "Morning" }, em: { sv: "Eftermiddag", en: "Afternoon" }, any: { sv: "Spelar ingen roll", en: "No preference" } },
      remind: { sms: { sv: "Sms", en: "Text message" }, email: { sv: "E-post", en: "Email" }, both: { sv: "Sms och e-post", en: "Text and email" } },
      flex: { sv: "Första lediga tid", en: "First available time" },
      none: { sv: "Inte valt ännu", en: "Not chosen yet" }, edit: { sv: "Ändra", en: "Edit" },
      rows: { what: { sv: "Behandling", en: "Treatment" }, how: { sv: "Form", en: "Format" }, course: { sv: "Utbildning", en: "Course" }, when: { sv: "Dagar", en: "Days" }, tod: { sv: "Tid på dagen", en: "Time of day" }, health: { sv: "Hälsa", en: "Health" }, remind: { sv: "Påminnelse", en: "Reminder" } },
      healthOk: { sv: "Inget hinder", en: "No obstacles" },
      noDays: { sv: "Inga dagar valda ännu", en: "No days chosen yet" },
      remove: { sv: "Ta bort", en: "Remove" }, max3: { sv: "Du kan välja upp till tre dagar.", en: "You can choose up to three days." },
      pickDay: { sv: "Välj minst en dag, eller slå på att du är flexibel.", en: "Choose at least one day, or switch on that you are flexible." },
      pickWhat: { sv: "Välj vad du vill boka.", en: "Choose what you would like to book." },
      pickHealth: { sv: "Svara på alla frågor för att gå vidare.", en: "Please answer every question to continue." },
      dows: { sv: ["Mån", "Tis", "Ons", "Tor", "Fre", "Lör", "Sön"], en: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] },
      prev: { sv: "Föregående månad", en: "Previous month" }, nextM: { sv: "Nästa månad", en: "Next month" },
      anyCourse: { sv: "Jag vet inte än", en: "Not sure yet" },
      cont: { sv: "Fortsätt", en: "Continue" }, send: { sv: "Skicka förfrågan", en: "Send request" }
    };
    var st = { what: null, mode: "plats", course: "", dates: [], tod: "any", flex: false, health: {}, remind: "sms" };
    var stepEls = {}; $$(".bstep", book).forEach(function (s) { stepEls[+s.getAttribute("data-step")] = s; });
    var cur = 0, autoT = null;
    var stepper = $(".bk-steps", book), form = $("form", book), bar = $(".bk-bar", book);
    var qkeys = $$(".bk-q input[value='no']", book).map(function (i) { return i.name.replace("hq-", ""); });

    var isFree = function () { return st.what === "konsultation" || st.what === "kursradgivning"; };
    var isTreatment = function () { return st.what && !isFree(); };
    var needsHealth = function () { return isTreatment() && T[st.what] && T[st.what].group === "pmu"; };
    var visible = function () { return [0, 1].concat(needsHealth() ? [2] : []).concat([3]); };
    var fmtDate = function (iso) { var d = new Date(iso + "T12:00:00"); try { return d.toLocaleDateString(lang === "en" ? "en-GB" : "sv-SE", { weekday: "short", day: "numeric", month: "short" }); } catch (e) { return iso; } };
    var whatLabel = function () { if (!st.what) return null; if (st.what === "konsultation") return L(S.consultT); if (st.what === "kursradgivning") return L(S.courseT); return L(T[st.what].fullName || T[st.what].name); };
    var err = function (i, msg) { var a = $(".alert--step", stepEls[i]); if (!a) return; a.textContent = msg ? L(msg) : ""; a.hidden = !msg; };

    /* Step indicator */
    function renderStepper() {
      var vis = visible(), pos = cur === 4 ? vis.length : vis.indexOf(cur);
      stepper.innerHTML = vis.map(function (s, i) {
        var done = i < pos, now = i === pos;
        return '<li class="' + (done ? "is-done" : now ? "is-current" : "") + '"' + (now ? ' aria-current="step"' : "") + '><button type="button"' + (done && cur !== 4 ? ' data-goto="' + s + '"' : " disabled") + "><i>" + (done ? CHECK : i + 1) + "</i><span>" + esc(L(S.steps[s])) + "</span></button></li>";
      }).join("");
      $$("[data-stepnum]", book).forEach(function (n) {
        var step = +n.closest(".bstep").getAttribute("data-step"), p = vis.indexOf(step);
        n.textContent = p > -1 ? L(S.stepOf).replace("{n}", p + 1).replace("{t}", vis.length) : "";
      });
    }

    /* Summary and mobile bar */
    var lastImg = null;
    function renderSummary() {
      var sum = $(".summary", book), img = $(".summary__img", sum);
      var src = st.what ? (isFree() ? (F[st.what] || {}).img : T[st.what].img) : null;
      if (src && src !== lastImg) { img.src = src; img.alt = isFree() ? "" : L(T[st.what].alt); img.hidden = false; img.classList.remove("is-enter"); void img.offsetWidth; if (!reduce) img.classList.add("is-enter"); lastImg = src; }
      if (!src) { img.hidden = true; lastImg = null; }
      var rows = [["what", whatLabel(), 0]];
      if (st.what === "konsultation") rows.push(["how", L(S.modes[st.mode]), 0]);
      if (st.what === "kursradgivning") rows.push(["course", st.course && C[st.course] ? L(C[st.course]) : L(S.anyCourse), 0]);
      rows.push(["when", st.flex ? L(S.flex) + (st.dates.length ? " · " + st.dates.map(fmtDate).join(", ") : "") : (st.dates.length ? st.dates.map(fmtDate).join(", ") : null), 1]);
      rows.push(["tod", L(S.tod[st.tod]), 1]);
      if (needsHealth()) rows.push(["health", qkeys.every(function (k) { return st.health[k] === "no"; }) ? L(S.healthOk) : null, 2]);
      if (cur >= 3) rows.push(["remind", L(S.remind[st.remind]), 3]);
      $("dl", sum).innerHTML = rows.map(function (r) {
        var canEdit = r[1] && cur !== 4 && r[2] < cur;
        return "<div><dt>" + esc(L(S.rows[r[0]])) + "</dt><dd" + (r[1] ? "" : ' class="is-empty"') + ">" + esc(r[1] || L(S.none)) + "</dd>" + (canEdit ? '<button type="button" class="summary__edit" data-goto="' + r[2] + '">' + esc(L(S.edit)) + "</button>" : "") + "</div>";
      }).join("");
      $("[data-bar-what]", book).textContent = whatLabel() || L(S.none);
      var bn = $("[data-bar-next]", book); bn.textContent = L(cur === 3 ? S.send : S.cont);
      bar.hidden = cur === 4;
    }

    /* Steps */
    function show(i, opts) {
      cur = i;
      Object.keys(stepEls).forEach(function (k) {
        var s = stepEls[k], on = +k === i;
        s.hidden = !on;
        if (on && !(opts && opts.first) && !reduce) { s.classList.remove("is-enter"); void s.offsetWidth; s.classList.add("is-enter"); }
      });
      renderStepper(); renderSummary();
      if (opts && opts.first) return;
      var h = $("h2", stepEls[i]); if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
      var top = book.getBoundingClientRect().top + window.scrollY - 130;
      if (window.scrollY > top || i === 4) window.scrollTo({ top: Math.max(0, top), behavior: reduce ? "auto" : "smooth" });
    }
    function go(dir) { var vis = visible(), p = vis.indexOf(cur); show(vis[Math.max(0, Math.min(vis.length - 1, p + dir))]); }
    function next() {
      clearTimeout(autoT);
      if (cur === 0 && !st.what) return err(0, S.pickWhat);
      if (cur === 1 && !st.dates.length && !st.flex) return err(1, S.pickDay);
      if (cur === 2) {
        if (!qkeys.every(function (k) { return st.health[k]; })) return err(2, S.pickHealth);
        if (qkeys.some(function (k) { return st.health[k] === "yes"; })) { var al = $("[data-health-alert]", book); al.hidden = false; al.scrollIntoView({ block: "center", behavior: reduce ? "auto" : "smooth" }); return; }
      }
      if (cur === 3) { if (form.requestSubmit) form.requestSubmit(); else form.dispatchEvent(new Event("submit", { cancelable: true })); return; }
      err(cur, null); go(1);
    }

    /* Category tabs */
    var tabs = $$(".bk-tabs [data-tab]", book), ink = $(".bk-tabs__ink", book);
    function moveInk() { var t = tabs.filter(function (x) { return x.getAttribute("aria-selected") === "true"; })[0]; if (!t || !ink) return; ink.style.setProperty("--x", t.offsetLeft + "px"); ink.style.setProperty("--w", t.offsetWidth + "px"); }
    function setTab(name) {
      tabs.forEach(function (t) { t.setAttribute("aria-selected", String(t.getAttribute("data-tab") === name)); });
      $$("[data-panel]", book).forEach(function (p) {
        var on = p.getAttribute("data-panel") === name;
        if (on && p.hidden && !reduce) { p.classList.remove("is-enter"); void p.offsetWidth; p.classList.add("is-enter"); }
        p.hidden = !on;
      });
      moveInk();
    }
    tabs.forEach(function (t) { t.addEventListener("click", function () { setTab(t.getAttribute("data-tab")); }); });
    window.addEventListener("resize", moveInk);

    function syncWhat() {
      $$(".bk-card", book).forEach(function (c) { c.classList.toggle("is-selected", $("input", c).checked); });
      $("[data-modes]", book).hidden = st.what !== "konsultation";
      $("[data-courserow]", book).hidden = st.what !== "kursradgivning";
      var hn = $("[data-health-name]", book); if (hn && isTreatment()) hn.textContent = L(T[st.what].name).toLowerCase();
      var terms = $("[data-terms]", book), tc = $("[data-terms] input", book);
      terms.hidden = !isTreatment(); tc.required = !!isTreatment();
      renderStepper(); renderSummary();
    }

    book.addEventListener("change", function (e) {
      var t = e.target;
      if (t.name === "b-what") {
        st.what = t.value; err(0, null); syncWhat();
        if (!isFree() && cur === 0 && !reduce) { clearTimeout(autoT); autoT = setTimeout(function () { if (cur === 0) next(); }, 520); }
      }
      if (t.name === "b-mode") { st.mode = t.value; renderSummary(); }
      if (t.name === "b-course") { st.course = t.value; renderSummary(); }
      if (t.name === "b-tod") { st.tod = t.value; renderSummary(); }
      if (t.name === "b-flex") { st.flex = t.checked; err(1, null); renderSummary(); }
      if (t.name === "b-remind") { st.remind = t.value; renderSummary(); }
      if (t.name && t.name.indexOf("hq-") === 0) {
        st.health[t.name.slice(3)] = t.value;
        var li = t.closest(".bk-q"); li.classList.toggle("is-yes", t.value === "yes"); li.classList.toggle("is-no", t.value === "no");
        $("[data-health-alert]", book).hidden = !qkeys.some(function (k) { return st.health[k] === "yes"; });
        err(2, null); renderSummary();
      }
    });
    book.addEventListener("click", function (e) {
      var g = e.target.closest("[data-goto]"); if (g) { show(+g.getAttribute("data-goto")); return; }
      if (e.target.closest("[data-next]") || e.target.closest("[data-bar-next]")) next();
      if (e.target.closest("[data-prev]")) go(-1);
      var u = e.target.closest("[data-unpick]"); if (u) { st.dates.splice(st.dates.indexOf(u.getAttribute("data-unpick")), 1); renderCal(); }
      if (e.target.closest("[data-switch-consult]")) {
        var r = $('input[name="b-what"][value="konsultation"]', book); r.checked = true; st.what = "konsultation"; setTab("free"); syncWhat(); show(1);
      }
    });

    /* Calendar */
    var cal = $(".cal", book), now = new Date(), today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    var view = new Date(today.getFullYear(), today.getMonth(), 1), maxView = new Date(today.getFullYear(), today.getMonth() + 4, 1);
    var iso = function (d) { return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); };
    function renderCal(anim) {
      var title; try { title = view.toLocaleDateString(lang === "en" ? "en-GB" : "sv-SE", { month: "long", year: "numeric" }); } catch (e) { title = iso(view).slice(0, 7); }
      $(".cal__head strong", cal).textContent = title;
      var pb = $("[data-cal-prev]", cal), nb = $("[data-cal-next]", cal);
      pb.disabled = view <= new Date(today.getFullYear(), today.getMonth(), 1); nb.disabled = view >= maxView;
      pb.setAttribute("aria-label", L(S.prev)); nb.setAttribute("aria-label", L(S.nextM));
      var grid = $(".cal__grid", cal), html = S.dows[lang].map(function (d) { return '<span class="cal__dow" aria-hidden="true">' + d + "</span>"; }).join("");
      var first = (view.getDay() + 6) % 7, days = new Date(view.getFullYear(), view.getMonth() + 1, 0).getDate();
      for (var i = 0; i < first; i++) html += "<span></span>";
      for (var d = 1; d <= days; d++) {
        var dt = new Date(view.getFullYear(), view.getMonth(), d), k = iso(dt), past = dt < today, label;
        try { label = dt.toLocaleDateString(lang === "en" ? "en-GB" : "sv-SE", { weekday: "long", day: "numeric", month: "long" }); } catch (e) { label = k; }
        html += '<button type="button" class="cal__day' + (dt.getTime() === today.getTime() ? " is-today" : "") + '" data-day="' + k + '" aria-pressed="' + (st.dates.indexOf(k) > -1) + '" aria-label="' + esc(label) + '"' + (past ? " disabled" : "") + ">" + d + "</button>";
      }
      grid.innerHTML = html;
      if (anim && !reduce) { grid.classList.remove("is-enter"); void grid.offsetWidth; grid.classList.add("is-enter"); }
      var ul = $(".picked", book);
      ul.setAttribute("data-empty", L(S.noDays));
      ul.innerHTML = st.dates.map(function (k) { return "<li>" + esc(fmtDate(k)) + '<button type="button" data-unpick="' + k + '" aria-label="' + esc(L(S.remove) + " " + fmtDate(k)) + '"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg></button></li>'; }).join("");
      renderSummary();
    }
    cal.addEventListener("click", function (e) {
      var b = e.target.closest("[data-day]");
      if (b) {
        var k = b.getAttribute("data-day"), i = st.dates.indexOf(k);
        if (i > -1) st.dates.splice(i, 1); else if (st.dates.length < 3) st.dates.push(k); else { err(1, S.max3); return; }
        st.dates.sort(); err(1, null); renderCal();
        var again = $('[data-day="' + k + '"]', cal); again && again.focus();
      }
      if (e.target.closest("[data-cal-prev]")) { view = new Date(view.getFullYear(), view.getMonth() - 1, 1); renderCal(true); }
      if (e.target.closest("[data-cal-next]")) { view = new Date(view.getFullYear(), view.getMonth() + 1, 1); renderCal(true); }
    });

    /* Submit */
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validateAll(form)) return;
      if ($(".hp input", form).value) return;
      var btn = $('button[type="submit"]', form), barBtn = $("[data-bar-next]", book);
      btn.disabled = true; barBtn.disabled = true; btn.textContent = L(MSG.sending); barBtn.textContent = L(MSG.sending);
      setTimeout(function () {
        var n = $('[name="fname"]', form).value.trim();
        try {
          sessionStorage.setItem("pdl-booking", JSON.stringify({
            fname: n, lname: $('[name="lname"]', form).value.trim(), email: $('[name="email"]', form).value.trim(),
            cc: $('[name="cc"]', form).value, phone: $('[name="phone"]', form).value.trim(), message: $('[name="message"]', form).value.trim(),
            what: st.what, dates: st.dates.slice(), tod: st.tod, flex: st.flex, remind: st.remind,
            health: needsHealth() ? (qkeys.some(function (k) { return st.health[k] === "yes"; }) ? "yes" : "no") : null,
            healthAnswers: needsHealth() ? st.health : null
          }));
        } catch (err2) {}
        $$("[data-confirm-name]", book).forEach(function (s) { s.textContent = n; });
        $("[data-confirm-ref]", book).textContent = "PDL-" + Date.now().toString(36).slice(-5).toUpperCase();
        $("[data-confirm-what]", book).textContent = whatLabel();
        $("[data-confirm-when]", book).textContent = (st.flex && !st.dates.length ? L(S.flex) : st.dates.map(fmtDate).join(", ")) + " · " + L(S.tod[st.tod]);
        var prepBox = $("[data-confirm-prep]", book), t = isTreatment() ? T[st.what] : null;
        if (t && t.prep && t.prep.length) {
          $("[data-prep-list]", book).innerHTML = t.prep.map(function (g) { return '<div class="bk-prep__g"><strong>' + esc(L(g.when)) + '</strong><ul class="bul">' + g.items.map(function (x) { return "<li>" + esc(L(x)) + "</li>"; }).join("") + "</ul></div>"; }).join("") + (t.prepNote ? '<p class="note">' + esc(L(t.prepNote)) + "</p>" : "");
          prepBox.hidden = false;
        } else prepBox.hidden = true;
        var read = $("[data-confirm-read]", book); read.hidden = !t; if (t) read.href = t.url;
        show(4);
        btn.disabled = false; barBtn.disabled = false;
      }, 900);
    });

    /* Start */
    var pre = new URLSearchParams(location.search).get("t"), preCourse = new URLSearchParams(location.search).get("kurs");
    var preIn = pre && $('input[name="b-what"][value="' + pre + '"]', book);
    if (preIn) { preIn.checked = true; st.what = pre; setTab(preIn.closest("[data-panel]").getAttribute("data-panel")); }
    else setTab("pmu");
    if (preCourse && $('select[name="b-course"] option[value="' + preCourse + '"]', book)) { $('select[name="b-course"]', book).value = preCourse; st.course = preCourse; }
    renderCal(); syncWhat(); show(0, { first: true });
    requestAnimationFrame(moveInk);
    doc.addEventListener("pdl:lang", function () { renderCal(); syncWhat(); moveInk(); });
  }

  /* ---------- Chat ---------- */
  var chat = $(".chat"), chatLog, chatOpenedOnce = false;
  var CH = {
    hi: { sv: "<p>Hej! Här får du snabba svar om behandlingar, utbildningar och bokning.</p><p>Välj en fråga nedan eller skriv din egen.</p>", en: "<p>Hi! Here you get quick answers about treatments, courses and booking.</p><p>Pick a question below or type your own.</p>" },
    fallback: { sv: "<p>Det kan jag tyvärr inte svara på här. Skicka din fråga till oss så svarar vi personligen.</p><p><a href=\"kontakt.html\">Skicka en fråga</a></p>", en: "<p>I can't answer that here, unfortunately. Send us your question and we will reply personally.</p><p><a href=\"kontakt.html\">Send a question</a></p>" },
    topics: [
      { id: "pain", chip: { sv: "Gör det ont?", en: "Does it hurt?" }, kw: ["ont", "smärt", "bedöv", "nål", "hurt", "pain", "numb", "needle"],
        a: { sv: "<p>Vi bedövar med salva före och under behandlingen, så du ska inte känna smärta eller obehag.</p><p>Lauras egenutvecklade No Trauma-teknik ger minimal svullnad, ingen blödning och inga skorpor under läkningen.</p>", en: "<p>We apply numbing cream before and during the treatment, so you should not feel pain or discomfort.</p><p>Laura's own No Trauma technique means minimal swelling, no bleeding and no scabs while it heals.</p>" } },
      { id: "last", chip: { sv: "Hur länge håller det?", en: "How long does it last?" }, kw: ["håll", "länge", "varar", "bleknar", "refill", "återbesök", "last", "long", "fade", "touch"],
        a: { sv: "<p>Kosmetisk tatuering är semi-permanent. Puderbryn håller i ca 1,5–3 år.</p><p>Ett återbesök görs efter ca 4–6 veckor (4–5 veckor för strokes och läppar) och en refill bör göras inom 12 månader. Vill du inte göra en refill kan du låta tatueringen läka bort.</p>", en: "<p>Cosmetic tattooing is semi-permanent. Powder brows last about 1.5–3 years.</p><p>A touch-up follows after about 4–6 weeks (4–5 weeks for strokes and lips) and a refill should be done within 12 months. If you skip the refill, the tattoo fades away.</p>" } },
      { id: "brows", chip: { sv: "Puder eller strokes?", en: "Powder or strokes?" }, kw: ["puder", "ombre", "stroke", "microblad", "nanostroke", "bryn", "brow"],
        a: { sv: "<p>Microblading (strokes) passar inte alla. Har du fet hy, förstorade porer, väldigt lite strån eller en gammal maskintatuering rekommenderar vi puderbryn, eller nanostrokes med maskin (1 000 kr tillägg).</p><p><a href=\"index.html#brynguiden\">Testa Brynguiden</a></p>", en: "<p>Microblading (strokes) does not suit everyone. With oily skin, enlarged pores, very few hairs or an old machine tattoo we recommend powder brows, or machine nanostrokes (SEK 1,000 extra).</p><p><a href=\"index.html#brynguiden\">Try the brow guide</a></p>" } },
      { id: "prep", chip: { sv: "Inför behandlingen", en: "Before your treatment" }, kw: ["inför", "förbered", "innan", "alkohol", "koffein", "kaffe", "sol", "prepar", "before", "coffee", "alcohol"],
        a: { sv: "<p><strong>Dagen innan:</strong> ta det lugnt med solning och alkohol.</p><p><strong>3 timmar innan:</strong> undvik koffein, Ipren och Treo.</p><p><strong>Läppar:</strong> peela och återfukta läpparna, till exempel med vitt vaselin, ca 3 dagar innan.</p>", en: "<p><strong>The day before:</strong> go easy on sunbathing and alcohol.</p><p><strong>3 hours before:</strong> avoid caffeine, Ipren and Treo.</p><p><strong>Lips:</strong> exfoliate and moisturise, for example with white petroleum jelly, about 3 days before.</p>" } },
      { id: "contra", chip: { sv: "Vem kan inte behandlas?", en: "Who can't be treated?" }, kw: ["gravid", "blodförtunn", "eksem", "utslag", "sår", "18", "pregnan", "blood", "eczema", "rash"],
        a: { sv: "<p>Inför kosmetisk tatuering får du inte:</p><ul><li>vara gravid</li><li>äta blodförtunnande medicin</li><li>ha sår, utslag eller eksem på området</li><li>ha någon blodsmittande sjukdom</li><li>vara under 18 år</li></ul><p>Om vi inte kan utföra behandlingen på grund av detta debiteras 50 %.</p>", en: "<p>Before cosmetic tattooing you must not:</p><ul><li>be pregnant</li><li>take blood-thinning medication</li><li>have wounds, rashes or eczema on the area</li><li>have a blood-borne disease</li><li>be under 18</li></ul><p>If we cannot carry out the treatment for one of these reasons, 50% is charged.</p>" } },
      { id: "cancel", chip: { sv: "Avbokning", en: "Cancellation" }, kw: ["avbok", "omboka", "flytta", "cancel", "reschedul", "move"],
        a: { sv: "<p>På kosmetisk tatuering gäller avbokning minst 24 timmar innan behandlingen. När du bokar godkänner du villkoren.</p>", en: "<p>For cosmetic tattooing, cancellations must be made at least 24 hours before the treatment. Booking means you accept these terms.</p>" } },
      { id: "consult", chip: { sv: "Gratis konsultation", en: "Free consultation" }, kw: ["konsult", "rådgiv", "zoom", "osäker", "consult", "advice", "unsure"],
        a: { sv: "<p>Är du osäker är du välkommen att boka en kostnadsfri konsultation på plats, per telefon eller via Zoom.</p><p><a href=\"boka.html?t=konsultation\">Boka konsultation</a></p>", en: "<p>If you are unsure, you are welcome to book a free consultation in person, by phone or on Zoom.</p><p><a href=\"boka.html?t=konsultation\">Book a consultation</a></p>" } },
      { id: "courses", chip: { sv: "Utbildningar", en: "Courses" }, kw: ["utbild", "kurs", "elev", "certifikat", "qliro", "avbetal", "akademi", "lära", "course", "training", "student", "academy", "learn", "certif"],
        a: { sv: "<p>Plaza Di Laura Academy har max 2 elever per kurstillfälle, avbetalning med Qliro och internationellt certifikat. Signature PMU Artist Program är 5 dagar och kostar 55 000 kr.</p><p><a href=\"akademi.html\">Se alla utbildningar</a> eller <a href=\"boka.html?t=kursradgivning\">boka kostnadsfri kursrådgivning</a>.</p>", en: "<p>Plaza Di Laura Academy takes a maximum of 2 students per course, offers instalments with Qliro and an international certificate. The Signature PMU Artist Program is 5 days and costs SEK 55,000.</p><p><a href=\"akademi.html\">See all courses</a> or <a href=\"boka.html?t=kursradgivning\">book free course advice</a>.</p>" } },
      { id: "where", chip: { sv: "Var finns ni?", en: "Where are you?" }, kw: ["adress", "hitta", "karta", "kungsgatan", "göteborg", "var ligger", "var finns", "address", "where", "location", "map", "gothenburg"],
        a: { sv: "<p>Kliniken och skolan finns på Kungsgatan 11 i centrala Göteborg.</p><p><a href=\"kontakt.html\">Kontakt och karta</a></p>", en: "<p>The clinic and school are at Kungsgatan 11 in central Gothenburg.</p><p><a href=\"kontakt.html\">Contact and map</a></p>" } },
      { id: "price", chip: { sv: "Pris", en: "Price" }, kw: ["pris", "kostar", "kostnad", "kronor", "price", "cost", "how much", "fee"],
        a: { sv: "<p>Skriv till oss så får du pris för den behandling du är intresserad av.</p><p>Utbildningen Signature PMU Artist Program kostar 55 000 kr och kan delbetalas via Qliro.</p><p><a href=\"kontakt.html\">Skicka en fråga</a></p>", en: "<p>Write to us and we will send you the price for the treatment you are interested in.</p><p>The Signature PMU Artist Program course costs SEK 55,000 and can be paid in instalments via Qliro.</p><p><a href=\"kontakt.html\">Send a question</a></p>" } },
      { id: "smp", kw: ["smp", "skalp", "hårbotten", "håravfall", "flint", "scalp", "hair loss", "bald"],
        a: { sv: "<p>SMP utförs av Robert Tomaszewski, en av branschens mest erfarna SMP-artister med över 13 års erfarenhet.</p><p><a href=\"behandling-smp.html\">Läs mer om SMP</a></p>", en: "<p>SMP is performed by Robert Tomaszewski, one of the most experienced SMP artists in the industry with over 13 years of experience.</p><p><a href=\"behandling-smp.html\">Read about SMP</a></p>" } },
      { id: "removal", kw: ["ta bort", "borttag", "remov", "lift", "laser", "missfärg", "discolo"],
        a: { sv: "<p>LIFT Ink Removal tar bort pigment utan laser och är särskilt effektiv för felaktig microblading, missfärgade bryn och för mörk permanent makeup.</p><p><a href=\"behandling-lift.html\">Läs mer</a></p>", en: "<p>LIFT Ink Removal removes pigment without a laser and is especially effective for poor microblading, discoloured brows and too-dark permanent makeup.</p><p><a href=\"behandling-lift.html\">Read more</a></p>" } },
      { id: "book", chip: { sv: "Boka tid", en: "Book" }, kw: ["boka", "bokning", "ledig tid", "book", "appointment"],
        a: { sv: "<p>Du kan skicka en bokningsförfrågan direkt här på sidan.</p><p><a href=\"boka.html\">Boka tid</a></p>", en: "<p>You can send a booking request right here on the site.</p><p><a href=\"boka.html\">Book now</a></p>" } }
    ]
  };
  function chatAdd(html, who) {
    var m = doc.createElement("div");
    m.className = "msg msg--" + who;
    m.innerHTML = html;
    chatLog.appendChild(m);
    // Bring the new message into view from its first line, so a long answer is read from the top,
    // never jumped past. Short messages simply settle at the bottom.
    var target = Math.min(m.offsetTop - 14, chatLog.scrollHeight - chatLog.clientHeight);
    if (target > chatLog.scrollTop) chatLog.scrollTo({ top: target, behavior: reduce ? "auto" : "smooth" });
    return m;
  }
  function chatAnswer(topic) {
    var typing = chatAdd("<i></i><i></i><i></i>", "bot");
    typing.classList.add("msg--typing");
    typing.setAttribute("aria-hidden", "true");
    setTimeout(function () { typing.remove(); chatAdd(L(topic ? topic.a : CH.fallback), "bot"); }, reduce ? 0 : 550);
  }
  function chatChips() {
    var box = $(".chat__chips", chat);
    box.innerHTML = CH.topics.filter(function (t) { return t.chip; }).map(function (t) { return '<button type="button" data-topic="' + t.id + '">' + esc(L(t.chip)) + "</button>"; }).join("");
  }
  function setChat(open) {
    if (!chat) return;
    chat.classList.toggle("is-open", open);
    chat.setAttribute("aria-hidden", String(!open));
    if (open) chat.removeAttribute("inert"); else chat.setAttribute("inert", "");
    doc.body.classList.toggle("chat-open", open);
    $$("[data-chat-open]").forEach(function (b) { b.setAttribute("aria-expanded", String(open)); });
    if (open) {
      if (!chatOpenedOnce) { chatOpenedOnce = true; chatAdd(L(CH.hi), "bot"); }
      setTimeout(function () { $(".chat__form input", chat).focus(); }, 60);
    } else if (lastChatOpener) lastChatOpener.focus();
  }
  var lastChatOpener = null;
  if (chat) {
    chatLog = $(".chat__log", chat);
    chat.setAttribute("inert", "");
    chatChips();
    $$("[data-chat-open]").forEach(function (b) { b.addEventListener("click", function () { lastChatOpener = b; setChat(!chat.classList.contains("is-open")); }); });
    $(".chat__close", chat).addEventListener("click", function () { setChat(false); });
    chat.addEventListener("click", function (e) {
      var b = e.target.closest("[data-topic]");
      if (!b) return;
      var t = CH.topics.filter(function (x) { return x.id === b.getAttribute("data-topic"); })[0];
      chatAdd(esc(L(t.chip)), "me"); chatAnswer(t);
    });
    $(".chat__form", chat).addEventListener("submit", function (e) {
      e.preventDefault();
      var inp = $("input", e.target), q = inp.value.trim();
      if (!q) return;
      chatAdd(esc(q), "me"); inp.value = "";
      var lq = q.toLowerCase(), best = null, score = 0;
      CH.topics.forEach(function (t) { var s = 0; t.kw.forEach(function (k) { if (lq.indexOf(k) > -1) s += k.length; }); if (s > score) { score = s; best = t; } });
      chatAnswer(best);
    });
    doc.addEventListener("pdl:lang", chatChips);
    // Topic row: edge fades follow the scroll position; a vertical mouse wheel scrolls it sideways.
    var chipBox = $(".chat__chips", chat);
    var chipEdges = function () {
      var max = chipBox.scrollWidth - chipBox.clientWidth, x = chipBox.scrollLeft;
      chipBox.classList.toggle("is-fit", max < 2);
      chipBox.classList.toggle("is-end", max >= 2 && x >= max - 2);
      chipBox.classList.toggle("is-mid", x > 2 && x < max - 2);
    };
    chipBox.addEventListener("scroll", chipEdges, { passive: true });
    chipBox.addEventListener("wheel", function (e) {
      if (Math.abs(e.deltaY) <= Math.abs(e.deltaX) || chipBox.scrollWidth <= chipBox.clientWidth) return;
      e.preventDefault();
      chipBox.scrollBy({ left: e.deltaY, behavior: "instant" });
    }, { passive: false });
    window.addEventListener("resize", chipEdges);
    doc.addEventListener("pdl:lang", function () { chipBox.scrollLeft = 0; chipEdges(); });
    chat.addEventListener("transitionend", chipEdges);
  }

  /* ---------- Sub-navigation ---------- */
  var sub = $(".subnav");
  if (sub && "IntersectionObserver" in window) {
    var links = $$("a", sub), map = {};
    links.forEach(function (a) { var t = doc.getElementById(a.getAttribute("href").slice(1)); if (t) map[t.id] = a; });
    var sio = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (l) { l.classList.remove("is-active"); });
        var a = map[en.target.id];
        if (!a) return;
        a.classList.add("is-active");
        var ul = a.closest("ul"), r = a.getBoundingClientRect(), ur = ul.getBoundingClientRect();
        var bar = $(".subnav__bar", ul);
        if (!bar) { bar = doc.createElement("span"); bar.className = "subnav__bar"; ul.appendChild(bar); }
        bar.style.setProperty("--x", a.offsetLeft + "px");
        bar.style.setProperty("--w", a.offsetWidth + "px");
        if (r.left < ur.left || r.right > ur.right) ul.scrollTo({ left: ul.scrollLeft + r.left - ur.left - 16, behavior: reduce ? "auto" : "smooth" });
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    Object.keys(map).forEach(function (id) { sio.observe(doc.getElementById(id)); });
  }

  /* =================== Motion and interaction layer =================== */
  var motion = root.classList.contains("reveal-on");
  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches && !reduce;

  /* Word-by-word headings */
  function splitText(el) {
    var i = 0;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          if (!n.textContent.trim()) return;
          var frag = doc.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(doc.createTextNode(" ")); return; }
            var w = doc.createElement("span"); w.className = "w";
            var wi = doc.createElement("span"); wi.className = "wi"; wi.style.setProperty("--i", i++); wi.textContent = part;
            w.appendChild(wi); frag.appendChild(w);
          });
          node.replaceChild(frag, n);
        } else if (n.nodeType === 1 && !n.classList.contains("w")) walk(n);
      });
    })(el);
    el.classList.add("split");
  }
  var splitEls = [];
  if (motion && "IntersectionObserver" in window) {
    var hio = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("split-in"); hio.unobserve(e.target); } });
    }, { threshold: 0.2 });
    // Split each heading just before it scrolls into view, so the work is spread out.
    var pre = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target; pre.unobserve(el);
        splitText(el); splitEls.push(el);
        if (!el.closest(".rv")) onIntro(function () { hio.observe(el); });
      });
    }, { rootMargin: "0px 0px 400px 0px" });
    $$(".h-1, .h-2, .meet__name, .ba__tab strong").forEach(function (el) {
      if (el.classList.contains("is-split") || el.closest(".hero__title")) return;
      pre.observe(el);
    });
    doc.addEventListener("pdl:lang", function () {
      splitEls.forEach(function (el) { if (!$(".w", el)) { splitText(el); el.classList.add("split-in"); } });
    });
  }

  /* Hero: result slides and pointer depth */
  var slidesBox = $("[data-slides]");
  if (slidesBox) {
    var slideEls = $$(".hero__slide", slidesBox), caps = $$(".hero__cap", slidesBox), dotEls = $$(".hero__dots button", slidesBox);
    var si = 0, sTimer = null, SLIDE_MS = 4200, sPaused = false;
    slidesBox.style.setProperty("--slide-ms", SLIDE_MS + "ms");
    var goSlide = function (n) {
      si = (n + slideEls.length) % slideEls.length;
      slideEls.forEach(function (s, k) { s.classList.toggle("is-active", k === si); });
      caps.forEach(function (c, k) { c.classList.toggle("is-active", k === si); });
      dotEls.forEach(function (d) { d.setAttribute("aria-pressed", "false"); });
      requestAnimationFrame(function () { requestAnimationFrame(function () { dotEls[si] && dotEls[si].setAttribute("aria-pressed", "true"); }); });
    };
    var play = function () { clearInterval(sTimer); if (reduce || sPaused) return; sTimer = setInterval(function () { goSlide(si + 1); }, SLIDE_MS); };
    dotEls.forEach(function (d, k) { d.addEventListener("click", function () { goSlide(k); play(); }); });
    slidesBox.addEventListener("mouseenter", function () { sPaused = true; clearInterval(sTimer); $(".hero__dots", slidesBox).classList.add("is-static"); });
    slidesBox.addEventListener("mouseleave", function () { sPaused = false; $(".hero__dots", slidesBox).classList.remove("is-static"); goSlide(si); play(); });
    if (reduce) $(".hero__dots", slidesBox).classList.add("is-static");
    if ("IntersectionObserver" in window) new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) play(); else clearInterval(sTimer); }); }).observe(slidesBox);
    else play();
    doc.addEventListener("visibilitychange", function () { if (doc.hidden) clearInterval(sTimer); else play(); });
  }
  var heroMedia = $(".hero__media");
  if (heroMedia && finePointer) {
    var hero = $(".hero");
    hero.addEventListener("pointermove", function (e) {
      var r = hero.getBoundingClientRect();
      heroMedia.style.setProperty("--mx", ((e.clientX - r.left) / r.width * 2 - 1).toFixed(3));
      heroMedia.style.setProperty("--my", ((e.clientY - r.top) / r.height * 2 - 1).toFixed(3));
    });
    hero.addEventListener("pointerleave", function () { heroMedia.style.setProperty("--mx", 0); heroMedia.style.setProperty("--my", 0); });
  }

  /* Marquees: pause off screen, pause button per section */
  var mqs = $$("[data-marquee]");
  if (mqs.length && "IntersectionObserver" in window) {
    var mio = new IntersectionObserver(function (es) { es.forEach(function (e) { e.target.classList.toggle("is-off", !e.isIntersecting); }); });
    mqs.forEach(function (m) { mio.observe(m); });
  }
  $$(".marquee__toggle").forEach(function (b) {
    var sec = b.closest("section");
    b.addEventListener("click", function () {
      var on = b.getAttribute("aria-pressed") !== "true";
      b.setAttribute("aria-pressed", String(on));
      var lab = on ? { sv: "Starta rörelsen", en: "Play motion" } : { sv: "Pausa rörelsen", en: "Pause motion" };
      b.setAttribute("aria-label", L(lab)); b.setAttribute("data-sv-aria-label", lab.sv); b.setAttribute("data-en-aria", lab.en);
      $$("[data-marquee]", sec).forEach(function (m) { m.classList.toggle("is-paused", on); });
    });
  });

  /* Before / after slider */
  var baPanes = $$("[data-ba]");
  baPanes.forEach(function (ba) {
    var range = $(".ba__range", ba), dragging = false;
    var setPos = function (p) { p = Math.max(0, Math.min(100, p)); ba.style.setProperty("--pos", p + "%"); range.value = Math.round(p); };
    var fromEvent = function (e) { var r = ba.getBoundingClientRect(); setPos((e.clientX - r.left) / r.width * 100); };
    ba.addEventListener("pointerdown", function (e) {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      dragging = true; ba.classList.remove("is-hint"); ba.classList.add("is-drag");
      if (e.pointerType === "mouse") ba.setPointerCapture(e.pointerId);
      fromEvent(e);
    });
    ba.addEventListener("pointermove", function (e) {
      if (!dragging) return;
      if (e.pointerType !== "mouse") { var r = ba.getBoundingClientRect(); if (Math.abs(e.movementY) > Math.abs(e.movementX) * 1.5 && !ba.__lockX) return; ba.__lockX = true; }
      fromEvent(e);
    });
    var stop = function () { dragging = false; ba.__lockX = false; ba.classList.remove("is-drag"); };
    ba.addEventListener("pointerup", stop); ba.addEventListener("pointercancel", stop); ba.addEventListener("lostpointercapture", stop);
    range.addEventListener("input", function () { ba.classList.remove("is-hint"); setPos(+range.value); });
  });
  if (baPanes.length) {
    var baBook = $("[data-ba-book]");
    $$("[data-ba-tab]").forEach(function (t) {
      t.addEventListener("click", function () {
        var k = t.getAttribute("data-ba-tab");
        $$("[data-ba-tab]").forEach(function (x) { x.setAttribute("aria-pressed", String(x === t)); });
        baPanes.forEach(function (p) {
          var on = p.getAttribute("data-key") === k;
          p.hidden = !on;
          if (on) { p.style.setProperty("--pos", "50%"); $(".ba__range", p).value = 50; if (!reduce) { p.classList.remove("is-enter"); void p.offsetWidth; p.classList.add("is-enter"); } if (baBook) baBook.href = p.getAttribute("data-book"); }
        });
      });
    });
    if (!reduce && "IntersectionObserver" in window) {
      var bio = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { setTimeout(function () { e.target.classList.add("is-hint"); }, 700); bio.unobserve(e.target); } });
      }, { threshold: 0.5 });
      bio.observe(baPanes[0]);
    }
  }

  /* Contextual cursor */
  var cursor = $(".cursor");
  if (cursor && finePointer) {
    root.classList.add("has-cursor");
    var CUR = { view: { sv: "Visa", en: "View" }, drag: { sv: "Dra", en: "Drag" }, read: { sv: "Läs", en: "Read" }, open: { sv: "Öppna", en: "Open" } };
    var tag = function (sel, key) { $$(sel).forEach(function (el) { el.setAttribute("data-cursor", key); }); };
    tag(".rtrack", "drag"); tag("[data-gallery] .rcard button", "view"); tag("[data-ba]", "drag");
    // Only where the pointer is over pictures to drag or open; never over text rows or cards, where it hid the words.
    var cx = -200, cy = -200, tx_ = -200, ty_ = -200, raf = null, curKey = null;
    var loop = function () {
      cx += (tx_ - cx) * 0.22; cy += (ty_ - cy) * 0.22;
      cursor.style.translate = cx.toFixed(1) + "px " + cy.toFixed(1) + "px";
      raf = (Math.abs(tx_ - cx) > 0.3 || Math.abs(ty_ - cy) > 0.3) ? requestAnimationFrame(loop) : null;
    };
    doc.addEventListener("pointermove", function (e) {
      if (e.pointerType !== "mouse") return;
      tx_ = e.clientX; ty_ = e.clientY;
      if (!curKey) { cx = tx_; cy = ty_; }
      var el = e.target.closest && e.target.closest("[data-cursor]");
      var key = el ? el.getAttribute("data-cursor") : null;
      if (key !== curKey) {
        curKey = key;
        cursor.classList.toggle("is-on", !!key);
        if (key) $(".cursor__label", cursor).textContent = L(CUR[key]);
      }
      if (!raf) raf = requestAnimationFrame(loop);
    }, { passive: true });
    doc.addEventListener("pointerleave", function () { curKey = null; cursor.classList.remove("is-on"); });
    window.addEventListener("blur", function () { curKey = null; cursor.classList.remove("is-on"); });
  }

  /* Reviews: one featured quote at a time. Auto-advance is driven by the progress line's CSS animation
     (animationend = next), so pausing it on hover, focus, off screen or with the button is just a class. */
  var rvw = $("[data-rvw]");
  if (rvw) {
    var rq = $$(".rvw__q", rvw), rtabs = $$(".rvw__tab", rvw), rStage = $(".rvw__stage", rvw), rCount = $("[data-rvw-count]", rvw);
    var rPlay = $("[data-rvw-play]", rvw), rTabsBox = $(".rvw__tabs", rvw), ri = 0, rUser = false, rHover = false, rSeen = false;
    var two = function (n) { return (n < 10 ? "0" : "") + n; };
    // The stage takes the height of the quote on show (not the longest one), easing between sizes.
    var rFit = function () { rStage.style.height = rq[ri].offsetHeight + "px"; };
    var rState = function () {
      rvw.classList.toggle("is-auto", !reduce);
      rvw.classList.toggle("is-paused", rUser || rHover || !rSeen);
      if (rPlay) { rPlay.setAttribute("aria-pressed", String(rUser)); rPlay.hidden = reduce; }
    };
    var rShow = function (n, byUser) {
      n = (n + rq.length) % rq.length;
      if (n === ri) return;
      var old = rq[ri];
      old.classList.add("is-leaving"); old.classList.remove("is-active");
      setTimeout(function () { old.classList.remove("is-leaving"); }, 500);
      rq[n].classList.add("is-active");
      ri = n; rFit();
      rtabs.forEach(function (t, i) { t.setAttribute("aria-selected", String(i === n)); t.tabIndex = i === n ? 0 : -1; });
      ri = n;
      if (rCount) rCount.textContent = two(n + 1) + " / " + two(rq.length);
      rStage.setAttribute("aria-live", byUser ? "polite" : "off");
      var t = rtabs[n];
      if (rTabsBox.scrollWidth > rTabsBox.clientWidth) rTabsBox.scrollTo({ left: t.offsetLeft - rTabsBox.offsetLeft - 16, behavior: reduce ? "auto" : "smooth" });
    };
    rtabs.forEach(function (t, i) {
      t.addEventListener("click", function () { rShow(i, true); });
      t.addEventListener("animationend", function (e) { if (e.animationName === "rvw-prog" && i === ri) rShow(ri + 1, false); });
      t.addEventListener("keydown", function (e) {
        var k = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (!k) return;
        e.preventDefault(); rShow(ri + k, true); rtabs[ri].focus();
      });
    });
    var rp = $("[data-rvw-prev]", rvw), rn = $("[data-rvw-next]", rvw);
    if (rp) rp.addEventListener("click", function () { rShow(ri - 1, true); });
    if (rn) rn.addEventListener("click", function () { rShow(ri + 1, true); });
    if (rPlay) rPlay.addEventListener("click", function () { rUser = !rUser; rState(); });
    rvw.addEventListener("mouseenter", function () { rHover = true; rState(); });
    rvw.addEventListener("mouseleave", function () { rHover = false; rState(); });
    rvw.addEventListener("focusin", function () { rHover = true; rState(); });
    rvw.addEventListener("focusout", function (e) { if (!rvw.contains(e.relatedTarget)) { rHover = false; rState(); } });
    if ("IntersectionObserver" in window) new IntersectionObserver(function (es) { rSeen = es[0].isIntersecting; rState(); }, { threshold: 0.25 }).observe(rvw);
    else rSeen = true;
    rFit();
    window.addEventListener("resize", rFit);
    doc.addEventListener("pdl:lang", rFit);
    if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(rFit);
    rState();
  }

  /* How it works: the card on top of the deck lights its index entry; covered cards ease back */
  var deck = $("[data-jdeck]");
  if (deck) {
    var jcards = $$(".jcard", deck), jlinks = $$("[data-jindex]"), jcur = -1, jstuck = -1, jtick = false, jtops = [];
    var stacked = function () { return getComputedStyle(jcards[0]).position === "sticky"; };
    var measure = function () { jtops = jcards.map(function (c) { return parseFloat(getComputedStyle(c).top) || 0; }); };
    // Where card i sits in the flow, measured from layout so reveal and scale transforms never skew it.
    var flowTop = function (i) {
      var gap = parseFloat(getComputedStyle(deck).rowGap) || 0, y = deck.getBoundingClientRect().top;
      for (var j = 0; j < i; j++) y += jcards[j].offsetHeight + gap;
      return y;
    };
    var jupdate = function () {
      jtick = false;
      var st = stacked(), line = window.innerHeight * 0.5, active = 0;
      // The index switches once a card has slid most of the way up; a card only eases back once the next is pinned on it.
      var early = window.innerHeight * 0.3, stuck = 0;
      jcards.forEach(function (c, i) {
        var t = flowTop(i);
        if (t <= (st ? jtops[i] + early : line)) active = i;
        if (st && t <= jtops[i] + 2) stuck = i;
      });
      if (active === jcur && stuck === jstuck) return;
      jcur = active; jstuck = stuck;
      jlinks.forEach(function (a, i) {
        a.classList.toggle("is-active", i === active);
        if (i === active) a.setAttribute("aria-current", "step"); else a.removeAttribute("aria-current");
      });
      jcards.forEach(function (c, i) { c.classList.toggle("is-covered", st && i < stuck); });
    };
    measure(); jupdate();
    window.addEventListener("scroll", function () { if (!jtick) { jtick = true; requestAnimationFrame(jupdate); } }, { passive: true });
    window.addEventListener("resize", function () { measure(); jcur = -1; jstuck = -1; jupdate(); });
    // A stuck card's anchor position is wherever it is pinned, so work out where it sits in the flow instead.
    jlinks.forEach(function (a, i) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        window.scrollTo({ top: flowTop(i) + window.scrollY - (stacked() ? jtops[i] : 140) + 1, behavior: reduce ? "auto" : "smooth" });
      });
    });
  }

  /* Path cards: push the body down by the chip row's height so the chips wait below the card edge */
  $$(".path").forEach(function (card) {
    var body = $(".path__body", card), more = $(".path__more", card);
    if (!body || !more) return;
    var set = function () {
      var h = more.offsetHeight;
      card.style.setProperty("--more-h", h ? (h + (parseFloat(getComputedStyle(body).rowGap) || 0)) + "px" : "0px");
    };
    set();
    if ("ResizeObserver" in window) new ResizeObserver(set).observe(more);
  });

  /* Course rows: floating image preview */
  var cpv = $(".cpreview"), cRows = $$("[data-preview]");
  if (cpv && cRows.length && finePointer) {
    var pimg = $("img", cpv), qx = 0, qy = 0, gx = 0, gy = 0, qraf = null;
    var qloop = function () {
      qx += (gx - qx) * 0.16; qy += (gy - qy) * 0.16;
      cpv.style.setProperty("--qx", qx.toFixed(1) + "px"); cpv.style.setProperty("--qy", qy.toFixed(1) + "px");
      qraf = (Math.abs(gx - qx) > 0.3 || Math.abs(gy - qy) > 0.3) ? requestAnimationFrame(qloop) : null;
    };
    cRows.forEach(function (a) {
      a.addEventListener("mouseenter", function (e) {
        if (pimg.getAttribute("src") !== a.getAttribute("data-preview")) pimg.src = a.getAttribute("data-preview");
        gx = e.clientX + 28; gy = e.clientY - 150;
        if (!cpv.classList.contains("is-on")) { qx = gx; qy = gy; }
        cpv.classList.add("is-on");
        if (!qraf) qraf = requestAnimationFrame(qloop);
      });
      a.addEventListener("mousemove", function (e) { gx = e.clientX + 28; gy = e.clientY - 150; if (!qraf) qraf = requestAnimationFrame(qloop); });
      a.addEventListener("mouseleave", function () { cpv.classList.remove("is-on"); });
    });
  }

  /* Magnetic buttons */
  if (finePointer) {
    // Not the floating chat button: a fixed control that drifts with the pointer feels unstable.
    $$(".btn--primary, .btn--light, .round-btn, .nav__book").forEach(function (b) {
      b.addEventListener("pointermove", function (e) {
        var r = b.getBoundingClientRect();
        var dx = (e.clientX - r.left) / r.width - 0.5, dy = (e.clientY - r.top) / r.height - 0.5;
        b.style.translate = (dx * 10).toFixed(1) + "px " + (dy * 8).toFixed(1) + "px";
      });
      b.addEventListener("pointerleave", function () { b.style.translate = ""; });
    });
  }

  /* Count up numbers when they appear */
  var counters = $$("[data-count]");
  if (counters.length && motion && "IntersectionObserver" in window) {
    var cio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        cio.unobserve(e.target);
        var el = e.target, txt = el.textContent, m = txt.match(/\d[\d\s., ]*\d|\d/);
        if (!m) return;
        var target = parseInt(m[0].replace(/[^\d]/g, ""), 10), pre = txt.slice(0, m.index), post = txt.slice(m.index + m[0].length);
        var loc = lang === "en" ? "en-GB" : "sv-SE", start = null, dur = 1500, myLang = lang;
        var fmt = function (n) { var s = n.toLocaleString(loc); return target >= 1000 ? s : String(n); };
        var step = function (t) {
          if (lang !== myLang) return;
          if (!start) start = t;
          var k = Math.min(1, (t - start) / dur), v = Math.round(target * (1 - Math.pow(1 - k, 3)));
          el.textContent = pre + fmt(v) + post;
          if (k < 1) requestAnimationFrame(step); else el.textContent = txt;
        };
        requestAnimationFrame(step);
      });
    }, { threshold: 0.6 });
    onIntro(function () { counters.forEach(function (c) { cio.observe(c); }); });
  }

  /* Results track: drag to scroll with a mouse */
  $$(".rtrack").forEach(function (tr) {
    var down = false, sx = 0, sl = 0, moved = false;
    tr.addEventListener("pointerdown", function (e) { if (e.pointerType !== "mouse" || e.button !== 0) return; down = true; moved = false; sx = e.clientX; sl = tr.scrollLeft; tr.style.scrollSnapType = "none"; });
    window.addEventListener("pointermove", function (e) { if (!down) return; var dx = e.clientX - sx; if (Math.abs(dx) > 4) moved = true; tr.scrollLeft = sl - dx; });
    window.addEventListener("pointerup", function () { if (!down) return; down = false; tr.style.scrollSnapType = ""; });
    tr.addEventListener("click", function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
    tr.addEventListener("dragstart", function (e) { e.preventDefault(); });
  });
})();
