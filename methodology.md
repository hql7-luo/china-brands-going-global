# Methodology

## Question

Which overseas model is more replicable: Pop Mart, MINISO or Mixue?

"Replicable" has two parts:

1. **Repeatable** by the company itself in more markets.
2. **Learnable** by other Chinese consumer brands.

Profitability is scored as its own dimension so it does not hide inside "replicable".

## Data rules

- Use company filings first (HKEX announcements, prospectus, press releases). Use news coverage only for figures stated on earnings calls or not in the filing, and mark them `secondary` in `data/sources.csv`.
- Keep each company's own definition of "overseas" and write the definition next to every chart.
- Compare first halves with first halves. Full-year and half-year numbers are never joined on one line.
- If a number is not disclosed, leave it blank. No estimates are filled in. (Mixue's overseas revenue is the main gap.)

## Scorecard rubric

Each cell is 1 (weak) to 5 (strong). The evidence for every score is in `data/scorecard.csv`.

| Dimension | What it asks | 5 looks like | 1 looks like |
|---|---|---|---|
| Proven in many markets | Has the model already worked in many countries? | 80+ countries across several regions | One or two countries |
| Not reliant on one hit | Would growth survive if the top product or IP cooled? | No product line dominates | One IP is a large share and moves the whole result |
| Partners fund the stores | Who pays for new stores? | Nearly all stores funded by franchisees or partners | Company funds every store |
| Other brands can learn it | Is the core edge something another Chinese brand could build? | Supply chain, sourcing and process | A creative hit that is hard to repeat |
| Latest overseas trend | What happened in the most recent half-year? | Revenue and same-store sales both growing | Revenue or store count falling |
| Profitability | How much profit per yuan of sales? (adjusted net margin, FY2025) | 30% or more | Below 10% |

Profitability bands: 30%+ = 5, 20-29.9% = 4, 15-19.9% = 3, 10-14.9% = 2, below 10% = 1.

## Weighting and sensitivity

- The README uses equal weights.
- Because any weighting is a judgment, `analysis/build_metrics.py` draws 10,000 random weight sets (Dirichlet distribution, seed 42) and counts how often each company ranks first.
- Result: MINISO 74%, Mixue 20%, Pop Mart 6%. The conclusion only flips when profitability carries most of the weight.
- The interactive page lets you set your own weights.

## Known limitations

- The scorecard is an analyst judgment, made transparent, not a statistical model.
- Mixue does not report overseas revenue or overseas margins.
- MINISO's overseas revenue mixes retail sales (direct stores) and wholesale sales (distributors), so revenue per store is not like-for-like with Pop Mart.
- Pop Mart changed its regional definition between FY2023 and FY2024, so FY2024 overseas growth is not calculated.
- Data is as of October 2026 (latest filings: 1H2026 interim results).
