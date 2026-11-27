# Knack Extra on WordPress

The site is now available two ways from the same source files:

| Build | Where it lives | Order form |
| --- | --- | --- |
| Static | `index.html` and friends, GitHub Pages | WhatsApp, no server |
| WordPress theme | `dist/knack-extra.zip` | Fluent Forms, orders recorded in WordPress |

Both read the same `assets/js/config.js`, so a price has one home. The theme is
**generated** from the static build, which means `index.html` stays the file you
edit and the templates are rebuilt from it.

```powershell
python tools/build_theme.py
```

That writes `dist/knack-extra/` and `dist/knack-extra.zip`. The zip is what you
upload. `dist/` is not committed.

---

## 1. Install the theme

1. WordPress admin, **Appearance, Themes, Add New, Upload Theme**
2. Choose `dist/knack-extra.zip`, install, activate

Nothing visible changes yet, because the front page still belongs to Elementor.
That is the next step.

## 2. Take the front page off Elementor

The install currently has two Elementor pages, **MAN POWA** and
**Man Powa Thank You**. The theme's front page template cannot render while an
Elementor page is serving the home URL, because Elementor overrides the theme on
any page built with it.

1. **Pages, Add New.** Title it `Home`. Add no content. Do not open Elementor.
   Publish it.
2. **Settings, Reading**, set *Your homepage displays* to **A static page**, and
   set *Homepage* to `Home`.
3. Load the site. You should see the sales page.
4. Once you are happy with it, move **MAN POWA** to the trash.

Leave **Man Powa Thank You** alone until section 4, because form 42 still
redirects to it.

## 3. The policies page

1. **Pages, Add New.** Title it `Policies`. Check the permalink reads
   `/policies/`, because the footer links are built from that slug.
2. In the sidebar under **Page Attributes, Template**, choose **Policies**.
3. Publish. Add no content: the template carries it.

Then **Settings, Permalinks**, choose **Post name**, and save. Save it once even
if it is already selected, so the rules are rewritten.

## 4. The order form

### Use the corrected form

`wordpress/knack-extra-order-form.json` is a replacement for form 42. It asks
for the same things the static site asked for: state as its own dropdown,
city, address, landmark, delivery notes, **one** package rather than a free
choice of all three, and the 18-or-over confirmation. It also carries five
hidden fields that the page fills in, so the entry records the order reference
and the total the customer actually saw.

1. **Fluent Forms, All Forms**, open the **Import/Export** tab
2. Import `wordpress/knack-extra-order-form.json`
3. Open the new form and read down it once. The import is built from the
   Fluent Forms export format rather than produced by Fluent Forms itself, so
   check each field type looks right. Anything that came through oddly is
   quicker to correct in the editor than in the JSON.
4. Note the new form's ID
5. **Appearance, Customize, Knack Extra order form**, set the ID, publish

Regenerate it after any price change:

```powershell
python tools/build_form.py
```

### If you keep form 42 instead

The theme renders whatever ID you set, so form 42 works. Fix these first:

- **The package field is a checkbox.** A customer can tick all three and there
  is no total anywhere. Change it to a Radio field.
- **It redirects to `https://betterresult2.store/powathanks/` on submit.**
  Change the confirmation to an inline message, or every order ends on the old
  site. This is the only reason to keep **Man Powa Thank You** alive.
- **The notification goes to `{wp.admin_email}`.** Point it at whoever
  processes orders.
- There is no state field, no phone validation and no spam protection.

The package sync in `site.js` matches on the option value first and the
quantity second, so it drives form 42's `1 Bottle = N18,999` labels as well as
the corrected form's `single` / `double` / `triple` values.

### Make the email actually arrive

WordPress sends mail through PHP's `mail()` by default, and on shared hosting
that fails silently often enough to lose orders. Install an SMTP plugin, point
it at a real mailbox, and send a test before you trust it.

Then place one real test order on a phone and confirm three things: the entry
appears under **Fluent Forms, Entries**, the notification email arrives, and
the entry carries the reference and total.

## 5. Finish the setup

- **Settings, General**: set the Site Title and Tagline. The browser tab title
  is built from them.
- **Settings, General**: set Site Language to English and the timezone to Lagos.
- Update `site.url` in `assets/js/config.js` to the live domain, rebuild, and
  re-upload. It is used for the canonical URL on the static build and for the
  structured data image.
- Delete the old pages and posts left over from the previous site. NAFDAC
  advertisement review, ARCON and Meta all look at the whole domain, not just
  the page you send them to. See `LAUNCH-CHECKLIST.md`.

---

## How the theme is put together

```
style.css              theme header only; the design system is assets/css/site.css
functions.php          bootstrap
inc/assets.php         ke_asset(), ke_policies_url(), enqueueing, font preloads
inc/order-form.php     ke_order_form(), the form ID, the no-plugin fallback
inc/customizer.php     the form ID setting
inc/seo.php            canonical and Open Graph, skipped if an SEO plugin is active
header.php             GENERATED from index.html
footer.php             GENERATED from index.html
front-page.php         GENERATED from index.html
page-policies.php      GENERATED from policies.html
page.php / index.php / 404.php   plain document layout
assets/                copied from the static build, minus assets/img/reserve/
assets/css/theme.css   WordPress-only adjustments, e.g. clearing the admin bar
assets/css/fluentform.css   makes the plugin's markup match the rest of the page
```

**Do not edit the four generated files.** Edit `index.html` or `policies.html`
and run `python tools/build_theme.py`. Each generated file says so at the top.

### config.js is still the only file with commercial facts in it

Fields are shaped `{ value, verified }`, and a field is only shown when
`verified` is true. That rule is unchanged by the move to WordPress. Edit it
under **Appearance, Theme File Editor**, or rebuild and re-upload.

### What the page does with the form

`site.js` keeps the rendered form and the order summary beside it in step:

- picking a package in the packages grid selects it inside the form
- changing it inside the form updates the summary panel, the total and the
  highlighted package card
- `order_reference`, `order_package`, `order_quantity`, `order_subtotal` and
  `order_total` are filled in before submission, so the entry is a record of an
  order rather than a name and an address

If Fluent Forms is deactivated, the section shows a short message and the
support link instead of an empty box, and an admin notice says why.

### What was not tested here

There is no PHP on the machine this was built on, so the templates were
verified by rendering them with WordPress's functions mocked out: the markup
balances, no asset path was left relative, and the form skin was checked
against the plugin's real class names. **The first load in WordPress is the
real test.** If a template errors, the cause is almost certainly in one of the
four hand-written files in `inc/`, not in the generated markup.

### A note on `reserve/`

`assets/img/reserve/` is deliberately excluded from the theme. It holds the
artwork that is held back because the picture itself makes a claim that is not
evidenced. Leaving it out of the upload means it is not one careless click
away from appearing in the Media Library.
