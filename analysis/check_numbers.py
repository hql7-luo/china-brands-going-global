"""
Step 3: sanity checks.
Recompute numbers the companies state themselves and make sure they match.
Run after build_metrics.py. Prints PASS/FAIL for each check.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
m = pd.read_csv(ROOT / "outputs" / "derived_metrics.csv")
r = pd.read_csv(ROOT / "data" / "reported_metrics.csv")


def derived(company, period, col):
    return m[(m.company == company) & (m.period == period)][col].iloc[0]


def reported(company, period, metric):
    return r[(r.company == company) & (r.period == period) & (r.metric == metric)].value.iloc[0]


# (description, our number, number stated by the company or its filing, tolerance)
checks = [
    ("Pop Mart 1H2026 overseas revenue YoY = -11.1%",
     derived("popmart", "1H2026", "overseas_revenue_yoy"), -11.1, 0.1),
    ("Pop Mart FY2025 overseas share = 43.8% (21.6 + 18.3 + 3.9)",
     derived("popmart", "FY2025", "overseas_revenue_share"), 43.8, 0.1),
    ("Pop Mart FY2025 gross margin = 72.1%",
     round(reported("popmart", "FY2025", "gross_profit") / reported("popmart", "FY2025", "revenue") * 100, 1), 72.1, 0.05),
    ("Pop Mart FY2025 adjusted net margin = 35.2%",
     derived("popmart", "FY2025", "net_margin"), 35.2, 0.05),
    ("Pop Mart Jun 2026 stores = 676",
     derived("popmart", "1H2026", "overseas_stores") + 455, 676, 0),
    ("MINISO FY2025 overseas revenue YoY = +29.3%",
     derived("miniso", "FY2025", "overseas_revenue_yoy"), 29.3, 0.1),
    ("MINISO FY2024 overseas revenue YoY = +41.9%",
     derived("miniso", "FY2024", "overseas_revenue_yoy"), 41.9, 0.1),
    ("MINISO 1H2026 overseas revenue YoY = +14.9%",
     derived("miniso", "1H2026", "overseas_revenue_yoy"), 14.9, 0.1),
    ("MINISO FY2025 adjusted net margin = 13.5%",
     derived("miniso", "FY2025", "net_margin"), 13.5, 0.05),
    ("MINISO Jun 2026 overseas stores = direct + partner + distributor",
     reported("miniso", "1H2026", "overseas_stores_direct")
     + reported("miniso", "1H2026", "overseas_stores_partner")
     + reported("miniso", "1H2026", "overseas_stores_distributor"), 3644, 0),
    ("Mixue 1H2026 overseas stores YoY = -7.5%",
     derived("mixue", "1H2026", "overseas_stores_yoy"), -7.5, 0.1),
    ("Mixue Jun 2026 stores = mainland 59,609 + overseas",
     59609 + reported("mixue", "1H2026", "overseas_stores"), 63987, 0),
    ("Mixue 1H2026 gross margin = 30.4%",
     derived("mixue", "1H2026", "gross_margin"), 30.4, 0.05),
]

failed = 0
for name, ours, stated, tol in checks:
    ok = abs(ours - stated) <= tol
    failed += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {name}  (ours: {ours})")

print(f"\n{len(checks) - failed}/{len(checks)} checks passed")
raise SystemExit(1 if failed else 0)
