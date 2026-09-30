"""
PaperBridge AI - Module 3: Open-Access Discovery & Paywall Fallback Logic
(Track B - Access & Difficulty Modules)

Reasoning & Academic Ethics:
- PaperBridge AI strictly respects copyright and academic publisher terms.
  It NEVER accesses unauthorized mirrors (e.g. Sci-Hub) or attempts paywall circumvention.
- Instead, it checks legitimate open-access archives:
    1. Pass 1: Semantic Scholar's native `isOpenAccess` and `openAccessPdf` data.
    2. Pass 2: Unpaywall API (the gold standard for legitimate green/gold OA lookup via DOI).

Paywall Fallback (revised, post-supervisor-review):
- Cosine similarity alone only measures topical closeness, not equivalence of rigor or
  scientific contribution -- this was a real, acknowledged gap in the original design.
- A candidate now only qualifies as a suggested "related open-access work" if it clears
  BOTH:
    (a) a minimum semantic similarity threshold, AND
    (b) a credibility bar -- a minimum citation count, OR shared field-of-study with the
        paywalled paper.
- If nothing clears both bars, the system returns no_alternative_found=True instead of
  forcing a weak match. This is the correct, honest behavior for a uniquely foundational
  paper (e.g. a landmark result) where no real substitute exists.
- Results are always labeled "related_work", never "alternative" or "replacement" --
  enforced here at the data layer, not left to the frontend to phrase correctly.
"""

import logging
import requests
from backend.config import Config

logger = logging.getLogger(__name__)

# Fast in-memory cache to prevent duplicate external lookups
_DOI_OA_CACHE = {}

# --- Paywall-fallback credibility thresholds (tune against real validation queries) ---
MIN_FALLBACK_SIMILARITY = 0.45      # below this, a match is considered topically unrelated
MIN_CREDIBLE_CITATIONS = 5          # a candidate is "credible" if it clears this citation count...
REQUIRE_SHARED_FIELD_IF_LOW_CITED = True  # ...OR shares a field-of-study with the original paper
MIN_BIBLIOGRAPHIC_OVERLAP = 2       # ...OR shares at least this many references with the original paper


def _bibliographic_overlap(candidate, original_paper):
    """
    Counts shared references between a candidate and the original (paywalled) paper.
    Two papers that cite a lot of the same prior work are more likely addressing the
    same specific sub-problem at a comparable depth -- a stronger depth-relatedness
    signal than topic similarity alone, which only reflects shared vocabulary/subject.
    Requires reference_ids populated by metadata.normalize_paper() (references.paperId
    field from Semantic Scholar). Returns 0 if either side lacks reference data --
    this is a bonus signal, not a requirement, since reference data isn't always present.
    """
    orig_refs = set(original_paper.get("reference_ids") or [])
    cand_refs = set(candidate.get("reference_ids") or [])
    if not orig_refs or not cand_refs:
        return 0
    return len(orig_refs & cand_refs)


def _same_author_match(candidate, original_paper):
    """
    Checks whether the candidate shares an author with the paywalled original --
    e.g. the authors' own open-access preprint of the same work. This is the
    highest-confidence fallback case: same authors writing on the same topic is a
    much stronger signal than semantic similarity to an unrelated author's paper.
    """
    orig_authors = {a.strip().lower() for a in (original_paper.get("authors") or []) if a}
    cand_authors = {a.strip().lower() for a in (candidate.get("authors") or []) if a}
    if not orig_authors or not cand_authors:
        return False
    return bool(orig_authors & cand_authors)


def check_unpaywall_oa(doi):
    """
    Queries the Unpaywall API for a given DOI to verify legitimate open-access status.
    Unpaywall requires an email parameter for tracking fair usage.
    Fast 1.5s timeout with caching to prevent slow response times in cloud hosting.

    Returns:
      (is_oa: bool, oa_url: str or None, oa_source: str or None)
    """
    if not doi:
        return False, None, None

    clean_doi = doi.strip()
    if clean_doi.startswith("http"):
        clean_doi = clean_doi.split("doi.org/")[-1]

    if clean_doi in _DOI_OA_CACHE:
        return _DOI_OA_CACHE[clean_doi]

    url = f"{Config.UNPAYWALL_BASE_URL}/{clean_doi}"
    params = {"email": Config.UNPAYWALL_EMAIL}

    try:
        resp = requests.get(url, params=params, timeout=1.5)
        if resp.status_code == 200:
            data = resp.json()
            is_oa = bool(data.get("is_oa", False))
            best_location = data.get("best_oa_location") or {}

            oa_url = best_location.get("url_for_pdf") or best_location.get("url") or None
            if oa_url and oa_url.startswith("http://"):
                oa_url = oa_url.replace("http://", "https://")

            host_type = best_location.get("host_type", "repository")
            oa_source = f"Unpaywall ({host_type.capitalize()} OA)" if is_oa else None

            result = (is_oa, oa_url, oa_source)
            _DOI_OA_CACHE[clean_doi] = result
            return result
    except Exception as e:
        logger.warning(f"Unpaywall lookup skipped or timed out for '{clean_doi}': {e}")

    result = (False, None, None)
    _DOI_OA_CACHE[clean_doi] = result
    return result


def verify_paper_accessibility(paper):
    """
    Runs dual-pass open-access verification on a single normalized paper dictionary.
    Updates `is_open_access`, `oa_url`, and `oa_source` in-place.
    """
    if not paper:
        return paper

    # Pass 1: Already flagged as OA from Semantic Scholar or ArXiv?
    if paper.get("is_open_access") and paper.get("oa_url"):
        return paper

    # Pass 2: Check Unpaywall via DOI if DOI is present
    doi = paper.get("doi")
    if doi:
        is_oa, oa_url, oa_source = check_unpaywall_oa(doi)
        if is_oa and oa_url:
            paper["is_open_access"] = True
            paper["oa_url"] = oa_url
            paper["oa_source"] = oa_source
            return paper

    # If neither pass yielded open access, mark as paywalled
    paper["is_open_access"] = False
    paper["oa_url"] = None
    paper["oa_source"] = None
    return paper


def verify_papers_accessibility_batch(papers_list, max_workers=5):
    """
    Verifies open-access status for a list of candidate papers concurrently
    using ThreadPoolExecutor, dropping execution latency from ~15s to ~1.5s.
    """
    if not papers_list:
        return papers_list

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(verify_paper_accessibility, papers_list))

    return papers_list


def _is_credible_alternative(candidate, original_paper):
    """
    Credibility check for a paywall-fallback candidate: a topically-similar open-access
    paper only counts as a genuine "related work" suggestion if it also clears a basic
    quality/relatedness bar -- otherwise similarity alone can surface a low-quality or
    unrelated-subfield match (the exact failure mode raised in supervisor review).

    A candidate qualifies if ANY of the following hold:
      - same author(s) as the original paper (highest-confidence case -- e.g. the
        authors' own preprint of the same work)
      - clears the citation count floor
      - shares a field-of-study tag with the original paper
      - shares at least MIN_BIBLIOGRAPHIC_OVERLAP references with the original paper
    """
    if _same_author_match(candidate, original_paper):
        return True

    citations = candidate.get("citation_count", 0) or 0
    if citations >= MIN_CREDIBLE_CITATIONS:
        return True

    if REQUIRE_SHARED_FIELD_IF_LOW_CITED:
        orig_fields = set(original_paper.get("fields_of_study") or [])
        cand_fields = set(candidate.get("fields_of_study") or [])
        if orig_fields and cand_fields and (orig_fields & cand_fields):
            return True

    if _bibliographic_overlap(candidate, original_paper) >= MIN_BIBLIOGRAPHIC_OVERLAP:
        return True

    return False


def find_credible_open_access_alternatives(candidate_papers, original_paper, exclude_id=None):
    """
    Filters + ranks a list of candidate papers into credible open-access "related work"
    suggestions for a paywalled `original_paper`.

    A candidate qualifies only if it:
      1. Is verified open-access,
      2. Clears MIN_FALLBACK_SIMILARITY on `relevance_score` (caller must have already run
         semantic similarity against the original paper's abstract before calling this),
      3. Clears the credibility bar (citation count OR shared field-of-study).

    Returns:
      (alternatives: list, no_alternative_found: bool)
      `alternatives` is sorted by relevance_score descending. Each item gets:
        - relationship_type: "related_work"  (never "alternative"/"replacement")
        - match_confidence: "Strong match" | "Moderate match" | "Weak match"
    """
    if not candidate_papers:
        return [], True

    verify_papers_accessibility_batch(candidate_papers)

    qualified = []
    for p in candidate_papers:
        if exclude_id and p.get("id") == exclude_id:
            continue
        if not p.get("is_open_access"):
            continue
        if p.get("relevance_score", 0.0) < MIN_FALLBACK_SIMILARITY:
            continue
        if not _is_credible_alternative(p, original_paper):
            continue

        score = p["relevance_score"]
        is_same_author = _same_author_match(p, original_paper)
        overlap = _bibliographic_overlap(p, original_paper)

        if is_same_author:
            # Same author(s) writing on the same topic -- the highest-confidence
            # fallback case (e.g. the authors' own preprint of this exact work).
            confidence = "Strong match"
        elif score >= 0.75 and (p.get("citation_count", 0) >= MIN_CREDIBLE_CITATIONS or overlap >= MIN_BIBLIOGRAPHIC_OVERLAP):
            confidence = "Strong match"
        elif score >= 0.6:
            confidence = "Moderate match"
        else:
            confidence = "Weak match"

        p["relationship_type"] = "related_work"
        p["match_confidence"] = confidence
        p["same_author_match"] = is_same_author
        p["bibliographic_overlap"] = overlap
        qualified.append(p)

    if not qualified:
        return [], True

    # Same-author matches first (highest-confidence case), then by relevance score.
    qualified.sort(key=lambda p: (p.get("same_author_match", False), p["relevance_score"]), reverse=True)
    return qualified, False


# Kept for backward compatibility with any existing callers; new code should use
# find_credible_open_access_alternatives, which adds the threshold + credibility filter.
def filter_open_access_alternatives(candidate_papers, exclude_id=None):
    if not candidate_papers:
        return []
    verify_papers_accessibility_batch(candidate_papers)
    return [
        p for p in candidate_papers
        if p.get("is_open_access") and (not exclude_id or p.get("id") != exclude_id)
    ]
