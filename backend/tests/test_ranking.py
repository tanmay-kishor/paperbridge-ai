"""Deterministic tests for PaperBridge v2 scoring and version handling."""

import unittest

from backend.pipeline.ranker import composite_score, deduplicate_versions


class TestRanking(unittest.TestCase):
    def test_composite_score_matches_v2_weights(self):
        paper = {
            "semantic_similarity": 0.8,
            "normalized_citation_overlap": 0.4,
            "citation_count_percentile_within_field": 0.6,
            "same_field_of_study": True,
        }
        expected = 0.5 * 0.8 + 0.25 * 0.4 + 0.15 * 0.6 + 0.10
        self.assertAlmostEqual(composite_score(paper), round(expected, 4))

    def test_version_deduplication_prefers_oa_version(self):
        papers = [
            {"id": "journal", "title": "A Study", "doi": "10.1234/study", "is_open_access": False, "citation_count": 100, "abstract": "short"},
            {"id": "preprint", "title": "A Study", "doi": "10.1234/study", "is_open_access": True, "citation_count": 10, "abstract": "longer abstract"},
        ]
        result = deduplicate_versions(papers)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "preprint")


    def test_title_like_topic_keeps_requested_title_match(self):
        from unittest.mock import patch
        from backend.pipeline import ranker

        requested = {
            "id": "requested-paper",
            "title": "A Structure for Deoxyribose Nucleic Acid",
            "abstract": "A structure for DNA.",
            "authors": ["J. D. Watson", "F. H. C. Crick"],
            "year": 1953,
            "citation_count": 1000,
            "fields_of_study": ["Biology"],
            "reference_ids": [],
            "author_ids": [],
            "is_open_access": False,
            "access_status": "paywalled",
        }
        recommendation = {
            "id": "recommendation",
            "title": "A Modern Review of DNA Structure",
            "abstract": "DNA review.",
            "authors": ["Other Author"],
            "year": 2020,
            "citation_count": 100,
            "fields_of_study": ["Biology"],
            "reference_ids": [],
            "author_ids": [],
            "is_open_access": True,
            "access_status": "open",
            "oa_url": "https://example.org/paper.pdf",
        }

        with patch.object(ranker, "retrieve_papers_by_topic", return_value=[recommendation]), \
             patch.object(ranker, "retrieve_paper_by_title_match", return_value=requested), \
             patch.object(ranker, "verify_papers_accessibility_batch", return_value=None):
            result = ranker.run_pipeline("A Structure for Deoxyribose Nucleic Acid", mode="topic", limit=10)

        titles = [p["title"] for p in result["results"]]
        self.assertIn("A Structure for Deoxyribose Nucleic Acid", titles)


if __name__ == "__main__":
    unittest.main()
