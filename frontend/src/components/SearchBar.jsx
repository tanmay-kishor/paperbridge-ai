import React from 'react';
import { Search, BookOpen, Hash, ArrowRight } from 'lucide-react';

export default function SearchBar({
  query,
  setQuery,
  mode,
  setMode,
  onSearch,
  loading,
  sampleQueries = []
}) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSearch(query.trim(), mode);
    }
  };

  const handleSelectSample = (sample) => {
    setQuery(sample.query);
    setMode(sample.mode || 'topic');
    onSearch(sample.query, sample.mode || 'topic');
  };

  return (
    <div className="search-card">
      <div className="mode-toggle-group">
        <button
          type="button"
          className={`mode-btn ${mode === 'topic' ? 'active' : ''}`}
          onClick={() => setMode('topic')}
        >
          <BookOpen size={16} />
          <span>By Research Topic</span>
        </button>
        <button
          type="button"
          className={`mode-btn ${mode === 'paper' ? 'active' : ''}`}
          onClick={() => setMode('paper')}
        >
          <Hash size={16} />
          <span>By Paper Title / DOI</span>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="search-input-wrapper">
        <input
          type="text"
          className="search-input-field"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={
            mode === 'topic'
              ? 'e.g. transformer models for time series, quantum key distribution...'
              : 'e.g. Attention Is All You Need or 10.1145/3318464.3389700...'
          }
          disabled={loading}
          autoFocus
        />
        <button
          type="submit"
          className="search-submit-btn"
          disabled={loading || !query.trim()}
        >
          {loading ? (
            <span>Analyzing...</span>
          ) : (
            <>
              <Search size={18} />
              <span>Discover Papers</span>
            </>
          )}
        </button>
      </form>

      {sampleQueries.length > 0 && (
        <div className="sample-chips-wrap">
          <span>Benchmark Quick-Test:</span>
          {sampleQueries.map((item, idx) => (
            <button
              key={idx}
              type="button"
              className="sample-chip"
              onClick={() => handleSelectSample(item)}
            >
              {item.query.length > 34 ? `${item.query.substring(0, 34)}...` : item.query}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
