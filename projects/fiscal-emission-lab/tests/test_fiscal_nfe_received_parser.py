import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fiscal_nfe_received_parser import parse_nfe_xml, validate_minimal, persist  # noqa: E402


class FiscalNFeReceivedParserTest(unittest.TestCase):
    def setUp(self):
        self.fixture = ROOT / "fixtures" / "nfe-recebida-sintetica.xml"

    def test_parse_synthetic_fixture_to_normalized_payload(self):
        payload = parse_nfe_xml(self.fixture, real_data=False, origin="fixture-test", company_slug="mensura-fixture")
        validate_minimal(payload)
        self.assertEqual(payload["schema_version"], "fiscal-nota-recebida-v0")
        self.assertEqual(payload["document_type"], "NFe")
        self.assertFalse(payload["source"]["real_data"])
        self.assertEqual(payload["issuer"]["cnpj"], "12345678000199")
        self.assertEqual(payload["recipient"]["cnpj"], "11222333000144")
        self.assertEqual(payload["number"], "1234")
        self.assertEqual(payload["total_amount"], 250.0)
        self.assertEqual(payload["items"][0]["description"], "Papel A4 sintetico para teste")
        self.assertTrue(payload["risk_guardrails"]["read_only"])
        self.assertTrue(payload["risk_guardrails"]["no_external_send"])
        self.assertTrue(payload["risk_guardrails"]["no_fiscal_status_change"])
        self.assertTrue(payload["risk_guardrails"]["no_payment_approval"])

    def test_persist_writes_json_and_ledger_without_external_effects(self):
        payload = parse_nfe_xml(self.fixture, real_data=False, origin="fixture-test", company_slug="mensura-fixture")
        with tempfile.TemporaryDirectory() as tmp:
            out = persist(payload, self.fixture, Path(tmp), copy_xml=True)
            self.assertTrue(out.exists())
            saved = json.loads(out.read_text())
            self.assertEqual(saved["access_key"], "35260412345678000199550010000012341000012345")
            self.assertTrue(Path(saved["artifacts"]["xml_path"]).exists())
            ledger = Path(tmp) / "ledger" / "notas-recebidas.jsonl"
            self.assertTrue(ledger.exists())
            self.assertIn("mensura-fixture", ledger.read_text())


if __name__ == "__main__":
    unittest.main()
