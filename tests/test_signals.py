import datetime as dt, os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backtests"))
import make_signals as ms
import make_trend_options as mt

class TestSignals(unittest.TestCase):
    def series(self, closes):
        d0 = dt.date(2020, 1, 1)
        return [(d0 + dt.timedelta(days=i), c) for i, c in enumerate(closes)]

    def test_trend_uses_prior_day_only(self):
        s = self.series([100.0] * 50 + [90.0, 120.0, 120.0])
        out = ms.trend_dates(s)
        self.assertNotIn(s[50][0], out)   # D-1 close 100 = average: not above
        self.assertNotIn(s[51][0], out)   # D-1 close 90 < average
        self.assertIn(s[52][0], out)      # D-1 close 120 > average, even though D's own close is irrelevant

    def test_vol_median(self):
        s = self.series([20.0] * 253 + [25.0, 15.0, 15.0])
        out = ms.vol_dates(s)
        self.assertIn(s[254][0], out)     # D-1 = 25 > median 20
        self.assertNotIn(s[255][0], out)  # D-1 = 15

    def test_orats_rows(self):
        days = {dt.date(2024, 1, 16), dt.date(2024, 2, 14), dt.date(2024, 2, 15)}
        self.assertEqual(ms.rows([dt.date(2024, 1, 16)], days), [("202401161000", "202402151600")])
        days.discard(dt.date(2024, 2, 15))  # exit falls back to the prior trading day
        self.assertEqual(ms.rows([dt.date(2024, 1, 16)], days)[0][1], "202402141600")

    def test_trend_options_flip_exit(self):
        d0 = dt.date(2021, 1, 4)  # a Monday; consecutive calendar days stand in for trading days
        closes = [100.0] * 50 + [110.0] * 10 + [90.0] * 30
        s = [(d0 + dt.timedelta(days=i), c) for i, c in enumerate(closes)]
        ms.START, ms.END = d0, d0 + dt.timedelta(days=200)
        calls = mt.trades(s, +1)
        # first Monday after the rise: day 56; trend flips when D-1 = day 60 (first 90) -> exit day 61
        self.assertEqual(calls[0], ((d0 + dt.timedelta(days=56)).strftime("%Y%m%d") + "1000",
                                    (d0 + dt.timedelta(days=61)).strftime("%Y%m%d") + "1000"))
        self.assertTrue(all(mt.sides(s)[dt.date(int(a[:4]), int(a[4:6]), int(a[6:8]))] == -1
                            for a, _ in mt.trades(s, -1)))

if __name__ == "__main__":
    unittest.main()
