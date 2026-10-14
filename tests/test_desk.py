import datetime as dt, json, os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from desk import bs, vol, strategy, risk, card, journal, schwab, sec, config

CFG = config.load()
ROOT = config.ROOT

class TestBS(unittest.TestCase):
    def test_textbook_value(self):  # Hull: S=K=100, T=1, r=5%, sigma=20% -> call 10.4506
        self.assertAlmostEqual(bs.price("call", 100, 100, 1, 0.2, 0.05), 10.4506, places=3)

    def test_put_call_parity(self):
        S, K, T, s, r = 103, 97, 0.3, 0.35, 0.04
        c, p = bs.price("call", S, K, T, s, r), bs.price("put", S, K, T, s, r)
        self.assertAlmostEqual(c - p, S - K * 2.718281828459045 ** (-r * T), places=6)

    def test_iv_roundtrip(self):
        prem = bs.price("put", 50, 45, 30 / 365, 0.42, 0.04)
        self.assertAlmostEqual(bs.implied_vol("put", prem, 50, 45, 30 / 365, 0.04), 0.42, places=4)
        self.assertIsNone(bs.implied_vol("call", 0.01, 100, 50, 0.1))  # below intrinsic

    def test_greek_signs(self):
        g = bs.greeks("call", 100, 100, 0.25, 0.3, 0.04)
        self.assertTrue(0.5 < g["delta"] < 0.6 and g["gamma"] > 0 and g["theta"] < 0 and g["vega"] > 0)
        # vega per vol point ~ price change for +1 pt
        diff = bs.price("call", 100, 100, 0.25, 0.31, 0.04) - bs.price("call", 100, 100, 0.25, 0.30, 0.04)
        self.assertAlmostEqual(g["vega"], diff, places=2)

class TestVol(unittest.TestCase):
    def test_realized_and_rank(self):
        closes = [100 * (1 + 0.01 * (-1) ** i) for i in range(40)]  # +-2% daily swings
        self.assertGreater(vol.realized_vol(closes, 20), 0.2)
        self.assertAlmostEqual(vol.iv_rank([0.2, 0.4], 0.3), 50.0)
        self.assertEqual(vol.iv_percentile([0.1, 0.2, 0.3, 0.4], 0.35), 75.0)

PUT_SPREAD = [{"action": "sell", "type": "put", "strike": 99, "expiry": "2026-11-20", "price": 1.30},
              {"action": "buy", "type": "put", "strike": 98, "expiry": "2026-11-20", "price": 0.85}]

class TestStrategy(unittest.TestCase):
    def test_credit_spread(self):
        self.assertAlmostEqual(strategy.net_premium(PUT_SPREAD), -0.45)
        mp, ml = strategy.max_profit_loss(PUT_SPREAD)
        self.assertAlmostEqual(mp, 45); self.assertAlmostEqual(ml, 55)
        self.assertEqual(strategy.breakevens(PUT_SPREAD), [98.55])

    def test_unlimited(self):
        naked = [{"action": "sell", "type": "call", "strike": 110, "expiry": "2026-11-20", "price": 2}]
        self.assertIsNone(strategy.max_profit_loss(naked)[1])
        long_call = [{"action": "buy", "type": "call", "strike": 110, "expiry": "2026-11-20", "price": 2}]
        mp, ml = strategy.max_profit_loss(long_call)
        self.assertIsNone(mp); self.assertAlmostEqual(ml, 200)

    def test_iron_condor_breakevens(self):
        legs = [{"action": "buy", "type": "put", "strike": 90, "expiry": "2026-11-20", "price": 0.5},
                {"action": "sell", "type": "put", "strike": 95, "expiry": "2026-11-20", "price": 1.5},
                {"action": "sell", "type": "call", "strike": 105, "expiry": "2026-11-20", "price": 1.5},
                {"action": "buy", "type": "call", "strike": 110, "expiry": "2026-11-20", "price": 0.5}]
        self.assertEqual(strategy.breakevens(legs), [93.0, 107.0])
        self.assertEqual(strategy.max_profit_loss(legs), (200.0, 300.0))

class TestRisk(unittest.TestCase):
    def test_sizing_2k(self):
        s = risk.size(55, PUT_SPREAD, CFG)  # $57.40 with fees: over 2% target, under 3% cap
        self.assertEqual(s["contracts"], 1)
        self.assertIn("hard cap", s["reason"])
        self.assertEqual(risk.size(450, PUT_SPREAD, CFG)["contracts"], 0)   # $5-wide spread: too big
        self.assertEqual(risk.size(None, PUT_SPREAD, CFG)["contracts"], 0)  # naked
        big = dict(CFG, account_size=20000)
        self.assertEqual(risk.size(55, PUT_SPREAD, big)["contracts"], 6)    # $400 / $57.40
        self.assertEqual(risk.size(55, PUT_SPREAD, CFG, open_risk=170)["contracts"], 0)  # only $30 room left

    def test_liquidity(self):
        legs = [dict(PUT_SPREAD[0], bid=1.0, ask=1.6, oi=100)]
        probs = risk.liquidity_problems(legs, CFG)
        self.assertEqual(len(probs), 2)
        self.assertTrue(risk.liquidity_problems(PUT_SPREAD, CFG))  # missing data is flagged

class TestCardJournal(unittest.TestCase):
    def setUp(self):
        self.plan = json.load(open(os.path.join(ROOT, "plans", "EXAMPLE_xyz_bull_put.json")))
        self.tmp = tempfile.mkdtemp()
        journal.PATH = os.path.join(self.tmp, "trades.csv")

    def test_card(self):
        c = card.build(self.plan, CFG)
        self.assertEqual(c["dte"], 37)
        self.assertEqual(str(c["time_stop"]), "2026-10-30")
        self.assertAlmostEqual(c["tp_price"], 0.225)
        text = card.render(c, CFG)
        self.assertIn("Price falls to $99.00", text)
        self.assertIn("Buy-to-close", text)
        self.assertNotIn("DO NOT TRADE", text)
        self.assertIn("PAPER TRADE", text)

    def test_blocked_card(self):
        plan = dict(self.plan, legs=[dict(l, strike=l["strike"] - (5 if l["action"] == "buy" else 0)) for l in self.plan["legs"]])
        self.assertIn("DO NOT TRADE AS WRITTEN", card.render(card.build(plan, CFG), CFG))

    def test_fill_close(self):
        c = card.build(self.plan, CFG)
        r = journal.open_trade(c, 0.47, 1)
        self.assertEqual(r["max_loss_total"], "53")    # better fill than mid: worst case $53
        self.assertEqual(r["take_profit"], "0.23")
        self.assertAlmostEqual(journal.open_risk(), 53)
        r = journal.close_trade(r["id"], 0.23, fee_total=2.40)
        self.assertEqual(r["pnl"], "21.60")
        self.assertEqual(journal.stats()["trades"], 1)

class TestParsers(unittest.TestCase):
    def test_schwab_normalize(self):
        d = {"callExpDateMap": {"2026-11-20:37": {"100.0": [{"bid": 1, "ask": 1.1, "mark": 1.05, "volatility": 31.5,
                                                             "delta": 0.4, "openInterest": 900, "totalVolume": 50}]}},
             "putExpDateMap": {"2026-11-20:37": {"99.0": [{"bid": 1.27, "ask": 1.33, "volatility": -999.0}]}}}
        rows = schwab.normalize(d)
        self.assertEqual(rows[0]["iv"], 0.315); self.assertEqual(rows[0]["expiry"], "2026-11-20")
        self.assertIsNone(rows[1]["iv"]); self.assertEqual(rows[1]["type"], "put")

    def test_refresh_days(self):
        os.environ["SCHWAB_REFRESH_ISSUED"] = "2026-10-10"
        self.assertEqual(schwab.refresh_days_left(dt.date(2026, 10, 16)), 1)
        del os.environ["SCHWAB_REFRESH_ISSUED"]

    def test_sec_describe(self):
        self.assertEqual(sec.describe({"form": "8-K", "items": "2.02,9.01"}), "8-K: earnings results, 9.01")

if __name__ == "__main__":
    unittest.main()
