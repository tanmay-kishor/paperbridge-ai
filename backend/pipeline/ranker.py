"""
PaperBridge AI - Module 5: Recommendation Ranker & Pipeline Orchestration
(Combines Track A and Track B into unified search logic)

Scoring Logic & Weighting (Viva Reference):
1. Primary Signal: Semantic Relevance (Cosine Similarity via Sentence Transformers)
   - Governs the rank ordering (weight: 85%).
2. Secondary Signal: Open-Access Prioritization
   - When papers have closely comparable semantic relevance, legitimately accessible
     open-access versions are prioritized so students are not blocked by paywalls.
3. Tertiary Signal: Citation Authority
   - Log-normalized citation count serves as an authoritative signal for canonical papers.
4. Explainability:
   - Every recommendation produces an explainable rationale ('why_recommended')
     stating the semantic match, access status, and reading level.
"""

import logging
import math
from backend.pipeline.metadata import (
    retrieve_papers_by_topic,
    retrieve_paper_by_identifier,
    get_offline_sample_papers
)
from backend.pipeline.embeddings import calculate_semantic_relevance
from backend.pipeline.open_access import (
    verify_paper_accessibility,
    verify_papers_accessibility_batch,
    find_credible_open_access_alternatives
)
from backend.pipeline.difficulty import assess_paper_difficulty

logger = logging.getLogger(__name__)

def generate_recommendation_reason(paper, is_fallback=False):
    """
    Constructs a plain-language explanation for why this paper was recommended.
    """
    relevance_pct = int(round(paper.get("relevance_score", 0.8) * 100))
    diff_level = paper.get("difficulty", {}).get("level", "Intermediate")
    oa_status = "Free PDF" if paper.get("is_open_access") else "Paywalled"
    citations = paper.get("citation_count", 0)

    if is_fallback:
        return (
            f"Open-Access Alternative ({relevance_pct}% semantic match to paywalled paper); "
            f"{diff_level} level; {oa_status} available."
        )

    citation_note = f" Highly cited ({citations:,} citations)." if citations > 500 else ""
    return (
        f"{relevance_pct}% semantic match; {diff_level} difficulty; {oa_status}.{citation_note}"
    )

def composite_score(paper):
    """
    Computes a composite score for ordering candidate recommendations.
    Weights:
      - 0.85 * semantic_relevance
      - 0.10 * open_access_boost
      - 0.05 * normalized_citation_signal
    """
    rel = paper.get("relevance_score", 0.5)
    oa_boost = 1.0 if paper.get("is_open_access") else 0.0
    citations = paper.get("citation_count", 0)
    # Logarithmic scaling for citations to prevent million-citation papers from overpowering relevance
    cite_signal = min(1.0, math.log1p(max(0, citations)) / 10.0)

    score = (0.85 * rel) + (0.10 * oa_boost) + (0.05 * cite_signal)
    return score

def run_pipeline(query, mode="topic", limit=10):
    """
    Full Recommendation Pipeline Execution:
    1. Input identification (topic vs paper title/DOI).
    2. Metadata retrieval (Semantic Scholar + fallback).
    3. Semantic embeddings + cosine similarity.
    4. Open-access verification (Unpaywall + S2 OA).
    5. Paywall fallback logic (if paper mode and paywalled).
    6. Readability & jargon density assessment.
    7. Multi-signal ranking and explainability generation.
    """
    clean_query = query.strip()
    logger.info(f"Executing PaperBridge recommendation pipeline: query='{clean_query}', mode='{mode}'")

    paywalled_original = None

    if mode == "paper":
        # Mode: Paper Title or DOI
        target_paper, candidates = retrieve_paper_by_identifier(clean_query)
        if target_paper:
            # Check accessibility of the target paper
            verify_paper_accessibility(target_paper)

            if not target_paper.get("is_open_access"):
                # PAYWALL FALLBACK TRIGGERED:
                # The user requested a paywalled paper. Its title/abstract/citation metadata
                # are public regardless of paywall status, so we use them (never the full text)
                # to search for credible, legitimately open-access related work.
                paywalled_original = {
                    "title": target_paper.get("title"),
                    "doi": target_paper.get("doi"),
                    "venue": target_paper.get("venue"),
                    "note": "This paper is paywalled. Related open-access work is shown below where a "
                            "credible match exists -- these are related work, not equivalent replacements."
                }

                # Semantic search using the target paper's content as query. Rank candidates
                # against the paywalled paper's abstract BEFORE filtering, since the threshold
                # and credibility check both depend on relevance_score being populated first.
                seed_text = f"{target_paper.get('title')}. {target_paper.get('abstract')}".strip()
                oa_candidates = retrieve_papers_by_topic(target_paper.get("title"), limit=limit * 3)
                calculate_semantic_relevance(seed_text, oa_candidates)

                open_alternatives, no_alternative_found = find_credible_open_access_alternatives(
                    oa_candidates, original_paper=target_paper, exclude_id=target_paper.get("id")
                )

                if no_alternative_found:
                    # Try the offline sample pool once more before concluding nothing exists,
                    # but still apply the same threshold/credibility bar -- never force a weak match.
                    all_samples = get_offline_sample_papers()
                    sample_candidates = [p for p in all_samples if p.get("id") != target_paper.get("id")]
                    calculate_semantic_relevance(seed_text, sample_candidates)
                    open_alternatives, no_alternative_found = find_credible_open_access_alternatives(
                        sample_candidates, original_paper=target_paper, exclude_id=target_paper.get("id")
                    )

                for p in open_alternatives:
                    assess_paper_difficulty(p)
                    p["is_paywall_fallback"] = True
                    p["why_recommended"] = generate_recommendation_reason(p, is_fallback=True)

                open_alternatives.sort(key=composite_score, reverse=True)
                final_results = open_alternatives[:limit]

                if no_alternative_found:
                    paywalled_original["note"] = (
                        "This paper is paywalled, and no comparable open-access work was found above "
                        "our relevance and credibility threshold. This paper may be a uniquely foundational "
                        "contribution without a close substitute -- accessing it directly (institutional "
                        "access, interlibrary loan, or contacting the authors) may be necessary."
                    )

                return {
                    "query": clean_query,
                    "mode": mode,
                    "total_results": len(final_results),
                    "results": final_results,
                    "paywalled_original": paywalled_original,
                    "no_alternative_found": no_alternative_found
                }

        # If paper is open-access: surface it first with is_exact_match=True and relevance_score=1.0
        if target_paper and target_paper.get("is_open_access"):
            assess_paper_difficulty(target_paper)
            target_paper["is_exact_match"] = True
            target_paper["is_paywall_fallback"] = False
            target_paper["relevance_score"] = 1.0
            target_paper["why_recommended"] = f"Exact match for '{clean_query}'; Free PDF available."

            other_candidates = [c for c in (candidates or []) if c.get("id") != target_paper.get("id")]
            if other_candidates:
                seed_text = f"{target_paper.get('title')}. {target_paper.get('abstract')}".strip()
                calculate_semantic_relevance(seed_text, other_candidates)
                verify_papers_accessibility_batch(other_candidates)
                for p in other_candidates:
                    assess_paper_difficulty(p)
                    p["is_paywall_fallback"] = False
                    p["is_exact_match"] = False
                    p["why_recommended"] = generate_recommendation_reason(p, is_fallback=False)
                other_candidates.sort(key=composite_score, reverse=True)

            final_results = [target_paper] + other_candidates[: limit - 1]
            return {
                "query": clean_query,
                "mode": mode,
                "total_results": len(final_results),
                "results": final_results,
                "paywalled_original": None,
                "no_alternative_found": False,
            }

        candidates_to_rank = candidates if candidates else [target_paper] if target_paper else []
    else:
        # Mode: Topic Query
        candidates_to_rank = retrieve_papers_by_topic(clean_query, limit=limit)

    if not candidates_to_rank:
        return {
            "query": clean_query,
            "mode": mode,
            "total_results": 0,
            "results": [],
            "paywalled_original": None,
            "no_alternative_found": False,
        }

    # Step 3: Semantic topic matching & Cosine Similarity
    calculate_semantic_relevance(clean_query, candidates_to_rank)

    # Step 4: Open Access Verification (Parallel Batch)
    verify_papers_accessibility_batch(candidates_to_rank)

    # Step 5: Readability & Difficulty Assessment
    for paper in candidates_to_rank:
        assess_paper_difficulty(paper)
        paper["is_paywall_fallback"] = False
        paper["why_recommended"] = generate_recommendation_reason(paper, is_fallback=False)

    # Step 6: Composite multi-signal ranking
    candidates_to_rank.sort(key=composite_score, reverse=True)
    final_results = candidates_to_rank[:limit]

    return {
        "query": clean_query,
        "mode": mode,
        "total_results": len(final_results),
        "results": final_results,
        "paywalled_original": None,
        "no_alternative_found": False
    }
