/* ============================================================================
   KNACK EXTRA - site engine
   Reads window.KNACK (assets/js/config.js) and builds every price, policy and
   contact detail on the page from it. Nothing commercial is hard-coded here.

   The one rule that matters: a config field shaped { value, verified } is only
   rendered when verified === true. Unverified facts are never shown to a
   customer and never invented.
   ========================================================================== */
(function () {
  'use strict';

  var C = window.KNACK;
  if (!C) { console.error('config.js did not load'); return; }

  /* ------------------------------------------------------------- helpers */

  var $  = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  // Walk a dotted path: "delivery.timeframe" -> C.delivery.timeframe
  function at(path) {
    return String(path).split('.').reduce(function (o, k) {
      return (o == null) ? undefined : o[k];
    }, C);
  }

  // A field is "live" when it exists, is verified, and holds something real.
  function live(path) {
    var f = at(path);
    if (f == null) return false;
    if (typeof f !== 'object' || !('verified' in f)) return !!f;
    if (!f.verified) return false;
    var v = f.value;
    if (v == null || v === '') return false;
    if (Array.isArray(v) && v.length === 0) return false;
    return true;
  }

  // The value of a field, or null when it is not live.
  function val(path) {
    if (!live(path)) return null;
    var f = at(path);
    return (f && typeof f === 'object' && 'value' in f) ? f.value : f;
  }

  function money(n) {
    return C.site.currencySymbol + Number(n).toLocaleString('en-NG');
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }

  // Replace {{path}} tokens in a string. Returns null if any token is unverified.
  function fill(str) {
    var ok = true;
    var out = String(str).replace(/\{\{([a-zA-Z0-9_.]+)\}\}/g, function (_, p) {
      var v = val(p);
      if (v == null) { ok = false; return ''; }
      return esc(String(v));
    });
    return ok ? out : null;
  }

  /* ------------------------------------------------- conditional elements */
  // data-req="path"          -> remove unless that path is live
  // data-req-any="a,b"       -> remove unless at least one is live
  function applyGates(root) {
    $$('[data-req]', root).forEach(function (n) {
      if (!live(n.getAttribute('data-req'))) n.remove();
    });
    $$('[data-req-any]', root).forEach(function (n) {
      var any = n.getAttribute('data-req-any').split(',').some(function (p) { return live(p.trim()); });
      if (!any) n.remove();
    });
  }

  /* ------------------------------------------------------- announcements */

  function renderAnnounce() {
    var list = $('#announce-list');
    if (!list) return;
    var a = C.announcement;
    if (!a || !a.enabled) { var bar = $('#announce'); if (bar) bar.remove(); return; }

    var items = a.items.filter(function (i) { return !i.requires || live(i.requires); });
    if (!items.length) { $('#announce').remove(); return; }

    items.forEach(function (i, idx) {
      var li = el('li', null, '<span class="dot"></span>' + esc(i.text));
      li.setAttribute('data-on', idx === 0 ? '1' : '0');
      list.appendChild(li);
    });

    // Mobile shows one at a time.
    if (items.length > 1) {
      var n = 0, nodes = $$('li', list);
      setInterval(function () {
        nodes[n].setAttribute('data-on', '0');
        n = (n + 1) % nodes.length;
        nodes[n].setAttribute('data-on', '1');
      }, 4000);
    }
  }

  /* --------------------------------------------------------- spec panels */

  function row(k, v) {
    return '<li><span class="k">' + esc(k) + '</span><span class="v">' + esc(v) + '</span></li>';
  }

  function renderSpecs() {
    var ul = $('#spec-list');
    if (!ul) return;
    var html = row('Product', C.product.name);

    [['Category', 'product.category'],
     ['Pack size', 'product.packSize'],
     ['Manufacturer', 'product.manufacturer'],
     ['Made in', 'product.countryOfOrigin'],
     ['NAFDAC registration', 'product.nafdacNumber']
    ].forEach(function (p) {
      var v = val(p[1]);
      if (v) html += row(p[0], v);
    });

    var st = val('product.storage');
    if (st) html += row('Storage', st);
    ul.innerHTML = html;

  }

  function renderWarnings() {
    var ul = $('#warnings-list');
    if (!ul) return;
    var w = val('product.warnings') || [];
    ul.innerHTML = w.map(function (t) {
      return '<li style="display:block;font-size:.85rem;line-height:1.5">' + esc(t) + '</li>';
    }).join('');
  }

  function renderMedicalNotice() {
    var n = $('#medical-notice');
    if (n) n.textContent = C.product.medicalNotice;
  }

  /* ------------------------------------------------------------ delivery */

  function deliveryFee() {
    if (val('delivery.free') === true) return 0;
    var f = val('delivery.fee');
    return (typeof f === 'number') ? f : null;   // null = "confirmed on the call"
  }

  function feeLabel() {
    var f = deliveryFee();
    if (f === 0) return 'Free';
    if (f === null) return 'Confirmed on the call';
    return money(f);
  }

  function renderDelivery() {
    var ul = $('#delivery-list');
    if (!ul) return;
    var html = '';

    if (live('delivery.coverage')) html += row('Where we deliver', val('delivery.coverage'));
    if (live('delivery.timeframe')) html += row('Usual delivery time', val('delivery.timeframe'));
    if (live('delivery.free') || live('delivery.fee')) html += row('Delivery cost', feeLabel());
    if (live('payment.onDelivery') && val('payment.onDelivery')) html += row('Payment', 'Cash to the rider on arrival');
    if (live('payment.cardOnDelivery') && val('payment.cardOnDelivery')) html += row('Card on delivery', 'Available');
    if (live('delivery.packaging')) html += row('Packaging', val('delivery.packaging'));
    if (live('delivery.carrier')) html += row('Courier', val('delivery.carrier'));

    if (!html) {
      html = '<li style="display:block;font-size:.9rem;line-height:1.55">Our team agrees the delivery cost and the arrival window with you on the phone, ' +
             'before anything is dispatched. Whatever is agreed on that call is what you pay the rider, and nothing is added afterwards.</li>';
    }
    ul.innerHTML = html;
  }

  function renderRefund() {
    var p = $('#refund-copy');
    if (!p) return;
    var s = val('refund.summary');
    if (s) {
      p.textContent = s;
    } else {
      var w = val('refund.windowDays');
      p.textContent = w
        ? 'Returns are accepted within ' + w + ' days. The conditions are set out in full in our returns policy.'
        : 'Check the parcel in front of the rider before you pay for it. If what arrives is not what you ordered, ' +
          'or the pack is damaged or already opened, do not pay, and call us straight away so we can put it right.';
    }
  }

  /* ----------------------------------------------------------------- FAQ */

  function renderFaq() {
    var box = $('#faq-list');
    if (!box) return;

    (C.faq || []).forEach(function (item, i) {
      if (item.requires && !live(item.requires)) return;
      var answer = fill(item.a);
      if (answer == null) return;        // a token inside was unverified

      var wrap = el('div', 'faq-item');
      var id = 'faq-a-' + i;
      wrap.innerHTML =
        '<h3 style="margin:0"><button class="faq-q" aria-expanded="false" aria-controls="' + id + '">' +
        '<span>' + esc(item.q) + '</span><span class="faq-icon" aria-hidden="true"></span></button></h3>' +
        '<div class="faq-a" id="' + id + '"><div class="inner">' + answer + '</div></div>';
      box.appendChild(wrap);
    });

    $$('.faq-q', box).forEach(function (btn) {
      btn.addEventListener('click', function () {
        var panel = document.getElementById(btn.getAttribute('aria-controls'));
        var open = btn.getAttribute('aria-expanded') === 'true';
        $$('.faq-q', box).forEach(function (o) {
          if (o === btn) return;
          o.setAttribute('aria-expanded', 'false');
          document.getElementById(o.getAttribute('aria-controls')).style.height = '0px';
        });
        btn.setAttribute('aria-expanded', open ? 'false' : 'true');
        panel.style.height = open ? '0px' : panel.querySelector('.inner').offsetHeight + 'px';
      });
    });
  }

  /* ------------------------------------------------------------ packages */

  var selected = null;

  function pkgById(id) {
    return C.packages.filter(function (p) { return p.id === id; })[0] || null;
  }

  function renderPackages() {
    var grid = $('#pkg-grid');
    if (!grid) return;

    C.packages.forEach(function (p) {
      var btn = el('button', 'pkg');
      btn.type = 'button';
      btn.setAttribute('role', 'radio');
      btn.setAttribute('aria-checked', 'false');
      btn.dataset.id = p.id;

      var was = (p.wasPrice && p.wasPrice.verified && p.wasPrice.value)
        ? '<span class="was">' + money(p.wasPrice.value) + '</span>' : '';
      var unit = p.qty > 1
        ? '<div class="unit">' + money(Math.round(p.price / p.qty)) + ' per bottle</div>' : '';
      var badge = p.badge ? '<span class="pkg-badge">' + esc(p.badge) + '</span>' : '';

      btn.innerHTML =
        badge +
        '<div class="pkg-img"><img src="assets/img/' + p.image + '.webp" width="380" height="380" loading="lazy" decoding="async" alt="' +
          esc(p.qty + (p.qty > 1 ? ' bottles' : ' bottle') + ' of Knack Extra Capsules') + '"></div>' +
        '<div class="pkg-body">' +
          '<div class="qty">' + p.qty + (p.qty > 1 ? ' bottles' : ' bottle') + '</div>' +
          '<h3>' + esc(p.name) + '</h3>' +
          '<div class="price">' + money(p.price) + was + '</div>' +
          unit +
          '<p class="blurb">' + esc(p.blurb) + '</p>' +
          '<div class="pick"><span class="tick"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.4" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg></span>' +
          '<span class="pick-label">Choose this</span></div>' +
        '</div>';

      btn.addEventListener('click', function () { selectPackage(p.id, true); });
      grid.appendChild(btn);
    });

    // Honest note about the unit pricing, driven by the actual numbers.
    var cheapest = C.packages.slice().sort(function (a, b) {
      return (a.price / a.qty) - (b.price / b.qty);
    })[0];
    var biggest = C.packages.slice().sort(function (a, b) { return b.qty - a.qty; })[0];
    var note = $('#pkg-foot');
    if (note && cheapest && biggest && cheapest.id !== biggest.id) {
      note.textContent = 'A note on value: the ' + cheapest.name.toLowerCase() + ' works out cheapest per bottle at ' +
        money(Math.round(cheapest.price / cheapest.qty)) + ', so it is the better buy if you want more than one. ' +
        'We would rather point that out than let you assume the largest pack is automatically the best deal.';
    }
  }

  function selectPackage(id, scroll) {
    var p = pkgById(id);
    if (!p) return;
    selected = p;

    $$('.pkg').forEach(function (n) {
      var on = n.dataset.id === id;
      n.dataset.selected = on ? '1' : '0';
      n.setAttribute('aria-checked', on ? 'true' : 'false');
      var lbl = $('.pick-label', n);
      if (lbl) lbl.textContent = on ? 'Selected' : 'Choose this';
    });

    updateSummary();
    track('package_select', id);

    if (scroll) {
      var t = $('#order');
      if (t) t.scrollIntoView({ behavior: prefersReduced() ? 'auto' : 'smooth', block: 'start' });
    }
  }

  function updateSummary() {
    if (!selected) return;
    var sub = selected.price;
    var fee = deliveryFee();
    var total = sub + (fee || 0);

    var set = function (id, v) { var n = $(id); if (n) n.textContent = v; };
    set('#sum-name', selected.name);
    set('#sum-qty', selected.qty + (selected.qty > 1 ? ' bottles' : ' bottle'));
    set('#sum-unit', money(Math.round(selected.price / selected.qty)));
    set('#sum-sub', money(sub));
    set('#sum-del', feeLabel());
    set('#sum-total', fee === null ? money(total) + '*' : money(total));

    var img = $('#sum-img');
    if (img) { img.src = 'assets/img/' + selected.image + '.webp'; img.alt = ''; }

    var note = $('#sum-note');
    if (note) {
      note.textContent = fee === null
        ? '* Delivery is confirmed when we call you, before anything is dispatched. You will not be charged anything you have not agreed to.'
        : 'You pay this amount to the rider when the parcel reaches you. Nothing is taken before then.';
    }
  }

  /* ------------------------------------------------- phone + validation */

  // Accepts 0803..., 234803..., +234803..., with spaces or dashes.
  function normalisePhone(raw) {
    var d = String(raw).replace(/[^\d+]/g, '');
    if (d.indexOf('+234') === 0) d = d.slice(4);
    else if (d.indexOf('234') === 0 && d.length >= 13) d = d.slice(3);
    else if (d.indexOf('0') === 0) d = d.slice(1);
    else if (d.indexOf('+') === 0) return null;
    if (!/^[789][01]\d{8}$/.test(d)) return null;   // 10 digits after the leading 0
    return '+234' + d;
  }

  function setError(inputId, errId, msg) {
    var inp = $(inputId), err = $(errId);
    if (inp) inp.setAttribute('aria-invalid', msg ? 'true' : 'false');
    if (err) { err.textContent = msg || ''; err.setAttribute('data-on', msg ? '1' : '0'); }
    return !msg;
  }

  function validate(showAll) {
    var ok = true;
    var v = function (id) { var n = $(id); return n ? n.value.trim() : ''; };

    if (showAll || v('#f-name')) {
      ok = setError('#f-name', '#e-name', v('#f-name').length < 2 ? 'Please enter your full name.' : '') && ok;
    }
    if (showAll || v('#f-phone')) {
      ok = setError('#f-phone', '#e-phone',
        !normalisePhone(v('#f-phone')) ? 'Enter a Nigerian number, for example 0803 000 0000.' : '') && ok;
    }
    if (v('#f-alt')) {
      ok = setError('#f-alt', '#e-alt', !normalisePhone(v('#f-alt')) ? 'That second number does not look right.' : '') && ok;
    }
    if (showAll || v('#f-state')) {
      ok = setError('#f-state', '#e-state', !v('#f-state') ? 'Please choose your state.' : '') && ok;
    }
    if (showAll || v('#f-city')) {
      ok = setError('#f-city', '#e-city', v('#f-city').length < 2 ? 'Please enter your city or LGA.' : '') && ok;
    }
    if (showAll || v('#f-address')) {
      ok = setError('#f-address', '#e-address', v('#f-address').length < 8 ? 'Please give the full delivery address.' : '') && ok;
    }
    if (showAll) {
      var c = $('#f-consent');
      ok = setError('#f-consent', '#e-consent', (c && !c.checked) ? 'Please confirm this before we can take the order.' : '') && ok;
      if (!selected) {
        var pf = $('#pkg-foot');
        if (pf) pf.textContent = 'Please choose a package above first.';
        ok = false;
      }
    }
    return ok;
  }

  /* -------------------------------------------------------------- orders */

  function reference() {
    var d = new Date();
    var p = function (n) { return String(n).padStart(2, '0'); };
    var rand = Math.random().toString(36).slice(2, 6).toUpperCase();
    return C.order.referencePrefix + p(d.getFullYear() % 100) + p(d.getMonth() + 1) + p(d.getDate()) + '-' + rand;
  }

  function fingerprint(o) {
    return [o.phone, o.package, o.address].join('|').toLowerCase().replace(/\s+/g, '');
  }

  function isDuplicate(fp) {
    try {
      var last = JSON.parse(localStorage.getItem('ke_last_order') || 'null');
      if (!last || last.fp !== fp) return false;
      var mins = (Date.now() - last.at) / 60000;
      return mins < (C.order.duplicateWindowMinutes || 30);
    } catch (e) { return false; }
  }

  function orderMessage(o) {
    var L = [];
    L.push('New order from the Knack Extra website');
    L.push('Reference: ' + o.ref);
    L.push('');
    L.push('Package: ' + o.package + ' (' + o.qty + (o.qty > 1 ? ' bottles' : ' bottle') + ')');
    L.push('Subtotal: ' + money(o.subtotal));
    L.push('Delivery: ' + o.deliveryLabel);
    L.push('Total payable: ' + money(o.total) + (o.feeUnknown ? ' plus delivery, to be confirmed' : ''));
    L.push('');
    L.push('Name: ' + o.name);
    L.push('Phone: ' + o.phone);
    if (o.altPhone) L.push('Second number: ' + o.altPhone);
    L.push('State: ' + o.state);
    L.push('City / LGA: ' + o.city);
    L.push('Address: ' + o.address);
    if (o.landmark) L.push('Landmark: ' + o.landmark);
    if (o.notes) L.push('Notes: ' + o.notes);
    L.push('');
    L.push('Marketing consent: ' + (o.marketing ? 'yes' : 'no'));
    L.push('Payment: on delivery');
    return L.join('\n');
  }

  function submitOrder(e) {
    e.preventDefault();
    if (!validate(true)) {
      var bad = $('[aria-invalid="true"]');
      if (bad) { bad.focus(); bad.scrollIntoView({ behavior: prefersReduced() ? 'auto' : 'smooth', block: 'center' }); }
      return;
    }

    var fee = deliveryFee();
    var o = {
      ref: reference(),
      at: Date.now(),
      name: $('#f-name').value.trim(),
      phone: normalisePhone($('#f-phone').value),
      altPhone: $('#f-alt').value.trim() ? normalisePhone($('#f-alt').value) : '',
      state: $('#f-state').value,
      city: $('#f-city').value.trim(),
      address: $('#f-address').value.trim(),
      landmark: $('#f-landmark').value.trim(),
      notes: $('#f-notes').value.trim(),
      marketing: $('#f-marketing').checked,
      package: selected.name,
      packageId: selected.id,
      qty: selected.qty,
      subtotal: selected.price,
      deliveryLabel: feeLabel(),
      feeUnknown: fee === null,
      total: selected.price + (fee || 0)
    };

    var fp = fingerprint(o);
    if (isDuplicate(fp)) {
      if (!window.confirm('It looks like you just sent this same order a moment ago. Send it again?')) return;
    }

    var btn = $('#submit-btn');
    btn.disabled = true;
    btn.textContent = 'Sending your order…';

    try {
      localStorage.setItem('ke_last_order', JSON.stringify({ fp: fp, at: Date.now() }));
      // The thank-you page reads this. Nothing personal goes in the URL.
      sessionStorage.setItem('ke_order', JSON.stringify(o));
    } catch (err) { /* private browsing - carry on */ }

    track('order_submit', o.packageId);

    var wa = val('contact.whatsapp');
    var text = encodeURIComponent(orderMessage(o));

    if (wa) {
      window.open('https://wa.me/' + String(wa).replace(/\D/g, '') + '?text=' + text, '_blank', 'noopener');
    } else {
      var mail = val('contact.email');
      if (mail) {
        window.location.href = 'mailto:' + mail + '?subject=' +
          encodeURIComponent('Website order ' + o.ref) + '&body=' + text;
      }
    }

    setTimeout(function () { window.location.href = 'thank-you.html'; }, 600);
  }

  /* ----------------------------------------------------- support links */

  function supportHref() {
    var wa = val('contact.whatsapp');
    if (wa) {
      return 'https://wa.me/' + String(wa).replace(/\D/g, '') +
             '?text=' + encodeURIComponent(C.contact.prefilledMessage);
    }
    var mail = val('contact.email');
    if (mail) return 'mailto:' + mail + '?subject=' + encodeURIComponent('Question about Knack Extra');
    var ph = val('contact.phone');
    if (ph) return 'tel:' + String(ph).replace(/\s/g, '');
    return '#order';
  }

  function wireSupport() {
    var href = supportHref();
    var external = href.indexOf('http') === 0;
    $$('[data-support-link]').forEach(function (a) {
      a.setAttribute('href', href);
      if (external) { a.setAttribute('target', '_blank'); a.setAttribute('rel', 'noopener'); }
      a.addEventListener('click', function () { track('support_click', ''); });
    });
    // No contact channel configured at all: hide the floating button rather
    // than leave a button that goes nowhere.
    if (href === '#order') {
      var fab = $('#support-fab');
      if (fab) fab.remove();
    }
  }

  /* ---------------------------------------------------------- footer */

  function renderFooter() {
    var ul = $('#foot-contact');
    if (ul) {
      var html = '';
      var ph = val('contact.phone');
      var wa = val('contact.whatsapp');
      var em = val('contact.email');
      var hr = val('contact.hours');
      var ad = val('site.businessAddress');
      if (ph) html += '<li><a href="tel:' + esc(String(ph).replace(/\s/g, '')) + '">' + esc(ph) + '</a></li>';
      if (wa) html += '<li><a href="' + esc(supportHref()) + '" target="_blank" rel="noopener">WhatsApp</a></li>';
      if (em) html += '<li><a href="mailto:' + esc(em) + '">' + esc(em) + '</a></li>';
      if (hr) html += '<li>' + esc(hr) + '</li>';
      if (ad) html += '<li>' + esc(ad) + '</li>';
      if (html) { ul.innerHTML = html; }
      else {
        // Nothing to show: drop the whole column instead of leaving a gap.
        var col = ul.parentNode;
        if (col && col.parentNode) col.parentNode.removeChild(col);
      }
    }

    var biz = val('site.businessName');
    var fb = $('#foot-business');
    if (fb && biz) {
      fb.textContent = biz + ' sells Knack Extra Capsules in Nigeria, with payment on delivery.';
    }

    var dis = $('#foot-disclaimer');
    if (dis) dis.textContent = C.legal.disclaimer;

    var cp = $('#foot-copy');
    if (cp) {
      cp.textContent = '© ' + new Date().getFullYear() + ' ' + (biz || C.site.brand) + '. All rights reserved.';
    }
  }

  function renderStates() {
    var sel = $('#f-state');
    if (!sel) return;
    C.order.states.forEach(function (s) {
      var o = document.createElement('option');
      o.value = s; o.textContent = s;
      sel.appendChild(o);
    });
  }

  function renderSubmitNote() {
    var n = $('#submit-note');
    if (!n) return;
    var wa = val('contact.whatsapp');
    var em = val('contact.email');
    if (wa) {
      n.textContent = 'This opens WhatsApp with your order already written out, so you only have to press send. ' +
        'We call you to confirm before anything is dispatched.';
    } else if (em) {
      n.textContent = 'This opens your email app with the order already written out. We call you to confirm before anything is dispatched.';
    } else {
      // No contact channel configured. Hide the form rather than show a
      // button that cannot do anything, and say nothing about why.
      n.textContent = '';
      var b = $('#submit-btn');
      if (b) { b.disabled = true; b.hidden = true; }
    }
  }

  function renderPrices() {
    var min = Math.min.apply(null, C.packages.map(function (p) { return p.price; }));
    $$('[data-price="min"]').forEach(function (n) { n.textContent = money(min); });
  }

  /* ------------------------------------------------------- interactions */

  function prefersReduced() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  function wireHeader() {
    var head = $('#head');
    var bar = $('#mobile-bar');
    var hero = $('.hero');
    var onScroll = function () {
      var y = window.scrollY;
      if (head) head.dataset.stuck = y > 24 ? '1' : '0';
      if (bar && hero) bar.dataset.on = (y > hero.offsetHeight * 0.65) ? '1' : '0';
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    var burger = $('#burger'), nav = $('#mobile-nav');
    if (burger && nav) {
      burger.addEventListener('click', function () {
        var open = burger.getAttribute('aria-expanded') === 'true';
        burger.setAttribute('aria-expanded', open ? 'false' : 'true');
        burger.setAttribute('aria-label', open ? 'Open menu' : 'Close menu');
        nav.dataset.open = open ? '0' : '1';
        document.body.style.overflow = open ? '' : 'hidden';
      });
      $$('a', nav).forEach(function (a) {
        a.addEventListener('click', function () {
          burger.setAttribute('aria-expanded', 'false');
          nav.dataset.open = '0';
          document.body.style.overflow = '';
        });
      });
    }
  }

  function wireReveal() {
    var nodes = $$('[data-rise]');
    if (!nodes.length) return;
    if (prefersReduced() || !('IntersectionObserver' in window)) {
      nodes.forEach(function (n) { n.dataset.in = '1'; });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.dataset.in = '1'; io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    nodes.forEach(function (n) { io.observe(n); });
  }

  // The hero clip carries no information, so it is started from here rather
  // than with an autoplay attribute: anyone who has asked their system for
  // reduced motion keeps the still poster frame, and so does anyone without
  // JavaScript. It is silent and has no controls either way.
  function wireHeroVideo() {
    var v = $('.hero-video');
    if (!v || prefersReduced()) return;
    v.muted = true;
    var p = v.play();
    if (p && p.catch) p.catch(function () { /* browser declined; poster stays */ });
  }

  function wireForm() {
    var form = $('#order-form');
    if (!form) return;
    form.addEventListener('submit', submitOrder);
    ['#f-name', '#f-phone', '#f-alt', '#f-state', '#f-city', '#f-address'].forEach(function (id) {
      var n = $(id);
      if (n) n.addEventListener('blur', function () { validate(false); });
    });
    var started = false;
    form.addEventListener('input', function () {
      if (!started) { started = true; track('checkout_start', ''); }
    }, { once: false });
  }

  /* ------------------------------------------------- first-party stats */
  // Aggregate counters in this browser only. Nothing leaves the device, no
  // third-party pixels, nothing about the product category is transmitted.

  function track(event, label) {
    try {
      var k = 'ke_stats';
      var s = JSON.parse(localStorage.getItem(k) || '{}');
      var key = label ? event + ':' + label : event;
      s[key] = (s[key] || 0) + 1;
      s._updated = Date.now();
      localStorage.setItem(k, JSON.stringify(s));
    } catch (e) { /* storage unavailable */ }
  }

  function trackSections() {
    if (!('IntersectionObserver' in window)) return;
    var seen = {};
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting && !seen[e.target.id]) {
          seen[e.target.id] = 1;
          track('view', e.target.id);
        }
      });
    }, { threshold: 0.4 });
    ['about', 'product', 'packages', 'delivery', 'faq', 'order'].forEach(function (id) {
      var n = document.getElementById(id);
      if (n) io.observe(n);
    });
  }

  /* ------------------------------------------------------ structured data */

  function injectSchema() {
    var offers = C.packages.map(function (p) {
      return {
        '@type': 'Offer',
        name: p.name,
        price: String(p.price),
        priceCurrency: C.site.currency,
        availability: 'https://schema.org/InStock',
        eligibleQuantity: { '@type': 'QuantitativeValue', value: p.qty, unitText: 'bottle' },
        url: C.site.url + '#packages'
      };
    });

    var product = {
      '@context': 'https://schema.org',
      '@type': 'Product',
      name: C.product.name,
      description: 'Herbal capsule product for adult men, sold in Nigeria with payment on delivery.',
      image: [C.site.url + 'assets/img/product-hero.webp'],
      offers: {
        '@type': 'AggregateOffer',
        priceCurrency: C.site.currency,
        lowPrice: String(Math.min.apply(null, C.packages.map(function (p) { return p.price; }))),
        highPrice: String(Math.max.apply(null, C.packages.map(function (p) { return p.price; }))),
        offerCount: String(C.packages.length),
        offers: offers
      }
    };
    var brandName = val('site.businessName');
    if (brandName) product.brand = { '@type': 'Brand', name: brandName };
    if (live('product.manufacturer')) product.manufacturer = { '@type': 'Organization', name: val('product.manufacturer') };

    var org = {
      '@context': 'https://schema.org',
      '@type': 'Organization',
      name: brandName || C.site.brand,
      url: C.site.url
    };
    if (live('contact.phone')) {
      org.contactPoint = [{ '@type': 'ContactPoint', telephone: val('contact.phone'), contactType: 'customer service', areaServed: 'NG' }];
    }
    if (live('site.businessAddress')) {
      org.address = { '@type': 'PostalAddress', streetAddress: val('site.businessAddress'), addressCountry: 'NG' };
    }

    var faqNodes = (C.faq || []).filter(function (f) {
      return (!f.requires || live(f.requires)) && fill(f.a) != null;
    }).map(function (f) {
      return { '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: fill(f.a) } };
    });

    var blocks = [product, org];
    if (faqNodes.length) blocks.push({ '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: faqNodes });

    blocks.forEach(function (b) {
      var s = document.createElement('script');
      s.type = 'application/ld+json';
      s.textContent = JSON.stringify(b);
      document.head.appendChild(s);
    });
  }

  /* ------------------------------------------------------------- start */

  function init() {
    renderAnnounce();
    applyGates(document);          // strip anything resting on an unverified fact
    renderPrices();
    renderSpecs();
    renderWarnings();
    renderMedicalNotice();
    renderDelivery();
    renderRefund();
    renderFaq();
    renderPackages();
    renderStates();
    renderFooter();
    renderSubmitNote();
    wireSupport();
    wireHeader();
    wireReveal();
    wireHeroVideo();
    wireForm();
    trackSections();
    injectSchema();

    selectPackage(C.packages[0].id, false);   // never preselect the dearest
    track('visit', '');

    window.addEventListener('resize', function () {
      $$('.faq-q[aria-expanded="true"]').forEach(function (b) {
        var p = document.getElementById(b.getAttribute('aria-controls'));
        p.style.height = p.querySelector('.inner').offsetHeight + 'px';
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
