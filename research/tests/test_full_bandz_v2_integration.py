"""Static regression contracts for full Bandz / CISD V2 integration.

NOTE: This protects exact detector source and expected integration boundaries.
It does not substitute for native Pine compilation or realtime replay tests.
"""
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"Bandz_Po3_Profiler.pine"
FULL=ROOT/"indicators/Bandz_Po3_Full_V2_Integrated.pine"

def detector(src: str)->str:
    a=src.index("type PoV2PivotEvent\n")
    b=src.index("\nfloat v2rPendingBull = na",a) if "\nfloat v2rPendingBull = na" in src[a:] else src.index("\n// Which CISD slot feeds the sequence:",a)
    return src[a:b].strip()

class FullBandzV2Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=BASE.read_text(encoding="utf-8")
        cls.full=FULL.read_text(encoding="utf-8")

    def test_frozen_v2_engine_is_exact(self):
        self.assertEqual(detector(self.base), detector(self.full),
                         "V2 state machine must not change during integration")

    def test_major_bandz_features_are_preserved(self):
        feature_markers=(
            "po3ShowCandles", "po3ShowProfile", "po3ShowTSpot", "po3ShowSmt",
            "po3ShowPsp", "po3ShowSmtLbl", "po3ShowTable", "po3ShowStdv",
            "po3ShowImb", "po3ShowMarks", "po3ShowLevels", "po3ShowVOpen",
            "po3ShowLiq", "po3ShowMtfCisd", "po3ShowEFvg", "poRenderLanes(",
            "poRenderLevels(", "poRenderProfile(", "poRenderSmt(",
            "poLayoutCalc(", "poSpotZone(", "poSpotStrict", "po3ShowCandles",
            "poRecs", "poSmtMarks", "poPspFlag", "poRequestCmp",
            "poCisdEvents", "poCisdFvgZones", "poUpdateMinimal(",
            "poCisdScope", "poSeqCisdTf", "poStdvLevels", "poCisdKzLondon",
        )
        for marker in feature_markers:
            with self.subTest(marker=marker):
                self.assertIn(marker,self.base)
                self.assertIn(marker,self.full)

    def test_legacy_cisd_detector_still_runs_unchanged(self):
        a=self.base.index("// ── CISD: close back through the open")
        b=self.base.index("// Which CISD slot feeds the sequence:",a)
        original=self.base[a:b]
        # The legacy detector, including its state reset logic, is untouched.
        head=original[:original.index("// Which CISD slot")] if "// Which CISD slot" in original else original
        self.assertIn(head,self.full)

    def test_v2_runs_before_sequence_dispatch_and_rendering(self):
        src=self.full
        self.assertLess(src.index("type PoV2PivotEvent"),src.index("poLinkCisd(PoRec"))
        self.assertLess(src.index("type PoV2PivotEvent"),src.index("if barstate.islast and bandzModulePo3"))
        self.assertEqual(src.count("type PoV2PivotEvent"),1)

    def test_engine_switch_and_two_unmixed_chart_routes(self):
        src=self.full
        self.assertIn('poCisdEngine = input.string("V2"',src)
        self.assertIn('options=["Legacy", "V2"]',src)
        self.assertIn('poCisdEngine == "Legacy" and (poCisdNewBull or poCisdNewBear)',src)
        self.assertIn('poCisdEngine == "V2" and v2rOn and barstate.isconfirmed',src)
        self.assertIn("ve.state == 1 and ve.confirmBar == bar_index",src)
        self.assertIn("poLinkCisd(rc, 0, ve.confirmBar, ve.originBar, ve.level, time)",src)
        self.assertIn("poLinkCisd(rc, 0, bar_index, nc.startBar, nc.level, time)",src)
        self.assertIn('poSeqCisdTf == "3m"',src)
        self.assertIn('poSeqCisdTf == "5m"',src)
        self.assertIn("poStdvOn and newest and not na(rc.c2Wick)",src)
        self.assertEqual(src.count("poLinkCisd(rc, 0"),2)

    def test_visuals_use_origin_and_never_change_detector(self):
        src=self.full
        self.assertIn("poLineI(ev.originBar, ev.level, ev.confirmBar + 3",src)
        self.assertIn('poCisdEngine == "Legacy" and poCisdScope == "All"',src)
        self.assertIn('poCisdEngine == "V2" and poCisdScope != "Sequence only"',src)
        self.assertIn("linkedV2 := true",src)
        self.assertIn("po3ShowCisd and poCisdScope == "+'"Sequence only"',src)
        self.assertNotIn("request.security(",detector(src))
        self.assertNotIn("lookahead_on",detector(src))

if __name__=="__main__":
    unittest.main()
