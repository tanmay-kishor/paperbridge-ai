# System Architecture & Data Contract (`docs/architecture.md`)

## 1. High-Level Architecture

PaperBridge AI follows a modular, layered service-oriented architecture:

```
+-------------------------------------------------------------+
|                   React Frontend (Vite)                     |
|  - SearchBar (Topic vs Title/DOI switch, quick chips)       |
|  - ResultsList & ResultCard (NN/g scannable visual triage)   |
|  - Vercel-ready API Client with offline benchmark fallback  |
+------------------------------+------------------------------+
                               | REST JSON (CORS)
+------------------------------v------------------------------+
|                    Flask Python Backend                     |
|  - api/routes.py: /api/search, /api/health                  |
|  - config.py: Configuration, cache settings, API keys       |
+------------------------------+------------------------------+
                               |
+------------------------------v------------------------------+
|                   Pipeline Orchestration                    |
|  +--------------------------------------------------------+ |
|  | 1. Metadata Retrieval (pipeline/metadata.py)           | |
|  |    - Semantic Scholar API query / DOI lookup           | |
|  |    - Metadata normalization & offline cache fallback   | |
|  +---------------------------+----------------------------+ |
|                              v                              |
|  +--------------------------------------------------------+ |
|  | 2. Semantic Topic Matching (pipeline/embeddings.py)    | |
|  |    - SentenceTransformer ('all-MiniLM-L6-v2')          | |
|  |    - Cosine similarity computation via scikit-learn/np | |
|  +---------------------------+----------------------------+ |
|                              v                              |
|  +--------------------------------------------------------+ |
|  | 3. Open-Access & Paywall Fallback (pipeline/open_access| |
|  |    - Pass 1: Semantic Scholar isOpenAccess             | |
|  |    - Pass 2: Unpaywall DOI lookup                      | |
|  |    - If requested paper is paywalled:                  | |
|  |      Feed abstract -> Semantic search -> Filter OA     | |
|  +---------------------------+----------------------------+ |
|                              v                              |
|  +--------------------------------------------------------+ |
|  | 4. Complexity / Difficulty (pipeline/difficulty.py)    | |
|  |    - Flesch-Kincaid Grade Level (textstat)             | |
|  |    - Jargon density (domain vocab & syllable ratio)    | |
|  |    - Classification: Foundational/Intermediate/Advanced| |
|  +---------------------------+----------------------------+ |
|                              v                              |
|  +--------------------------------------------------------+ |
|  | 5. Recommendation Ranker (pipeline/ranker.py)          | |
|  |    - Multi-signal composite scoring & explainability   | |
|  +--------------------------------------------------------+ |
+-------------------------------------------------------------+
```

---

## 2. API Contract Specification

### `GET /api/health`
**Response:**
```json
{
  "status": "healthy",
  "service": "PaperBridge AI",
  "version": "1.0.0"
}
```

### `POST /api/search`
**Request Body:**
```json
{
  "query": "transformer models for time series",
  "mode": "topic", // "topic" | "paper"
  "limit": 10
}
```

**Response Body:**
```json
{
  "query": "transformer models for time series",
  "mode": "topic",
  "total_results": 5,
  "results": [
    {
      "id": "s2_paper_12345",
      "title": "Informer: Beyond Efficient Transformer for Long Sequence Time-Series Forecasting",
      "authors": ["Haoyi Zhou", "Shanghang Zhang", "Jieqi Peng"],
      "year": 2021,
      "venue": "AAAI",
      "abstract": "Many real-world applications require the prediction of long sequence time-series...",
      "doi": "10.1609/aaai.v35i12.17325",
      "citation_count": 2450,
      "relevance_score": 0.91,
      "is_open_access": true,
      "oa_url": "https://arxiv.org/pdf/2012.07436.pdf",
      "oa_source": "Unpaywall (Green OA / arXiv)",
      "difficulty": {
        "level": "Intermediate",
        "fk_grade": 12.4,
        "jargon_density": 0.18,
        "summary": "Standard academic presentation with moderate technical terminology."
      },
      "is_paywall_fallback": false,
      "why_recommended": "High semantic similarity (91%) to time-series transformers; fully accessible open-access PDF."
    }
  ],
  "paywalled_original": null
}
```
