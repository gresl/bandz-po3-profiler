"""Static regression checks for the full-feature Visual Test Pine build.

We freeze the complete code after its input block. The only permitted changes
relative to full integration are indicator title, tooltip text and settings UI.
This is not a substitute for a TradingView-native Pine compile.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FULL = ROOT / "indicators" / "Bandz_Po3_Full_V2_Integrated.pine"
VISUAL = ROOT / "indicators" / "Bandz_Po3_V2_Visual_Test.pine"
MARKER = "bool   poStdvOn        = po3ShowStdv"

def input_count(text):
    return len(re.findall(r"\binput\.(?:bool|float|int|string|symbol|session|time|timeframe|color)\s*\(",text))

class VisualTestContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full = FULL.read_text(encoding="utf-8")
        cls.visual = VISUAL.read_text(encoding="utf-8")

    def test_all_computational_logic_is_exactly_preserved(self):
        """No research clean-up changes Po3/CISD/SMT rendering or state machine."""
        self.assertIn(MARKER, self.full)
        self.assertIn(MARKER, self.visual)
        self.assertEqual(self.full[self.full.index(MARKER):],
                         self.visual[self.visual.index(MARKER):])

    def test_50_settings_removed_and_v2_controls_retained(self):
        self.assertEqual(input_count(self.full)-input_count(self.visual), 50)
        for key in (
            "Chart CISD engine", "CISD", "Sequence CISD from",
            "Pivot confirmation: left/right bars", "Bars to locate opposing stretch",
            "Maximum additional stretch bars", "Minimum opposing candles",
            "Candidate expiry bars", "Require minimum stretch / ATR14",
            "Minimum stretch / ATR14", "History lines (All / highlighted)",
            "Show invalidated CISDs (faded)",
        ):
            with self.subTest(input=key):
                self.assertIn(key,self.visual)
        self.assertIn('poCisdEngine = input.string("V2"',self.visual)
        self.assertIn('bool  v2rOn = poCisdEngine == "V2"',self.visual)

    def test_research_diagnostics_are_fixed_off_and_not_input_controls(self):
        fixed_off = (
            "poCisdDiagnostics", "poCisdFvgZones", "poCisdQualDisp",
            "poCisdQualFvg", "poCisdQualStats", "poCisdAuditOn",
            "poCisdOutcomeOn", "poCisdParityAudit", "v2rParallel",
            "v2rLines", "v2rPanel", "v2dOn", "v2SkipOn",
            "v2BatchExportOn", "v2LogOn", "v2LogLifecycle",
        )
        for name in fixed_off:
            with self.subTest(setting=name):
                self.assertRegex(self.visual,rf"(?m)^\s*bool\s+{name}\s*=\s*false\s*$")
                self.assertNotRegex(self.visual,rf"(?m)^\s*bool\s+{name}\s*=\s*input\.")
        for research_name in ("4B · CISD structural research",
                              "4C · CISD V2 pivot research",
                              "4D · Legacy CISD skip diagnostics",
                              "4E · Research batch CSV export",
                              "4F · Essential Pine Logs"):
            self.assertNotIn(research_name,self.visual)

    def test_legacy_and_v2_configuration_baselines_are_stable(self):
        expected=(
            "poCisdHistoryKeep = 100", "poCisdViewFilter = \"All\"",
            "poCisdQualC2 = \"Off\"", "poCisdQualBodyPct = 55.0",
            "poCisdQualAtr = 0.6", "poCisdQualClosePct = 70.0",
            "poCisdKzLondon = \"0200-0500\"", "poCisdKzNy = \"0700-1000\"",
            "v2dBars = 96", "v2dSameTicks = 3", "v2dNearTicks = 20",
            "v2rMinAtr = input.float(0.5", "v2rPivotLen = input.int(1",
            "v2rBridge = input.int(2", "v2rScanBars = input.int(12",
            "v2rMinRun = input.int(1", "v2rExpiry = input.int(10",
            "v2rAtrGate = input.bool(true",
        )
        normalized=re.sub(r" +"," ",self.visual)
        for item in expected:
            with self.subTest(item=item):
                self.assertIn(item,normalized)

    def test_full_po3_modules_still_present(self):
        for name in (
            "poRenderLanes", "poRenderLevels", "poRenderProfile",
            "poRenderSmt", "poCisdScope", "poLinkCisd",
            "poStdvLevels", "poSpotZone", "po3ShowEFvg", "poPspOn",
            "po3ShowMtfCisd", "poSsmtOn", "poCisdEngine",
            "poCisdNewBull", "v2rNewBull", "poCisdNewBear", "v2rNewBear",
        ):
            with self.subTest(module=name):
                self.assertIn(name,self.visual)

if __name__ == "__main__":
    unittest.main()
