"""
Unit tests for Module 1: Metadata Retrieval & Normalization
"""

import unittest
from backend.pipeline.metadata import normalize_paper, get_offline_sample_papers, retrieve_papers_by_topic

class TestMetadataModule(unittest.TestCase):

    def test_normalize_paper_with_complete_data(self):
        raw = {
            "paperId": "test_123",
            "title": "Deep Learning for Natural Language Processing",
            "authors": [{"name": "Jane Doe"}, {"name": "John Smith"}],
            "year": 2023,
            "venue": "ACL",
            "abstract": "This paper presents advances in transformer models.",
            "externalIds": {"DOI": "10.1234/acl.2023.1", "ArXiv": "2301.00001"},
            "citationCount": 55,
            "isOpenAccess": True,
            "openAccessPdf": {"url": "https://arxiv.org/pdf/2301.00001.pdf"}
        }

        normalized = normalize_paper(raw)
        self.assertIsNotNone(normalized)
        self.assertEqual(normalized["id"], "test_123")
        self.assertEqual(normalized["title"], "Deep Learning for Natural Language Processing")
        self.assertEqual(len(normalized["authors"]), 2)
        self.assertEqual(normalized["authors"][0], "Jane Doe")
        self.assertEqual(normalized["doi"], "10.1234/acl.2023.1")
        self.assertTrue(normalized["is_open_access"])
        self.assertEqual(normalized["oa_url"], "https://arxiv.org/pdf/2301.00001.pdf")

    def test_normalize_paper_with_missing_fields(self):
        raw = {"title": "Minimal Paper"}
        normalized = normalize_paper(raw)
        self.assertIsNotNone(normalized)
        self.assertEqual(normalized["title"], "Minimal Paper")
        self.assertEqual(normalized["authors"], ["Unknown Author"])
        self.assertFalse(normalized["is_open_access"])
        self.assertIsNone(normalized["oa_url"])

    def test_offline_fallback_papers_loaded(self):
        samples = get_offline_sample_papers()
        self.assertGreater(len(samples), 0)
        first = samples[0]
        self.assertIn("title", first)
        self.assertIn("abstract", first)

    def test_retrieve_by_topic_returns_results(self):
        results = retrieve_papers_by_topic("transformer", limit=3)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

if __name__ == "__main__":
    unittest.main()
