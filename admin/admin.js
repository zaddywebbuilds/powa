/* ============================================================================
   Knack Extra - store settings
   Edits a working copy of window.KNACK and writes it back out as config.js.
   Nothing here talks to a server, because there isn't one.
   ========================================================================== */
(function () {
  'use strict';

  var $  = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  var ORIGINAL = JSON.parse(JSON.stringify(window.KNACK));
  var D = JSON.parse(JSON.stringify(window.KNACK));   // working copy
  var dirty = false;

  function at(obj, path) {
    return String(path).split('.').reduce(function (o, k) { return o == null ? undefined : o[k]; }, obj);
  }
  function parentOf(obj, path) {
    var parts = String(path).split('.');
    var last = parts.pop();
    var p = parts.reduce(function (o, k) { return o[k]; }, obj);
    return [p, last];
  }
  function setVal(path, v) {
    var pl = parentOf(D, path), p = pl[0], k = pl[1];
    if (p[k] && typeof p[k] === 'object' && 'verified' in p[k]) p[k].value = v;
    else p[k] = v;
    touch();
  }
  function getVal(path) {
    var f = at(D, path);
    return (f && typeof f === 'object' && 'verified' in f) ? f.value : f;
  }
  function setVerified(path, on) {
    var f = at(D, path);
    if (f && typeof f === 'object' && 'verified' in f) { f.verified = !!on; touch(); }
  }
  function getVerified(path) {
    var f = at(D, path);
    return !!(f && typeof f === 'object' && f.verified);
  }
  function isLive(path) {
    var f = at(D, path);
    if (f == null) return false;
    if (typeof f !== 'object' || !('verified' in f)) return !!f;
    if (!f.verified) return false;
    var v = f.value;
    if (v == null || v === '') return false;
    if (Array.isArray(v) && !v.length) return false;
    return true;
  }

  function touch() {
    dirty = true;
    $('#status').textContent = 'Unsaved changes. Use Save changes to download the new config.js.';
    $('#status').style.color = '#742C2C';
    renderReadiness();
    renderPkgWarn();
  }

  /* ------------------------------------------------------------- binding */

  function bindFields() {
    // text / number / textarea bound to a dotted path
    $$('[data-path]').forEach(function (n) {
      var path = n.getAttribute('data-path');
      var v = getVal(path);
      if (n.hasAttribute('data-list')) n.value = Array.isArray(v) ? v.join('\n') : '';
      else n.value = (v == null) ? '' : v;

      n.addEventListener('input', function () {
        var out;
        if (n.hasAttribute('data-list')) {
          out = n.value.split('\n').map(function (s) { return s.trim(); }).filter(Boolean);
        } else if (n.hasAttribute('data-num')) {
          out = n.value === '' ? null : Number(n.value);
        } else {
          out = n.value.trim();
        }
        setVal(path, out);
      });
    });

    // "confirmed" checkboxes
    $$('[data-verify]').forEach(function (n) {
      var path = n.getAttribute('data-verify');
      n.checked = getVerified(path);
      syncToggle(n);
      n.addEventListener('change', function () { setVerified(path, n.checked); syncToggle(n); });
    });

    // plain boolean values
    $$('[data-bool]').forEach(function (n) {
      var path = n.getAttribute('data-bool');
      n.checked = getVal(path) === true;
      syncToggle(n);
      n.addEventListener('change', function () { setVal(path, n.checked); syncToggle(n); });
    });

    // preview mode
    var pm = $('#previewMode');
    pm.checked = !!D.site.previewMode;
    syncToggle(pm);
    updatePreviewLabel();
    pm.addEventListener('change', function () {
      D.site.previewMode = pm.checked;
      syncToggle(pm);
      updatePreviewLabel();
      touch();
    });
  }

  function syncToggle(input) {
    var label = input.closest('.vtoggle');
    if (label) label.setAttribute('data-on', input.checked ? '1' : '0');
  }

  function updatePreviewLabel() {
    $('#previewLabel').textContent = $('#previewMode').checked
      ? 'Preview mode is ON. Customers see the pre-launch bar.'
      : 'Preview mode is OFF. The site is in live commercial mode.';
  }

  /* ----------------------------------------------------------- readiness */

  var CHECKS = [
    ['site.businessName',     'Registered business name'],
    ['site.businessAddress',  'Business address'],
    ['contact.whatsapp',      'WhatsApp number (orders go here)'],
    ['contact.phone',         'Customer phone number'],
    ['contact.email',         'Support email'],
    ['contact.hours',         'Support hours'],
    ['product.category',      'Product category'],
    ['product.packSize',      'Pack size'],
    ['product.manufacturer',  'Manufacturer'],
    ['product.nafdacNumber',  'NAFDAC registration number'],
    ['product.ingredients',   'Ingredient list'],
    ['product.dosage',        'Approved dosage'],
    ['product.warnings',      'Warnings and precautions'],
    ['delivery.free',         'Whether delivery is free'],
    ['delivery.timeframe',    'Delivery timeframe'],
    ['delivery.coverage',     'Areas covered'],
    ['delivery.packaging',    'Packaging'],
    ['payment.onDelivery',    'Payment on delivery'],
    ['refund.windowDays',     'Return window'],
    ['refund.summary',        'Return policy summary'],
    ['refund.conditions',     'Return conditions']
  ];

  function renderReadiness() {
    var done = 0;
    var html = CHECKS.map(function (c) {
      var ok = isLive(c[0]);
      if (ok) done++;
      return '<li><span class="pill ' + (ok ? 'ok">Confirmed' : 'no">Outstanding') + '</span>' + c[1] + '</li>';
    }).join('');
    $('#readiness').innerHTML =
      '<li style="font-weight:700;border-bottom:1px solid var(--line)">' + done + ' of ' + CHECKS.length +
      ' confirmed' + (done === CHECKS.length ? '. You are clear to turn preview mode off.' : '.') + '</li>' + html;
  }

  /* ------------------------------------------------------------ packages */

  function renderPkgEditor() {
    var box = $('#pkg-editor');
    box.innerHTML = D.packages.map(function (p, i) {
      return '' +
      '<div style="border:1px solid var(--line);border-radius:9px;padding:14px;margin-bottom:12px">' +
        '<div class="row">' +
          '<div class="f"><label>Name</label><input type="text" data-pkg="' + i + '" data-k="name" value="' + escAttr(p.name) + '"></div>' +
          '<div class="f"><label>Bottles</label><input type="number" min="1" step="1" data-pkg="' + i + '" data-k="qty" value="' + p.qty + '"></div>' +
        '</div>' +
        '<div class="row">' +
          '<div class="f"><label>Price (&#8358;)</label><input type="number" min="0" step="100" data-pkg="' + i + '" data-k="price" value="' + p.price + '"></div>' +
          '<div class="f"><label>Previous price <span class="note">only if it was genuinely charged</span></label>' +
            '<input type="number" min="0" step="100" data-pkg="' + i + '" data-k="wasPrice" value="' + (p.wasPrice && p.wasPrice.value != null ? p.wasPrice.value : '') + '">' +
            '<label class="vtoggle" data-on="' + (p.wasPrice && p.wasPrice.verified ? 1 : 0) + '">' +
              '<input type="checkbox" data-pkg="' + i + '" data-k="wasVerified"' + (p.wasPrice && p.wasPrice.verified ? ' checked' : '') + '>' +
              '<span>Confirmed as a real previous price</span></label>' +
          '</div>' +
        '</div>' +
        '<div class="f"><label>Badge <span class="note">factual only. Leave empty unless it is true.</span></label>' +
          '<input type="text" data-pkg="' + i + '" data-k="badge" value="' + escAttr(p.badge || '') + '"></div>' +
        '<div class="f"><label>Short description</label>' +
          '<input type="text" data-pkg="' + i + '" data-k="blurb" value="' + escAttr(p.blurb || '') + '"></div>' +
      '</div>';
    }).join('');

    $$('[data-pkg]', box).forEach(function (n) {
      n.addEventListener('input', function () {
        var p = D.packages[Number(n.getAttribute('data-pkg'))];
        var k = n.getAttribute('data-k');
        if (k === 'qty' || k === 'price') p[k] = Number(n.value) || 0;
        else if (k === 'wasPrice') { p.wasPrice = p.wasPrice || {}; p.wasPrice.value = n.value === '' ? null : Number(n.value); }
        else if (k === 'wasVerified') { p.wasPrice = p.wasPrice || {}; p.wasPrice.verified = n.checked; syncToggle(n); }
        else if (k === 'badge') p.badge = n.value.trim() || null;
        else p[k] = n.value;
        touch();
      });
    });
  }

  function renderPkgWarn() {
    var box = $('#pkg-warn');
    if (!box) return;
    var msgs = [];

    var sorted = D.packages.slice().sort(function (a, b) { return a.qty - b.qty; });
    for (var i = 1; i < sorted.length; i++) {
      var prev = sorted[i - 1], cur = sorted[i];
      if (!prev.qty || !cur.qty) continue;
      if ((cur.price / cur.qty) > (prev.price / prev.qty)) {
        msgs.push('The ' + cur.name + ' costs ' + naira(Math.round(cur.price / cur.qty)) +
          ' per bottle, which is more than the ' + prev.name + ' at ' + naira(Math.round(prev.price / prev.qty)) +
          '. A customer who does the arithmetic has no reason to buy the bigger pack.');
      }
    }
    D.packages.forEach(function (p) {
      if (p.wasPrice && p.wasPrice.value && !p.wasPrice.verified) {
        msgs.push('The previous price on the ' + p.name + ' is not marked as confirmed, so it stays hidden. ' +
          'Showing a struck-through price that was never charged is a misleading price claim.');
      }
      if (p.badge && /popular|best.?sell|most/i.test(p.badge)) {
        msgs.push('The badge on the ' + p.name + ' claims popularity. Only use that if you have the sales figures to back it.');
      }
    });

    box.innerHTML = msgs.length
      ? '<div class="warn"><strong>Worth looking at</strong>' + msgs.map(function (m) { return '<div>&bull; ' + m + '</div>'; }).join('') + '</div>'
      : '';
  }

  function naira(n) { return '₦' + Number(n).toLocaleString('en-NG'); }
  function escAttr(s) { return String(s == null ? '' : s).replace(/"/g, '&quot;').replace(/</g, '&lt;'); }

  /* --------------------------------------------------------------- stats */

  function renderStats() {
    var body = $('#stats-body');
    var s = {};
    try { s = JSON.parse(localStorage.getItem('ke_stats') || '{}'); } catch (e) {}
    var keys = Object.keys(s).filter(function (k) { return k !== '_updated'; }).sort();
    body.innerHTML = keys.length
      ? keys.map(function (k) {
          return '<tr><td>' + k.replace(/_/g, ' ') + '</td><td class="num">' + s[k] + '</td></tr>';
        }).join('')
      : '<tr><td colspan="2" style="color:var(--muted)">Nothing recorded in this browser yet. Open the site in this same browser and the counts appear here.</td></tr>';

    var wa = at(D, 'contact.whatsapp');
    var link = $('#wa-link');
    if (wa && wa.verified && wa.value) {
      link.href = 'https://wa.me/' + String(wa.value).replace(/\D/g, '');
    } else {
      link.removeAttribute('href');
      link.textContent = 'Add a WhatsApp number first';
      link.style.opacity = '.5';
      link.style.pointerEvents = 'none';
    }
  }

  /* ----------------------------------------------------------- serialise */

  // Comments worth keeping in the emitted file, keyed by the line they precede.
  var NOTES = {
    'site.previewMode':       'true = pre-launch banner on. false = live commercial mode.',
    'contact.whatsapp':       'Orders are sent to this number. Digits only, with country code.',
    'product.packSize':       'Only mark verified against a real bottle, not the artwork.',
    'product.nafdacNumber':   'Registration is not evidence that a product works.',
    'product.ingredients':    'Never published unless verified against the printed label.',
    'product.dosage':         'Copy from the pack word for word, or leave empty.',
    'payment.cardOnDelivery': 'Only true if the rider genuinely carries a POS terminal.',
    'refund.conditions':      'Write these out. Unconditional refund wording with hidden conditions causes disputes.'
  };

  function ser(v, indent, path) {
    var pad = '  '.repeat(indent);
    var padIn = '  '.repeat(indent + 1);

    if (v === null) return 'null';
    if (typeof v === 'string') return JSON.stringify(v);
    if (typeof v === 'number' || typeof v === 'boolean') return String(v);

    if (Array.isArray(v)) {
      if (!v.length) return '[]';
      var simple = v.every(function (x) { return typeof x === 'string' && x.length < 60; });
      if (simple && v.length <= 4) return '[' + v.map(function (x) { return JSON.stringify(x); }).join(', ') + ']';
      return '[\n' + v.map(function (x) { return padIn + ser(x, indent + 1, path); }).join(',\n') + '\n' + pad + ']';
    }

    var keys = Object.keys(v);
    if (!keys.length) return '{}';
    // keep { value, verified } on one line where it is short
    if (keys.length === 2 && 'value' in v && 'verified' in v) {
      var inline = '{ value: ' + ser(v.value, indent, path) + ', verified: ' + v.verified + ' }';
      if (inline.length < 96) return inline;
    }
    return '{\n' + keys.map(function (k) {
      var p = path ? path + '.' + k : k;
      var note = NOTES[p] ? padIn + '// ' + NOTES[p] + '\n' : '';
      return note + padIn + key(k) + ': ' + ser(v[k], indent + 1, p);
    }).join(',\n') + '\n' + pad + '}';
  }

  function key(k) { return /^[A-Za-z_$][A-Za-z0-9_$]*$/.test(k) ? k : JSON.stringify(k); }

  function buildFile() {
    return '' +
'/* ============================================================================\n' +
'   KNACK EXTRA - SINGLE SOURCE OF TRUTH\n' +
'   ----------------------------------------------------------------------------\n' +
'   Every price, contact detail, policy and claim on this website is read from\n' +
'   this file. Nothing is hard-coded into the pages.\n' +
'\n' +
'   Generated by /admin/ on ' + new Date().toISOString().slice(0, 16).replace('T', ' ') + '.\n' +
'\n' +
'   RULES THIS FILE ENFORCES\n' +
'   1. Any field shaped { value, verified } is only rendered on the public site\n' +
'      when verified is true. Unverified facts are hidden, never invented.\n' +
'   2. site.previewMode true shows the pre-launch banner and lists what is\n' +
'      still missing. Set it false only after the launch checklist is done.\n' +
'   3. Nothing in here may state a medical result, a cure, a timeframe for an\n' +
'      effect, or an approval that has not been evidenced.\n' +
'   ========================================================================== */\n\n' +
'window.KNACK = ' + ser(D, 0, '') + ';\n';
  }

  /* ------------------------------------------------------------- actions */

  function wireTabs() {
    $$('.tab').forEach(function (t) {
      t.addEventListener('click', function () {
        $$('.tab').forEach(function (o) { o.setAttribute('aria-selected', 'false'); });
        $$('.panel').forEach(function (p) { p.hidden = true; });
        t.setAttribute('aria-selected', 'true');
        $('#' + t.getAttribute('data-p')).hidden = false;
        if (t.getAttribute('data-p') === 'p-export') $('#preview-code').textContent = buildFile();
        if (t.getAttribute('data-p') === 'p-stats') renderStats();
      });
    });
  }

  function wireActions() {
    $('#goexport').addEventListener('click', function () {
      $$('.tab').forEach(function (o) {
        o.setAttribute('aria-selected', o.getAttribute('data-p') === 'p-export' ? 'true' : 'false');
      });
      $$('.panel').forEach(function (p) { p.hidden = p.id !== 'p-export'; });
      $('#preview-code').textContent = buildFile();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    $('#download').addEventListener('click', function () {
      var blob = new Blob([buildFile()], { type: 'application/javascript' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'config.js';
      a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
      $('#status').textContent = 'Downloaded. Replace assets/js/config.js with it and commit.';
      $('#status').style.color = '#21543D';
      dirty = false;
    });

    $('#copy').addEventListener('click', function () {
      navigator.clipboard.writeText(buildFile()).then(function () {
        $('#copy').textContent = 'Copied';
        setTimeout(function () { $('#copy').textContent = 'Copy to clipboard'; }, 1600);
      });
    });

    $('#revert').addEventListener('click', function () {
      if (dirty && !window.confirm('Throw away your unsaved changes?')) return;
      D = JSON.parse(JSON.stringify(ORIGINAL));
      dirty = false;
      bindFields();
      renderPkgEditor();
      renderReadiness();
      renderPkgWarn();
      $('#status').textContent = 'Reverted to the saved config.';
      $('#status').style.color = '';
    });

    $('#clear-stats').addEventListener('click', function () {
      try { localStorage.removeItem('ke_stats'); } catch (e) {}
      renderStats();
    });

    window.addEventListener('beforeunload', function (e) {
      if (!dirty) return;
      e.preventDefault();
      e.returnValue = '';
    });
  }

  /* --------------------------------------------------------------- start */

  bindFields();
  renderPkgEditor();
  renderReadiness();
  renderPkgWarn();
  renderStats();
  wireTabs();
  wireActions();
  $('#preview-code').textContent = buildFile();
})();
