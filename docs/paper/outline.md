# Research Paper Outline: PaperBridge AI

**Title:** PaperBridge AI: Semantic Discovery, Legitimate Open-Access Retrieval, and Cognitive Difficulty Estimation for Academic Literature

## 1. Introduction
- Background: Academic paper discovery explosion, limitations of keyword-based search (Google Scholar, PubMed).
- The "Three Bridges" problem:
  1. Semantic gap (synonyms vs exact keyword hits).
  2. The paywall dead-end (finding a relevant paper only to hit a $40 paywall).
  3. The cognitive difficulty barrier (junior students stumbling upon hyper-dense theoretical papers).
- Research Questions & Core Contributions.

## 2. Related Work
- Academic search engines: Semantic Scholar, Connected Papers, Google Scholar.
- Open-access aggregators: Unpaywall, CORE, arXiv.
- Text readability and academic complexity assessment in NLP.

## 3. System Methodology & Architecture
- Data Acquisition & Normalization: Semantic Scholar API.
- Dense Semantic Vectorization: Sentence Transformers (`all-MiniLM-L6-v2`) and Cosine Similarity.
- Dual-Pass Open-Access Verification and Paywall Fallback Logic.
- Complexity Analysis: Flesch-Kincaid Grade Level + Jargon Density metric.
- Composite Multi-Signal Recommendation Ranker.

## 4. Experimental Evaluation & Validation
- Evaluation across 10 diverse computer science and scientific queries.
- Comparative analysis: Keyword search vs Dense semantic similarity.
- Accuracy of Open-Access detection against Unpaywall ground truth.
- Qualitative assessment of difficulty bucketing (Foundational vs Intermediate vs Advanced).

## 5. Security & Robustness Considerations
- Input sanitization, SSRF prevention, and ethical open-access compliance.

## 6. Limitations and Future Work
- Cold start on brand-new papers; reliance on abstract rather than full-text PDF parsing.

## 7. Conclusion
