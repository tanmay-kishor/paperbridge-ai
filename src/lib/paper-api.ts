/**
 * PaperBridge AI - API Client
 * Keeps Flask integration encapsulated behind this module.
 * Connects to the Flask backend via VITE_PAPERBRIDGE_API_URL and preserves
 * local demo data when unset (in accordance with project architecture rules).
 */

export const PAPERBRIDGE_ENDPOINTS = {
  search: "/api/search",
  health: "/api/health",
  samples: "/api/samples",
} as const;

export type SearchMode = "topic" | "paper";
export type DifficultyLevel = "Foundational" | "Intermediate" | "Advanced";

export type PaperSearchRequest = {
  query: string;
  mode?: SearchMode;
  limit?: number;
};

export type BackendDifficulty = {
  score: number;
  level: DifficultyLevel;
  jargon_density: number;
  is_jargon_dense: boolean;
  explanation?: string;
};

export type PaperResult = {
  id: string;
  title: string;
  authors: string[];
  year: number | null;
  venue?: string;
  abstract: string;
  doi?: string | null;
  arxiv_id?: string | null;
  citation_count: number;
  is_open_access: boolean;
  oa_url?: string | null;
  oa_source?: string | null;
  fields_of_study?: string[];
  reference_ids?: string[];
  relevance_score: number;
  difficulty?: BackendDifficulty;
  why_recommended?: string;
  is_paywall_fallback?: boolean;
  is_exact_match?: boolean;
  relationship_type?: "related_work" | string;
  match_confidence?: "Strong match" | "Moderate match" | "Weak match" | string;
  same_author_match?: boolean;
  bibliographic_overlap?: number;
};

export type PaywalledOriginal = {
  title: string;
  doi?: string | null;
  venue?: string | null;
  note?: string;
};

export type PaperSearchResponse = {
  query: string;
  mode: SearchMode;
  total_results: number;
  results: PaperResult[];
  paywalled_original?: PaywalledOriginal | null;
  no_alternative_found?: boolean;
};

export const LOCAL_DEMO_PAPERS: PaperResult[] = [
  {
    id: "demo-specter-2020",
    title: "SPECTER: Document-level Representation Learning using Citation-informed Transformers",
    authors: ["Arman Cohan", "Sergey Feldman", "Iz Beltagy", "Doug Downey", "Daniel S. Weld"],
    year: 2020,
    venue: "ACL 2020",
    doi: "10.18653/v1/2020.acl-main.207",
    arxiv_id: "2004.07180",
    citation_count: 1842,
    abstract:
      "A citation-informed transformer model for learning scientific document representations that transfer across scholarly tasks.",
    relevance_score: 0.97,
    difficulty: {
      score: 10.2,
      level: "Intermediate",
      jargon_density: 0.05,
      is_jargon_dense: false,
      explanation: "Intermediate reading level with balanced scholarly vocabulary.",
    },
    is_open_access: true,
    oa_url: "https://arxiv.org/pdf/2004.07180.pdf",
    oa_source: "arXiv (Open Access)",
    why_recommended:
      "97% semantic match; Intermediate difficulty; Free PDF. Highly cited (1,842 citations).",
  },
  {
    id: "demo-survey-2023",
    title: "A Survey on Deep Learning for Scientific Discovery",
    authors: ["J. Wang", "Y. Zhang", "H. Chen", "M. Rostova", "K. Tanaka"],
    year: 2023,
    venue: "ACM Computing Surveys",
    doi: "10.1145/3571730",
    citation_count: 520,
    abstract:
      "A broad review of deep learning methods used across scientific domains, from representation learning to knowledge discovery.",
    relevance_score: 0.89,
    difficulty: {
      score: 7.1,
      level: "Foundational",
      jargon_density: 0.03,
      is_jargon_dense: false,
      explanation: "Accessible foundational overview suitable for introductory research.",
    },
    is_open_access: true,
    oa_url: "https://arxiv.org/pdf/2301.00002.pdf",
    oa_source: "arXiv (Open Access)",
    is_paywall_fallback: true,
    relationship_type: "related_work",
    match_confidence: "Strong match",
    same_author_match: true,
    bibliographic_overlap: 5,
    why_recommended:
      "Open-Access Alternative (89% semantic match to paywalled paper); Foundational level; Free PDF available.",
  },
  {
    id: "demo-citation-networks-2011",
    title: "Citation Networks and the Semantic Structure of Science",
    authors: ["M. Rosvall", "C. T. Bergstrom"],
    year: 2011,
    venue: "PLOS ONE",
    doi: "10.1371/journal.pone.0018227",
    citation_count: 850,
    abstract:
      "A network-based view of how citation paths reveal the organization and evolution of scientific fields.",
    relevance_score: 0.81,
    difficulty: {
      score: 13.8,
      level: "Advanced",
      jargon_density: 0.08,
      is_jargon_dense: true,
      explanation: "Advanced network analysis requiring familiarity with information theory.",
    },
    is_open_access: false,
    oa_url: null,
    oa_source: null,
    why_recommended:
      "81% semantic match; Advanced difficulty; Paywalled. Highly cited (850 citations).",
  },
];

export function getLocalDemoResponse(payload: PaperSearchRequest): PaperSearchResponse {
  const query = payload.query.toLowerCase().trim();
  const filtered = LOCAL_DEMO_PAPERS.filter((p) => {
    if (!query) return true;
    return (
      p.title.toLowerCase().includes(query) ||
      p.abstract.toLowerCase().includes(query) ||
      p.authors.some((a) => a.toLowerCase().includes(query))
    );
  });

  return {
    query: payload.query,
    mode: payload.mode || "topic",
    total_results: filtered.length,
    results: filtered,
    paywalled_original: null,
    no_alternative_found: false,
  };
}

export async function searchPapers(payload: PaperSearchRequest): Promise<PaperSearchResponse> {
  const apiBase = import.meta.env["VITE_PAPERBRIDGE_API_URL"];

  // Rule: preserve local demo data when VITE_PAPERBRIDGE_API_URL is unset
  if (!apiBase) {
    return getLocalDemoResponse(payload);
  }

  const response = await fetch(`${apiBase}${PAPERBRIDGE_ENDPOINTS.search}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: payload.query,
      mode: payload.mode || "topic",
      limit: payload.limit ?? 10,
    }),
  });

  if (!response.ok) {
    let msg = "Paper search is temporarily unavailable.";
    try {
      const err = await response.json();
      if (err?.error) msg = err.error;
    } catch {
      // ignore json parse error
    }
    throw new Error(msg);
  }

  return response.json() as Promise<PaperSearchResponse>;
}
