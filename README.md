# Knack Extra

Single-product sales site for Knack Extra Capsules, Nigeria. Static files, no
build step, no framework, no dependencies to install. Hosted on GitHub Pages.

Live: https://zaddywebbuilds.github.io/powa/

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

Or do it through the dashboard at `/admin/`, which writes the file for you.

---

## How it fits together

```
index.html            the sales page
thank-you.html        order confirmation, reads sessionStorage, nothing in the URL
policies.html         delivery, returns, privacy, terms
admin/                owner dashboard: edits config.js, exports it for you to commit
assets/js/config.js   >>> every price, policy and contact detail lives here <<<
assets/js/site.js     renders the page from that config
assets/css/site.css   design system
assets/img/           optimised WebP (2.8 MB total)
assets/img/reserve/   art held back, see below
assets/fonts/         self-hosted Playfair Display + Manrope, latin subset
source-art/           full-resolution originals, never served
```

### config.js is the only file with commercial facts in it

Nothing is hard-coded into the pages. Prices appear once. Change a price there
and it updates the hero, the package cards, the order summary, the WhatsApp
message and the structured data together.

Fields are shaped `{ value, verified }`. **A field is only shown to customers
when `verified` is true.** An unconfirmed fact is left off the page entirely.
The site never fills a gap with a guess, and it never tells the visitor that a
gap exists either: the section simply reads as though that line was never
there.

`site.previewMode` is a flag the `/admin/` readiness view reads. It puts
nothing on the customer-facing pages.

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

---

## Images

Fifteen images are used on the page. All are AI-generated and **the bottle
labels in every one of them carry garbled text** — "Casual In Sexuit
Penfarinione", "Stemm Mattural Blrength" and similar. It is not real product
copy.

Where the bottle is large (the hero, the final banner), a heavy dark scrim
drops the lower half of the pack into shadow, and the product panel uses a
crop that stops above the label text. That is a holding measure. Replace these
with genuine photographs of the real bottle, front and back, before the site is
advertised anywhere, and the scrims can then be lightened in `site.css`.

`assets/img/reserve/` holds four images deliberately kept off the page:

| File | Why it is held back |
| --- | --- |
| `reserve-ingredients.webp` | Shows ginseng, ginger, citrus and seeds. The real ingredient list is unknown, so this would be an invented claim. |
| `reserve-refund-badge.webp` | "100% money back guaranteed" with no written conditions behind it. |
| `reserve-package-podium.webp` | Puts a crown on the middle pack. There is no sales data to support "most popular". |
| `reserve-payment-delivery.webp` | Shows a card being tapped on a POS terminal. Only use it if the rider genuinely carries one. |

The worried man and the relaxed man are never placed next to each other, and
neither is captioned as a result. They are not a before-and-after.

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

Images are regenerated from `source-art/` with Pillow. The scripts that did it
are not kept in the repo; `assets/img/_manifest.json` records the sizes.
