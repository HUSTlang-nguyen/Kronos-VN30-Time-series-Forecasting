"""Do not confuse a dated report with a report about the wrong session/index."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from review_close_publications import extract_close


class PublicationTests(unittest.TestCase):
    def article(
        self, date="26/10/2022", value="990.41", comment="Kết thúc phiên giao dịch"
    ):
        return f"<h1>Bản tin thị trường ngày {date}</h1><h2>TTCK VIỆT NAM</h2><b>VN-INDEX</b>993.36<b>VN30</b>{value}<p>{comment}</p><h2>ETF &amp; PHÁI SINH</h2>"

    def test_correct_index_and_session(self):
        self.assertEqual(extract_close(self.article(), "2022-10-26")["value"], 990.41)

    def test_thousands_separator(self):
        self.assertEqual(
            extract_close(self.article(value="1,990.41"), "2022-10-26")["value"],
            1990.41,
        )

    def test_wrong_date_rejected(self):
        self.assertEqual(
            extract_close(self.article(), "2022-10-27")["status"],
            "unverified_publication_date",
        )

    def test_intraday_without_close_semantics_rejected(self):
        self.assertEqual(
            extract_close(self.article(comment="Phiên sáng"), "2022-10-26")["status"],
            "unverified_close_semantics",
        )

    def test_script_numbers_are_not_report_values(self):
        html = self.article().replace(
            "<b>VN30</b>990.41", "<script>VN30 990.41</script>"
        )
        self.assertEqual(
            extract_close(html, "2022-10-26")["status"], "unverified_index_value"
        )

    def test_unverified_candidate_is_not_verified_close(self):
        result = extract_close(self.article(comment="Phiên sáng"), "2022-10-26")
        self.assertEqual(result["candidate_value"], 990.41)
        self.assertNotIn("value", result)


if __name__ == "__main__":
    unittest.main()
