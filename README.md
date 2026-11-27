# Knack Extra

Single-product sales site for Knack Extra Capsules, Nigeria. Static files, no
build step, no framework, no dependencies to install. Hosted on GitHub Pages.

Live: https://zaddywebbuilds.github.io/powa/

It also builds as a WordPress theme, so the same pages can be served from a
WordPress install with the order form rendered by Fluent Forms and every order
recorded as an entry. See **README-WORDPRESS.md**. The static build is the
source: the theme is generated from it.

---

## Before anything else: set the WhatsApp number

Orders are sent to a WhatsApp number. Until a real one is set, the order
button hides itself rather than pretend to work.

Open `assets/js/config.js` and edit:

```js
whatsapp: { value: "2348031234567", verified: true, label: "WhatsApp" },
```

Digits only, country code first, no `+` and no spaces. Set `verified: true`.
Do the same for `contact.phone` and `site.businessName`. Then commit and push.

---

## How it fits together

```
index.html            the sales page
thank-you.html        order confirmation, reads sessionStorage, nothing in the URL
policies.html         delivery, returns, privacy, terms
assets/js/config.js   >>> every price, policy and contact detail lives here <<<
assets/js/site.js     renders the page from that config
assets/css/site.css   design system
assets/img/           optimised WebP
assets/img/reserve/   art held back, see below
assets/video/         the hero clip, silent and looping
assets/fonts/         self-hosted Playfair Display + Manrope, latin subset
source-art/           full-resolution originals, never served
source-art/fixed/     the same art with the label text repaired
tools/                the retouch, image, theme and form build scripts
wp-theme/             the hand-written half of the WordPress theme
wordpress/            the Fluent Forms order form, ready to import
dist/                 build output, not committed
```

### config.js is the only file with commercial facts in it

Nothing is hard-coded into the pages. Prices appear once. Change a price there
and it updates the hero, the package cards, the order summary, the WhatsApp
message and the structured data together.

Fields are shaped `{ value, verified }`. **A field is only shown to customers
when `verified` is true.** An unconfirmed fact is left off the page entirely.
The site never fills a gap with a guess, and it never tells the visitor that a
gap exists either: the section simply reads as though that line was never
there. What is still outstanding is tracked in `LAUNCH-CHECKLIST.md`.

---

## Orders

There is no server and no database, so there is no order table anywhere.

1. Customer picks a package and fills the form.
2. The form validates in the browser (Nigerian phone formats, required fields,
   duplicate guard within 30 minutes).
3. It opens WhatsApp with the whole order written out: reference, package,
   totals, name, phone, full address, landmark, notes, marketing consent.
4. The customer presses send. It lands in your WhatsApp.
5. The browser goes to `thank-you.html`, which shows the reference and totals.

No personal detail is ever put in a URL. Order data sits in `sessionStorage`
just long enough to render the confirmation, then is cleared, so a refresh
cannot look like a second order.

If you later want a real order database and a proper dashboard, that needs a
host that can run server code. Cloudflare Pages with D1 would do it without a
VPS, but it is a different deployment.

---

## Deploying

GitHub Pages, from the `main` branch, root folder. `.nojekyll` is present so
the `assets/` folder is served as-is. Push and it republishes.

### Or as a WordPress theme

```powershell
python tools/build_theme.py
```

This slices `index.html` and `policies.html` into WordPress templates, rewrites
every relative asset path, swaps the hand-written order form for the Fluent
Forms shortcode, and writes `dist/knack-extra.zip` ready to upload under
Appearance, Themes.

```powershell
python tools/build_form.py
```

This writes `wordpress/knack-extra-order-form.json`, the order form itself,
with the states and the package prices read out of `config.js` so they cannot
drift away from the prices on the page. Both are documented in
**README-WORDPRESS.md**.

`header.php`, `footer.php`, `front-page.php` and `page-policies.php` are
generated. Edit the HTML and rebuild rather than editing them.

---

## Images

Every image is AI-generated, and every bottle in them was printed with garbled
label text: "Casual In Sexuit Penfarinione", "Stemm Mattural Blrength", and a
legible "Makes Erection Strong" claim underneath.

That text has been removed. On each bottle the bullet band was rebuilt from the
clean label rows above and below it and reprinted with three lines that are
true and that come from `config.js`:

```
Herbal food supplement
For adult men, 18 and over
Not a medicine. Read the label.
```

The shrink-wrap cap on `product-usage` and the mirrored reflections carried the
same nonsense; those are dissolved into the surface they sit on rather than
reset, because nothing there is meant to be read.

### Weight, and why it is shaped this way

Nearly all of the traffic is mobile, much of it on a weak connection, so the
page is built around that rather than adapted to it afterwards.

| | before | now |
| --- | --- | --- |
| images (19) | 1,490 KB | 438 KB |
| hero video | 685 KB | 132 KB |
| fonts | 84 KB | 84 KB |
| html, css, js | 81 KB | 116 KB raw, 32 KB gzipped |
| **first load, 375px phone** | **2,340 KB** | **770 KB** |

Three things got it there.

**The image ladder is measured, not guessed.** `tools/build_responsive.py`
holds the rendered CSS width of every image at five viewport widths, read out
of the live page, and sizes each variant from that. Rebuild with:

```powershell
python tools/build_responsive.py
```

Re-measure if the layout changes materially. With the page open at a given
width, scrolled top to bottom so the lazy images have loaded:

```js
Object.fromEntries([...document.images].map(i => [
  i.currentSrc.split('/').pop().replace(/(-\d+)?\.webp$/, ''),
  Math.round(i.getBoundingClientRect().width)]))
```

**Phones are served one named file, not a srcset.** `srcset` multiplies
`sizes` by the device's own pixel ratio and there is no way to cap it, so a
DPR 3 phone fetches three device pixels per CSS pixel. The phone and tablet
bands are `<source media>` entries instead, which name one exact file and
ignore DPR; only the desktop bands keep a DPR-aware `srcset`. Phones get about
1.7 device pixels per CSS pixel, which is invisible at arm's length and is the
single biggest lever on the page.

**The video is chosen in JavaScript.** The `<video>` has no `src` in the
markup, so nothing downloads until `wireHeroVideo()` decides. Reduced motion,
Save-Data and a connection the browser reports as 2g all keep the still poster
and cost nothing beyond its 12 KB. Everyone else gets a file sized for their
screen: `hero-sprout-480.mp4` at 132 KB on a phone, `hero-sprout.mp4` at
685 KB on a desktop.

**Cache busting is no longer optional.** The hero video has no `src` in the
markup, so a visitor holding a stale `site.js` would get fresh HTML, no video
source and no video at all, and the package thumbnails would quietly fall back
to the full size art. `tools/stamp_assets.py` appends a content hash to the
CSS and JS links in the static pages, so a stale file can never be paired with
fresh markup. Run it after changing either:

```powershell
python tools/stamp_assets.py
```

The WordPress build does not need it: every enqueue is versioned on the file's
own modification time.

The `@font-face` rules were moved out of `assets/fonts/fonts.css` and inlined
at the top of `site.css`. Behind an `@import` the browser could not even
discover the font stylesheet until `site.css` had arrived, which cost a whole
round trip on a high latency connection.

`tools/` holds the scripts, and they are repeatable:

```powershell
python tools/fix_labels.py
```

```powershell
python tools/build_images.py
```

```powershell
python tools/build_responsive.py
```

`fix_labels.py` rewrites `source-art/fixed/`, `build_images.py` turns those into
the served WebP variants at the sizes recorded in `assets/img/_manifest.json`.
`tools/relabel.py` is the engine; `tools/_grid.py` prints a coordinate grid over
a crop when a region needs re-measuring. `tools/fix_delivery.py` is separate:
it reframes the delivery photograph, and says in its own header why painting
the card terminal out was abandoned.

What is still **not** fixed: "100% HERBAL PRODUCT" and "30 CAPSULES" are printed
legibly on the artwork and neither is verified. Replace the art with photographs
of the real bottle before advertising anywhere.

`assets/img/reserve/` holds the one image that stays off the page:

| File | Why it is held back |
| --- | --- |
| `reserve-ingredients.webp` | Headed "NATURAL INGREDIENTS" over ginseng, ginger, citrus and seeds. The real ingredient list is unknown, so the picture itself is the claim, and nothing short of replacing the image fixes that. |

Three others were brought back into use after the claim was taken out of them:

| File | What changed |
| --- | --- |
| `returns-badge.webp` | Said "100% MONEY BACK GUARANTEED", which has no written conditions behind it. The badge now reads "RETURNS / 14 DAYS / FROM DELIVERY", which is `refund.windowDays` and is verified. The navy was also pulled to the site's own near-black. |
| `package-podium.webp` | Six bottles of garbled fine print, now reset. The crown stays: it sits over the two-bottle pack, which genuinely is the lowest price per bottle, and the packages section says so in words. |
| `doorstep-handover.webp` | Was a rider holding out a POS terminal while the customer offered a bank card, with `payment.cardOnDelivery` false. Painting the terminal out was tried and left streaks across the doorway behind it, so the frame was moved instead: it now starts to the right of the terminal and shows the customer at his door with the parcel. See `tools/fix_delivery.py`. |

The worried man and the relaxed man are never placed next to each other, and
neither is captioned as a result. They are not a before-and-after.

---

## The hero clip

`assets/video/hero-sprout.mp4` is 3.7 seconds, 752x416, silent, 685 KB, and
`assets/video/hero-sprout-480.mp4` is the same clip at 480 wide and 132 KB for
phones. It is a seed germinating in soil. It carries no product, no text and
no claim.

The supplied source ran 10 seconds. Only the first 4.5 are used. After that,
gold 3D lettering rotates around the sprout reading "ALL FROM NA...",
"NATURAL ROO..." and similar: garbled, like the bottle labels were, and
unfixable across 130 frames of moving type. Read as intended it also says the
product is all from natural roots, which is a composition claim, and
`product.ingredients` is unverified. So the tail is cut, not repaired.

It is closed into a seamless loop: the last 0.8s dissolves into the first 0.8s
and that blend sits at the end, so the final and first frames are the same
moment. Rebuild it with:

```powershell
python tools/build_hero_video.py
```

It is started from `site.js`, not by an `autoplay` attribute, and the `src` is
set there too, so an unwanted clip is never downloaded at all. Anyone who has
asked their system for reduced motion, anyone on Save-Data or a 2g connection,
and anyone without JavaScript keeps the still poster frame instead. It is muted, has no controls and cannot be put into
picture-in-picture.

---

## What this site deliberately does not do

No countdown timers. No stock counters. No fake sales notifications. No
exit-intent popups. No invented reviews, ratings or customer counts. No
generated portraits presented as customers. No third-party advertising pixels
or retargeting, which for this product category would also mean leaking
sensitive page context to an ad platform.

Page view counts are kept in the visitor's own browser and transmitted nowhere.

The claims from the original page — "clinically tested and approved", "safe,
without side effects", "instant result", the "87% of women" statistic — are not
reproduced. They had no evidence behind them.

---

## Editing content

Run it locally with any static server:

```powershell
python -m http.server 4173
```

Then open http://localhost:4173.

Images are regenerated from `source-art/` with Pillow, by the scripts in
`tools/`. `assets/img/_manifest.json` records every served size.
