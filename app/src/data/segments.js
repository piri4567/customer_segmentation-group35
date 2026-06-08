// Static metadata for the 5 customer segments.
// Mirrors SEGMENT_DEFINITIONS from src/clustering.py and statistics from cluster_summary.csv.

export const SEGMENTS = [
  {
    id: 0,
    name: "Tech-Savvy Singles",
    short: "Tech",
    color: "#4F8EF7",
    tone: "tech",
    customers: 3323,
    pct: 10.1,
    avgSpend: 23741,
    avgAge: 54.6,
    avgChildren: 0.6,
    avgTenure: 6.7,
    description:
      "These customers spend heavily on electronics and video games, have almost no children at home, and visit fewer stores than average. Despite lower visit frequency they are high-value per visit. Tech launch cycles, gaming bundles, and device upgrade programmes are the most effective levers for this group.",
    characteristics: [
      "Highest electronics and video-game lifetime spend of any segment",
      "Fewest children at home (average 0.6)",
      "Below-average store visit count — concentrated spend pattern",
      "Shorter customer tenure than average at 6.7 years",
    ],
    campaigns: [
      {
        title: "Buy 1 Video Game, get 1 free",
        rationale:
          "Basket rules for this cluster show strong video game co-purchase patterns. A BOGOF offer directly targets the defining category and drives volume.",
      },
      {
        title: "Buy AirPods and Bluetooth Headphones, get 20% off your next electronics purchase",
        rationale:
          "The top association rule links audio accessories. The follow-on discount reinforces this natural co-purchase and drives repeat electronics spend.",
      },
      {
        title: "Device trade-in: bring an old device, get 15% off a new one",
        rationale:
          "Upgrade mechanics match this segment's propensity for tech purchases and build long-term stickiness.",
      },
      {
        title: "Tech Tier Loyalty Programme — Bronze, Silver and Gold tiers based on annual electronics + gaming spend",
        rationale:
          "Each tier unlocks escalating benefits: early access to product launches, progressive discounts (5% / 10% / 15%) on tech purchases, and quarterly VIP preview events. Converts concentrated high-value tech spending into recurring, predictable loyalty without blanket discounts.",
      },
    ],
  },
  {
    id: 1,
    name: "Budget-Conscious Shoppers",
    short: "Budget",
    color: "#F87171",
    tone: "budget",
    customers: 2337,
    pct: 7.1,
    avgSpend: 10602,
    avgAge: 56.6,
    avgChildren: 1.8,
    avgTenure: 9.4,
    description:
      "The most price-sensitive segment. They spread their spend across the highest number of distinct stores, indicating active cross-shopping behaviour. Above-average promotion usage signals strong price responsiveness. Loyalty mechanics that reward consolidation are the highest-impact strategy here.",
    characteristics: [
      "Lowest average lifetime spend at EUR 10,602",
      "Highest number of distinct stores visited — strongest cross-shopping signal",
      "Above-average promotional purchase rate",
      "Moderate household size (average 1.8 children)",
    ],
    campaigns: [
      {
        title: "50% off the second basket item in the baby food and household category",
        rationale:
          "Basket analysis shows household and essentials dominance. A half-price second item drives quantity consolidation and rewards in-store spending.",
      },
      {
        title: "Buy 3 household products, earn EUR 5 off your total bill",
        rationale:
          "Directly rewards basket consolidation, reducing the cross-shopping behaviour identified in this cluster.",
      },
      {
        title: "Loyalty card double-points every Wednesday",
        rationale:
          "Creates a recurring anchor visit day. The price-sensitive profile of this group makes points rewards highly effective at building habitual visits.",
      },
      {
        title: "Price Match Promise — match any competitor price within 7 days and earn an extra 10% in loyalty points",
        rationale:
          "These customers visit the highest number of distinct stores, signalling active competitor price-checking. A formal price-match policy with a points bonus reframes their cross-shopping behaviour into a reason to consolidate purchases with us. Standard practice in modern grocery retail (Aldi, Walmart, Tesco).",
      },
    ],
  },
  {
    id: 2,
    name: "Core Everyday Shoppers",
    short: "Core",
    color: "#34C97A",
    tone: "core",
    customers: 13460,
    pct: 40.7,
    avgSpend: 19247,
    avgAge: 49.3,
    avgChildren: 1.5,
    avgTenure: 8.0,
    description:
      "The backbone of the customer base at 41% of all customers. Grocery and fresh produce are the dominant categories, with broad product diversity. Spending and demographics are moderate across all dimensions. Incremental basket size growth through cross-category promotions represents the largest single revenue opportunity.",
    characteristics: [
      "Largest segment: 40.7% of the customer base",
      "Grocery and vegetables are dominant spend categories",
      "Broadest product diversity across all segments",
      "Youngest age profile at 49.3 years average",
    ],
    campaigns: [
      {
        title: "Get 20% off Fish when you also buy Meat",
        rationale:
          "The top association rule for this cluster is a meat-to-fish co-purchase with strong lift. The discount formalises this natural buying behaviour.",
      },
      {
        title: "Buy any 5 vegetables, receive salad dressing for free",
        rationale:
          "Vegetable basket rules show strong salad associations. A free accompaniment grows fresh-category engagement and basket size.",
      },
      {
        title: "Weekly fresh deals: 30% off selected vegetables every Friday",
        rationale:
          "Creates habitual visit cadence and deepens loyalty to fresh produce — the category where this segment already over-indexes.",
      },
      {
        title: "Recipe of the Week — every Monday a featured recipe with all ingredients automatically discounted at checkout when the full set is in the basket",
        rationale:
          "Combines broad product diversity with a concrete reason to grow basket size. The auto-discount at checkout (triggered by the complete ingredient set) is a proven mechanic used by Tesco UK and Carrefour. Builds a recurring weekly anchor without requiring active promotional browsing.",
      },
    ],
  },
  {
    id: 3,
    name: "High-Value Families",
    short: "Families",
    color: "#A78BFA",
    tone: "family",
    customers: 6942,
    pct: 21.0,
    avgSpend: 42729,
    avgAge: 56.1,
    avgChildren: 3.8,
    avgTenure: 11.1,
    description:
      "The most profitable and loyal segment. Large households, the longest customer tenure, and spend spread across every category. Even modest churn reduction in this group has outsized revenue impact. VIP recognition and family-oriented bundle offers are the highest-return investment.",
    characteristics: [
      "Highest average lifetime spend: EUR 42,729 — 2.5x the portfolio average",
      "Largest household size (average 3.8 children)",
      "Longest customer tenure at 11.1 years — most loyal segment",
      "Spend distributed broadly across all categories",
    ],
    campaigns: [
      {
        title: "Family bundle: groceries, meat and fish at 15% off total basket",
        rationale:
          "Multi-category basket composition is the defining trait of this cluster. A bundle reward matches their natural purchasing pattern and grows total basket value.",
      },
      {
        title: "VIP loyalty tier: double cashback on all purchases above EUR 200",
        rationale:
          "The high average spend makes this segment the natural fit for a premium loyalty tier. Meaningful cashback reinforces loyalty at scale.",
      },
      {
        title: "Birthday month offer: 20% off any single category of your choice",
        rationale:
          "A personalised milestone reward reinforces the emotional connection to the brand for the most profitable and longest-tenured customers.",
      },
      {
        title: "Family Box monthly subscription — curated pre-assembled basket combining groceries, meat, fish and hygiene at 10% off the aggregate, delivered on a scheduled day",
        rationale:
          "Consolidates natural multi-category purchasing into a single recurring transaction, lowers acquisition cost, and adds a convenience dimension that matches time-pressured large households (average 3.8 children).",
      },
    ],
  },
  {
    id: 4,
    name: "Pet and Home Essentials",
    short: "Pet & Home",
    color: "#F59E0B",
    tone: "pet",
    customers: 6976,
    pct: 21.1,
    avgSpend: 17321,
    avgAge: 55.5,
    avgChildren: 1.9,
    avgTenure: 8.3,
    description:
      "Characterised by consistent, predictable pet-food and hygiene purchases with very low penetration in meat and fish. The regularity of their purchasing behaviour makes this segment ideal for subscription-based offers, which lock in repeat revenue and raise switching costs.",
    characteristics: [
      "Highest pet-food and hygiene spend ratio of any segment",
      "Very low meat and fish category penetration",
      "Highly predictable and routine purchasing patterns",
      "Lowest promotional purchase rate — not price-driven",
    ],
    campaigns: [
      {
        title: "Buy 2 bags of pet food, get 1 free",
        rationale:
          "Pet food is the defining category of this cluster. A multi-buy offer directly incentivises the behaviour already observed in basket data.",
      },
      {
        title: "Spend EUR 50 in hygiene products, earn a free cleaning kit",
        rationale:
          "Hygiene is the second defining category. A threshold reward increases average transaction value and deepens category loyalty.",
      },
      {
        title: "Subscribe and Save: 10% off recurring pet food orders",
        rationale:
          "The predictable, routine purchase pattern of this segment makes subscription conversion straightforward and high-value for both parties.",
      },
      {
        title: "Pantry Auto-Refill — customer-defined subscription across pet food and hygiene with selectable cadence (monthly or bimonthly), 10% off, priority delivery, and cancel anytime",
        rationale:
          "Extends standard Subscribe and Save into a flexible bundle across the two defining categories of this cluster. Customer-chosen cadence respects consumption rhythm rather than imposing a fixed schedule. Mirrors Chewy and Amazon Subscribe and Save mechanics, proven at scale for routine-purchase segments.",
      },
    ],
  },
];

export const SEGMENT_BY_ID = Object.fromEntries(SEGMENTS.map((s) => [s.id, s]));
