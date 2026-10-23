"""
Step 2: draw the README charts from outputs/derived_metrics.csv.
Run build_metrics.py first.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parent.parent
CHARTS = ROOT / "charts"
CHARTS.mkdir(exist_ok=True)

metrics = pd.read_csv(ROOT / "outputs" / "derived_metrics.csv")
score = pd.read_csv(ROOT / "data" / "scorecard.csv")
summary = pd.read_csv(ROOT / "outputs" / "scorecard_summary.csv")

# Colors: one fixed color per company, used the same way in every chart
COLOR = {"popmart": "#2a78d6", "miniso": "#eb6834", "mixue": "#1baf7a"}
NAME = {"popmart": "Pop Mart", "miniso": "MINISO", "mixue": "Mixue"}
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"

# Use Inter if it is installed, otherwise fall back to the default sans font
if any("Inter" in f.name for f in font_manager.fontManager.ttflist):
    plt.rcParams["font.family"] = "Inter"
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "font.size": 10.5, "axes.titlesize": 12, "axes.titleweight": "semibold",
    "axes.titlecolor": INK, "axes.titlelocation": "left",
})


def value(company, period, col):
    row = metrics[(metrics.company == company) & (metrics.period == period)]
    return row[col].iloc[0]


def tidy(ax, grid_axis="y"):
    """Recessive chrome: no top/right spines, hairline grid behind the data."""
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_visible(grid_axis != "y")
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def headline(fig, title, subtitle):
    fig.text(0.015, 0.97, title, fontsize=15, fontweight="semibold", color=INK, va="top")
    fig.text(0.015, 0.905, subtitle, fontsize=10.5, color=INK2, va="top")


def footnote(fig, text):
    fig.text(0.015, 0.02, text, fontsize=8.5, color=MUTED, va="bottom")


def save(fig, name):
    fig.savefig(CHARTS / name, dpi=200)
    plt.close(fig)
    print("saved", name)


# ---------------------------------------------------------------------------
# Chart 1: overseas revenue, full years and first halves
# ---------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5.2),
                               gridspec_kw={"width_ratios": [3, 2]})
fig.subplots_adjust(left=0.06, right=0.98, top=0.76, bottom=0.17, wspace=0.18)
headline(fig, "Pop Mart grew overseas fastest, then fell first",
         "Overseas revenue, RMB billion. MINISO kept growing every period.")

bar_w = 0.22
for ax, periods, title in [(ax1, ["FY2023", "FY2024", "FY2025"], "Full year"),
                           (ax2, ["1H2025", "1H2026"], "First half")]:
    for i, company in enumerate(["popmart", "miniso"]):
        xs = [k + (i - 0.5) * (bar_w + 0.03) for k in range(len(periods))]
        ys = [value(company, p, "overseas_revenue") / 1000 for p in periods]
        ax.bar(xs, ys, width=bar_w, color=COLOR[company], label=NAME[company])
        for x, y, p in zip(xs, ys, periods):
            label = f"{y:.1f}"
            # Show the reported year-over-year change on the latest half-year bars
            if p == "1H2026":
                label += f"\n{value(company, p, 'overseas_revenue_yoy'):+.1f}%"
            ax.text(x, y + 0.2, label, ha="center", va="bottom", fontsize=9.5,
                    color=INK, linespacing=1.3)
    ax.set_xticks(range(len(periods)), periods, color=INK2)
    ax.set_title(title, color=INK2, fontsize=11, fontweight="normal", pad=8)
    tidy(ax)

ax1.set_ylim(0, 19)
ax2.set_ylim(0, 7.6)
ax1.legend(frameon=False, loc="upper left", fontsize=10, labelcolor=INK2, bbox_to_anchor=(0, 1.02))
footnote(fig, "Mixue does not disclose overseas revenue. Pop Mart FY2023 includes HK/Macau/Taiwan "
              "(old definition); FY2024+ = Asia Pacific + Americas + Europe.\n"
              "Source: company annual and interim results announcements (see data/sources.csv).")
save(fig, "01_overseas_revenue.png")


# ---------------------------------------------------------------------------
# Chart 2: overseas share, FY2025 vs 1H2026 (dumbbell)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 4.4))
fig.subplots_adjust(left=0.2, right=0.95, top=0.72, bottom=0.2)
headline(fig, "Overseas share shrank at all three in 2026",
         "Overseas share, first half 2025 (open dot) vs first half 2026 (filled dot)")

rows = [("popmart", "overseas_revenue_share", "Pop Mart\nrevenue share"),
        ("miniso", "overseas_revenue_share", "MINISO\nrevenue share"),
        ("mixue", "overseas_store_share", "Mixue\nstore share*")]
for y, (company, col, label) in enumerate(reversed(rows)):
    start, end = value(company, "1H2025", col), value(company, "1H2026", col)
    ax.plot([start, end], [y, y], color=COLOR[company], linewidth=2, solid_capstyle="round")
    ax.scatter([start], [y], s=70, facecolor=SURFACE, edgecolor=COLOR[company], linewidth=2, zorder=3)
    ax.scatter([end], [y], s=70, color=COLOR[company], edgecolor=SURFACE, linewidth=2, zorder=3)
    ax.text(start + 1.0, y + 0.22, f"{start:.1f}%", ha="left", fontsize=9.5, color=INK2)
    ax.text(end - 1.0, y + 0.22, f"{end:.1f}%", ha="right", fontsize=9.5,
            color=INK, fontweight="semibold")
ax.set_yticks(range(3), [r[2] for r in reversed(rows)], color=INK)
ax.set_xlim(0, 50)
ax.set_ylim(-0.6, 2.6)
ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
tidy(ax, grid_axis="x")
ax.spines["left"].set_visible(False)
footnote(fig, "*Mixue does not disclose overseas revenue, so its line uses the share of stores "
              "outside mainland China.\nMINISO share = MINISO brand overseas revenue / group revenue.")
save(fig, "02_overseas_share.png")


# ---------------------------------------------------------------------------
# Chart 3: overseas store count, indexed to Dec 2024 = 100
# ---------------------------------------------------------------------------
periods = ["FY2024", "1H2025", "FY2025", "1H2026"]
labels = ["Dec 2024", "Jun 2025", "Dec 2025", "Jun 2026"]
fig, ax = plt.subplots(figsize=(10, 5))
fig.subplots_adjust(left=0.07, right=0.78, top=0.76, bottom=0.17)
headline(fig, "Only Mixue's overseas store count is shrinking",
         "Overseas store count, indexed (Dec 2024 = 100)")

for company in ["popmart", "miniso", "mixue"]:
    counts = [value(company, p, "overseas_stores") for p in periods]
    index = [c / counts[0] * 100 for c in counts]
    ax.plot(range(4), index, color=COLOR[company], linewidth=2,
            solid_capstyle="round", solid_joinstyle="round")
    ax.scatter(range(4), index, s=36, color=COLOR[company], edgecolor=SURFACE, linewidth=2, zorder=3)
    ax.text(3.12, index[-1], f"{NAME[company]}  {int(counts[-1]):,} stores",
            va="center", fontsize=10, color=INK)
ax.axhline(100, color=AXIS, linewidth=1)
ax.set_xticks(range(4), labels, color=INK2)
ax.set_ylim(70, 260)
tidy(ax)
footnote(fig, "Overseas = outside mainland China, except Pop Mart (excludes HK/Macau/Taiwan). "
              "MINISO = MINISO-brand stores.\nSource: company results announcements.")
save(fig, "03_overseas_stores.png")


# ---------------------------------------------------------------------------
# Chart 4: gross margin and net margin
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(10, 5))
fig.subplots_adjust(left=0.06, right=0.86, top=0.74, bottom=0.17, wspace=0.28)
headline(fig, "Pop Mart earns the most per yuan; margins slipped for all in 2026",
         "Margins by period, %. Net margin is non-IFRS adjusted where reported (Mixue: reported).")

xpos = {"FY2024": 0, "FY2025": 1, "1H2025": 2.5, "1H2026": 3.5}
for ax, col, title, top in [(axes[0], "gross_margin", "Gross margin", 80),
                            (axes[1], "net_margin", "Net margin", 40)]:
    for company in ["popmart", "miniso", "mixue"]:
        for group in [["FY2024", "FY2025"], ["1H2025", "1H2026"]]:
            xs = [xpos[p] for p in group]
            ys = [value(company, p, col) for p in group]
            ax.plot(xs, ys, color=COLOR[company], linewidth=2, solid_capstyle="round")
            ax.scatter(xs, ys, s=36, color=COLOR[company], edgecolor=SURFACE, linewidth=2, zorder=3)
        last = value(company, "1H2026", col)
        ax.text(3.7, last, f"{last:.1f}", va="center", fontsize=9.5, color=INK)
    ax.set_xticks(list(xpos.values()), list(xpos.keys()), color=INK2)
    ax.set_xlim(-0.3, 4.1)
    ax.set_ylim(0, top)
    ax.set_title(title, color=INK2, fontsize=11, fontweight="normal", pad=8)
    tidy(ax)
# Legend to the right of the second panel
for k, company in enumerate(["popmart", "miniso", "mixue"]):
    fig.lines.append(plt.Line2D([0.885, 0.905], [0.62 - k * 0.07] * 2, color=COLOR[company],
                                linewidth=2.5, transform=fig.transFigure))
    fig.text(0.912, 0.62 - k * 0.07, NAME[company], va="center", fontsize=10, color=INK)
footnote(fig, "Full-year and half-year figures are kept as separate segments (seasonality). "
              "Source: company results announcements.")
save(fig, "04_margins.png")


# ---------------------------------------------------------------------------
# Chart 5: replicability scorecard (heatmap)
# ---------------------------------------------------------------------------
dims = ["breadth", "hit_independence", "capital_light", "transferability",
        "momentum", "unit_economics"]
dim_label = {
    "breadth": "Proven in many markets",
    "hit_independence": "Not reliant on one hit",
    "capital_light": "Partners fund the stores",
    "transferability": "Other brands can learn it",
    "momentum": "Latest overseas trend",
    "unit_economics": "Profitability",
}
order = ["miniso", "mixue", "popmart"]
grid = score.pivot(index="dimension", columns="company", values="score").loc[dims, order]

# Sequential blue steps for scores 1..5 (light = low, dark = high)
steps = {1: "#cde2fb", 2: "#9ec5f4", 3: "#5598e7", 4: "#256abf", 5: "#104281"}

fig, ax = plt.subplots(figsize=(10, 5.8))
fig.subplots_adjust(left=0.03, right=0.97, top=0.8, bottom=0.1)
headline(fig, "MINISO's model is the most replicable; Pop Mart's the most profitable",
         "Analyst scorecard, 1 (weak) to 5 (strong). Evidence for every cell is in data/scorecard.csv.")
ax.set_xlim(0, 4.2)
ax.set_ylim(len(dims) + 1.6, -0.9)
ax.axis("off")

col_x = {c: 1.75 + k * 0.82 for k, c in enumerate(order)}
for c in order:
    ax.add_patch(plt.Rectangle((col_x[c] - 0.33, -0.78), 0.66, 0.08, color=COLOR[c], lw=0))
    ax.text(col_x[c], -0.42, NAME[c], ha="center", va="center", fontsize=11.5,
            fontweight="semibold", color=INK)
for r, d in enumerate(dims):
    ax.text(0.02, r + 0.5, dim_label[d], va="center", fontsize=11, color=INK)
    for c in order:
        s = int(grid.loc[d, c])
        ax.add_patch(plt.Rectangle((col_x[c] - 0.38, r + 0.06), 0.76, 0.88,
                                   color=steps[s], lw=0))
        ax.text(col_x[c], r + 0.5, str(s), ha="center", va="center", fontsize=12,
                fontweight="semibold", color=INK if s <= 2 else "#ffffff")
# Summary rows
avg_row = len(dims) + 0.15
ax.plot([0.02, 4.15], [avg_row, avg_row], color=AXIS, linewidth=1)
ax.text(0.02, avg_row + 0.45, "Average (equal weights)", va="center", fontsize=11,
        fontweight="semibold", color=INK)
ax.text(0.02, avg_row + 1.1, "Ranks #1 in random weightings", va="center", fontsize=10.5, color=INK2)
for c in order:
    row = summary[summary.company == c].iloc[0]
    ax.text(col_x[c], avg_row + 0.45, f"{row.equal_weight_score:.2f}", ha="center",
            va="center", fontsize=12.5, fontweight="semibold", color=INK)
    ax.text(col_x[c], avg_row + 1.1, f"{row.rank_first_share_pct:.0f}%", ha="center",
            va="center", fontsize=10.5, color=INK2)
footnote(fig, "Random weightings: 10,000 draws of dimension weights (Dirichlet, seed 42). "
              "Scores use FY2025 and 1H2026 disclosures.")
save(fig, "05_scorecard.png")
