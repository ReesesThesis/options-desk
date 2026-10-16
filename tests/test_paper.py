import datetime as dt, os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "paper"))
import momentum_paper as mp

class TestPaper(unittest.TestCase):
    def setUp(self):
        # 300 weekdays ending well past the first month-end after FIRST
        days, d = [], mp.FIRST - dt.timedelta(days=420)
        while len(days) < 330:
            if d.weekday() < 5:
                days.append(d)
            d += dt.timedelta(days=1)
        self.cal = [x for x in days if x <= dt.date(2026, 11, 10)]
        mk = lambda g: {x: (100 * g ** i, 100 * g ** i) for i, x in enumerate(days)}
        self.px = {"A": mk(1.004), "B": mk(1.003), "C": mk(1.002), "D": mk(1.001), "E": mk(1.0), "F": mk(0.999),
                   "SPY": mk(1.001), "SPMO": mk(1.001)}

    def test_first_period_and_rollover(self):
        st = {"periods": [], "finished": False}
        mp.step(st, self.px, self.cal, list("ABCDEF"))
        p0, p1 = st["periods"][0], st["periods"][1]
        self.assertEqual(p0["picks"], list("ABCDE"))          # F has the weakest momentum
        self.assertEqual(p0["entry"]["date"], "2026-10-19")   # next weekday after Fri 2026-10-16
        self.assertEqual(p0["exit"]["month_end"], "2026-10-30")
        self.assertEqual(p0["exit"]["date"], "2026-11-02")
        self.assertEqual(p1["entry"]["date"], "2026-11-02")   # new period opens at the same open
        self.assertIsNone(p1["exit"])                         # November not over in this data
        self.assertFalse(mp.step(st, self.px, self.cal, list("ABCDEF")))  # re-running changes nothing

if __name__ == "__main__":
    unittest.main()
