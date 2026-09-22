"""
Unit tests for Module 2: Sentence Transformers & Cosine Similarity Ranking
"""

import unittest
from backend.pipeline.embeddings import compute_embeddings, calculate_semantic_relevance

class TestEmbeddingsModule(unittest.TestCase):

    def test_compute_embeddings_shape(self):
        texts = [
            "Attention Is All You Need",
            "Transformer architectures for natural language processing."
        ]
        embeddings = compute_embeddings(texts)
        self.assertEqual(embeddings.shape[0], 2)
        self.assertEqual(embeddings.shape[1], 384)

    def test_semantic_similarity_ranking_order(self):
        query = "time series sequence forecasting transformers"
        candidates = [
            {
                "id": "p_irrelevant",
                "title": "Historical Cooking Techniques of Ancient Rome",
                "abstract": "An archaeological analysis of bread baking and olive oil preservation."
            },
            {
                "id": "p_relevant",
                "title": "Informer: Long Sequence Time-Series Forecasting Transformer",
                "abstract": "We present an efficient Transformer architecture designed specifically for multi-step temporal sequence forecasting."
            }
        ]

        scored = calculate_semantic_relevance(query, candidates)
        self.assertIn("relevance_score", scored[0])
        self.assertIn("relevance_score", scored[1])

        # The Informer paper should have a much higher similarity score than ancient cooking
        self.assertGreater(scored[1]["relevance_score"], scored[0]["relevance_score"])
        self.assertGreater(scored[1]["relevance_score"], 0.6)

if __name__ == "__main__":
    unittest.main()
