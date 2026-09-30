"""Approximate research-paper reading difficulty assessment."""

import re

try:
    import textstat
except ImportError:  # Keep the API testable before dependencies are installed.
    textstat = None

ACADEMIC_TERM_PATTERN = re.compile(
    r"\b(asymptotic|stochastic|formulation|eigenvalue|symplectic|probabilistic|"
    r"covariance|heterogeneous|isomorphism|orthogonal|derivation|hyperparameter|"
    r"gradient|loss function|backpropagation|manifold|latent space|convergence|"
    r"regularization|semi-supervised|self-supervised|adversarial|theorem|lemma|"
    r"methodology|empirical|approximation|optimization)\b",
    re.IGNORECASE,
)


def _fallback_syllables(word):
    word = re.sub(r"[^a-z]", "", word.lower())
    if not word:
        return 0
    groups = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e") and groups > 1:
        groups -= 1
    return max(1, groups)


def _fallback_fk_grade(text):
    words = re.findall(r"\b[A-Za-z]+\b", text)
    sentences = max(1, len(re.findall(r"[.!?]+", text)))
    syllables = sum(_fallback_syllables(w) for w in words)
    if not words:
        return 0.0
    return 0.39 * (len(words) / sentences) + 11.8 * (syllables / len(words)) - 15.59


def compute_jargon_density(text):
    words = re.findall(r"\b[A-Za-z\-]+\b", text)
    if not words:
        return 0.0
    polysyllabic_count = textstat.polysyllabcount(text) if textstat else sum(
        1 for word in words if _fallback_syllables(word) >= 3
    )
    domain_terms = len(ACADEMIC_TERM_PATTERN.findall(text))
    density = min(1.0, (polysyllabic_count + domain_terms * 1.5) / len(words))
    return round(float(density), 3)


def assess_paper_difficulty(paper):
    if not paper:
        return paper
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    text = f"{title}. {abstract}".strip()

    if len(text.split()) < 8:
        paper["difficulty"] = {
            "level": "Intermediate",
            "fk_grade": 12.0,
            "jargon_density": 0.15,
            "summary": "Approximate academic level inferred from limited available text.",
        }
        return paper

    try:
        fk_grade = float(textstat.flesch_kincaid_grade(text)) if textstat else _fallback_fk_grade(text)
    except Exception:
        fk_grade = _fallback_fk_grade(text)
    jargon_density = compute_jargon_density(text)

    if fk_grade < 10.5 and jargon_density < 0.22:
        level = "Foundational"
        summary = "Lower reading complexity with relatively accessible sentence structure and terminology."
    elif fk_grade > 14.0 or jargon_density > 0.24:
        level = "Advanced"
        summary = "Higher reading complexity with dense technical terminology and/or complex sentence structure."
    else:
        level = "Intermediate"
        summary = "Typical academic reading complexity with moderate technical terminology."

    paper["difficulty"] = {
        "level": level,
        "fk_grade": round(fk_grade, 1),
        "jargon_density": jargon_density,
        "summary": summary,
    }
    return paper
