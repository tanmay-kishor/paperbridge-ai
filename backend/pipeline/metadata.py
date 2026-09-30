"""
PaperBridge AI - Module 1: Academic Paper Metadata Retrieval & Normalization
(Track A - Core AI Pipeline)

Reasoning for Semantic Scholar API:
- Semantic Scholar indexes over 200M academic papers across all disciplines.
- A single request retrieves title, abstract, authors, publication venue, year,
  citation count, external IDs (DOI, ArXiv), and initial open-access flags.
- This avoids multiple separate API calls and provides standard metadata structure.

Security & Resilience:
- Sanitizes query strings and validates DOIs.
- Applies strict timeouts (8 seconds) to prevent hanging requests.
- Implements an automatic local fallback to `data/test_papers.json` if the external
  API returns HTTP 429 (Rate Limit), connection errors, or empty results.
"""

import json
import logging
import os
import re
import requests
from backend.config import Config

logger = logging.getLogger(__name__)

# Standard fields requested from Semantic Scholar Graph API
# fieldsOfStudy + externalIds.DOI support the credibility/threshold filter used by the
# paywall-fallback logic (see open_access.py). references.paperId is used for
# bibliographic-overlap scoring (see open_access.py:_bibliographic_overlap) -- a
# depth-relatedness proxy stronger than topic similarity alone: two papers that cite
# a lot of the same prior work are more likely addressing the same specific
# sub-problem at a comparable depth, not just using similar words.
S2_FIELDS = (
    "paperId,title,abstract,authors,year,venue,citationCount,isOpenAccess,"
    "openAccessPdf,externalIds,fieldsOfStudy,references.paperId"
)

def normalize_paper(raw_paper):
    """
    Normalizes raw paper metadata from Semantic Scholar (or offline cache)
    into a standardized dictionary schema for downstream pipeline modules.
    
    Fields guaranteed:
      - id (str)
      - title (str)
      - authors (list of str)
      - year (int or None)
      - venue (str)
      - abstract (str)
      - doi (str or None)
      - citation_count (int)
      - is_open_access (bool)
      - oa_url (str or None)
      - oa_source (str or None)
    """
    if not isinstance(raw_paper, dict):
        return None

    paper_id = raw_paper.get("paperId") or raw_paper.get("id") or "unknown_id"
    title = (raw_paper.get("title") or "Untitled Paper").strip()
    abstract = (raw_paper.get("abstract") or "").strip()

    # Normalize author names
    raw_authors = raw_paper.get("authors") or []
    authors = []
    for a in raw_authors:
        if isinstance(a, dict):
            name = a.get("name")
            if name:
                authors.append(name.strip())
        elif isinstance(a, str):
            authors.append(a.strip())
    if not authors:
        authors = ["Unknown Author"]

    # Year & Venue
    year = raw_paper.get("year")
    try:
        year = int(year) if year else None
    except (ValueError, TypeError):
        year = None

    venue = (raw_paper.get("venue") or "").strip()

    # External Identifiers (DOI / ArXiv)
    external_ids = raw_paper.get("externalIds") or {}
    doi = external_ids.get("DOI") or raw_paper.get("doi") or None
    arxiv_id = external_ids.get("ArXiv") or raw_paper.get("arxiv_id") or None

    # Citation Count
    try:
        citation_count = int(raw_paper.get("citationCount") or raw_paper.get("citation_count") or 0)
    except (ValueError, TypeError):
        citation_count = 0

    # Initial Open Access Flag (from Semantic Scholar)
    is_open_access = bool(raw_paper.get("isOpenAccess") or raw_paper.get("is_open_access") or False)
    oa_pdf = raw_paper.get("openAccessPdf") or {}
    oa_url = oa_pdf.get("url") if isinstance(oa_pdf, dict) else (raw_paper.get("oa_url") or None)
    
    # If ArXiv ID exists and no direct PDF URL was provided, construct legitimate arXiv PDF URL
    if not oa_url and arxiv_id:
        oa_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        is_open_access = True

    oa_source = raw_paper.get("oa_source") or ("Semantic Scholar OA" if is_open_access else None)

    # Fields of study (used as a hard filter for the paywall-fallback credibility check)
    fields_of_study = raw_paper.get("fieldsOfStudy") or raw_paper.get("fields_of_study") or []
    if not isinstance(fields_of_study, list):
        fields_of_study = []

    # Reference paper IDs (used for bibliographic-overlap scoring in open_access.py).
    # Semantic Scholar returns a list of {"paperId": ...} dicts under "references".
    raw_refs = raw_paper.get("references") or []
    reference_ids = [r.get("paperId") for r in raw_refs if isinstance(r, dict) and r.get("paperId")]

    return {
        "id": paper_id,
        "title": title,
        "authors": authors,
        "year": year,
        "venue": venue,
        "abstract": abstract,
        "doi": doi,
        "arxiv_id": arxiv_id,
        "citation_count": citation_count,
        "is_open_access": is_open_access,
        "oa_url": oa_url,
        "oa_source": oa_source,
        "fields_of_study": fields_of_study,
        "reference_ids": reference_ids
    }

def get_offline_sample_papers():
    """
    Loads offline candidate papers from `data/test_papers.json` for testing
    or graceful offline degradation.
    """
    try:
        if os.path.exists(Config.SAMPLE_PAPERS_PATH):
            with open(Config.SAMPLE_PAPERS_PATH, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
            return [normalize_paper(p) for p in raw_list if p]
    except Exception as e:
        logger.warning(f"Unable to read sample papers fallback: {e}")
    return []

def retrieve_papers_from_arxiv(topic_query, limit=10):
    """
    Queries the arXiv API for live academic research papers.
    Serves as an immediate, live fallback whenever Semantic Scholar returns HTTP 429
    (common on shared cloud hosting IP addresses).
    """
    import xml.etree.ElementTree as ET
    import urllib.parse

    clean_query = urllib.parse.quote_plus(topic_query.strip())
    url = f"https://export.arxiv.org/api/query?search_query=all:{clean_query}&start=0&max_results={limit}"

    try:
        logger.info(f"Querying arXiv API for: '{topic_query}'")
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200:
            root = ET.fromstring(resp.text)
            ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
            entries = root.findall("atom:entry", ns)
            papers = []
            for e in entries:
                title_elem = e.find("atom:title", ns)
                title = title_elem.text.strip().replace("\n", " ") if title_elem is not None else ""
                
                # Check for empty or error arXiv response entry
                if not title or title == "Error":
                    continue
                    
                summary_elem = e.find("atom:summary", ns)
                abstract = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None else ""
                
                id_elem = e.find("atom:id", ns)
                raw_id = id_elem.text.strip() if id_elem is not None else ""
                arxiv_id = raw_id.split("/abs/")[-1] if "/abs/" in raw_id else raw_id
                
                # Extract authors
                authors = []
                for a in e.findall("atom:author", ns):
                    name_elem = a.find("atom:name", ns)
                    if name_elem is not None and name_elem.text:
                        authors.append(name_elem.text.strip())
                if not authors:
                    authors = ["Unknown Author"]
                
                # Extract year
                published_elem = e.find("atom:published", ns)
                year = None
                if published_elem is not None and published_elem.text:
                    try:
                        year = int(published_elem.text[:4])
                    except (ValueError, TypeError):
                        year = None
                
                # Direct PDF URL
                oa_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else None
                
                doi_elem = e.find("arxiv:doi", ns)
                doi = doi_elem.text.strip() if doi_elem is not None else None
                
                papers.append({
                    "id": f"arxiv_{arxiv_id}",
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "venue": "arXiv",
                    "abstract": abstract,
                    "doi": doi,
                    "arxiv_id": arxiv_id,
                    "citation_count": 0,
                    "is_open_access": True,
                    "oa_url": oa_url,
                    "oa_source": "arXiv (Open Access)"
                })
            if papers:
                logger.info(f"Retrieved {len(papers)} live papers from arXiv API.")
                return papers
    except Exception as e:
        logger.warning(f"Error querying arXiv API: {e}")

def normalize_openalex_work(w):
    """
    Normalizes a single work record from OpenAlex into the standard PaperBridge paper dict.
    """
    if not w or not isinstance(w, dict):
        return None

    title = (w.get("title") or "").strip()
    if not title:
        return None

    # Reconstruct abstract from OpenAlex abstract_inverted_index if available
    abstract = ""
    inv_index = w.get("abstract_inverted_index")
    if isinstance(inv_index, dict) and inv_index:
        try:
            pos_words = sorted([(pos, word) for word, positions in inv_index.items() for pos in positions])
            abstract = " ".join([pw[1] for pw in pos_words]).strip()
        except Exception:
            abstract = ""

    # Authors
    authors = []
    for a in w.get("authorships", []):
        author_obj = a.get("author") or {}
        name = author_obj.get("display_name")
        if name:
            authors.append(name)
    if not authors:
        authors = ["Academic Researcher"]

    # Venue / Source
    primary_loc = w.get("primary_location") or {}
    source_obj = primary_loc.get("source") or {}
    venue = source_obj.get("display_name") or "Scholarly Publication"

    # DOI
    raw_doi = w.get("doi") or ""
    doi = raw_doi.replace("https://doi.org/", "").replace("http://doi.org/", "") or None

    # Open Access Information
    oa_info = w.get("open_access") or {}
    is_oa = bool(oa_info.get("is_oa", False))
    oa_url = oa_info.get("oa_url") or primary_loc.get("pdf_url") or primary_loc.get("landing_page_url")
    oa_status = (oa_info.get("oa_status") or "open").capitalize()
    oa_source = f"OpenAlex ({oa_status} OA)" if is_oa else None

    # Fields of study / concepts
    concepts = [c.get("display_name") for c in w.get("concepts", []) if c.get("display_name")]

    # Referenced works
    ref_ids = [r.split("/")[-1] for r in w.get("referenced_works", [])[:10]]

    # Work ID
    raw_id = w.get("id") or ""
    openalex_id = raw_id.split("/")[-1] if "/" in raw_id else raw_id

    return {
        "id": f"openalex_{openalex_id}",
        "title": title,
        "authors": authors,
        "year": w.get("publication_year"),
        "venue": venue,
        "abstract": abstract if abstract else title,
        "doi": doi,
        "arxiv_id": None,
        "citation_count": w.get("cited_by_count", 0) or 0,
        "is_open_access": is_oa,
        "oa_url": oa_url if is_oa else None,
        "oa_source": oa_source,
        "fields_of_study": concepts[:5],
        "reference_ids": ref_ids
    }

def retrieve_papers_from_openalex(topic_query, limit=10):
    """
    Queries the OpenAlex API for live academic research papers.
    OpenAlex catalogs 250M+ scholarly works with integrated Unpaywall open-access status.
    Provides 100,000 free requests/day in the polite pool.
    """
    import urllib.parse
    clean_query = urllib.parse.quote_plus(topic_query.strip())
    url = f"{Config.OPENALEX_BASE_URL}/works?search={clean_query}&per_page={min(limit, 25)}"
    headers = {
        "User-Agent": f"PaperBridge/1.0 (mailto:{Config.OPENALEX_EMAIL})"
    }

    try:
        logger.info(f"Querying OpenAlex API for topic: '{topic_query}'")
        resp = requests.get(url, headers=headers, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            papers = [normalize_openalex_work(w) for w in results]
            valid_papers = [p for p in papers if p and p.get("title")]
            if valid_papers:
                logger.info(f"Retrieved {len(valid_papers)} live papers from OpenAlex API.")
                return valid_papers
    except Exception as e:
        logger.warning(f"Error querying OpenAlex API: {e}")

    return []

def retrieve_papers_by_topic(topic_query, limit=10):
    """
    Queries academic paper repositories by topic keywords.
    Strategy:
    1. Query Semantic Scholar Graph API.
    2. If Semantic Scholar returns 429 (rate-limited) or fails, query arXiv API for live papers.
    3. If external network is down, fall back to offline benchmark dataset.
    """
    headers = {}
    if Config.SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = Config.SEMANTIC_SCHOLAR_API_KEY

    url = f"{Config.S2_BASE_URL}/paper/search"
    params = {
        "query": topic_query,
        "limit": min(limit, Config.MAX_RESULT_LIMIT),
        "fields": S2_FIELDS
    }

    try:
        logger.info(f"Querying Semantic Scholar API for topic: '{topic_query}'")
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            raw_papers = data.get("data", [])
            normalized = [normalize_paper(p) for p in raw_papers if p and p.get("title")]
            if normalized:
                return normalized
        elif resp.status_code == 429:
            logger.warning("Semantic Scholar rate limit reached (HTTP 429). Falling back to OpenAlex & arXiv.")
        else:
            logger.warning(f"Semantic Scholar API returned HTTP {resp.status_code}: {resp.text[:120]}")
    except Exception as e:
        logger.warning(f"Network error querying Semantic Scholar API: {e}. Falling back to OpenAlex & arXiv.")

    # High-availability live fallback 1: OpenAlex API (250M+ works catalog)
    openalex_papers = retrieve_papers_from_openalex(topic_query, limit=limit)
    if openalex_papers:
        return openalex_papers

    # High-availability live fallback 2: arXiv API
    arxiv_papers = retrieve_papers_from_arxiv(topic_query, limit=limit)
    if arxiv_papers:
        return arxiv_papers

    # Resilient offline fallback: return filtered sample papers matching topic keywords or sample list
    samples = get_offline_sample_papers()
    keywords = [k.lower() for k in re.split(r"\s+", topic_query) if len(k) > 2]
    matched = []
    for p in samples:
        searchable_text = f"{p['title']} {p['abstract']}".lower()
        if any(kw in searchable_text for kw in keywords):
            matched.append(p)
    return matched if matched else ([] if keywords else samples[:limit])

def is_title_match(query_title: str, candidate_title: str) -> bool:
    """
    Determines if candidate_title is a legitimate match for query_title.
    Prevents unrelated search results from being claimed as exact title matches.
    """
    if not query_title or not candidate_title:
        return False
    q = re.sub(r"[^\w\s]", "", query_title.lower()).strip()
    c = re.sub(r"[^\w\s]", "", candidate_title.lower()).strip()
    if not q or not c:
        return False
    # Exact or substring match (ignoring punctuation and casing)
    if q == c or q in c or c in q:
        return True
    # Word overlap ratio for multi-word queries
    q_words = set(w for w in q.split() if len(w) > 2)
    c_words = set(w for w in c.split() if len(w) > 2)
    if not q_words:
        return False
    overlap = len(q_words & c_words) / len(q_words)
    return overlap >= 0.6

def retrieve_paper_by_identifier(query):
    """
    Retrieves a specific paper by DOI or exact Title from Semantic Scholar / OpenAlex.
    Returns (target_paper_dict, candidate_papers_list).
    If no matching paper is found, returns (None, []).
    """
    clean_query = query.strip()
    if not clean_query:
        return None, []
    
    # Check if query is formatted as DOI
    is_doi = clean_query.startswith("10.") or "doi.org/" in clean_query
    headers = {}
    if Config.SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = Config.SEMANTIC_SCHOLAR_API_KEY

    target_paper = None

    if is_doi:
        doi_val = clean_query.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
        url = f"{Config.S2_BASE_URL}/paper/DOI:{doi_val}"
        try:
            resp = requests.get(url, params={"fields": S2_FIELDS}, headers=headers, timeout=5)
            if resp.status_code == 200:
                target_paper = normalize_paper(resp.json())
        except Exception as e:
            logger.warning(f"Error fetching paper by DOI from S2: {e}")

        # If DOI was not resolved by Semantic Scholar, resolve via OpenAlex
        if not target_paper:
            try:
                oa_url = f"{Config.OPENALEX_BASE_URL}/works/https://doi.org/{doi_val}"
                oa_resp = requests.get(
                    oa_url,
                    headers={"User-Agent": f"PaperBridge/1.0 (mailto:{Config.OPENALEX_EMAIL})"},
                    timeout=5
                )
                if oa_resp.status_code == 200:
                    target_paper = normalize_openalex_work(oa_resp.json())
            except Exception as e:
                logger.warning(f"Error fetching paper by DOI from OpenAlex: {e}")

        # Offline fallback: check if DOI matches one of our benchmark sample papers
        if not target_paper:
            samples = get_offline_sample_papers()
            for p in samples:
                if p.get("doi") and (doi_val.lower() == p["doi"].lower() or doi_val.lower() in p["doi"].lower()):
                    target_paper = p
                    break

        # If not found after checking S2, OpenAlex, and benchmark DOIs, DO NOT force a fallback!
        if not target_paper:
            logger.info(f"No paper found for DOI '{clean_query}'.")
            return None, []

    else:
        # User entered a Paper Title to look up
        # 1. Search Semantic Scholar / OpenAlex / arXiv for candidates
        candidates = retrieve_papers_by_topic(clean_query, limit=5)
        for c in candidates:
            if is_title_match(clean_query, c.get("title", "")):
                target_paper = c
                break

        # 2. Check offline sample papers for a title match
        if not target_paper:
            samples = get_offline_sample_papers()
            for p in samples:
                if is_title_match(clean_query, p.get("title", "")):
                    target_paper = p
                    break

        # If no paper matched the requested title, return None and empty list
        if not target_paper:
            logger.info(f"No paper found matching title '{clean_query}'.")
            return None, []

    # Target paper was found! Retrieve related candidate papers on the same subject to power recommendations / fallbacks
    topic_keywords = target_paper.get("title") or clean_query
    related_candidates = retrieve_papers_by_topic(topic_keywords, limit=10)

    # Ensure target paper is in candidate list if not already present
    if target_paper:
        candidate_ids = {c["id"] for c in related_candidates}
        if target_paper["id"] not in candidate_ids:
            related_candidates.insert(0, target_paper)

    return target_paper, related_candidates

