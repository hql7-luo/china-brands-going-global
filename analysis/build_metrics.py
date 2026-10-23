"""
Step 1: turn reported numbers into comparable metrics.

Reads  data/reported_metrics.csv and data/scorecard.csv
Writes outputs/derived_metrics.csv, outputs/scorecard_summary.csv, docs/data.js
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

COMPANIES = ["popmart", "miniso", "mixue"]
NAMES = {"popmart": "Pop Mart", "miniso": "MINISO", "mixue": "Mixue"}
PERIODS = ["FY2023", "FY2024", "FY2025", "1H2025", "1H2026"]


# Load reported numbers into a simple lookup: get("popmart", "FY2025", "revenue")
reported = pd.read_csv(ROOT / "data" / "reported_metrics.csv")
lookup = {
    (row.company, row.period, row.metric): row.value
    for row in reported.itertuples()
}


def get(company, period, metric):
    """Return a reported value, or None if the company did not disclose it."""
    return lookup.get((company, period, metric))


def pct(part, whole):
    if part is None or whole is None:
        return None
    return round(part / whole * 100, 1)


def growth(new, old):
    if new is None or old is None:
        return None
    return round((new / old - 1) * 100, 1)


# Each company reports "overseas" a little differently, so build it in one place
def overseas_revenue(company, period):
    if company == "popmart":
        # FY2024 onward: Asia Pacific + Americas + Europe (excludes HK/Macau/Taiwan)
        parts = [get(company, period, m) for m in
                 ["rev_asia_pacific", "rev_americas", "rev_europe_other"]]
        if None not in parts:
            return round(sum(parts), 1)
        # FY2023 only has the older "HK/Macau/Taiwan + overseas" line
        return get(company, period, "overseas_revenue")
    if company == "miniso":
        return get(company, period, "overseas_revenue")
    return None  # Mixue does not disclose overseas revenue


def overseas_stores(company, period):
    if company == "popmart":
        parts = [get(company, period, m) for m in
                 ["stores_asia_pacific", "stores_americas", "stores_europe_other"]]
        return None if None in parts else sum(parts)
    return get(company, period, "overseas_stores")


def all_stores(company, period):
    if company == "miniso":
        a = get(company, period, "mainland_stores")
        b = get(company, period, "overseas_stores")
        return None if a is None or b is None else a + b
    return get(company, period, "stores_total")


def gross_margin(company, period):
    reported_gm = get(company, period, "gross_margin")
    if reported_gm is not None:
        return reported_gm
    return pct(get(company, period, "gross_profit"), get(company, period, "revenue"))


def net_margin(company, period):
    # Adjusted (non-IFRS) where the company reports it, otherwise reported profit
    profit = get(company, period, "adj_net_profit") or get(company, period, "net_profit")
    return pct(profit, get(company, period, "revenue"))


# Build one row per company and period
rows = []
for c in COMPANIES:
    for p in PERIODS:
        rows.append({
            "company": c,
            "period": p,
            "revenue": get(c, p, "revenue"),
            "overseas_revenue": overseas_revenue(c, p),
            "overseas_revenue_share": pct(overseas_revenue(c, p), get(c, p, "revenue")),
            "overseas_stores": overseas_stores(c, p),
            "all_stores": all_stores(c, p),
            "overseas_store_share": pct(overseas_stores(c, p), all_stores(c, p)),
            "gross_margin": gross_margin(c, p),
            "net_margin": net_margin(c, p),
        })
metrics = pd.DataFrame(rows)

# Year-over-year growth for overseas revenue and overseas stores
prior = {"FY2024": "FY2023", "FY2025": "FY2024", "1H2026": "1H2025"}
for col in ["overseas_revenue", "overseas_stores"]:
    metrics[col + "_yoy"] = [
        growth(r[col], metrics.loc[(metrics.company == r.company) &
                                   (metrics.period == prior[r.period]), col].squeeze())
        if r.period in prior else None
        for _, r in metrics.iterrows()
    ]

# Pop Mart changed its region definition between FY2023 and FY2024,
# so that one growth rate would compare two different things. Leave it blank.
metrics.loc[(metrics.company == "popmart") & (metrics.period == "FY2024"),
            "overseas_revenue_yoy"] = None

metrics.to_csv(OUT / "derived_metrics.csv", index=False)


# Store model: how much revenue the brand itself books per store (FY2025)
def avg(a, b):
    return (a + b) / 2

store_model = pd.DataFrame([
    {
        "company": "popmart",
        "basis": "Mainland China retail-store revenue / avg. mainland stores",
        "revenue_per_store_rmb_m": get("popmart", "FY2025", "mainland_store_revenue")
        / avg(get("popmart", "FY2024", "stores_mainland"), get("popmart", "FY2025", "stores_mainland")),
        "who_pays_for_store": "Company (self-operated)",
    },
    {
        "company": "miniso",
        "basis": "MINISO brand revenue / avg. MINISO stores (mix of retail and wholesale)",
        "revenue_per_store_rmb_m": get("miniso", "FY2025", "brand_revenue")
        / avg(all_stores("miniso", "FY2024"), all_stores("miniso", "FY2025")),
        "who_pays_for_store": "Mostly partners and distributors overseas",
    },
    {
        "company": "mixue",
        "basis": "Goods and equipment sold to franchisees / avg. stores",
        "revenue_per_store_rmb_m": get("mixue", "FY2025", "goods_equipment_revenue")
        / avg(get("mixue", "FY2024", "stores_total"), get("mixue", "FY2025", "stores_total")),
        "who_pays_for_store": "Franchisees",
    },
])
store_model["revenue_per_store_rmb_m"] = store_model["revenue_per_store_rmb_m"].round(2)
store_model.to_csv(OUT / "store_model.csv", index=False)


# Scorecard: equal weights by default, then test how robust the ranking is
score = pd.read_csv(ROOT / "data" / "scorecard.csv")
table = score.pivot(index="dimension", columns="company", values="score")
dimensions = ["breadth", "hit_independence", "capital_light",
              "unit_economics", "momentum", "transferability"]
table = table.loc[dimensions, COMPANIES]

equal_avg = table.mean().round(2)

# Sensitivity: 10,000 random weightings; how often does each company rank first?
rng = np.random.default_rng(42)
weights = rng.dirichlet(np.ones(len(dimensions)), size=10_000)
weighted = weights @ table.values           # shape: (10000, 3)
winner = weighted.argmax(axis=1)
win_share = {c: round(float((winner == i).mean() * 100), 1) for i, c in enumerate(COMPANIES)}

summary = pd.DataFrame({
    "company": COMPANIES,
    "equal_weight_score": [equal_avg[c] for c in COMPANIES],
    "rank_first_share_pct": [win_share[c] for c in COMPANIES],
})
summary.to_csv(OUT / "scorecard_summary.csv", index=False)


# Export a small JSON file for the GitHub Pages explorer
def clean(df):
    return json.loads(df.replace({np.nan: None}).to_json(orient="records"))

page_data = {
    "companies": [{"id": c, "name": NAMES[c]} for c in COMPANIES],
    "dimensions": dimensions,
    "scorecard": clean(score),
    "metrics": clean(metrics),
    "store_model": clean(store_model),
    "summary": clean(summary),
}
# Saved as a .js file so the page also works when opened straight from disk
(ROOT / "docs" / "data.js").write_text(
    "window.DATA = " + json.dumps(page_data, ensure_ascii=False, indent=1) + ";\n")

print(metrics.to_string(index=False))
print()
print(store_model[["company", "revenue_per_store_rmb_m"]].to_string(index=False))
print()
print(summary.to_string(index=False))
