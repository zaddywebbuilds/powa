# Launch checklist

Work top to bottom. The website is finished; these are the things outside the
code that decide whether it can legally trade and advertise.

---

## 1. Make the order flow work

- [ ] Real WhatsApp number in `config.js` → `contact.whatsapp`, `verified: true`
- [ ] Phone number in `contact.phone`
- [ ] Support email in `contact.email`
- [ ] Support hours in `contact.hours`
- [ ] Place one live test order yourself, end to end, and check the message arrives

Until the WhatsApp number is set, the order button hides itself.

## 2. Identify the seller

- [ ] Registered business name in `site.businessName`
- [ ] Business address in `site.businessAddress`

A commercial site with no identified seller behind it is a problem both for the
law and for the customer. It is also the first thing Meta's reviewers look for.

## 3. Get the product facts in writing

Ask the supplier for each of these on paper or by email. A phone call is not a
document. None of them appear on the site until `verified: true`.

- [ ] Pack size. The "30 capsules" on the artwork is AI-generated, not evidence.
- [ ] Manufacturer name and country
- [ ] Full ingredient list, copied from the printed label
- [ ] Approved dosage, word for word from the pack
- [ ] Contraindications, side effects and medicine interactions
- [ ] NAFDAC registration number, with the certificate

## 4. Replace the product photography

- [ ] Photograph the real bottle, front and back, in daylight
- [ ] Replace `hero-dark`, `hero-dark-alt`, `product-hero`, `bundle-one/two/three`
- [ ] Lighten the hero and final-banner scrims in `site.css` once the labels are real

Every supplied bottle image has garbled label text on it. The scrims and crops
currently hide it. That is a patch, not a fix.

## 5. Write the terms down

- [ ] Return conditions in `refund.conditions`: who is eligible, whether an
      opened pack qualifies, who pays return postage, how long a refund takes
- [ ] Confirm free nationwide delivery and the 1–3 day window with the courier
      you actually use, not with the old sales page
- [ ] Confirm whether the parcel is genuinely unbranded before claiming it is
- [ ] Only set `payment.cardOnDelivery` if the rider carries a POS terminal

## 6. Fix the package pricing

Current prices carried over from the old page:

| Package | Price | Per bottle |
| --- | --- | --- |
| 1 bottle | ₦18,999 | ₦18,999 |
| 2 bottles | ₦27,000 | ₦13,500 |
| 3 bottles | ₦46,999 | ₦15,666 |

The 3-bottle pack costs more per bottle than the 2-bottle pack, so a customer
who does the arithmetic has no reason to buy it. The site says so out loud,
because hiding it would be worse. Decide a price for the 3-pack that beats
₦13,500 per bottle — around ₦37,999 — or drop the pack.

- [ ] Agree the new price with the owner and update it in `/admin/`

## 7. Reviews

The reviews section is switched off and empty. The four testimonials on the old
page were chat screenshots with no names, no consent and medical claims inside
them.

- [ ] Collect real feedback with the customer's permission to publish it
- [ ] Strip phone numbers and anything identifying
- [ ] Remove any claim about a medical result
- [ ] Add them to `reviews.items` and set `reviews.enabled: true`

Do not invent reviews, ratings, star counts or "verified purchase" badges.

---

## 8. Before you advertise anywhere

This is separate from everything above, and the website being finished does not
help with any of it.

- [ ] **NAFDAC product registration.** Mandatory for a herbal product sold
      commercially in Nigeria.
- [ ] **NAFDAC advertisement approval.** A separate approval from registration.
- [ ] **ARCON / Advertising Standards Panel approval** for the advert itself.

### Paid social

- **Meta** restricts sexual-enhancement products, and reviews the landing page
  as well as the advert. Calling it "men's wellness" does not change how the
  product is classified.
- **TikTok** prohibits advertising products intended to enhance sexual
  performance or pleasure. There is no wording that gets around this.

Do not build a separate page for reviewers, redirect conditionally, or disguise
what the product is. Cloaking is what gets an ad account banned permanently
rather than an advert rejected.

### Organic posting

Paid rules and organic rules are different, and both change. Check each
platform's current commerce policy before posting, rather than assuming organic
is automatically allowed.

---

## 9. Claims that must never appear

Not on the site, not in an advert, not in a WhatsApp reply to a customer:

works instantly · guaranteed results · lasts 60 minutes · permanent cure · no
side effects · safe for everyone · clinically proven · doctor recommended ·
cures erectile dysfunction · increases sperm count · saves your marriage ·
stops your partner cheating · better than prescription medication

Coded phrasing that means the same thing counts as the same claim.

---

## 10. Final pass

- [ ] Open `/admin/` → Launch readiness, confirm everything is green
- [ ] Test an order on a real phone on mobile data, not just wifi
- [ ] Check the policies page reads correctly with the real terms in place
- [ ] Set `site.previewMode: false`
