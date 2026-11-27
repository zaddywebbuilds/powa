# Knack Extra on WordPress

The site is available two ways from the same source files:

| Build | Where it lives | Order form |
| --- | --- | --- |
| Static | `index.html` and friends, GitHub Pages | WhatsApp, no server |
| WordPress plugin | `dist/knack-extra-plugin.zip` | Fluent Forms, orders recorded in WordPress |

Both read the same `assets/js/config.js`, so a price has one home. The plugin
is **generated** from the static build, which means `index.html` stays the file
you edit and the templates are rebuilt from it.

```powershell
python tools/build_plugin.py
```

That writes `dist/knack-extra-plugin/` and `dist/knack-extra-plugin.zip`. The
zip is what you upload. `dist/` is not committed.

---

## Why a plugin and not a theme

The site this goes on carries several sales pages, and Knack Extra is one of
them at a path like `/knackextra/`.

A WordPress theme governs **every** page on a site. Shipping this as a theme
would have restyled the other sales pages and taken over the home page. A
plugin leaves the active theme exactly where it is and claims only the pages
you assign its templates to. Nothing else on the site changes, and no page
built with Elementor is touched.

---

## 1. Install

**Plugins → Add New → Upload Plugin**, choose `dist/knack-extra-plugin.zip`,
install, **Activate**.

Nothing visible changes yet. The plugin is waiting for you to give it a page.

## 2. The sales page

1. **Pages → Add New.** Title it whatever you want to appear in the browser
   tab, for example `Knack Extra`.
2. Set the permalink to `knackextra`, so the page is at
   `yoursite.com/knackextra/`.
3. In the sidebar under **Page Attributes → Template**, choose
   **Knack Extra sales page**.
4. **Publish.** Add no content: the template carries the whole page.

Open `/knackextra/`. The design should be there in full.

## 3. The policies page

The footer and the returns section link to this, and those links stay hidden
until it exists.

1. **Pages → Add New.** Title it `Policies`.
2. Under **Page Attributes**, set **Parent** to the Knack Extra page, so it
   lands at `/knackextra/policies/`, and set **Template** to
   **Knack Extra policies**.
3. Publish, again with no content.

The plugin finds this page by its template, not by its slug, so you can name
and place it however you like.

Then **Settings → Permalinks → Save**. Save it once even if nothing looks
wrong, so the rewrite rules are rebuilt.

## 4. The order form

### Use the supplied form

`wordpress/knack-extra-order-form.json` is a replacement for the form that
came with the site. It asks for the same things the static page asked for:
state as its own dropdown, city, address, landmark, delivery notes, **one**
package rather than a free choice of all three, and the 18-or-over
confirmation. It also carries five hidden fields the page fills in, so an
entry records the order reference and the total the customer actually saw.

1. **Fluent Forms → All Forms → Import/Export**, import the JSON
2. Open the new form and read down it once. It was built to the Fluent Forms
   export format rather than produced by Fluent Forms, so check each field
   type looks right. Anything odd is quicker to fix in the editor.
3. Note the form's ID
4. **Settings → Knack Extra**, enter the ID, save

Regenerate it after any price change:

```powershell
python tools/build_form.py
```

### If you keep the original form 42

The plugin renders whatever ID you set, so form 42 works. Fix these first:

- **The package field is a check box.** A customer can tick all three and
  there is no total anywhere. Change it to a Radio field.
- **It redirects to `https://betterresult2.store/powathanks/` on submit.**
  Change the confirmation to an inline message, or every order ends on the old
  page.
- **The notification goes to `{wp.admin_email}`.** Point it at whoever
  processes orders.
- There is no state field, no phone validation and no spam protection.

The package sync in `site.js` matches on the option value first and the
quantity second, so it drives form 42's `1 Bottle = N18,999` labels as well as
the supplied form's `single` / `double` / `triple` values.

### Make the email actually arrive

WordPress sends mail through PHP's `mail()` by default, and on shared hosting
that fails silently often enough to lose orders. Install an SMTP plugin, point
it at a real mailbox, and send a test before you trust it.

Then place one real test order on a phone and confirm three things: the entry
appears under **Fluent Forms → Entries**, the notification arrives, and the
entry carries the reference and the total.

## 5. Finish

- **Settings → General**: Site Title and Tagline feed the browser tab title.
- Set Site Language to English and the timezone to Lagos.
- Update `site.url` in `assets/js/config.js` to the live domain, rebuild, and
  re-upload. It is used for the canonical URL on the static build.
- Read `LAUNCH-CHECKLIST.md`. NAFDAC advertisement review, ARCON and Meta all
  look at the whole domain, not just the page you send them to, so the old
  pages still matter.

---

## How the plugin is put together

```
knack-extra.php            plugin header and bootstrap
inc/template.php           registers the two page templates, finds pages by template
inc/assets.php             ke_asset(), enqueueing, font preloads, theme CSS isolation
inc/order-form.php         ke_order_form(), the form ID, the no-plugin fallback
inc/settings.php           Settings, Knack Extra
inc/seo.php                canonical and Open Graph, skipped if an SEO plugin is active
templates/sales.php        GENERATED from index.html
templates/policies.php     GENERATED from policies.html
assets/                    copied from the static build, minus assets/img/reserve/
assets/css/wordpress.css   WordPress-only adjustments, e.g. clearing the admin bar
assets/css/fluentform.css  makes the plugin's form markup match the rest of the page
```

**Do not edit the two generated templates.** Edit `index.html` or
`policies.html` and run `python tools/build_plugin.py`. Both files say so at
the top.

### What it does to the rest of the site

Nothing, with one deliberate exception. On its own two pages the plugin
dequeues any stylesheet served from the active theme's directory, because
these templates render a complete document with their own header, footer and
design system, the way a page builder's canvas template does, and the theme's
opinions about body, headings and buttons would only fight it. Stylesheets are
found by their URL rather than a guessed handle, so it works whatever theme is
active, and every other page keeps the theme untouched. To switch it off:

```php
add_filter( 'knack_dequeue_theme_styles', '__return_false' );
```

### config.js is still the only file with commercial facts in it

Fields are shaped `{ value, verified }`, and a field is only shown when
`verified` is true. That rule is unchanged by the move to WordPress.

### What the page does with the form

`site.js` keeps the rendered form and the order summary beside it in step:

- picking a package in the packages grid selects it inside the form
- changing it inside the form updates the summary panel, the total and the
  highlighted package card
- `order_reference`, `order_package`, `order_quantity`, `order_subtotal` and
  `order_total` are filled in before submission

If Fluent Forms is deactivated, the section shows a short message and the
support link rather than an empty box, and an admin notice says why.

### Cache busting

Every stylesheet and script is enqueued with the file's own modification time
as its version. This is not cosmetic: the hero video has no `src` in the
markup, so a stale `site.js` would mean no video at all.

### What was not tested here

There is no PHP on the machine this was built on, so the templates were
verified by rendering them with WordPress's functions mocked out: the markup
balances, no asset path was left relative, both pages render, the order form
lands in the right place and the package sync works in both directions. **The
first load in WordPress is the real test.** If a template errors, the cause is
almost certainly in one of the five hand-written files in `inc/`, not in the
generated markup, and the error names the file and line.

### A note on `reserve/`

`assets/img/reserve/` is deliberately excluded from the plugin. It holds the
artwork held back because the picture itself makes a claim that is not
evidenced. Leaving it out means it is not one click away from the Media
Library.
