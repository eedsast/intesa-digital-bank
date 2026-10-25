# Intesa Digital — digital bank concept site

Concept marketing site for a new EU digital bank, built for the Intesa digital
banking PoC. Structure follows the chari.com pattern: one home page carrying the
overall value proposition, routing to two audience propositions, each split into
a **basic** layer and a **value-add** layer.

The site reads "Intesa Digital". The logo in the header is a typographic
wordmark set in the site's own display face — **not** Intesa Sanpaolo's registered
mark. Drop the official asset into `assets/` and swap the `<span class="mark">` /
`<span class="brand-name">` pair in the header for an `<img>` before this is shown
to anyone outside the PoC.

Product names, rates, fees and figures are illustrative and are not an offer.

## Open it

Double-click `index.html`, or serve the folder if you prefer a real origin:

    cd intesa-digital-bank
    python -m http.server 8000      # then open http://localhost:8000

No build step, no dependencies, no package manager. Fonts come from Google Fonts
over the network; everything else is local.

## Layout

    intesa-digital-bank/
      index.html          all five pages: home, individuals, business, solution, phases
      css/styles.css      design tokens + every style rule
      js/products.js      one description per catalogue chip, keyed by audience
      js/app.js           page routing, mobile menu, anchor handling, product modal
      assets/             images, logos, favicons go here
      README.md

The site has no footer, no FAQ accordions and no site-wide product nav entry:
the nav is Home / Individuals / Business & merchants / Solution / Phase approach, and the
same five buttons appear in every page hero with the current page filled.

### index.html

Five sibling `<main>` elements — `#page-home`, `#page-individuals`, `#page-business`,
`#page-solution`, `#page-phases`. Only one is visible at a time; the others carry the `hidden`
attribute. Anything inside a `<section class="band">` is a full-width horizontal
band with a `.wrap` container inside it.

### css/styles.css

The `:root` block at the top is the whole design system. Rebranding means editing
that block and nothing else:

| Token | Role |
|---|---|
| `--paper`, `--surface`, `--surface-2` | page, card and alternating band backgrounds |
| `--ink`, `--ink-soft`, `--ink-deep` | body text, secondary text, dark sections |
| `--line`, `--line-deep` | borders on light and dark surfaces |
| `--accent`, `--accent-tint` | individuals route accent (institutional green) |
| `--biz`, `--biz-tint` | business route accent (institutional blue) |
| `--api`, `--api-tint` | API-set nodes on the architecture map |
| `--on-brand` | text colour that sits on an accent fill |
| `--brand`, `--brand-tint` | whichever accent the current page uses |
| `--f-display`, `--f-body`, `--f-mono` | Bricolage Grotesque, Instrument Sans, IBM Plex Mono |

The palette is defined three times: once on bare `:root` (light), once under
`@media (prefers-color-scheme: dark)`, once under `:root[data-theme="dark"]`.
Change a colour in all three or the page will read correctly in only one theme.

Each page scopes its own accent at the bottom of the file:

    #page-individuals { --brand: var(--accent); --brand-tint: var(--accent-tint) }
    #page-business    { --brand: var(--biz);    --brand-tint: var(--biz-tint) }

### The architecture figure

`.arch-svg` inside `#page-solution` is generated from
`core-banking-mockup-claude/Target Architecture - high level.drawio` — same geometry, same
fills and strokes. It is inline rather than an `<img>` so it survives being published as a
single self-contained file. **Regenerate it rather than hand-editing it**: when the drawio
changes, re-run the converter and replace the `<svg class="arch-svg">…</svg>` block, then
re-check the node colours in `.n-done` / `.n-p1` / `.n-p2` / `.n-api` / `.n-ext` against the
file's legend, since those are literal hex values copied from it.

### js/products.js

`window.PRODUCTS` is `{ individuals: {...}, business: {...} }`, each a map from the
chip's **rendered text** to its description. Five product names appear on both sides
(Mobile app, Web app, Per-card limits, Multi-currency wallets, FX remittance) and mean
different things, which is why the map is split by audience rather than flat.

The keys must match what the chip renders, entities resolved — `Merchant & category
locks`, not `Merchant &amp; category locks`; `BNPL — Pay in 3, interest-free` with a real
em dash. If a chip has no entry the modal says so rather than opening blank, so a
mismatch is visible rather than silent.

A value is either a **plain string** (the description, nothing else) or an **object**:

    "Mobile app": {
      description:   "...",
      prerequisites: "...",
      solution:      "...",
      saas:          "..."
    }

Any field left out renders as "To be defined." in muted italic; a field that is present
renders as normal body text. Both forms work side by side, so filling in a product means
turning its string into an object and adding the fields you have — nothing else changes.

Section values may carry light markup — `<strong>`, `<em>`, `<br>` — because `fillSection`
writes them with `innerHTML`. That is safe here only because `products.js` is part of the
site's source; never point that function at text a visitor can supply.

### js/app.js

One IIFE. `show(name)` toggles the three pages, syncs the nav highlight and
scrolls to top. The global click handler does two things: links carrying
`data-nav="home|individuals|business"` switch page, and plain `#anchor` links
first reveal the `<main>` that owns the target before scrolling to it.

## The product modal

Every chip in a catalogue is clickable — `.fam li` on the home panels, `.tag` on the two
proposition pages — and opens `#pm` with four sections. `openModal` works out which
catalogue the chip came from (`.route--ind` / `.route--biz` on home, the owning `<main>`
on a detail page), reads the family heading above it, and looks the description up in
`window.PRODUCTS`. The panel takes the audience accent through `.pm--biz`.

Chips are keyboard reachable (`tabindex`/`role` are applied at load), Enter and Space
open the modal, Escape closes it, and body scroll is locked while it is open.

## Adding a page

1. Add `<main id="page-yourname" hidden>` in `index.html`.
2. Add it to the `pages` object at the top of `js/app.js`.
3. Add a nav link with `data-nav="yourname"`.
4. If it needs its own accent, scope `--brand` on `#page-yourname` in the CSS.

## Component classes worth knowing

| Class | What it is |
|---|---|
| `.band`, `.band--alt`, `.band--deep`, `.band--tight` | full-width sections; alt is the tinted band, deep is the dark one |
| `.wrap` | centred 1180px container with the side gutter |
| `.eyebrow` | small mono uppercase label above a heading |
| `.h-xl` / `.h-lg` / `.h-md` / `.h-sm` | the type scale |
| `.grid.g-2/.g-3/.g-4` + `.card` | the proposition card grids |
| `.famcard` + `.tag` | product-shelf families and their chips |
| `.routes` + `.route` | audience route cards; `.routes--one` makes them full width |
| `.route--panel` + `.fams` + `.fam` | the home catalogue panels: family heading + chip list per product group |
| `.layer` | basic vs value-add explainer blocks |
| `.feat` (`.rev` to flip) | alternating text + mockup spotlight |
| `.phone` / `.phone-screen` | the CSS app mockups — no images involved |
| `.ticks` | checkmark bullet list |
| `.pm` / `.pm-panel` / `.pm-sec` | the product modal, its panel and its four sections |
| `.arch` / `.layer-row` / `.node` | the architecture map; `.n-done`, `.n-p1`, `.n-p2`, `.n-api`, `.n-ext` mirror the legend in `Target Architecture - high level.drawio` |
| `.arch-fig` / `.arch-svg` | the embedded architecture diagram, in a light panel that scrolls sideways |
| `.card--p1` / `.card--p2` / `.card--p3` | phase module cards, bordered by phase |
| `.stats` / `.stat` | the dark figures strip |
| `.steps` / `.step` | numbered onboarding sequence |
| `.plans` / `.plan` (`.hi` to highlight) | pricing tiers |
| `.ctaband` | accent-filled closing call to action |

## Content map

**Home** — hero · basic vs value-add explainer · two full-width catalogue panels ·
stats · onboarding steps.

The home page carries the whole product catalogue now. The standalone product shelf,
the "Two audiences, one flywheel" band and the closing CTA band were all removed; the
two route cards became full-width `.route--panel` blocks that list every product
grouped into six families each (`.fams` / `.fam` in the CSS), ending on the
"Open the … proposition" link.

**Individuals** — hero · basic proposition (10 cards) · value-add in four groups
(credit at the point of purchase, growing money, everyday life, control and
protection) · two spotlights (instalments, open-banking aggregation) · three
plan tiers · cross-sell to business · CTA.

**Solution** — hero · target architecture (nine layers, `.arch` / `.layer-row` / `.node`,
the drawio rendered as inline SVG) · layer-by-layer
breakdown of the same map · how to read it.

**Phase approach** — hero · Phase I core platform · Phase II extensions · out of scope.
Content mirrors `core-banking-mockup-claude/phase_approach.html`; the service-boundary codes
under each module name are the link back to it.

**Business & merchants** — hero · basic proposition (12 cards) · value-add in
four groups (sell more, fund the business, run the business, build on us) ·
two spotlights (BNPL risk transfer, revenue-based financing) · three tiers
(Merchant / Business / Platform) · cross-sell to individuals · CTA.

## Before this goes in front of anyone outside the PoC

- Replace the placeholder wordmark with the official Intesa asset (see above).
- Confirm the licence route. The hero now reads "an electronic money institution
  or a full credit institution" — an EMI cannot take deposits and cannot carry the
  lending shelf, so the Individuals basic proposition is written to cover both
  routes. Once the route is fixed, cut the half that does not apply.
- Replace illustrative pricing on the plan and tier cards, or label it clearly.
- Add the licensing statement, supervisory authority, deposit guarantee scheme
  details and pre-contractual consumer-credit information. There is no footer
  on the site now, so there is currently nowhere these appear.
- Decide which products are launch scope and which are roadmap; the shelf is
  the full addressable catalogue, not a day-one list.
