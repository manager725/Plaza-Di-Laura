# Plaza Di Laura prototype: handoff notes (v2)

Internal. Built 24 Nov 2026. Not deployed (the user deploys on Vercel). `docs/`, `_build/` and all `.md` files are excluded from the deploy by `.vercelignore`.

## What it is
A clickable prototype of a redesigned bylaura.se: 23 static pages, Swedish with an English toggle, light and dark themes.

- Home, Behandlingar (overview), 9 treatment pages, Akademi (overview), 6 course pages, Resultat, Om Laura, Kontakt, Boka (booking flow), 404.
- Run locally: `python -m http.server` in the project folder, then open http://127.0.0.1:8000. Everything is client-side; a local server just makes sure the self-hosted font loads the same way it will on Vercel.
- Edit: change `_build/content/*.json` or the templates in `_build/build.py`, then `python -I _build/build.py`. Never hand-edit the generated .html files.

## Direction (chosen without a Phase 2 vote, at the user's request)
Balanced register. Jost (self-hosted, no Google requests), warm porcelain #F7F3EF, charcoal #26211F, one accent: clay rose #975548 from her lip results. Designed dark theme. Every homepage section has its own layout. Wordless brow-stroke loader on the first visit per session (under 1.2 s, off with reduced motion).

Signature tool: **Brynguiden**, four questions that recommend puderbryn, strokes, nanostrokes or LIFT Ink Removal using only the rules on her own strokes and LIFT pages.

## Demo-only parts and what production needs
| Part | Now | Production |
|---|---|---|
| Booking (boka.html) | Request flow: treatment or free consultation or course advice, up to 3 preferred days, time of day, a health check with her own contraindication list (PMU only), details, confirmation. Nothing is sent. | Connect her real booking system (the old Bokadirekt profile is gone), or send requests by email/CRM. Real availability needs her opening hours and calendar. |
| Contact form | Validation, honeypot, success state. Nothing is sent. | A form endpoint (Shopify contact form, Formspree, or her email tool). |
| Chat ("Frågor?") | Scripted answers taken from her own pages: pain, longevity, brows, preparation, contraindications, cancellation, consultation, courses, price, address, SMP, LIFT. Free text matches keywords and falls back to the contact form. | Keep as an FAQ assistant, or replace with a live chat tool. |
| Map | Click-to-load Google Maps (nothing loads before consent), plus a directions link. | Same. |
| Course PDF | Links to her existing Shopify file for the Signature PMU course. | PDFs for the other five courses. |

## What the client must supply (nothing is shown as a placeholder; missing items are simply left out)
**Contact and booking:** current booking tool or link, phone, email, opening hours, postcode, org number.
**Prices:** all nine treatments (only the nanostrokes add-on, 1 000 kr, is known) and every course except Signature PMU (55 000 kr). Course dates.
**Course details:** length, format and what is included for Grundkurs SMP, Microneedling and Ink Removal; who teaches SMP; PDFs for five courses.
**Treatment details:** longevity, aftercare, preparation and contraindications for fräknar, lashliner, microneedling, SMP, LIFT and fettfrysning; cancellation terms beyond kosmetisk tatuering.
**Numbers to confirm** (her site contradicts itself, so none of the disputed ones are used): customers 1 500+ vs 15 000+; students 300 vs 350 ("hundratals" is used); 15 vs 20+ years of cosmetic tattooing; fat freezing "only clinic in Västra Götaland" vs "in Göteborg" (Göteborg is used); "ingen" vs "minimal svullnad"; review score 4.8/5 from 300+ reviews (left out: its Bokadirekt source no longer exists).
**Approval:** the English translation of all copy; permission to show the before/after photos.
**Photos:** higher-resolution studio portraits (the hero portraits are only 682 to 739 px wide); the clinic's own photos to replace stock-style images now used for microneedling (serum bottles), SMP, LIFT (product bottle) and fat freezing (machine).

## Before going live
- Remove `<meta name="robots" content="noindex, nofollow">` (generated in `head()` in build.py), the `X-Robots-Tag` header in vercel.json and the `Disallow: /` in robots.txt. Add a sitemap.
- Canonical, og:url and og:image assume https://bylaura.se/ with clean URLs (vercel.json has cleanUrls on). Redirect map from the Shopify URLs: /products/puderbryn-ombrebryn to /behandling-puderbryn, /products/microblading to /behandling-strokes, /products/grundkurs-kosmetisk-tatuering-alla-metoder to /utbildning-signature-pmu, /pages/om-oss to /om-laura, /pages/kontakt to /kontakt, /pages/plaza-di-laura-academy to /akademi, /pages/plaza-di-laura-klinik and /pages/kosmetisk-tatuering to /behandlingar.
- Analytics: placeholder comment in the head; load GA4/GTM only after consent, and add a consent banner at that point.
- Platform: she is on Shopify (Horizon theme, by ENCO Digital). The design can be rebuilt as a Shopify theme, or run as a static site with a booking integration.

## v2 (24 Nov 2026): motion and interaction
After seeing v1 the user asked for more hover effects, animation, transitions and unique sections. Added: before/after drag slider (her bryn, läppar and fräknar results, cut from her side-by-side photos), treatment ticker, drifting review rows, footer wordmark, expanding path cards, hero result slides and pointer depth, word-by-word headings, curtain image reveals, parallax, count-ups, colour-sweep magnetic buttons, contextual cursor, floating course previews, page transitions. Full list in DESIGN.md.

## v3 (24 Nov 2026): client records (Kundkort)
Laura sent a "Client record" mockup from another salon (history, treatments, bookings, consent form, payments, medical record, documentation photos, contact). Built as a staff app demo: `kundkort.html` (linked as "Kundkort för personal" in the footer, not in the main nav).
- Demo BankID or email login, client list with search, filters (touch-up soon, refill, new, academy) and a daily overview, record with the eight sections in a menu card styled after her mockup but in her own brand.
- Six fictional example clients ("Exempelkund"; phone numbers from the 070-174 06 xx range Sweden reserves for fiction). Real facts only where they exist: her contraindication list, her booking terms in the consent form, Robert Tomaszewski for SMP, the 55 000 kr course paid with Qliro. Treatment amounts show "Enligt prislista" because her prices are unknown.
- A booking sent on boka.html is saved for the session and appears in the app as a new client ("Ny"), with requested days, message, health answers and an unsigned consent form. The booking confirmation shows a dashed "Prototyp:" link into the app; remove it for production.
- Photos in the example records are her own results images, labelled as example photos.
- Closer to her mockup: each card has a large profile photo area at the top with the menu card overlapping it. "Ta profilbild" opens the camera on a phone or a file picker on a computer; the photo stays on that device for the visit only (nothing is uploaded).
- "Mobilvy" button (desktop): shows the app inside a phone frame next to a "Kundkort" heading, like her picture. The phone is a live, clickable copy of the app (kundkort.html?embed=1).
- Files: assets/css/app.css, assets/js/kundkort.js, page_kundkort() in build.py.
- Outline for Laura: docs/Plaza-Di-Laura-client-records-outline.pdf (one page, source docs/client-records-outline.html), with version 1 scope, later phases, build options, GDPR and five questions. No prices or timeline (none given yet).
- Production needs a real backend: logins, EU-hosted encrypted storage, access logs, BankID signing, SMS provider, payments. Static hosting is not enough for real client data.

## v4 (24 Nov 2026): new fonts, booking rebuilt, client photos
- Fonts: Instrument Serif headings with italic accent words, Plus Jakarta Sans for text (see DESIGN.md).
- Booking (boka.html) rebuilt: category tabs with a sliding indicator, photo cards that auto-advance to the next step, clickable step indicator with checkmarks, calendar plus chosen-day chips, time-of-day tiles, "I am flexible" switch, one Yes/No toggle per health question (any Yes offers a free consultation instead), preparation tips beside the questions, floating-label form, reminder preference (sms, email, both), live summary with the treatment photo and "Ändra" links, sticky action bar on phones, confirmation with an animated check, reference number, ticket summary and treatment-specific preparation steps.
- Fixed: the old treatment choices nested a second bordered box inside each card, a broken image showed in the summary (the [hidden] attribute was overridden by img display:block; now [hidden] always hides), and sticky panels slid under the desktop header (new --sticky offset includes the utility bar).
- Kundkort: every example client now has a photo in the list and on the card, cropped to the treated area (brows, lips, freckles, scalp) rather than a face, labelled "Exempelbild, behandlat område". A website booking now carries the per-question health answers, flexible dates and reminder choice into the new client card.

## v5 (24 Nov 2026): intro loader
- New branded intro on the first page of each visit: a brow draws itself stroke by stroke, the Plaza Di Laura wordmark wipes in, a counter runs to 100 % with real page loading, then the page lifts away as a curved two-colour curtain and the hero animates in. About 2.5 s; any click, key or scroll skips it. Not shown again while browsing, and off for visitors who reduce motion.
- To show it again during a demo: add ?intro to any page address, for example index.html?intro.
- Checks: 15 loader checks (first visit, counter, hero after the curtain, no repeat, replay, click to skip, reduced motion, English, dark, mobile) plus the full regression (40 site, 26 app, 9 phone-view checks, all pages 320 to 1920 px) pass.

## v6 (25 Nov 2026): luxury type, smooth cards, sharp footer
- Fonts: Cormorant Garamond headings with italic accents and Jost text (replacing Instrument Serif and Plus Jakarta Sans), lighter weights, wider label tracking. Details in DESIGN.md.
- Fixed: the treatment ticker showed a line of brow-drawing code instead of its small brow separators (a naming clash in the generator).
- Path cards (Behandlingar / Academy) now animate with movement and fades only, so they stay smooth; the other card dims while one is hovered.
- Footer wordmark is live text instead of an enlarged image: sharp at every size, letters rise in on scroll and lift in a rose wave under the pointer.
- Header is fully opaque, so page text no longer shows through it while scrolling.
- Checks: all pages at 6 sizes from 320 to 1920 px clean, 40 site, 26 app, 9 phone-view and 15 loader checks pass.

## v7 (25 Nov 2026): quieter treatment rows, new "How it works"
- Treatment rows: no filled box or cursor bubble; a rose hairline draws under the row, the text glides, the arrow tilts, other rows fade back. The cursor label now only shows over images and drag areas.
- "How it works" rebuilt as a stacking deck of five photo cards with a pinned step index and consultation button (photos: Laura, her studio, the machine, healed brows, a healed client).
- Checks: all pages at 6 sizes clean, 40 site and 15 loader checks pass.

## Responsive QA (25 Nov 2026)
- Automated audit of all 23 pages at 14 sizes (320x568 to 2560x1440, incl. landscape phone 844x390 and touch tablets): no sideways scroll, no clipped text, no text under 12 px on phones, every touch control at least 40 px (44 px rules under pointer: coarse). Only remaining flags are intentional: the hidden spam-trap field and photos zoomed inside clipped frames.
- Visual review of 106 screenshot sheets (10 key pages at phone, tablet, laptop and landscape phone) plus Kundkort. Fixed: hero layout below 960 px and on landscape phones (side by side, header not sticky on short screens), mid-word hyphenation in headings (only main headings on phones under 480 px may hyphenate), No Trauma arc crossing its label, old-style numerals on the course price, Om Laura portrait crop, contact form row alignment, empty booking summary placeholder, footer column headings, fact table alignment, heading spacing, path card label legibility, step index timing, reduced-motion entrance delays, Kundkort login note spacing.
- Left as is (content or photo limits): the Lashliner and Fettfrysning source photos are low resolution or tightly cropped; odd-numbered card grids end on a single card.

## QA (24 Nov 2026)
- 23 pages at 23 sizes from 320x568 to 2560x1440: no horizontal scroll, no console errors, one H1 per page.
- 37 scripted interaction checks pass: Brynguiden (3 paths), SV/EN toggle and persistence, theme, mega menus, chat, the full booking flow including validation and the contraindication stop, the contact form, the mobile drawer, results filters and the lightbox.
- v4: 40 site checks (incl. full booking with health toggles and reference number), 26 app checks, 9 photo and phone-view checks pass; no overflow at 320 to 1920 px; scrub clean.
- v3: 26 scripted checks on the client-record app pass (login, list, filters, search, all sections, consent modal, reminder, photo compare, health flag, English, booking to new client, phone list and record views). Full site re-run clean at 5 sizes, 37/37 site checks pass.
- v2 re-run: all 23 pages clean at 320 to 2560 px, 37/37 interaction checks pass, touch drag on the slider works, reduced motion turns marquees into static swipe rows. Lighthouse after v2: Accessibility 100, Best Practices 100, CLS 0; homepage Performance best run 89 (noisy machine).
- Lighthouse mobile: Accessibility 100 and Best Practices 100 on all tested pages. SEO loses points only to the intentional preview noindex. Performance is noisy on this machine (homepage best run 94); re-check on PageSpeed Insights after deploy, where Vercel's compression also applies.
- Scrub: no AI or tool names, no em dashes, no image metadata.
