import React from 'react';
import ResultCard from './ResultCard.jsx';
import { AlertTriangle, Info } from 'lucide-react';

export default function ResultsList({ results, paywalledOriginal, query, mode, onFindAlternatives }) {
  if (!results || results.length === 0) {
    return (
      <div className="state-box">
        <p>No research papers matched your search query. Try broadening your terms or using one of the benchmark topics above.</p>
      </div>
    );
  }

  return (
    <section>
      {/* Paywalled Paper Notice Banner */}
      {paywalledOriginal && (
        <div className="banner-notice paywall-alert">
          <AlertTriangle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong>Paywall Fallback Active:</strong> The queried publication{' '}
            <em>"{paywalledOriginal.title}"</em> (DOI: {paywalledOriginal.doi || 'N/A'}) is paywalled.
            PaperBridge AI has automatically surfaced the closest legitimate, open-access alternatives below based on semantic abstract similarity.
          </div>
        </div>
      )}

      {/* Results Meta Info */}
      <div className="results-meta-header">
        <div>
          Showing <span className="results-count">{results.length}</span> ranked publications for{' '}
          <em>"{query}"</em> ({mode === 'paper' ? 'Title/DOI mode' : 'Topic mode'})
        </div>
        <div>Ranked by Semantic Relevance</div>
      </div>

      {/* Cards List */}
      <div className="results-list">
        {results.map((paper, idx) => (
          <ResultCard
            key={paper.id || idx}
            paper={paper}
            rank={idx + 1}
            onFindAlternatives={onFindAlternatives}
          />
        ))}
      </div>
    </section>
  );
}
