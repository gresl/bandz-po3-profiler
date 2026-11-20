"""Regression guard: clean chart script must not change frozen V2 detector behavior.

This is a source-integrity test, not a Pine compiler or realtime parity test.
"""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"Bandz_Po3_Profiler.pine"
CLEAN=ROOT/"indicators/Bandz_CISD_V2_Clean.pine"

def core(source: str)->str:
    a=source.index("type PoV2PivotEvent\n")
    b=source.index("\nfloat v2rPendingBull = na",a)
    return source[a:b].strip()

class FrozenEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=BASE.read_text(encoding="utf-8")
        cls.clean=CLEAN.read_text(encoding="utf-8")

    def test_verbatim_detector_core(self):
        self.assertEqual(core(self.base),core(self.clean),
                         "Do not edit frozen V2 candidate/confirmation logic")

    def test_all_original_detector_inputs_present(self):
        for variable in ("v2rOn", "v2rPivotLen", "v2rBridge",
                         "v2rScanBars", "v2rMinRun", "v2rExpiry",
                         "v2rAtrGate", "v2rMinAtr"):
            self.assertRegex(self.clean, rf"\b{variable}\s*=\s*input\.")
            self.assertEqual(len(re.findall(rf"\b{variable}\s*=\s*input\.",self.clean)),1)

    def test_frozen_chart_validation_settings_selected(self):
        self.assertIn('v2rOn       = input.bool(true,',self.clean)
        self.assertIn('v2rAtrGate  = input.bool(true,',self.clean)
        self.assertIn('v2rMinAtr   = input.float(0.5,',self.clean)
        self.assertIn('v2rPivotLen = input.int(1,',self.clean)
        self.assertIn('v2rBridge   = input.int(2,',self.clean)
        self.assertIn('v2rScanBars = input.int(12,',self.clean)
        self.assertIn('v2rMinRun   = input.int(1,',self.clean)
        self.assertIn('v2rExpiry   = input.int(10,',self.clean)

    def test_closed_bar_alerts_not_linked_to_legacy(self):
        self.assertIn("if v2rOn and barstate.isconfirmed",core(self.clean))
        self.assertEqual(self.clean.count("alertcondition("),2)
        self.assertIn("alertcondition(v2rOn and v2rNewBull",self.clean)
        self.assertIn("alertcondition(v2rOn and v2rNewBear",self.clean)
        self.assertNotIn("alert(",self.clean)
        self.assertNotIn("poLinkCisd(",self.clean)
        self.assertNotIn("request.security(",self.clean)
        self.assertNotIn("lookahead_on",self.clean)

    def test_chart_levels_generated_only_at_confirm_bar(self):
        self.assertIn("shownSide and ev.state == 1 and ev.confirmBar == bar_index",self.clean)
        self.assertIn("if v2rOn and v2rLines and showConfirmed and barstate.isconfirmed",self.clean)
        self.assertIn("if invalidated and not showInvalidated",self.clean)
        self.assertIn("line.set_style(ln, line.style_dotted)",self.clean)
        self.assertIn("while drawnLines.size() > historyLines",self.clean)
        self.assertIn("line.delete(drawnLines.shift())",self.clean)
        self.assertIn("v2rPanel = input.bool(false,",self.clean)
        self.assertIn("showPending = input.bool(false,",self.clean)

if __name__=="__main__":
    unittest.main()
