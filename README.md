# options-desk

Research desk for options trading: data (Schwab API), Greeks and implied volatility, SEC filings,
trade cards with the exact Webull orders and alerts to set, and a trade journal.
Claude does the research on a schedule; the owner places every trade. See `CLAUDE.md`.

```
python3 desk.py card plans/EXAMPLE_xyz_bull_put.json    # see what a trade card looks like
python3 -m unittest discover -s tests
```
Standard library only (Python 3.10+); nothing to install.
