"""
PaperBridge AI - Module 3: Open-Access Discovery & Paywall Fallback Logic
(Track B - Access & Difficulty Modules)

Reasoning & Academic Ethics:
- PaperBridge AI strictly respects copyright and academic publisher terms.
  It NEVER accesses unauthorized mirrors (e.g. Sci-Hub) or attempts paywall circumvention.
- Instead, it checks legitimate open-access archives:
    1. Pass 1: Semantic Scholar's native `isOpenAccess` and `openAccessPdf` data.
    2. Pass 2: Unpaywall API (the gold standard for legitimate green/gold OA lookup via DOI).
- Paywall Fallback:
  If a user searches for a specific paper and it is behind a paywall, rather than
  returning a useless dead-end, PaperBridge AI extracts the abstract and semantics
  of the paywalled paper, filters candidate papers for VERIFIED open-access availability,
  and returns the closest freely accessible research alternatives.
"""

import logging
import requests
from backend.config import Config

logger = logging.getLogger(__name__)

# Fast in-memory cache to prevent duplicate external lookups
_DOI_OA_CACHE = {}

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
            # Ensure protocol is secure https
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

    return False, None, None

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

def filter_open_access_alternatives(candidate_papers, exclude_id=None):
    """
    Filters a list of candidate papers to keep only those with verified open-access copies.
    Optionally excludes a target paywalled paper id.
    """
    if not candidate_papers:
        return []

    verify_papers_accessibility_batch(candidate_papers)

    oa_alternatives = []
    for p in candidate_papers:
        if exclude_id and p.get("id") == exclude_id:
            continue
        if p.get("is_open_access"):
            oa_alternatives.append(p)

    return oa_alternatives
