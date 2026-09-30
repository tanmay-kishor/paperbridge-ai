"""Tests for semantic similarity with a dependency-safe fallback."""

import unittest

from backend.pipeline.embeddings import calculate_semantic_relevance


class TestEmbeddingsModule(unittest.TestCase):
    def test_semantic_similarity_adds_scores(self):
        query = "time series sequence forecasting transformers"
        candidates = [
            {
                "id": "p_irrelevant",
                "title": "Historical Cooking Techniques of Ancient Rome",
                "abstract": "An archaeological analysis of bread baking and olive oil preservation.",
            },
            {
                "id": "p_relevant",
                "title": "Informer: Long Sequence Time-Series Forecasting Transformer",
                "abstract": "We present an efficient Transformer architecture designed specifically for multi-step temporal sequence forecasting.",
            },
        ]
        scored = calculate_semantic_relevance(query, candidates)
        self.assertTrue(all("semantic_similarity" in p for p in scored))
        self.assertGreater(scored[1]["semantic_similarity"], scored[0]["semantic_similarity"])
        self.assertIn(scored[1]["embedding_method"], {"specter2", "tfidf_fallback"})


if __name__ == "__main__":
    unittest.main()
