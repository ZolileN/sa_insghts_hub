export const PROVINCES = [
  "All Provinces",
  "Western Cape",
  "Gauteng",
  "KwaZulu-Natal",
  "Eastern Cape",
  "Limpopo",
  "Mpumalanga",
  "North West",
  "Free State",
  "Northern Cape",
] as const;

export type Province = typeof PROVINCES[number];

export const PROVINCE_LIST = PROVINCES.filter((p) => p !== "All Provinces");

export const TOPICS = [
  {
    id: "crime",
    label: "Crime Statistics",
    shortLabel: "Crime",
    description: "SAPS quarterly data — murders, robbery, burglary; drill down to precinct",
    icon: "ShieldAlert",
    cadence: "Quarterly",
  },
  {
    id: "property",
    label: "Property Prices & Rental",
    shortLabel: "Property",
    description: "Median prices, rental yields, and market momentum by province",
    icon: "Home",
    cadence: "Monthly",
  },
  {
    id: "fraud",
    label: "Bank Fraud & Financial Crime",
    shortLabel: "Fraud",
    description: "SABRIC banking fraud losses and incident categories",
    icon: "Lock",
    cadence: "Annual",
  },
  {
    id: "employment",
    label: "Unemployment & Income",
    shortLabel: "Employment",
    description: "Stats SA QLFS unemployment, youth joblessness, and incomes",
    icon: "TrendingDown",
    cadence: "Quarterly",
  },
  {
    id: "energy",
    label: "Load Shedding & Energy",
    shortLabel: "Energy",
    description: "Eskom load shedding stage, tariffs, and generation mix",
    icon: "Zap",
    cadence: "Live",
  },
  {
    id: "finance",
    label: "Interest Rates & Inflation",
    shortLabel: "Finance",
    description: "SARB repo rate, prime rate, and CPI headline inflation",
    icon: "Banknote",
    cadence: "Monthly",
  },
  {
    id: "health",
    label: "Healthcare & Disease Burden",
    shortLabel: "Health",
    description: "HIV, TB, maternal health, and provincial health capacity",
    icon: "HeartPulse",
    cadence: "Quarterly",
  },
  {
    id: "education",
    label: "Education & Matric Data",
    shortLabel: "Education",
    description: "NSC pass rates, bachelor passes, and subject performance",
    icon: "GraduationCap",
    cadence: "Annual",
  },
  {
    id: "forex",
    label: "ZAR Exchange Rate & Forex",
    shortLabel: "Forex",
    description: "Live USD/ZAR and major currency crosses",
    icon: "CircleDollarSign",
    cadence: "Live",
  },
  {
    id: "water",
    label: "Water & Service Delivery",
    shortLabel: "Water",
    description: "Dam levels, provincial reservoirs, and major dam status",
    icon: "Droplets",
    cadence: "Weekly",
  },
] as const;

export type TopicId = typeof TOPICS[number]["id"];
