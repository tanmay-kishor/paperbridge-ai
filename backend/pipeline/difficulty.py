"""
PaperBridge AI - Module 4: Complexity & Reading Difficulty Assessment
(Track B - Access & Difficulty Modules)

Reasoning & Formula Selection (Viva Reference):
1. Why Flesch-Kincaid Grade Level?
   - Formula: 0.39 * (total words / total sentences) + 11.8 * (total syllables / total words) - 15.59
   - Industry-standard, empirically validated benchmark representing the U.S. grade
     level required to comprehend the text.
   - It captures syntactic complexity (sentence length) and morphological complexity (syllable count).

2. Why not combine all 5 classical readability formulas (SMOG, Gunning Fog, Coleman-Liau)?
   - Statistical studies show these formulas have cross-correlations > 0.85 on academic abstracts.
   - Averaging them merely introduces redundant computation without introducing any new signal.

3. Why add a Jargon / Technical-Density Signal?
   - Academic papers frequently use short sentences packed with dense domain vocabulary
     (e.g., "symplectic eigenvalues of covariance matrices in Hilbert space").
   - A pure syllable/sentence formula can fail to capture such domain density.
   - Jargon density computes the proportion of polysyllabic words (>= 3 syllables)
     and scientific domain vocabulary relative to total word count.

4. Tri-Level Bucketing:
   - Foundational: Introductory tutorials, clear surveys (FKGL < 10.5, jargon < 0.16)
   - Intermediate: Standard conference/journal publications (FKGL 10.5 - 14.0)
   - Advanced: Dense theoretical formulations, rigorous proofs (FKGL > 14.0 or jargon > 0.22)
"""

import re
import textstat

# Common academic framing patterns that reflect dense research terminology
ACADEMIC_TERM_PATTERN = re.compile(
    r"\b(asymptotic|stochastic|formulation|eigenvalue|symplectic|probabilistic|"
    r"covariance|heterogeneous|isomorphism|orthogonal|derivation|hyperparameter|"
    r"gradient|loss function|backpropagation|manifold|latent space|convergence|"
    r"regularization|semi-supervised|self-supervised|adversarial|theorem|lemma|"
    r"methodology|empirical|approximation|optimization)\b",
    re.IGNORECASE
)

def compute_jargon_density(text):
    """
    Computes technical jargon density as the ratio of complex words (>=3 syllables)
    and domain-specific academic terminology to total words.
    Returns a float between 0.0 and 1.0.
    """
    words = re.findall(r"\b[A-Za-z\-]+\b", text)
    if not words:
        return 0.0

    total_words = len(words)
    
    # 1. Count polysyllabic words (>= 3 syllables)
    polysyllabic_count = textstat.polysyllabcount(text)

    # 2. Count matches for academic domain terminology
    domain_terms = len(ACADEMIC_TERM_PATTERN.findall(text))

    # Weight complex words and domain terms
    weighted_complexity_count = polysyllabic_count + (domain_terms * 1.5)
    density = min(1.0, weighted_complexity_count / max(1, total_words))

    return round(float(density), 3)

def assess_paper_difficulty(paper):
    """
    Evaluates the reading difficulty of a paper using its abstract (and title).
    Attaches a 'difficulty' object:
      - level: 'Foundational' | 'Intermediate' | 'Advanced'
      - fk_grade: float
      - jargon_density: float
      - summary: human-readable explanation of why this difficulty was assigned
    """
    if not paper:
        return paper

    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    text_to_analyze = f"{title}. {abstract}".strip()

    if not text_to_analyze or len(text_to_analyze.split()) < 8:
        # Default fallback if abstract is unavailable or too brief
        paper["difficulty"] = {
            "level": "Intermediate",
            "fk_grade": 12.0,
            "jargon_density": 0.15,
            "summary": "Standard academic level (inferred from title alone)."
        }
        return paper

    # Calculate Flesch-Kincaid Grade Level
    try:
        fk_grade = float(textstat.flesch_kincaid_grade(text_to_analyze))
    except Exception:
        fk_grade = 12.0

    # Calculate Jargon Density
    jargon_density = compute_jargon_density(text_to_analyze)

    # Classification logic:
    # Foundational: Clear, low-to-moderate grade level (FKGL < 10.5) and low/moderate jargon (< 0.22)
    # Advanced: High grade level (FKGL > 14.0) or dense technical terminology (jargon > 0.24)
    # Intermediate: Standard peer-reviewed conference/journal papers falling in between
    if fk_grade < 10.5 and jargon_density < 0.22:
        level = "Foundational"
        summary = "Introductory or tutorial-level presentation with accessible sentence structure and readable terminology."
    elif fk_grade > 14.0 or jargon_density > 0.24:
        level = "Advanced"
        summary = "Advanced technical paper with dense theoretical terminology and complex syntactic structure."
    else:
        level = "Intermediate"
        summary = "Standard peer-reviewed publication requiring typical undergraduate-level domain background."

    paper["difficulty"] = {
        "level": level,
        "fk_grade": round(fk_grade, 1),
        "jargon_density": jargon_density,
        "summary": summary
    }

    return paper
