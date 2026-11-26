/* ============================================================================
   KNACK EXTRA - SINGLE SOURCE OF TRUTH
   ----------------------------------------------------------------------------
   Every price, contact detail, policy and claim on this website is read from
   this file. Nothing is hard-coded into the pages. Edit here, or use the
   owner dashboard at /admin/ which writes this file for you.

   RULES THIS FILE ENFORCES
   1. Any field with `verified: false` is NOT rendered on the public website.
      It is listed in the dashboard as outstanding instead.
   2. `site.previewMode: true` shows a pre-launch banner and lists what is
      still missing. Set it to false only after the launch checklist is done.
   3. Nothing in here may state a medical result, a cure, a timeframe for an
      effect, or a clinical/regulatory approval that has not been evidenced.
      See LAUNCH-CHECKLIST.md.
   ========================================================================== */

window.KNACK = {

  /* ---------------------------------------------------------------- site -- */
  site: {
    // Pre-launch gate. true  = staging banner on, outstanding items listed.
    //                 false = live commercial mode.
    previewMode: true,

    brand: "Knack Extra",
    wordmark: "KNACK EXTRA",
    // Legal entity that sells the product. Required before launch.
    businessName: { value: "", verified: false },
    businessAddress: { value: "", verified: false },
    tagline: "Men's personal wellness",
    url: "https://zaddywebbuilds.github.io/powa/",
    locale: "en-NG",
    currency: "NGN",
    currencySymbol: "₦"
  },

  /* ------------------------------------------------------------- contact -- */
  // Same line for WhatsApp and calls.
  contact: {
    whatsapp:    { value: "2349167075671", verified: true, label: "WhatsApp" },
    phone:       { value: "+234 916 707 5671", verified: true },
    email:       { value: "", verified: false },
    hours:       { value: "Monday to Saturday, 9am - 6pm WAT", verified: true },
    prefilledMessage:
      "Hello, I would like more information about Knack Extra and your delivery options."
  },

  /* ------------------------------------------------------- announcement -- */
  announcement: {
    enabled: true,
    // Shown only when the matching commercial term is verified below.
    items: [
      { text: "Free nationwide delivery", requires: "delivery.free" },
      { text: "Payment on delivery", requires: "payment.onDelivery" },
      { text: "Speak to a person before you order", requires: null }
    ]
  },

  /* ------------------------------------------------------------- product -- */
  product: {
    name: "Knack Extra Capsules",
    shortName: "Knack Extra",

    // What the product IS. Written to the seller's own description, with no
    // medical outcome attached. Do not expand this without documentation.
    category: { value: "Herbal food supplement for adult men", verified: true },

    // "30 CAPSULES" appears on the packaging artwork supplied, but that
    // artwork is AI-generated and has not been checked against a real bottle.
    packSize: { value: "30 capsules per bottle", verified: false },

    manufacturer: { value: "", verified: false },
    countryOfOrigin: { value: "", verified: false },

    // Nigeria: NAFDAC registration is mandatory for a herbal product sold
    // commercially. Leave empty until you hold the certificate. A registration
    // number is never evidence that the product works.
    nafdacNumber: { value: "", verified: false },

    // Ingredients are UNKNOWN. The supplied "natural ingredients" artwork
    // shows ginseng, ginger, citrus and seeds. None of that is confirmed, so
    // the ingredients section stays switched off.
    ingredients: { value: [], verified: false },

    // Dosage from the original sales page was "2 capsules, 1 to 2 hours
    // before" with no supporting documentation. Not republished.
    dosage: { value: "", verified: false },
    storage: { value: "Store in a cool, dry place, away from direct sunlight and out of reach of children.", verified: true },

    warnings: {
      value: [
        "For adults aged 18 and over.",
        "Not suitable for anyone who is pregnant or breastfeeding.",
        "Speak to a pharmacist or doctor first if you take prescription medication, or if you live with a heart condition, high blood pressure, diabetes, or kidney or liver disease.",
        "Stop using the product and seek medical advice if you have a reaction to it.",
        "A food supplement does not replace a varied diet or medical treatment."
      ],
      verified: true
    },

    medicalNotice:
      "Persistent sexual health concerns should be discussed with a qualified healthcare professional. Do not use a supplement in place of a medical assessment or prescribed treatment."
  },

  /* ------------------------------------------------------------ packages -- */
  // Prices carried over from the seller's existing page, unchanged.
  // NOTE: the 2-bottle pack is the lowest price per bottle, so the 3-bottle
  // pack is currently the worst value. See LAUNCH-CHECKLIST.md item 3.
  packages: [
    {
      id: "single",
      name: "Single Bottle",
      qty: 1,
      price: 18999,
      // The seller's page lists 23,000 as the normal price. Only show it as a
      // struck-through price once you can show it was genuinely charged.
      wasPrice: { value: 23000, verified: false },
      image: "bundle-one",
      badge: null,
      blurb: "One bottle. The simplest way to start."
    },
    {
      id: "double",
      name: "Double Pack",
      qty: 2,
      price: 27000,
      wasPrice: { value: null, verified: false },
      image: "bundle-two",
      // Factual, arithmetic-based badge. Not "most popular" - no sales data.
      badge: "Lowest price per bottle",
      featured: true,
      blurb: "Two bottles at the lowest unit price we offer."
    },
    {
      id: "triple",
      name: "Triple Pack",
      qty: 3,
      price: 46999,
      wasPrice: { value: null, verified: false },
      image: "bundle-three",
      badge: null,
      blurb: "Three bottles in one delivery."
    }
  ],

  /* ------------------------------------------------------------ delivery -- */
  delivery: {
    // The seller's page states free express delivery nationwide in 1-3 days.
    // Confirm in writing, then set verified: true.
    free: { value: true, verified: true },
    fee: { value: 0, verified: true },
    timeframe: { value: "1 to 3 days", verified: true },
    coverage: { value: "All 36 states and the FCT", verified: true },
    packaging: { value: "Plain outer packaging with no product name printed on it", verified: false },
    carrier: { value: "", verified: false }
  },

  /* ------------------------------------------------------------- payment -- */
  payment: {
    onDelivery: { value: true, verified: true },
    // Do not switch this on unless the rider genuinely carries a POS terminal.
    cardOnDelivery: { value: false, verified: false },
    transfer: { value: false, verified: false },
    note: "You pay the delivery rider when the parcel reaches you. We never ask for card details on this website."
  },

  /* -------------------------------------------------------------- refund -- */
  refund: {
    // Seller's page claims "100% money back guarantee" and "return policy up
    // to 14 days" with no conditions stated. Unconditional refund language is
    // not published until the real conditions are written down.
    windowDays: { value: 14, verified: true },
    conditions: { value: [], verified: false },
    summary: {
      value: "Returns are accepted within 14 days of delivery. Check the parcel in front of the rider before you pay, and if anything is wrong contact us with your order reference so we can agree the return with you.",
      verified: true
    },
    contactFirst: true
  },

  /* ------------------------------------------------------------- reviews -- */
  // Switched OFF. The original page showed four unverifiable chat screenshots
  // with no names, no consent and medical efficacy claims in them. Nothing
  // here is invented. Add real, consented, claim-free reviews and flip this on.
  reviews: {
    enabled: false,
    items: []
  },

  /* ----------------------------------------------------------------- faq -- */
  // Answers that depend on an unverified field above are hidden automatically.
  faq: [
    { q: "What is Knack Extra?",
      a: "Knack Extra is a herbal capsule product sold in Nigeria for adult men. We publish the full label details, including the ingredient list and registration information, as soon as they are confirmed in writing by the supplier. Until then our support team will read you the current label before you order.",
      requires: null },
    { q: "What does it contain?",
      a: "The confirmed ingredient list is not published yet. We would rather show you nothing than show you something we cannot stand behind. Ask our support team for the current label before you place an order.",
      requires: null },
    { q: "How many capsules are in a bottle?",
      a: "Each bottle contains {{product.packSize}}.",
      requires: "product.packSize" },
    { q: "How should it be used?",
      a: "Follow the directions printed on the pack you receive. If anything on the label is unclear, speak to a pharmacist before you take it.",
      requires: null },
    { q: "Are there precautions I should know about?",
      a: "Yes. It is for adults over 18. Speak to a pharmacist or doctor first if you take prescription medication, or if you live with a heart condition, high blood pressure, diabetes, or kidney or liver disease. Stop using it and get medical advice if you react badly to it.",
      requires: null },
    { q: "Can I take it alongside other medication?",
      a: "Ask a pharmacist or your doctor, and show them the pack. We are not able to advise on medicine interactions, and we will not guess.",
      requires: null },
    { q: "Is it registered with NAFDAC?",
      a: "Registration number {{product.nafdacNumber}}. Registration confirms that a product has been through NAFDAC's process. It is not evidence that a product works.",
      requires: "product.nafdacNumber" },
    { q: "What packages are available?",
      a: "One, two or three bottles. Prices are shown in full on the packages section above, and the total you see is the total you pay.",
      requires: null },
    { q: "Can I pay on delivery?",
      a: "Yes. You pay the rider in cash when the parcel reaches you. We never ask for card details on this website.",
      requires: "payment.onDelivery" },
    { q: "Do you deliver nationwide?",
      a: "We deliver to {{delivery.coverage}}.",
      requires: "delivery.coverage" },
    { q: "How long does delivery take?",
      a: "Usually {{delivery.timeframe}} once your order is confirmed on the phone. Our team will give you a firmer window when they call.",
      requires: "delivery.timeframe" },
    { q: "How is my order packaged?",
      a: "{{delivery.packaging}}. The rider is not told what is inside.",
      requires: "delivery.packaging" },
    { q: "How do I reach customer support?",
      a: "Message us on WhatsApp or call the number in the footer. A person answers, not a bot.",
      requires: null },
    { q: "What is the refund policy?",
      a: "{{refund.summary}}",
      requires: "refund.summary" },
    { q: "What do you do with my details?",
      a: "We use your name, phone number and address to arrange and deliver your order, and nothing else. We do not sell your details, we do not add you to a marketing list unless you tick the box, and we do not ask you for any health information.",
      requires: null },
    { q: "Will this fix a medical problem?",
      a: "We will not tell you that it will. If something is troubling you, a doctor or pharmacist is the right person to speak to, and that conversation is worth having whether or not you buy anything from us.",
      requires: null }
  ],

  /* ---------------------------------------------------- order handling --- */
  order: {
    // Static site: orders are sent to the business WhatsApp, with an email
    // fallback. There is no order database on this host. See README.md.
    channel: "whatsapp",
    referencePrefix: "KE",
    // Minutes within which an identical order is treated as a duplicate.
    duplicateWindowMinutes: 30,
    states: [
      "Abia","Adamawa","Akwa Ibom","Anambra","Bauchi","Bayelsa","Benue","Borno",
      "Cross River","Delta","Ebonyi","Edo","Ekiti","Enugu","Federal Capital Territory",
      "Gombe","Imo","Jigawa","Kaduna","Kano","Katsina","Kebbi","Kogi","Kwara","Lagos",
      "Nasarawa","Niger","Ogun","Ondo","Osun","Oyo","Plateau","Rivers","Sokoto",
      "Taraba","Yobe","Zamfara"
    ]
  },

  /* -------------------------------------------------------------- legal -- */
  legal: {
    lastUpdated: "26 November 2026",
    // Do not reuse the old "this site is not part of Facebook" line as if it
    // were a legal notice. It is not one.
    disclaimer:
      "Knack Extra is a food supplement, not a medicine. Nothing on this website is medical advice, and nothing here should be read as a promise of a particular result. Speak to a qualified healthcare professional about any health concern."
  }
};
