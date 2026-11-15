"""Deterministic synthetic examples; never presented as observed market signals."""
import unittest
from research.cisd_v2_oracle import bars_from_ohlc, evaluate

BEARISH = [
    (100, 102, 99, 101),
    (101, 104, 100, 103),
    (103, 106, 101, 102),
    (102, 103, 100, 101),
    (101, 102, 98, 99),
]
BULLISH = [
    (110, 111, 108, 109),
    (109, 110, 106, 107),
    (107, 109, 104, 108),
    (108, 110, 107, 109),
    (109, 112, 108, 111),
]


class TestV2PivotLifecycle(unittest.TestCase):
    def test_no_backfilled_confirmation_before_the_close(self):
        self.assertFalse(any(not ev.bullish and ev.state == "CONFIRMED"
                             for ev in evaluate(bars_from_ohlc(BEARISH[:4]))))
        bearish = [ev for ev in evaluate(bars_from_ohlc(BEARISH)) if not ev.bullish]
        self.assertEqual(len(bearish), 1)
        self.assertEqual((bearish[0].pivot, bearish[0].born, bearish[0].origin), (2, 3, 0))
        self.assertEqual(bearish[0].level, 100)
        self.assertEqual(bearish[0].confirmed_at, bars_from_ohlc(BEARISH)[4].closing)

    def test_bullish_mirror(self):
        bullish = [ev for ev in evaluate(bars_from_ohlc(BULLISH)) if ev.bullish]
        self.assertEqual(len(bullish), 1)
        self.assertEqual((bullish[0].pivot, bullish[0].born, bullish[0].origin), (2, 3, 0))
        self.assertEqual(bullish[0].level, 110)
        self.assertEqual(bullish[0].confirmed_at, bars_from_ohlc(BULLISH)[4].closing)

    def test_pivot_breach_rejects_pending_before_confirmation(self):
        rows = BEARISH[:4] + [(101, 107, 100.5, 101.2)]
        bear = [e for e in evaluate(bars_from_ohlc(rows)) if not e.bullish]
        self.assertEqual(bear[-1].state, "REJECTED")
        self.assertEqual(bear[-1].reason, "PIVOT_BREACH")

    def test_expiry(self):
        rows = BEARISH[:4] + [(101, 102, 100, 101)] * 3
        bears = [e for e in evaluate(bars_from_ohlc(rows), expiry=2) if not e.bullish]
        self.assertEqual(bears[-1].state, "EXPIRED")

    def test_min_run_and_size_filter_can_reject(self):
        self.assertFalse([e for e in evaluate(bars_from_ohlc(BEARISH), min_run=4) if not e.bullish])
        self.assertFalse([e for e in evaluate(bars_from_ohlc(BEARISH), min_range=100) if not e.bullish])

    def test_invalidation_after_confirm_preserves_confirm_close(self):
        rows = BEARISH + [(99, 107, 98, 100)]
        bear = [e for e in evaluate(bars_from_ohlc(rows)) if not e.bullish][0]
        self.assertEqual(bear.state, "INVALIDATED")
        self.assertEqual(bear.confirmed_at, bars_from_ohlc(rows)[4].closing)
        self.assertEqual(bear.terminal_at, bars_from_ohlc(rows)[5].closing)


if __name__ == '__main__':
    unittest.main()
