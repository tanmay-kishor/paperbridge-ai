"""
Unit tests for Module 3: Open Access Discovery & Paywall Fallback Logic
"""

import unittest
from backend.pipeline.open_access import verify_paper_accessibility, filter_open_access_alternatives

class TestOpenAccessModule(unittest.TestCase):

    def test_verify_paper_already_oa(self):
        paper = {
            "id": "p1",
            "title": "Open Access Paper",
            "is_open_access": True,
            "oa_url": "https://arxiv.org/pdf/1706.03762.pdf",
            "oa_source": "Semantic Scholar OA"
        }
        verified = verify_paper_accessibility(paper)
        self.assertTrue(verified["is_open_access"])
        self.assertEqual(verified["oa_url"], "https://arxiv.org/pdf/1706.03762.pdf")

    def test_verify_paywalled_paper_stays_paywalled(self):
        paper = {
            "id": "p2",
            "title": "Paywalled Paper with Invalid DOI",
            "doi": "10.9999/fake_nonexistent_doi_12345",
            "is_open_access": False,
            "oa_url": None
        }
        verified = verify_paper_accessibility(paper)
        self.assertFalse(verified["is_open_access"])
        self.assertIsNone(verified["oa_url"])

    def test_filter_open_access_alternatives(self):
        candidates = [
            {
                "id": "paywalled_target",
                "title": "Paywalled DB",
                "is_open_access": False,
                "oa_url": None
            },
            {
                "id": "oa_alternative_1",
                "title": "Open DB",
                "is_open_access": True,
                "oa_url": "https://vldb.org/paper.pdf",
                "oa_source": "VLDB Open Access"
            }
        ]
        alternatives = filter_open_access_alternatives(candidates, exclude_id="paywalled_target")
        self.assertEqual(len(alternatives), 1)
        self.assertEqual(alternatives[0]["id"], "oa_alternative_1")

if __name__ == "__main__":
    unittest.main()
