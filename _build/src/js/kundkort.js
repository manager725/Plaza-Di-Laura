/* Plaza Di Laura: Kundkort (staff app prototype). All clients are fictional examples. */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var lang = function () { return root.getAttribute("data-lang") === "en" ? "en" : "sv"; };
  var L = function (o) { if (o == null) return ""; if (typeof o === "string") return o; return o[lang()] != null ? o[lang()] : o.sv; };
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var DATA = JSON.parse($("#kk-data").textContent);
  var TR = DATA.treatments;
  var ss = { get: function (k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }, set: function (k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} } };

  /* ---------- Dates ---------- */
  var today = new Date(); today.setHours(12, 0, 0, 0);
  var day = function (n) { var d = new Date(today); d.setDate(d.getDate() + n); return d; };
  var loc = function () { return lang() === "en" ? "en-GB" : "sv-SE"; };
  var fmt = function (d, long) { try { return d.toLocaleDateString(loc(), long ? { weekday: "short", day: "numeric", month: "long", year: "numeric" } : { day: "numeric", month: "short", year: "numeric" }); } catch (e) { return d.toDateString(); } };
  var daysFrom = function (d) { return Math.round((d - today) / 864e5); };
  var rel = function (d) {
    var n = daysFrom(d), en = lang() === "en";
    if (n === 0) return en ? "today" : "idag";
    if (n === 1) return en ? "tomorrow" : "imorgon";
    if (n === -1) return en ? "yesterday" : "igår";
    if (n > 0) return en ? "in " + n + " days" : "om " + n + " dagar";
    return en ? -n + " days ago" : "för " + -n + " dagar sedan";
  };

  /* ---------- Strings ---------- */
  var S = {
    sections: [
      ["history", { sv: "Klienthistorik", en: "Client history" }], ["payments", { sv: "Betalningar", en: "Payments" }],
      ["treatments", { sv: "Behandlingar", en: "Treatments" }], ["health", { sv: "Hälsodeklaration", en: "Medical record" }],
      ["bookings", { sv: "Bokningar", en: "Bookings" }], ["photos", { sv: "Dok. bilder", en: "Doc. photos" }],
      ["consent", { sv: "Samtycke", en: "Consent form" }], ["contact", { sv: "Kontakt", en: "Contact" }]
    ],
    secTitles: { history: { sv: "Klienthistorik", en: "Client history" }, treatments: { sv: "Behandlingar", en: "Treatments" }, bookings: { sv: "Bokningar", en: "Bookings" }, consent: { sv: "Samtycke", en: "Consent form" }, payments: { sv: "Betalningar", en: "Payments" }, health: { sv: "Hälsodeklaration", en: "Medical record" }, photos: { sv: "Dokumentationsbilder", en: "Documentation photos" }, contact: { sv: "Kontakt", en: "Contact" } },
    since: { sv: "Kund sedan", en: "Client since" }, example: { sv: "Exempelkund", en: "Example client" },
    newFromWeb: { sv: "Ny bokning via webbplatsen", en: "New booking from the website" },
    touchup: { sv: "Återbesök", en: "Touch-up" }, first: { sv: "Första behandling", en: "First treatment" }, refill: { sv: "Refill", en: "Refill" },
    consult: { sv: "Kostnadsfri konsultation", en: "Free consultation" }, courseAdvice: { sv: "Kostnadsfri kursrådgivning", en: "Free course advice" },
    session2: { sv: "Besök 2 av 2", en: "Visit 2 of 2" }, session1: { sv: "Besök 1 av 2", en: "Visit 1 of 2" },
    dueSoon: { sv: "Återbesök snart", en: "Touch-up soon" }, refillLate: { sv: "Refill försenad", en: "Refill overdue" }, refillDue: { sv: "Refill inom", en: "Refill due" },
    newTag: { sv: "Ny", en: "New" }, academy: { sv: "Akademi", en: "Academy" }, flag: { sv: "Kontrollera hälsa", en: "Check health" },
    signed: { sv: "Signerat med BankID", en: "Signed with BankID" }, unsigned: { sv: "Inte signerat än", en: "Not signed yet" },
    paid: { sv: "Betald", en: "Paid" }, pending: { sv: "Väntar", en: "Pending" }, perList: { sv: "Enligt prislista", en: "Per price list" },
    artist: { sv: "Behandlare", en: "Practitioner" }, pigment: { sv: "Pigment", en: "Pigment" }, needle: { sv: "Nål", en: "Needle" },
    numbing: { sv: "Bedövning", en: "Numbing" }, numbingVal: { sv: "Bedövningssalva före och under", en: "Numbing cream before and during" },
    aftercare: { sv: "Eftervård", en: "Aftercare" }, aftercareVal: { sv: "Ingår, instruktioner givna", en: "Included, instructions given" },
    method: { sv: "Metod", en: "Method" }, notes: { sv: "Anteckning", en: "Note" },
    noPhotos: { sv: "Inga bilder än. Bilder läggs till efter varje besök: före, direkt efter och läkt.", en: "No photos yet. Photos are added after every visit: before, right after and healed." },
    noPayments: { sv: "Inga betalningar än.", en: "No payments yet." },
    noTreat: { sv: "Ingen behandling utförd än.", en: "No treatment carried out yet." },
    before: { sv: "Före", en: "Before" }, after: { sv: "Direkt efter", en: "Right after" }, healed: { sv: "Läkt", en: "Healed" },
    exPhoto: { sv: "Exempelbilder från resultatgalleriet", en: "Example photos from the results gallery" },
    addPhoto: { sv: "Lägg till bild", en: "Add photo" }, compare: { sv: "Jämför före och efter", en: "Compare before and after" },
    remind: { sv: "Skicka påminnelse", en: "Send reminder" }, bookTouch: { sv: "Boka återbesök", en: "Book touch-up" }, confirm: { sv: "Bekräfta tid", en: "Confirm time" },
    view: { sv: "Visa", en: "View" }, sendSign: { sv: "Skicka för signering", en: "Send for signing" }, previewClient: { sv: "Visa som kunden ser det", en: "View as the client sees it" },
    phone: { sv: "Telefon", en: "Phone" }, email: { sv: "E-post", en: "Email" }, city: { sv: "Ort", en: "City" }, pref: { sv: "Föredrar", en: "Prefers" }, marketing: { sv: "Nyhetsutskick", en: "Newsletter" },
    yes: { sv: "Ja", en: "Yes" }, no: { sv: "Nej", en: "No" }, sms: { sv: "Sms", en: "Text message" },
    requested: { sv: "Önskade dagar", en: "Preferred days" }, awaiting: { sv: "Väntar på bekräftelse", en: "Awaiting confirmation" },
    upcoming: { sv: "Kommande", en: "Upcoming" }, past: { sv: "Tidigare", en: "Past" },
    validFor: { sv: "Gäller besöket", en: "Valid for the visit" },
    toast: {
      remind: { sv: "Påminnelse skickad via sms (demo)", en: "Reminder sent by text (demo)" },
      sign: { sv: "Samtyckesformulär skickat för BankID-signering (demo)", en: "Consent form sent for BankID signing (demo)" },
      confirm: { sv: "Tiden bekräftad och kunden får ett sms (demo)", en: "Time confirmed, the client gets a text (demo)" },
      photo: { sv: "Här öppnas kameran i den riktiga appen (demo)", en: "The real app opens the camera here (demo)" },
      call: { sv: "Samtal och sms kopplas på i den riktiga appen (demo)", en: "Calls and texts connect in the real app (demo)" }
    },
    filters: [["all", { sv: "Alla", en: "All" }], ["soon", { sv: "Återbesök snart", en: "Touch-up soon" }], ["refill", { sv: "Refill", en: "Refill" }], ["new", { sv: "Nya", en: "New" }], ["academy", { sv: "Akademi", en: "Academy" }]],
    stats: { today: { sv: "besök idag", en: "visits today" }, week: { sv: "återbesök inom 7 dagar", en: "touch-ups within 7 days" }, refill: { sv: "refill att påminna om", en: "refills to remind" }, unsigned: { sv: "osignerade formulär", en: "unsigned forms" } },
    none: { sv: "Inga klienter matchar.", en: "No clients match." },
    nextLbl: { sv: "Nästa", en: "Next" },
    healthQ: [
      ["pregnant", { sv: "Gravid", en: "Pregnant" }], ["thinners", { sv: "Äter blodförtunnande medicin", en: "Takes blood-thinning medication" }],
      ["skin", { sv: "Sår, utslag eller eksem på området", en: "Wounds, rashes or eczema on the area" }], ["blood", { sv: "Blodsmittande sjukdom", en: "Blood-borne disease" }],
      ["under18", { sv: "Under 18 år", en: "Under 18" }], ["prev", { sv: "Tidigare tatuering i området", en: "Previous tattoo in the area" }], ["allergy", { sv: "Kända allergier", en: "Known allergies" }]
    ],
    lauraList: { sv: "Lauras kontraindikationer", en: "Laura's contraindications" }, extra: { sv: "Övrigt", en: "Other" },
    consentItems: [
      { sv: "Effekten är inte permanent utan varar i ca 1,5–3 år.", en: "The effect is not permanent and lasts about 1.5–3 years." },
      { sv: "Behandlingen kräver ett återbesök efter ca 4–6 veckor för ett färdigt resultat.", en: "The treatment needs a touch-up after about 4–6 weeks for the finished result." },
      { sv: "Refill bör göras inom 12 månader. Annars kan tatueringen få läka bort.", en: "A refill should be done within 12 months. Otherwise the tattoo can be left to fade." },
      { sv: "Avbokning ska ske minst 24 timmar innan behandlingen.", en: "Cancellations must be made at least 24 hours before the treatment." },
      { sv: "Om behandlingen inte kan utföras på grund av kontraindikationer debiteras 50 %.", en: "If the treatment cannot be carried out because of contraindications, 50% is charged." },
      { sv: "Jag har svarat sanningsenligt på hälsodeklarationen.", en: "I have answered the health declaration truthfully." }
    ]
  };

  /* ---------- Example clients (fictional) ---------- */
  var T = function (slug) { return TR[slug] ? TR[slug].name : { sv: slug, en: slug }; };
  var clients = [
    { id: "anna", name: "Anna Andersson", since: -40, tags: ["pmu"], phone: "070-174 06 05", email: "anna.andersson@exempel.se", city: "Göteborg", pref: "sms", marketing: true,
      visits: [{ d: -38, t: "puderbryn", kind: "first", artist: "Laura Lindqvist", pigment: { sv: "Varm mellanbrun, anpassad efter underton", en: "Warm medium brown, matched to undertone" }, needle: { sv: "Skuggningsnål", en: "Shading needle" }, note: { sv: "Önskar mjuk start vid näsroten.", en: "Wants a soft start at the bridge of the nose." } }],
      upcoming: [{ d: 3, t: "puderbryn", kind: "touchup", time: "10:00" }],
      refillBy: 327, consent: -39, health: { d: -39, a: {} },
      payments: [{ d: -38, item: "puderbryn", method: "Swish", status: "paid" }], photos: { set: "bryn", d: -38 } },
    { id: "maria", name: "Maria Svensson", since: -420, tags: ["pmu"], phone: "070-174 06 12", email: "maria.svensson@exempel.se", city: "Mölndal", pref: "email", marketing: false,
      visits: [{ d: -410, t: "lappar", kind: "first", artist: "Laura Lindqvist", pigment: { sv: "Naturlig rosé", en: "Natural rosé" }, needle: { sv: "Läppnål", en: "Lip needle" }, note: { sv: "Peelade och återfuktade enligt instruktion.", en: "Exfoliated and moisturised as instructed." } },
             { d: -378, t: "lappar", kind: "touchup", artist: "Laura Lindqvist", pigment: { sv: "Naturlig rosé", en: "Natural rosé" }, needle: { sv: "Läppnål", en: "Lip needle" } }],
      upcoming: [], refillBy: -45, consent: -411, health: { d: -411, a: {} },
      payments: [{ d: -410, item: "lappar", method: { sv: "Kort", en: "Card" }, status: "paid" }], photos: { set: "lappar", d: -410 } },
    { id: "sara", name: "Sara Lindberg", since: -22, tags: ["pmu"], phone: "070-174 06 21", email: "sara.lindberg@exempel.se", city: "Göteborg", pref: "sms", marketing: true,
      visits: [{ d: -20, t: "fraknar", kind: "first", artist: "Laura Lindqvist", pigment: { sv: "Ljusbrun, varierande nyans", en: "Light brown, varied tones" }, needle: { sv: "Fräknenål", en: "Freckle needle" }, note: { sv: "Fräknar placerade asymmetriskt över näsa och kinder.", en: "Freckles placed asymmetrically over nose and cheeks." } }],
      upcoming: [], refillBy: 345, consent: -21, health: { d: -21, a: {} },
      payments: [{ d: -20, item: "fraknar", method: "Swish", status: "paid" }], photos: { set: "fraknar", d: -20 } },
    { id: "johan", name: "Johan Berg", since: -16, tags: ["smp"], phone: "070-174 06 33", email: "johan.berg@exempel.se", city: "Kungälv", pref: "sms", marketing: false,
      visits: [{ d: -14, t: "smp", kind: "session1", artist: "Robert Tomaszewski", pigment: { sv: "Anpassat efter hårfärg och hudton", en: "Matched to hair colour and skin tone" }, needle: { sv: "SMP-nål", en: "SMP needle" } }],
      upcoming: [{ d: 9, t: "smp", kind: "session2", time: "13:00" }], refillBy: null, consent: -15, health: { d: -15, a: {} },
      payments: [{ d: -14, item: "smp", method: { sv: "Kort", en: "Card" }, status: "paid" }], photos: null },
    { id: "karin", name: "Karin Nilsson", since: -3, tags: ["pmu"], phone: "070-174 06 47", email: "karin.nilsson@exempel.se", city: "Partille", pref: "email", marketing: true,
      visits: [], upcoming: [{ d: 0, t: "konsultation", kind: "consult", time: "15:30", forT: "lift" }], refillBy: null, consent: null,
      health: { d: -2, a: { prev: { sv: "Ja, gammal microblading som blivit grå", en: "Yes, old microblading that has turned grey" } } },
      payments: [], photos: null, note: { sv: "Gammal tatuering i brynen. Bedöm LIFT Ink Removal innan ny behandling.", en: "Old tattoo in the brows. Assess LIFT Ink Removal before any new treatment." } },
    { id: "elin", name: "Elin Johansson", since: -30, tags: ["academy"], phone: "070-174 06 58", email: "elin.johansson@exempel.se", city: "Borås", pref: "email", marketing: true,
      visits: [], upcoming: [{ d: 25, t: "course", kind: "course", time: "09:00" }], refillBy: null, consent: null, health: null,
      payments: [{ d: -28, item: "course", method: "Qliro", status: "paid", amount: DATA.coursePrice }], photos: null }
  ];

  var CROP = { anna: "50% 22%", maria: "50% 62%", sara: "52% 70%", johan: "38% 78%", karin: "50% 18%", elin: "50% 55%" };
  clients.forEach(function (c) { if (DATA.avatars && DATA.avatars[c.id]) { c.pic = DATA.avatars[c.id]; c.pos = CROP[c.id] || "50% 50%"; } });

  /* A booking sent from the website in this session becomes a new client */
  try {
    var b = JSON.parse(ss.get("pdl-booking") || "null");
    if (b && b.fname) {
      var dates = (b.dates || []).map(function (iso) { return daysFrom(new Date(iso + "T12:00:00")); });
      clients.unshift({ id: "web", isNew: true, name: (b.fname + " " + (b.lname || "")).trim(), since: 0, tags: b.what === "kursradgivning" ? ["academy", "new"] : ["new"],
        phone: (b.cc || "+46") + " " + (b.phone || ""), email: b.email || "", city: "", pref: b.remind === "email" ? "email" : "sms", marketing: false,
        visits: [], requested: { what: b.what, dates: dates, tod: b.tod, flex: !!b.flex }, upcoming: [], refillBy: null, consent: null,
        health: b.health ? { d: 0, a: (function () { var a = {}; var ha = b.healthAnswers || {}; Object.keys(ha).forEach(function (k) { if (ha[k] === "yes") a[k] = { sv: "Ja", en: "Yes" }; }); if (b.health === "yes" && !Object.keys(a).length) a.flag = true; return a; })(), fromWeb: true } : null,
        payments: [], photos: null, message: b.message || "" });
    }
  } catch (e) {}

  var nameOf = function (slug) {
    if (slug === "konsultation") return S.consult;
    if (slug === "kursradgivning") return S.courseAdvice;
    if (slug === "course") return DATA.courseName;
    return T(slug);
  };
  var kindLbl = function (k) { return { first: S.first, touchup: S.touchup, session1: S.session1, session2: S.session2, consult: S.consult, course: DATA.courseName }[k] || ""; };
  var initials = function (n) { return n.split(/\s+/).map(function (p) { return p.charAt(0); }).join("").slice(0, 2).toUpperCase(); };
  var nextOf = function (c) { return (c.upcoming || []).slice().sort(function (a, b) { return a.d - b.d; })[0]; };
  var status = function (c) {
    var out = [], n = nextOf(c);
    if (c.isNew) out.push(["new", S.newTag]);
    if (n && n.kind === "touchup" && n.d >= 0 && n.d <= 7) out.push(["due", S.dueSoon]);
    if (c.refillBy != null && c.refillBy < 0) out.push(["warn", S.refillLate]);
    else if (c.refillBy != null && c.refillBy < 60) out.push(["due", S.refillDue]);
    if (c.tags.indexOf("academy") > -1) out.push(["", S.academy]);
    if (c.health && Object.keys(c.health.a || {}).length) out.push(["warn", S.flag]);
    return out;
  };
  var badge = function (s) { return '<span class="badge' + (s[0] ? " badge--" + s[0] : "") + '">' + esc(L(s[1])) + "</span>"; };

  /* ---------- Icons ---------- */
  var I = {
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/></svg>',
    back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>',
    phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M6.5 3.5h3l1.5 4-2 1.5a11 11 0 0 0 6 6l1.5-2 4 1.5v3a2 2 0 0 1-2 2A16.5 16.5 0 0 1 4.5 5.5a2 2 0 0 1 2-2Z"/></svg>',
    sms: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 5.5h16v10H9l-5 4v-14Z"/></svg>',
    mail: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="3.5" y="5.5" width="17" height="13" rx="1.5"/><path d="m4 7 8 6 8-6"/></svg>',
    cal: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15.5" rx="1.5"/><path d="M3.5 9.5h17M8 3v4M16 3v4M12 12.5v5M9.5 15h5"/></svg>',
    cam: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 8h3l1.5-2.5h7L17 8h3v11H4z"/><circle cx="12" cy="13.5" r="3.5"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>'
  };

  /* ---------- Toast and modal ---------- */
  var toastEl = $(".toast"), toastT = null;
  var toast = function (msg) { toastEl.innerHTML = I.check + esc(L(msg)); toastEl.classList.add("is-on"); clearTimeout(toastT); toastT = setTimeout(function () { toastEl.classList.remove("is-on"); }, 2600); };
  var modal = $(".app-modal");
  var openModal = function (title, html) {
    $(".app-modal__head h2", modal).textContent = L(title);
    $(".app-modal__body", modal).innerHTML = html;
    if (modal.showModal) modal.showModal(); else modal.setAttribute("open", "");
  };
  $(".app-modal__close", modal).addEventListener("click", function () { modal.close ? modal.close() : modal.removeAttribute("open"); });
  modal.addEventListener("click", function (e) { if (e.target === modal) modal.close(); });

  /* ---------- Login ---------- */
  var login = $(".login"), app = $(".app");
  var EMBED = /[?&]embed=1/.test(location.search);
  if (EMBED) { root.classList.add("is-embed"); var sb = doc.createElement("div"); sb.className = "status-bar"; sb.setAttribute("aria-hidden", "true"); doc.body.appendChild(sb); }
  var enter = function () {
    login.hidden = true; app.hidden = false; renderAll();
    var want = location.hash.slice(1), m = want.match(/^c=(\w+)/);
    if (want === "ny" && clients[0].isNew) openClient("web");
    else if (m && byId(m[1])) openClient(m[1]);
    else if (window.innerWidth >= 960) openClient(clients[0].id, true);
  };
  $$("[data-login]").forEach(function (b) {
    b.addEventListener("click", function () {
      $(".login__btns").hidden = true; $(".login__wait").hidden = false;
      setTimeout(function () { ss.set("pdl-staff", "1"); enter(); }, reduce ? 50 : 1400);
    });
  });

  /* ---------- List ---------- */
  var filter = "all", query = "";
  var matches = function (c) {
    var n = nextOf(c);
    if (query && c.name.toLowerCase().indexOf(query) === -1 && c.email.toLowerCase().indexOf(query) === -1) return false;
    if (filter === "soon") return n && n.kind === "touchup" && n.d >= 0 && n.d <= 14;
    if (filter === "refill") return c.refillBy != null && c.refillBy < 60;
    if (filter === "new") return !!c.isNew || c.since > -7;
    if (filter === "academy") return c.tags.indexOf("academy") > -1;
    return true;
  };
  var subline = function (c) {
    var n = nextOf(c);
    if (c.isNew) return L(S.newFromWeb);
    if (n) return L(S.nextLbl) + ": " + L(nameOf(n.t)) + " · " + rel(day(n.d));
    var last = c.visits[c.visits.length - 1];
    return last ? L(nameOf(last.t)) + " · " + rel(day(last.d)) : "";
  };
  var current = null;
  function renderList() {
    var ul = $(".client-list"), rows = clients.filter(matches);
    ul.innerHTML = rows.length ? rows.map(function (c, i) {
      var st = status(c).slice(0, 1).map(badge).join("");
      return '<li><button type="button" class="client-row" data-client="' + c.id + '" aria-current="' + (c.id === current) + '" style="animation-delay:' + (reduce ? 0 : i * 45) + 'ms"><span class="avatar' + (c.pic ? " avatar--img" : "") + '">' + (c.pic ? '<img src="' + c.pic + '" alt="" loading="lazy" style="object-position:' + c.pos + '">' : initials(c.name)) + '</span><span><strong>' + esc(c.name) + "</strong><small>" + esc(subline(c)) + "</small></span>" + st + "</button></li>";
    }).join("") : '<li class="list-empty">' + esc(L(S.none)) + "</li>";
  }
  function renderStats() {
    var todayN = 0, week = 0, refill = 0, unsigned = 0;
    clients.forEach(function (c) {
      (c.upcoming || []).forEach(function (u) { if (u.d === 0) todayN++; if (u.kind === "touchup" && u.d >= 0 && u.d <= 7) week++; });
      if (c.refillBy != null && c.refillBy < 60) refill++;
      if (!c.consent && (c.tags.indexOf("pmu") > -1 || c.isNew)) unsigned++;
    });
    var box = $(".app-stats");
    var items = [[todayN, S.stats.today, "all"], [week, S.stats.week, "soon"], [refill, S.stats.refill, "refill"], [unsigned, S.stats.unsigned, "new"]];
    box.innerHTML = items.map(function (s) { return '<button type="button" class="stat" data-filter-go="' + s[2] + '"><strong>' + s[0] + "</strong><span>" + esc(L(s[1])) + "</span></button>"; }).join("");
  }
  function renderFilters() {
    $(".app-filters").innerHTML = S.filters.map(function (f) { return '<button type="button" data-filter="' + f[0] + '" aria-pressed="' + (f[0] === filter) + '">' + esc(L(f[1])) + "</button>"; }).join("");
  }
  function renderAll() { renderFilters(); renderStats(); renderList(); if (current) renderRecord(current, true); }

  doc.addEventListener("click", function (e) {
    var f = e.target.closest("[data-filter]"); if (f) { filter = f.getAttribute("data-filter"); renderFilters(); renderList(); }
    var g = e.target.closest("[data-filter-go]"); if (g) { filter = g.getAttribute("data-filter-go"); renderFilters(); renderList(); }
    var r = e.target.closest("[data-client]"); if (r) openClient(r.getAttribute("data-client"));
    var t = e.target.closest("[data-toast]"); if (t) toast(S.toast[t.getAttribute("data-toast")]);
    var s = e.target.closest("[data-sec]"); if (s) { var el = doc.getElementById("sec-" + s.getAttribute("data-sec")); if (el) { el.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" }); $$(".rec-menu button").forEach(function (x) { x.classList.toggle("is-current", x === s); }); } }
    if (e.target.closest("[data-back]")) { app.classList.remove("is-detail"); current = null; renderList(); window.scrollTo(0, 0); }
    var m = e.target.closest("[data-modal]"); if (m) showModal(m.getAttribute("data-modal"));
  });
  $(".app-search input").addEventListener("input", function (e) { query = e.target.value.trim().toLowerCase(); renderList(); });

  /* ---------- Record ---------- */
  function openClient(id, quiet) {
    current = id;
    app.classList.add("is-detail");
    renderList();
    renderRecord(id);
    if (!quiet && window.innerWidth < 960) window.scrollTo(0, 0);
    else if (!quiet) $(".app-main").scrollIntoView({ block: "start" });
  }
  var byId = function (id) { return clients.filter(function (c) { return c.id === id; })[0]; };

  function secHistory(c) {
    var ev = [];
    if (c.isNew) {
      ev.push({ d: 0, t: L(S.newFromWeb), s: L(nameOf(c.requested.what)), done: true });
      if (c.health) ev.push({ d: 0, t: L(S.secTitles.health), s: c.health.a.flag ? L(S.flag) : L({ sv: "Inget av Lauras kontraindikationer gäller", en: "None of Laura's contraindications apply" }), done: true });
    }
    if (c.health && !c.isNew) ev.push({ d: c.health.d, t: L(S.secTitles.health), s: L(S.signed), done: true });
    if (c.consent != null) ev.push({ d: c.consent, t: L(S.secTitles.consent), s: L(S.signed), done: true });
    c.visits.forEach(function (v) { ev.push({ d: v.d, t: L(nameOf(v.t)), s: L(kindLbl(v.kind)) + " · " + v.artist, done: true }); });
    if (c.photos) ev.push({ d: c.photos.d, t: L(S.secTitles.photos), s: L(S.before) + ", " + L(S.after).toLowerCase(), done: true });
    (c.upcoming || []).forEach(function (u) { ev.push({ d: u.d, t: L(nameOf(u.t)), s: L(kindLbl(u.kind)) + (u.time ? " · " + u.time : ""), future: u.d > 0 }); });
    if (c.refillBy != null) ev.push({ d: c.refillBy, t: L(S.refill), s: L({ sv: "Senast inom 12 månader", en: "Within 12 months at the latest" }), future: c.refillBy > 0 });
    ev.sort(function (a, b) { return b.d - a.d; });
    return '<ol class="tline">' + ev.map(function (e, i) { return '<li class="' + (e.future ? "is-future" : "is-done") + '" style="animation-delay:' + (reduce ? 0 : i * 60) + 'ms"><time>' + esc(fmt(day(e.d))) + " · " + esc(rel(day(e.d))) + "</time><strong>" + esc(e.t) + "</strong><span>" + esc(e.s) + "</span></li>"; }).join("") + "</ol>";
  }
  function secTreatments(c) {
    if (!c.visits.length) return '<div class="rec-empty">' + esc(L(S.noTreat)) + (c.note ? "<br><br>" + esc(L(c.note)) : "") + "</div>";
    return c.visits.slice().reverse().map(function (v) {
      var pmu = TR[v.t] && TR[v.t].group === "pmu";
      var rows = [[S.artist, v.artist], [S.method, L(kindLbl(v.kind))], [S.pigment, L(v.pigment)], [S.needle, L(v.needle)]];
      if (pmu) rows.push([S.numbing, L(S.numbingVal)], [S.aftercare, L(S.aftercareVal)]);
      return '<article class="rec-card"><div class="rec-card__top"><div><strong>' + esc(L(nameOf(v.t))) + "</strong><small>" + esc(fmt(day(v.d), true)) + '</small></div><span class="badge badge--ok">' + esc(L(S.paid)) + '</span></div><dl class="kv">' +
        rows.map(function (r) { return "<dt>" + esc(L(r[0])) + "</dt><dd>" + esc(r[1]) + "</dd>"; }).join("") + "</dl>" + (v.note ? '<p class="rec-note">' + esc(L(v.note)) + "</p>" : "") + "</article>";
    }).join("");
  }
  function secBookings(c) {
    var html = "";
    if (c.isNew) {
      html += '<article class="rec-card"><div class="rec-card__top"><div><strong>' + esc(L(nameOf(c.requested.what))) + "</strong><small>" + esc(L(S.requested)) + ": " + esc((c.requested.flex ? [L({ sv: "Första lediga tid", en: "First available time" })] : []).concat(c.requested.dates.map(function (n) { return fmt(day(n)); })).join(", ")) + '</small></div><span class="badge badge--due">' + esc(L(S.awaiting)) + "</span></div>" +
        (c.message ? '<p class="rec-note">' + esc(c.message) + "</p>" : "") + '<div class="rec-btns"><button type="button" class="btn btn--primary btn--sm" data-toast="confirm">' + esc(L(S.confirm)) + "</button></div></article>";
    }
    (c.upcoming || []).forEach(function (u) {
      html += '<article class="rec-card"><div class="rec-card__top"><div><strong>' + esc(L(nameOf(u.t))) + "</strong><small>" + esc(fmt(day(u.d), true)) + (u.time ? " · " + u.time : "") + '</small></div><span class="badge badge--due">' + esc(L(S.upcoming)) + "</span></div><dl class=\"kv\"><dt>" + esc(L(S.method)) + "</dt><dd>" + esc(L(kindLbl(u.kind))) + (u.forT ? " · " + esc(L(nameOf(u.forT))) : "") + "</dd></dl></article>";
    });
    if (c.refillBy != null) {
      var late = c.refillBy < 0;
      html += '<article class="rec-card"><div class="rec-card__top"><div><strong>' + esc(L(S.refill)) + "</strong><small>" + esc(L({ sv: "Senast", en: "By" })) + " " + esc(fmt(day(c.refillBy))) + " · " + esc(rel(day(c.refillBy))) + '</small></div><span class="badge ' + (late ? "badge--warn" : "badge--due") + '">' + esc(L(late ? S.refillLate : S.refillDue)) + '</span></div><div class="rec-btns"><button type="button" class="btn btn--ink btn--sm" data-toast="remind">' + esc(L(S.remind)) + '</button><a class="btn btn--ghost btn--sm" href="boka.html?t=' + (c.visits[0] ? c.visits[0].t : "") + '">' + esc(L(S.bookTouch)) + "</a></div></article>";
    }
    c.visits.slice().reverse().forEach(function (v) {
      html += '<article class="rec-card"><div class="rec-card__top"><div><strong>' + esc(L(nameOf(v.t))) + "</strong><small>" + esc(fmt(day(v.d))) + " · " + esc(L(kindLbl(v.kind))) + '</small></div><span class="badge">' + esc(L(S.past)) + "</span></div></article>";
    });
    return html || '<div class="rec-empty">' + esc(L({ sv: "Inga bokningar.", en: "No bookings." })) + "</div>";
  }
  function secConsent(c) {
    if (c.tags.indexOf("academy") > -1 && !c.isNew) return '<div class="rec-empty">' + esc(L({ sv: "Inget behandlingssamtycke behövs för kursrådgivning och utbildning.", en: "No treatment consent is needed for course advice and training." })) + "</div>";
    var ok = c.consent != null;
    return '<article class="rec-card"><div class="rec-card__top"><div><strong>' + esc(L({ sv: "Samtycke kosmetisk tatuering", en: "Consent: cosmetic tattooing" })) + "</strong><small>" + esc(ok ? L(S.signed) + " · " + fmt(day(c.consent)) : L(S.unsigned)) + '</small></div><span class="badge ' + (ok ? "badge--ok" : "badge--due") + '">' + esc(ok ? L({ sv: "Signerat", en: "Signed" }) : L(S.unsigned)) + '</span></div><div class="rec-btns"><button type="button" class="btn btn--ghost btn--sm" data-modal="consent">' + esc(L(ok ? S.view : S.previewClient)) + "</button>" + (ok ? "" : '<button type="button" class="btn btn--primary btn--sm" data-toast="sign">' + esc(L(S.sendSign)) + "</button>") + "</div></article>";
  }
  function secPayments(c) {
    if (!c.payments.length) return '<div class="rec-empty">' + esc(L(S.noPayments)) + "</div>";
    return c.payments.map(function (p) {
      return '<article class="rec-card"><div class="rec-card__top"><div><strong>' + esc(L(nameOf(p.item))) + "</strong><small>" + esc(fmt(day(p.d))) + " · " + esc(L(p.method)) + '</small></div><span class="badge badge--ok">' + esc(L(S.paid)) + '</span></div><dl class="kv"><dt>' + esc(L({ sv: "Belopp", en: "Amount" })) + "</dt><dd>" + esc(p.amount ? L(p.amount) : L(S.perList)) + "</dd></dl></article>";
    }).join("");
  }
  function secHealth(c) {
    if (!c.health) return '<div class="rec-empty">' + esc(L({ sv: "Ingen hälsodeklaration behövs för utbildning.", en: "No health declaration is needed for training." })) + "</div>";
    var a = c.health.a || {};
    var item = function (q) {
      var v = a[q[0]], flag = !!v || (a.flag && q[0] !== "prev" && q[0] !== "allergy");
      var ans = v ? L(v) : (a.flag && q[0] !== "prev" && q[0] !== "allergy" ? L({ sv: "Se kundens svar", en: "See the client's answer" }) : L(S.no));
      return '<li class="' + (flag ? "is-flag" : "") + '"><span>' + esc(L(q[1])) + "</span><strong>" + esc(ans) + "</strong></li>";
    };
    var base = S.healthQ.slice(0, 5), extra = S.healthQ.slice(5);
    return '<article class="rec-card"><div class="rec-card__top"><div><strong>' + esc(L(S.secTitles.health)) + "</strong><small>" + esc(L(S.signed)) + " · " + esc(fmt(day(c.health.d))) + '</small></div><span class="badge ' + (Object.keys(a).length ? "badge--warn" : "badge--ok") + '">' + esc(Object.keys(a).length ? L(S.flag) : L({ sv: "Godkänd", en: "Cleared" })) + "</span></div>" +
      '<p class="small muted" style="margin:0 0 8px">' + esc(L(S.lauraList)) + '</p><ul class="qa">' + base.map(item).join("") + '</ul><p class="small muted" style="margin:14px 0 8px">' + esc(L(S.extra)) + '</p><ul class="qa">' + extra.map(item).join("") + "</ul>" +
      (c.note ? '<p class="rec-note">' + esc(L(c.note)) + "</p>" : "") + '<div class="rec-btns"><button type="button" class="btn btn--ghost btn--sm" data-modal="health">' + esc(L(S.previewClient)) + "</button></div></article>";
  }
  function secPhotos(c) {
    if (!c.photos) return '<div class="rec-empty">' + esc(L(S.noPhotos)) + '</div><div class="rec-btns"><button type="button" class="btn btn--ghost btn--sm" data-toast="photo">' + esc(L(S.addPhoto)) + "</button></div>";
    var set = DATA.img[c.photos.set];
    if (!set) return "";
    return '<div class="ph-group"><h3>' + esc(fmt(day(c.photos.d))) + " · " + esc(L(nameOf(c.visits[0].t))) + '</h3><div class="ph-grid">' +
      '<figure class="ph"><img src="' + set.before + '" alt="' + esc(L(S.before)) + '" loading="lazy"><figcaption>' + esc(L(S.before)) + "</figcaption></figure>" +
      '<figure class="ph"><img src="' + set.after + '" alt="' + esc(L(S.after)) + '" loading="lazy"><figcaption>' + esc(L(S.after)) + "</figcaption></figure>" +
      '<button type="button" class="ph ph--add" data-toast="photo">' + I.cam + "<span>" + esc(L(S.healed)) + "</span></button></div></div>" +
      '<div class="ph-group"><h3>' + esc(L(S.compare)) + '</h3><div class="cmp" data-cmp><img src="' + set.after + '" alt=""><div class="cmp__b"><img src="' + set.before + '" alt=""></div><div class="cmp__h"></div><input type="range" min="0" max="100" value="50" aria-label="' + esc(L(S.compare)) + '"></div><div class="cmp-tags"><span>' + esc(L(S.before)) + "</span><span>" + esc(L(S.after)) + "</span></div>" +
      '<p class="small muted" style="margin-top:10px">' + esc(L(S.exPhoto)) + "</p></div>";
  }
  function secContact(c) {
    var rows = [[S.phone, c.phone], [S.email, c.email]];
    if (c.city) rows.push([S.city, c.city]);
    rows.push([S.pref, c.pref === "sms" ? L(S.sms) : L(S.email)], [S.marketing, c.marketing ? L(S.yes) : L(S.no)]);
    return '<article class="rec-card"><dl class="kv">' + rows.map(function (r) { return "<dt>" + esc(L(r[0])) + "</dt><dd>" + esc(r[1]) + "</dd>"; }).join("") + '</dl><div class="rec-btns"><button type="button" class="btn btn--ghost btn--sm" data-toast="call">' + esc(L(S.phone)) + '</button><button type="button" class="btn btn--ghost btn--sm" data-toast="call">' + esc(L(S.sms)) + '</button><button type="button" class="btn btn--ghost btn--sm" data-toast="call">' + esc(L(S.email)) + "</button></div></article>";
  }

  var PHOTOS = {};
  doc.addEventListener("change", function (e) {
    var inp = e.target.closest && e.target.closest("[data-profile]");
    if (!inp || !inp.files || !inp.files[0]) return;
    var id = inp.getAttribute("data-profile");
    if (PHOTOS[id]) URL.revokeObjectURL(PHOTOS[id]);
    PHOTOS[id] = URL.createObjectURL(inp.files[0]);
    renderRecord(id, true);
    toast({ sv: "Profilbild sparad på den här enheten (demo)", en: "Profile photo saved on this device (demo)" });
  });

  var SEC = { history: secHistory, treatments: secTreatments, bookings: secBookings, consent: secConsent, payments: secPayments, health: secHealth, photos: secPhotos, contact: secContact };
  var ORDER = ["history", "treatments", "bookings", "consent", "payments", "health", "photos", "contact"];
  function renderRecord(id, keepScroll) {
    var c = byId(id); if (!c) return;
    var st = status(c);
    var flags = { bookings: !!(c.isNew || st.some(function (s) { return s[0] === "due" || s[0] === "warn"; })), health: !!(c.health && Object.keys(c.health.a || {}).length), consent: c.consent == null && c.tags.indexOf("pmu") > -1 };
    var sinceTxt = c.isNew ? L(S.newFromWeb) : L(S.since) + " " + fmt(day(c.since));
    var html = '<div class="rec"><section class="rec-hero"><div class="rec-hero__top"><button type="button" class="app-back" data-back>' + I.back + esc(L({ sv: "Klienter", en: "Clients" })) + '</button><div class="rec-actions"><button type="button" data-toast="call" aria-label="' + esc(L(S.phone)) + '">' + I.phone + '</button><button type="button" data-toast="call" aria-label="' + esc(L(S.sms)) + '">' + I.sms + '</button><button type="button" data-toast="call" aria-label="' + esc(L(S.email)) + '">' + I.mail + '</button><a href="boka.html" aria-label="' + esc(L({ sv: "Ny bokning", en: "New booking" })) + '">' + I.cal + "</a></div></div>" +
      '<div class="rec-id"><div><h2>' + esc(c.name) + "</h2><p>" + esc(sinceTxt) + (c.isNew ? "" : " · " + esc(L(S.example))) + '</p><div class="badges">' + st.map(badge).join("") + "</div></div></div>" +
      '<div class="rec-photo' + (PHOTOS[c.id] || c.pic ? " has-photo" : "") + '">' +
        (PHOTOS[c.id] ? '<img src="' + PHOTOS[c.id] + '" alt="' + esc(L({ sv: "Profilbild", en: "Profile photo" })) + '">'
          : c.pic ? '<img src="' + c.pic + '" alt="" style="object-position:' + c.pos + '"><span class="rec-photo__tag">' + esc(L({ sv: "Exempelbild, behandlat område", en: "Example photo, treated area" })) + "</span>"
          : '<span class="rec-photo__init" aria-hidden="true">' + initials(c.name) + "</span>") +
      '<label class="rec-photo__btn">' + I.cam + "<span>" + esc(L(PHOTOS[c.id] || c.pic ? { sv: "Byt bild", en: "Change photo" } : { sv: "Ta profilbild", en: "Take profile photo" })) + '</span><input type="file" accept="image/*" capture="user" data-profile="' + c.id + '"></label></div></section>' +
      '<div class="rec-menu-wrap"><nav class="rec-menu" aria-label="' + esc(L({ sv: "Delar av kundkortet", en: "Sections of the client record" })) + '"><span class="rec-menu__name">' + esc(c.name) + "</span><ul>" +
      S.sections.map(function (s) { return '<li><button type="button" data-sec="' + s[0] + '"' + (flags[s[0]] ? " data-flag" : "") + "><i></i>" + esc(L(s[1])) + "</button></li>"; }).join("") + "</ul></nav></div>" +
      '<div class="rec-body">' + ORDER.map(function (k) { return '<section class="rec-sec" id="sec-' + k + '"><div class="rec-sec__head"><h2>' + esc(L(S.secTitles[k])) + "</h2></div>" + SEC[k](c) + "</section>"; }).join("") + "</div></div>";
    var main = $(".app-main");
    main.innerHTML = html;
    initCompare(main);
  }

  function initCompare(scope) {
    $$("[data-cmp]", scope).forEach(function (el) {
      var r = $("input", el), drag = false;
      var set = function (p) { p = Math.max(0, Math.min(100, p)); el.style.setProperty("--pos", p + "%"); r.value = Math.round(p); };
      var from = function (e) { var b = el.getBoundingClientRect(); set((e.clientX - b.left) / b.width * 100); };
      el.addEventListener("pointerdown", function (e) { drag = true; if (e.pointerType === "mouse") el.setPointerCapture(e.pointerId); from(e); });
      el.addEventListener("pointermove", function (e) { if (drag) from(e); });
      ["pointerup", "pointercancel", "lostpointercapture"].forEach(function (n) { el.addEventListener(n, function () { drag = false; }); });
      r.addEventListener("input", function () { set(+r.value); });
    });
  }

  function showModal(kind) {
    var c = byId(current);
    if (kind === "consent") {
      openModal(S.secTitles.consent, '<p>' + esc(L({ sv: "Viktigt att läsa igenom. Kunden godkänner villkoren i samband med bokning.", en: "Important to read. The client accepts the terms when booking." })) + "</p><ol>" + S.consentItems.map(function (i) { return "<li>" + esc(L(i)) + "</li>"; }).join("") + "</ol>" +
        (c && c.consent != null ? '<div class="sign">' + I.check + "<div><strong>" + esc(c.name) + "</strong><br>" + esc(L(S.signed)) + " · " + esc(fmt(day(c.consent), true)) + "</div></div>" : '<div class="sign">' + esc(L({ sv: "Kunden signerar med BankID från sin telefon.", en: "The client signs with BankID on their phone." })) + "</div>"));
    } else if (kind === "health") {
      openModal(S.secTitles.health, "<p>" + esc(L({ sv: "Så här ser formuläret ut för kunden innan besöket. Inför behandling får du inte:", en: "This is how the form looks to the client before the visit. Before treatment you must not:" })) + "</p><ul>" +
        S.healthQ.slice(0, 5).map(function (q) { return "<li>" + esc(L(q[1])) + "</li>"; }).join("") + "</ul><p style=\"margin-top:14px\">" + esc(L({ sv: "Kunden svarar Ja eller Nej på varje fråga och signerar. Svarar kunden Ja föreslås en kostnadsfri konsultation i stället.", en: "The client answers Yes or No to each question and signs. If they answer Yes, a free consultation is suggested instead." })) + "</p>");
    }
  }

  doc.addEventListener("pdl:lang", function () { if (!app.hidden) renderAll(); });
  window.addEventListener("resize", function () { if (window.innerWidth >= 960 && !current && !app.hidden) openClient(clients[0].id, true); });
  var stage = $(".phone-stage"), frame = stage && $("iframe", stage);
  var setStage = function (open) {
    if (!stage) return;
    if (open) { frame.src = "kundkort.html?embed=1" + (current ? "#c=" + current : ""); stage.hidden = false; doc.body.classList.add("is-locked"); var cl = $("[data-phone-close]", stage); cl && cl.focus(); }
    else { stage.hidden = true; frame.src = "about:blank"; doc.body.classList.remove("is-locked"); var o = $("[data-phone-open]"); o && o.focus(); }
  };
  $$("[data-phone-open]").forEach(function (b) { b.addEventListener("click", function () { setStage(true); }); });
  $$("[data-phone-close]").forEach(function (b) { b.addEventListener("click", function () { setStage(false); }); });
  doc.addEventListener("keydown", function (e) { if (e.key === "Escape" && stage && !stage.hidden) setStage(false); });
  window.addEventListener("message", function (e) { if (e.origin === location.origin && e.data === "pdl-close-phone" && stage && !stage.hidden) setStage(false); });
  if (EMBED) doc.addEventListener("keydown", function (e) { if (e.key === "Escape" && !(modal.open)) { try { parent.postMessage("pdl-close-phone", location.origin); } catch (err) {} } });

  window.addEventListener("hashchange", function () { if (location.hash === "#ny" && !app.hidden && clients[0].isNew) openClient("web"); });
  if (ss.get("pdl-staff")) enter();
})();
