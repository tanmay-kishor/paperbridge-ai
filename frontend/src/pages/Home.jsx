import React, { useState, useEffect } from 'react';
import SearchBar from '../components/SearchBar.jsx';
import ResultsList from '../components/ResultsList.jsx';
import { searchPapers, checkBackendHealth, getSampleQueries } from '../api/client.js';
import { Sparkles, GraduationCap, AlertCircle, Info } from 'lucide-react';

export default function Home() {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState('topic');
  const [results, setResults] = useState(null);
  const [paywalledOriginal, setPaywalledOriginal] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState({ connected: false, checking: true });
  const [sampleQueries, setSampleQueries] = useState([]);
  const [fallbackNotice, setFallbackNotice] = useState(null);

  // Check backend health & load sample queries on startup
  useEffect(() => {
    async function init() {
      const health = await checkBackendHealth();
      setBackendStatus({ connected: health.connected, checking: false });

      const samples = await getSampleQueries();
      if (samples && samples.queries) {
        setSampleQueries(samples.queries);
      }
    }
    init();
  }, []);

  const handleSearch = async (searchQuery, searchMode) => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);
    setFallbackNotice(null);

    const res = await searchPapers(searchQuery, searchMode);

    if (res.success && res.data) {
      setResults(res.data.results || []);
      setPaywalledOriginal(res.data.paywalled_original || null);
      if (res.fallbackNotice) {
        setFallbackNotice(res.fallbackNotice);
      }
    } else {
      setError(res.error || 'Failed to retrieve papers. Please try again.');
      setResults([]);
      setPaywalledOriginal(null);
    }
    setLoading(false);
  };

  const handleFindAlternatives = (paper) => {
    // Uses the paper's DOI if available, otherwise exact Title
    const targetQuery = paper.doi || paper.title;
    setQuery(targetQuery);
    setMode('paper');
    handleSearch(targetQuery, 'paper');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="app-container">
      {/* Navbar with Connection Indicator */}
      <header className="navbar">
        <div className="nav-inner">
          <a href="/" className="brand-logo">
            <div className="brand-icon-wrap">
              <GraduationCap size={20} />
            </div>
            <span>PaperBridge AI</span>
          </a>

          <div
            className={`connection-pill ${backendStatus.connected ? 'connected' : ''}`}
            title={backendStatus.connected ? 'Connected to Flask Backend API' : 'Backend is not running; operating in Vercel Demo Mode'}
          >
            <span className="connection-dot" />
            <span>
              {backendStatus.checking
                ? 'Checking API...'
                : backendStatus.connected
                ? 'Backend Live'
                : 'Preview / Demo Mode'}
            </span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="main-content">
        {/* Hero Section */}
        <section className="hero">
          <h1 className="hero-title">
            Bridge to <span className="gradient-text">Accessible</span> Academic Research
          </h1>
          <p className="hero-subtitle">
            Find semantically relevant papers, verify legitimate open-access versions,
            and assess cognitive difficulty before reading — all in one search.
          </p>
        </section>

        {/* Search Bar Component */}
        <SearchBar
          query={query}
          setQuery={setQuery}
          mode={mode}
          setMode={setMode}
          onSearch={handleSearch}
          loading={loading}
          sampleQueries={sampleQueries}
        />

        {/* Fallback Notice for Vercel Preview */}
        {fallbackNotice && (
          <div className="banner-notice info">
            <Info size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
            <span>{fallbackNotice}</span>
          </div>
        )}

        {/* Error Notification */}
        {error && (
          <div className="banner-notice paywall-alert">
            <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
            <span>{error}</span>
          </div>
        )}

        {/* Loading Spinner */}
        {loading && (
          <div className="state-box">
            <div className="spinner" />
            <p>Computing semantic embeddings, verifying open-access availability, and assessing readability...</p>
          </div>
        )}

        {/* Results Presentation */}
        {!loading && results && (
          <ResultsList
            results={results}
            paywalledOriginal={paywalledOriginal}
            query={query}
            mode={mode}
            onFindAlternatives={handleFindAlternatives}
          />
        )}

        {/* Initial Empty State Guide */}
        {!loading && !results && !error && (
          <div className="state-box">
            <Sparkles size={32} style={{ margin: '0 auto 0.75rem', color: '#3b82f6' }} />
            <h3 style={{ color: '#0f172a', marginBottom: '0.5rem', fontWeight: 700 }}>Ready to Explore Research Literature</h3>
            <p style={{ maxWidth: '500px', margin: '0 auto' }}>
              Select a benchmark test topic above or enter any research topic, paper title, or DOI to evaluate semantic matching, accessibility verification, and difficulty scoring.
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <div>PaperBridge AI Prototype — B.Tech 5th Sem Mini-Project | Powered by Semantic Scholar, Sentence Transformers & Unpaywall</div>
      </footer>
    </div>
  );
}
