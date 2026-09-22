/**
 * PaperBridge AI - Frontend API Client
 * Manages HTTP communication with the Flask backend.
 * 
 * Includes:
 * 1. Healthcheck polling to detect backend connection status.
 * 2. Search requests with timeout handling and error catching.
 * 3. Fallback demo mode for preview deployments (e.g., hosted on Vercel without a live backend).
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Check backend connectivity
 */
export async function checkBackendHealth() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);
    
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (response.ok) {
      const data = await response.json();
      return { connected: true, data };
    }
    return { connected: false, error: `HTTP ${response.status}` };
  } catch (err) {
    return { connected: false, error: err.name === 'AbortError' ? 'Connection timed out' : 'Backend unreachable' };
  }
}

/**
 * Execute search query against Flask backend
 * @param {string} query - The search text or DOI
 * @param {string} mode - 'topic' or 'paper'
 * @param {number} limit - Maximum results (default 10)
 */
export async function searchPapers(query, mode = 'topic', limit = 10) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ query: query.trim(), mode, limit })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Server responded with status ${response.status}`);
    }

    const data = await response.json();
    return { success: true, data, isFallback: false };
  } catch (err) {
    console.warn("Live API request failed, checking offline demo fallback:", err);

    // Fallback: If deployed on Vercel or live server is not connected,
    // provide realistic simulated demo responses for standard test queries
    const fallbackData = getOfflineDemoFallback(query, mode);
    if (fallbackData) {
      return {
        success: true,
        data: fallbackData,
        isFallback: true,
        fallbackNotice: "Preview Mode: Displaying benchmark demonstration data (Flask backend is offline or connecting)."
      };
    }

    return {
      success: false,
      error: err.message || "Failed to communicate with the PaperBridge API."
    };
  }
}

/**
 * Fetch sample benchmark queries
 */
export async function getSampleQueries() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/samples`);
    if (response.ok) {
      return await response.json();
    }
  } catch (err) {
    // Silent fail to fallback
  }

  // Built-in fallback samples
  return {
    queries: [
      {
        query: "transformer models for time series forecasting",
        mode: "topic",
        description: "Sequence models applied to temporal regression."
      },
      {
        query: "quantum key distribution protocols security",
        mode: "topic",
        description: "BB84, E91, and continuous-variable QKD protocols."
      },
      {
        query: "Attention Is All You Need",
        mode: "paper",
        description: "Landmark Transformer paper by Vaswani et al. (2017)."
      },
      {
        query: "10.1145/3318464.3389700",
        mode: "paper",
        description: "Paywalled SIGMOD paper (triggers open-access fallback)."
      }
    ]
  };
}

/**
 * Offline demo fallback dataset for Vercel preview or disconnected environments
 */
function getOfflineDemoFallback(query, mode) {
  const q = query.toLowerCase();

  if (q.includes("transformer") || q.includes("time series")) {
    return {
      query,
      mode,
      total_results: 2,
      results: [
        {
          id: "demo_informer",
          title: "Informer: Beyond Efficient Transformer for Long Sequence Time-Series Forecasting",
          authors: ["Haoyi Zhou", "Shanghang Zhang", "Jieqi Peng", "Shuai Zhang", "Jianxin Li"],
          year: 2021,
          venue: "AAAI",
          abstract: "Many real-world applications require the prediction of long sequence time-series, such as electricity consumption planning. Long sequence time-series forecasting (LSTF) demands a high prediction capacity. We design an efficient Transformer-based model for LSTF, named Informer, with ProbSparse self-attention.",
          doi: "10.1609/aaai.v35i12.17325",
          citation_count: 3100,
          relevance_score: 0.94,
          is_open_access: true,
          oa_url: "https://arxiv.org/pdf/2012.07436.pdf",
          oa_source: "Unpaywall / arXiv",
          difficulty: {
            level: "Intermediate",
            fk_grade: 12.8,
            jargon_density: 0.19,
            summary: "Standard technical conference paper with moderate architectural notation."
          },
          is_paywall_fallback: false,
          why_recommended: "Ranked #1 for time-series transformers; 94% semantic match; verified open-access preprint available."
        },
        {
          id: "demo_autoformer",
          title: "Autoformer: Decomposition Transformers with Auto-Correlation for Long-Term Series Forecasting",
          authors: ["Haixu Wu", "Jiehui Xu", "Jianmin Wang", "Mingsheng Long"],
          year: 2021,
          venue: "NeurIPS",
          abstract: "Extending the forecast horizon is a critical challenge. Existing models adopt self-attention to discover sub-series similarity, which is computationally prohibitive. We propose Autoformer with an Auto-Correlation mechanism.",
          doi: "10.48550/arXiv.2106.13008",
          citation_count: 1850,
          relevance_score: 0.89,
          is_open_access: true,
          oa_url: "https://arxiv.org/pdf/2106.13008.pdf",
          oa_source: "Unpaywall / arXiv",
          difficulty: {
            level: "Advanced",
            fk_grade: 14.5,
            jargon_density: 0.24,
            summary: "Theoretical decomposition and autocorrelation mathematical framing."
          },
          is_paywall_fallback: false,
          why_recommended: "High semantic similarity (89%); novel autocorrelation mechanism; free PDF."
        }
      ],
      paywalled_original: null
    };
  }

  if (q.includes("3318464.3389700") || q.includes("adaptive query")) {
    return {
      query,
      mode: "paper",
      total_results: 1,
      results: [
        {
          id: "demo_oa_alt",
          title: "OpenQuery: An Open Source Dynamic Query Engine for Heterogeneous Cloud Systems",
          authors: ["Sarah Lin", "Devin Miller"],
          year: 2021,
          venue: "VLDB Endowment",
          abstract: "Dynamic query optimization in heterogeneous cloud computing allows low latency joins across distributed database nodes. We evaluate OpenQuery, an accessible open-source framework matching commercial adaptive query engines, with complete replication scripts.",
          doi: "10.14778/3476249.3476251",
          citation_count: 89,
          relevance_score: 0.88,
          is_open_access: true,
          oa_url: "https://www.vldb.org/pvldb/vol14/p2100-lin.pdf",
          oa_source: "Unpaywall (Gold Open Access)",
          difficulty: {
            level: "Intermediate",
            fk_grade: 11.9,
            jargon_density: 0.16,
            summary: "Systems paper with accessible architecture diagrams and clear benchmarks."
          },
          is_paywall_fallback: true,
          why_recommended: "Closest open-access paper matching the paywalled paper's abstract (88% semantic similarity)."
        }
      ],
      paywalled_original: {
        title: "Adaptive Query Optimization in Distributed Cloud Databases",
        doi: "10.1145/3318464.3389700",
        venue: "ACM SIGMOD",
        note: "This paper is behind a publisher paywall. PaperBridge AI automatically retrieved the closest legitimate open-access alternatives below."
      }
    };
  }

  // Generic fallback for any other query in demo mode
  return {
    query,
    mode,
    total_results: 1,
    results: [
      {
        id: "demo_general",
        title: "Attention Is All You Need",
        authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit"],
        year: 2017,
        venue: "NeurIPS",
        abstract: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose the Transformer, based solely on attention mechanisms.",
        doi: "10.48550/arXiv.1706.03762",
        citation_count: 112000,
        relevance_score: 0.85,
        is_open_access: true,
        oa_url: "https://arxiv.org/pdf/1706.03762.pdf",
        oa_source: "arXiv (Green Open Access)",
        difficulty: {
          level: "Intermediate",
          fk_grade: 11.5,
          jargon_density: 0.15,
          summary: "Accessible foundational architecture paper."
        },
        is_paywall_fallback: false,
        why_recommended: "Benchmark demonstration result."
      }
    ],
    paywalled_original: null
  };
}
