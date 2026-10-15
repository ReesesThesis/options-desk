import datetime as dt, os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backtests"))
import make_signals as ms

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

if __name__ == "__main__":
    unittest.main()
