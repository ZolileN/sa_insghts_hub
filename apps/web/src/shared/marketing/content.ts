export const AUDIENCE = [
  {
    num: "01",
    role: "Property professionals",
    desc: "Estate agents, developers, and investors who need suburb-level crime, property yield, and rental data before making decisions worth millions.",
    tags: ["Estate agents", "Property funds", "Developers"],
  },
  {
    num: "02",
    role: "Security & risk analysts",
    desc: "Security companies, insurers, and corporate risk teams tracking crime trends, hotspot precincts, and safety metrics by province.",
    tags: ["Security firms", "Insurers", "Risk managers"],
  },
  {
    num: "03",
    role: "Financial professionals",
    desc: "Analysts, advisors, and investors who need live forex rates, SARB rate decisions, CPI trends, and employment data in one place.",
    tags: ["Investment analysts", "Financial advisors", "Economists"],
  },
  {
    num: "04",
    role: "Researchers & journalists",
    desc: "Academic researchers, data journalists, and think tanks who need clean, consistently-sourced SA data with exportable formats.",
    tags: ["Universities", "Media houses", "NGOs"],
  },
  {
    num: "05",
    role: "Government & municipalities",
    desc: "Municipal planners, COGTA officials, and policy teams who need consolidated cross-departmental data for service delivery decisions.",
    tags: ["Metro planners", "COGTA", "Policy teams"],
  },
  {
    num: "06",
    role: "Everyday South Africans",
    desc: "Anyone making big life decisions — where to live, where to send kids to school, whether to buy or rent — who deserves access to real data, not guesswork.",
    tags: ["Home buyers", "Parents", "Semigrants"],
  },
] as const;

export const AI_FEATURES = [
  "Province-aware — answers change based on your active filter",
  "Multi-turn memory — conversation history per topic",
  "Grounded in real data — not hallucination",
  "Suggested questions to get you started instantly",
] as const;

export const AI_CHIPS = [
  "Is Cape Town safer than Joburg?",
  "Crime trend since 2020?",
  "Safest suburb to buy in WC?",
] as const;

export const PRICING_PLANS = [
  {
    tier: "Free",
    price: "R0",
    period: "forever",
    featured: false,
    cta: "Get started free",
    href: "/dashboard/crime",
    primary: false,
    features: [
      { text: "All 10 topic dashboards", included: true },
      { text: "National-level data", included: true },
      { text: "Interactive charts", included: true },
      { text: "Province filter", included: true },
      { text: "AI Q&A analyst", included: false },
      { text: "Data export (CSV/PDF)", included: false },
      { text: "Email alerts", included: false },
    ],
  },
  {
    tier: "Pro",
    price: "R199",
    priceSuffix: "/mo",
    period: "billed monthly · cancel anytime",
    featured: true,
    badge: "MOST POPULAR",
    cta: "Start Pro trial",
    href: "mailto:zolile@mlkcomputer.com",
    primary: true,
    features: [
      { text: "Everything in Free", included: true },
      { text: "AI Q&A (unlimited)", included: true },
      { text: "Suburb-level drill-down", included: true },
      { text: "CSV & PDF export", included: true },
      { text: "Email + WhatsApp alerts", included: true },
      { text: "Saved comparisons", included: true },
      { text: "Priority data refresh", included: true },
    ],
  },
  {
    tier: "Business",
    price: "R899",
    priceSuffix: "/mo",
    period: "5 seats · API access included",
    featured: false,
    cta: "Contact for access",
    href: "mailto:zolile@mlkcomputer.com",
    primary: false,
    features: [
      { text: "Everything in Pro", included: true },
      { text: "5 team seats", included: true },
      { text: "REST API access", included: true },
      { text: "White-label reports", included: true },
      { text: "Slack integration", included: true },
      { text: "Dedicated support", included: true },
      { text: "Custom data requests", included: true },
    ],
  },
] as const;

export const TOPIC_MARKETING = [
  { emoji: "🔴", name: "Crime Statistics", source: "SAPS quarterly reports", cadence: "Quarterly", id: "crime" },
  { emoji: "🏠", name: "Property & Rental", source: "Lightstone · FNB Barometer", cadence: "Monthly", id: "property" },
  { emoji: "🔐", name: "Bank Fraud", source: "SABRIC annual report", cadence: "Annual", id: "fraud" },
  { emoji: "📉", name: "Unemployment", source: "Stats SA QLFS", cadence: "Quarterly", id: "employment" },
  { emoji: "⚡", name: "Load Shedding", source: "Eskom live API", cadence: "Live", id: "energy" },
  { emoji: "💰", name: "Interest Rates", source: "SARB · Stats SA CPI", cadence: "Monthly", id: "finance" },
  { emoji: "🏥", name: "Healthcare", source: "NDOH DHIS2 · SANAC", cadence: "Quarterly", id: "health" },
  { emoji: "🎓", name: "Education", source: "DBE NSC results", cadence: "Annual", id: "education" },
  { emoji: "💱", name: "ZAR Exchange Rate", source: "open.er-api.com", cadence: "Live", id: "forex" },
  { emoji: "💧", name: "Water & Dams", source: "DWS weekly report", cadence: "Weekly", id: "water" },
] as const;
