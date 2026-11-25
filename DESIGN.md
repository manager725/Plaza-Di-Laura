# Plaza Di Laura prototype: design system

Internal file. Never ship to the client (excluded by .vercelignore).

## Direction
Balanced register: a calm, trust-first clinic with editorial beauty imagery. Brand kept as-is: thin, widely spaced charcoal wordmark on warm off-white, studio portraits of Laura in white, close-up results. Neutrals plus one hue (clay rose, taken from her lip results). Light theme is the default; the dark theme is designed, not inverted. Swedish first, English through the toggle.

## Tokens
| Role | Light | Dark |
|---|---|---|
| --bg | #F7F3EF | #171413 |
| --surface | #FFFDFB | #1F1B19 |
| --tint (nude band) | #EEE5DD | #29231F |
| --ink | #26211F | #F2ECE6 |
| --ink-2 | #4A423E | #D8CEC6 |
| --muted | #6B615B | #ADA298 |
| --line | #DED3C9 | #3B332F |
| --brand (primary CTA, focus, active) | #975548 | #E3A497 |
| --brand-hover | #7D4439 | #EDB8AD |
| --on-brand | #FFFFFF | #1A1513 |
Academy band (both themes): bg #221D1B, ink #F2ECE6, muted #BDB2A9, accent #E3A497. All text pairs checked at AA (lowest: muted on tint 4.84:1).

## Type (changed 25 Nov 2026: the user found Instrument Serif + Plus Jakarta Sans "tacky, AI-looking" and asked for a luxury, fashion feel)
Cormorant Garamond (variable 300 to 700, plus italic) for headings and big moments (h1, h2, card and treatment titles, ticker, quotes, prices), weight 400 for large sizes and 500 for small titles, lining numerals, one italic accent word in brand colour per key heading. Jost (variable 100 to 900) for all text, buttons, menus, labels and app UI; its thin geometric caps match her logo. Both self-hosted in assets/fonts (no Google requests); the old files are parked in _build/fonts-unused. Body 16.5px / 1.68, 400. Buttons and bold text 500 (never 600 or 700, which looks heavy and cheap in Jost); buttons tracked 0.03em. Labels 11.5px, 500, caps, tracking 0.2em. Hero headline clamp(44px, 5.3vw, 80px). Numbers in the staff app stay in the sans. The giant footer wordmark is live Jost 200 text sized with container units (11.6cqi), not an image, so it stays sharp.

## Layout and shape
Container 1280px, gutter clamp(16px, 4vw, 40px). Section padding 80 to 112px (Balanced). Radius: 2px on images, 8px on panels and cards, 6px on buttons and fields. Every homepage section uses a different layout; never three same-background sections in a row.

## Motion (v2, 24 Nov 2026: the user asked for much more hover, animation and interaction)
Balanced layout, Expressive motion layer. Everything is off under prefers-reduced-motion, and fine-pointer effects only run on desktop.
- Intro loader (v5): first page of each tab session, ?intro replays it. A nanostroke brow draws itself (hair strokes, then the ombre powder wipes in), the wordmark wipes in, a 0 to 100 counter follows real loading (fonts and eager images, 1.7 s minimum, 4.2 s maximum), then the page lifts as a two-layer curved curtain (warm off-white, then clay rose). Any click, key or scroll skips it; hero entrances and reveals wait for the curtain (loader-hold). Off with reduced motion; a CSS safety hides it after 8 s.
- Load: hero headline rises word by word (split at build time), hero copy fades up in sequence, inset photo cycles three results (4.2 s, progress dots, pauses on hover), photos shift with the pointer.
- Scroll: section labels draw a short line, headings rise word by word (split just before they enter), cards fade up in a stagger, feature images open with a curtain wipe (observed through their parent, because a fully clipped element never intersects), parallax on path cards, image cards and page heroes (CSS scroll timelines where supported), steps fill in, the No Trauma brow line draws itself, numbers count up, a 2 px progress line runs under the header.
- Hover: buttons sweep their colour in and pull slightly towards the pointer, the two path cards zoom their photo, slide their text up to reveal the chip list and dim the other card (transform and opacity only: the earlier flex-grow and max-height version re-flowed text every frame and felt janky), the footer wordmark letters lift and blush rose in a small wave, treatment rows draw a rose hairline underneath while the text glides, the arrow tilts and the other rows recede (the user rejected the earlier filled tint box), the preview wipes in, image cards reveal their text, cards lift with an arrow badge, review cards tilt, course rows show a floating photo, a contextual cursor label (Visa, Dra) appears only over galleries, the review track and the slider, never over text rows or cards (it hid the words).
- How it works (v7, 25 Nov 2026; the user found the five small numbered circles plain): a deck of five step cards, each with a big Cormorant italic numeral, title, text and one of her photos. At 768 px wide and 700 px tall and up, each card is sticky 16 px lower than the last, so they stack as you scroll; covered cards scale to 0.965 and fade. Card tones deepen with --i (brand mixed 0 to 20 % into surface) and the last card is the dark band. From 1024 px the intro, a step index (active step: rose numeral and hairline, aria-current) and the consultation button stay pinned on the left; index clicks scroll to the card's flow position. Active detection uses layout positions (offsetHeight from the deck top), never getBoundingClientRect of the cards, because their reveal and scale transforms skew it.
- Hero (v9): full-height editorial split (100svh minus the header, 620 to 940 px). Text column aligned to the container's left edge, vertically centred, with a hairline footer row (Sedan 2006 · Kungsgatan 11 and an animated scroll cue). The portrait bleeds to the right screen edge with no radius, opens bottom-up as a curtain and settles from a slow zoom (kept at scale 1.04 so the pointer parallax never shows an edge). The italic name caption sits top right in ink on desktop (the chat button owns the bottom corner). The results inset straddles the column split from 1200 px.
- Reviews (v9, centred): label with lines both sides, centred heading, a faint oversized rose quote mark behind, one large centred quote (balanced lines) that reveals with a soft upward clip, slim round arrows either side, names centred as tabs, counter, note and pause below.
- Reviews (v8, replaced the two card marquees): one featured quote in Cormorant with a big rose opening quote mark, prev/next, counter and pause on the left, client names as tabs. Auto-advance (7 s) is the active tab's underline animation (animationend = next), paused on hover, focus, off screen, by the button, and off with reduced motion. The stage height follows the active quote (650 ms ease).
- Meet Laura (v8): portrait plus an overlapping black-and-white inset, a slowly turning circular title badge with the small brow at its centre, "Laura *Lindqvist*", her own headline as an italic pull quote, three facts (2006, 15+, 20+) that stack as rows under 480 px. Never put a span inside a split heading: the splitter wraps every word in spans (that broke the old name subtitle).
- New homepage sections: treatment ticker (dark band, big type), before/after drag slider with three of her real results, two drifting rows of reviews, giant footer wordmark. Marquees pause on hover, focus, off screen and with a visible button.
- Page changes use cross-document view transitions where supported.
- Theme switch (25 Nov 2026, the user reported stutter): document.startViewTransition snapshots the page and the new theme opens as a circle from the toggle (650 ms, html.theme-vt). Never transition colours on every element: the homepage has about 1,600 elements and each frame cost a full restyle. Instant switch without View Transitions support or with reduced motion.
- Performance rules learned: no will-change on per-word spans (it created hundreds of GPU layers), no mask-image on marquees, no backdrop-filter, no forced reflows in timers, never animate width, flex-grow, grid tracks or max-height on hover (animate transform and opacity instead).

## Signature moment
Brynguiden: four questions that recommend puderbryn, strokes, nanostrokes or LIFT Ink Removal using only the rules on her own treatment pages.

## Rules
Real content only (from bylaura.se and her course PDF). No placeholders on the page: missing content is left out and reported in chat. No em dashes. No AI or tool names anywhere. Contradicted numbers (customer and student counts) are not used.
