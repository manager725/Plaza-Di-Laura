# Plaza Di Laura: Phase 1 discovery, audit and content inventory

Checked 24 Nov 2026 against https://bylaura.se/ (Shopify, Horizon theme 3.4.0, built by ENCO Digital, Swedish only). Raw page text was pulled from every nav and footer page, all 16 treatment and course pages, and the course PDF. Screenshots are in `docs/evidence/`.

Phase 0 (approved 24 Nov 2026): aesthetic clinic plus academy, Balanced register, full clickthrough prototype, Swedish with an English toggle. Phase 12 case: "site already looks modern (Shopify)", so the pitch rests on conversion, trust and SEO gaps proven below, not only visuals.

## Content inventory

| Field | What her material says | Source |
|---|---|---|
| Offer: treatments | Kosmetisk tatuering: Ögonbryn Ombre/Puder (puderbryn/ombrebryn, incl. återbesök), Ögonbryn Strokes (microblading 3D / nanostrokes, nanostrokes "1000 kr tillägg"), Läppar (lipblush/ombrelips/soft lips), Fräknar (faux freckles), Lashliner. Microneedling. SMP (performed by Robert Tomaszewski, with sister business His Hair Sweden). LIFT Ink Removal (non-laser). Fettfrysning & Cellulitreducering (Proshock Ice). Free consultation on site, by phone or Zoom. | /pages/plaza-di-laura-klinik, /products/* |
| Offer: academy | Grundkurs PMU (hub) leading to Signature PMU Artist Program (5 days, **55.000 kr**, Qliro instalments), Signature Microblading & Nanostroke Brow Program (4 days), Freckle Technique Program (3 days), Grundkurs SMP, Grundkurs Microneedling, Grundkurs Ink Removal. Max 2 students per course, choose methods freely, starter kit with a Biomaser wireless machine, international certificate, lifetime support, free practice at the school. | /products/grundkurs-*, course PDF p.7 |
| Buyer | 1) Clients in Gothenburg (mostly women for PMU and skin; men for SMP). 2) Career changers buying a 55.000 kr course, decision over weeks or months. B2C. | inferred from offer |
| Conversion goal | Primary: book a treatment (currently Bokadirekt). Secondary: book free course advice (kursrådgivning) or apply for a course. | CTAs on every page |
| Proof | EST. 2006. "4.8/5, 300+ omdömen" (linked to Bokadirekt). Laura's "No Trauma Technique" (no pain, swelling, bleeding or scabs). Suppliers: Biomaser, Kwadron, Permablend, LI Pigments, MAST, Cheyenne. "Först i Norden med flera av utbildningarna". Proshock Ice "omskriven i media som tex Aftonbladet". Laura is developing a CSN-eligible YH programme. | home, /pages/om-oss, /pages/kosmetisk-tatuering, academy |
| Reviews | 13 short client reviews, verbatim, first name plus initial (Anneli W., Paula K., Andela J., Agneta L., My K., Linda E., Linda L., Frida A., Alexandra Ö., Jasmine Z., Susanna A., Tommy B.). One student quote with full name (Novah Wallin). | home, /pages/om-oss |
| People | Laura Lindqvist, founder, PMU artist and educator. Robert Tomaszewski, SMP artist, 13+ years, co-founder of the SMP method via His Hair Sweden (hishairsweden.se). | /pages/om-oss, /products/smp |
| Contact | Address only in body text: Kungsgatan 11, central Göteborg. **No phone, email, opening hours, postcode or map anywhere on the site.** Contact page is a bare form (namn, e-post, telefon, kommentar). | /pages/kontakt, academy, SMP |
| Locale | sv-SE, prices in "kr", Qliro for instalments. No org number shown. | site-wide |
| Brand assets | Wordmark PNG "PLAZA DI LAURA / ACADEMY" (thin, widely spaced charcoal caps, 1200x628) and a white version (605x52). Studio portraits of Laura (cream backdrop, white outfit, black accents). 23 before/after photos with captions (bryn, läppar, fräknar), watermarked. Course photos (elever_under_kurs). Current theme is black, white and greys, partly Montserrat. | /cdn/shop/files |
| Existing content | Results gallery with filters (Alla, Bryn, Läppar, Fräknar). Treatment pages with process, contraindications, aftercare, refill timing (återbesök 4 to 6 weeks, refill within 12 months, lasts 1.5 to 3 years). Course PDF (8 pages). | /products/*, course PDF |
| Compliance | Privacy policy. Booking terms in body text: cancel at least 24 hours ahead; 50% charged if a contraindication stops the treatment. No terms page, no org number. | /policies/privacy-policy, /products/puderbryn-ombrebryn |

## Top 5 issues hurting conversion (ranked)

1. **Every booking button sends visitors to competitors.** All "Boka", "Boka nu", "Boka behandling", "Boka gratis rådgivning" and "Recensioner" links (on every page) point to bokadirekt.se/places/salong-plaza-di-laura-10058, which now 301-redirects to Bokadirekt's "Hudvård, Göteborg" listing of 242 other businesses. The "Boka utbildningsrådgivning" button on Om Laura redirects to Lily's Beauty Salon, "Ansiktsbehandling klassisk 90 min, 1 495 kr". The 4.8/5 review claim therefore cannot be checked by a visitor either. Evidence: `docs/evidence/booking-button-lands-on-competitor-list.png`, `course-advice-button-lands-on-other-salon.png` (24 Nov 2026, 10:52 UTC).
2. **No way to reach her directly.** No phone, email, hours, map or full address on the contact page or footer. Evidence: `docs/evidence/current-contact-390.png`.
3. **No prices.** Treatments are Shopify products that show "0.00 kr" in site search. The only real price (55.000 kr) is inside a PDF download. PMU buyers compare prices before booking.
4. **Numbers contradict each other, which reads as untrustworthy.** Customers: "1500+" (home) vs "över 15 000" (Om Laura, Kosmetisk tatuering). Experience: "EST. 2006", "20+ år" and "över 15 år". Students: "hundratals", "över 300" and "över 350". Fat freezing: "enda kliniken i västra götaland" vs "enda kliniken i Göteborg".
5. **Slow on phones.** Lighthouse mobile (median of 3): Performance 58, Accessibility 93, Best Practices 79, SEO 85. LCP 4.5 s (mobile hero is a 639 KB PNG, desktop hero a 2.5 MB PNG, empty alt), TBT about 900 ms. SEO loses on six "Läs mer" links and an invalid robots.txt; accessibility on an unnamed logo link and low-contrast review names and gallery tabs.

Also noted: clinic clients and academy students share one funnel (every course page ends with the clinic CTA "Letar du efter en klinik..."; "Ansök till utbildning" goes to the generic form); a newsletter signup with no evidence of a newsletter; "Butik" page says "Kommer snart!".

## Verified facts and gaps

- Verified on her own pages: address Kungsgatan 11, Göteborg; EST. 2006; course price 55.000 kr; course lengths 5/4/3 days; max 2 students; suppliers list; Robert Tomaszewski for SMP.
- Web search found no third-party coverage of Plaza Di Laura or Laura Lindqvist (the search tool is not tuned to Swedish local results, so this is not proof of absence).
- Not verifiable: the 4.8/5 and 300+ review figures (their source profile is gone), the Aftonbladet mention, Instagram and TikTok follower counts.
- Must come from the client: current booking tool and link, phone, email, opening hours, postcode, org number, treatment prices, course prices beyond the PMU programme, course dates, which customer and student numbers are correct.
