"""
Unit tests for Module 4: Complexity and Reading Difficulty Assessment
"""

import unittest
from backend.pipeline.difficulty import compute_jargon_density, assess_paper_difficulty

class TestDifficultyModule(unittest.TestCase):

    def test_compute_jargon_density_simple_text(self):
        simple_text = "This is a simple guide to learning computer science and writing code."
        density = compute_jargon_density(simple_text)
        self.assertLess(density, 0.15)

    def test_compute_jargon_density_academic_text(self):
        academic_text = (
            "We establish asymptotic convergence proofs for stochastic optimization "
            "over Riemannian manifolds with non-convex eigenvalues."
        )
        density = compute_jargon_density(academic_text)
        self.assertGreater(density, 0.20)

    def test_assess_paper_difficulty_foundational(self):
        paper = {
            "title": "A Beginner's Guide to Machine Learning",
            "abstract": "This tutorial explains the basic ideas of machine learning. We use simple examples and code."
        }
        assessed = assess_paper_difficulty(paper)
        self.assertIn("difficulty", assessed)
        self.assertEqual(assessed["difficulty"]["level"], "Foundational")
        self.assertLess(assessed["difficulty"]["fk_grade"], 11.0)

    def test_assess_paper_difficulty_advanced(self):
        paper = {
            "title": "Device-Independent Asymptotic Security Proofs for Continuous-Variable QKD",
            "abstract": (
                "We establish a non-asymptotic composable security proof against collective coherent "
                "eavesdropping attacks in Hilbert space utilizing symplectic diagonalization of arbitrary "
                "Gaussian state covariances and entropic uncertainty relations."
            )
        }
        assessed = assess_paper_difficulty(paper)
        self.assertIn("difficulty", assessed)
        self.assertEqual(assessed["difficulty"]["level"], "Advanced")
        self.assertGreater(assessed["difficulty"]["jargon_density"], 0.20)

if __name__ == "__main__":
    unittest.main()
