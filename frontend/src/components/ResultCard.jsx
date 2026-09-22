import React from 'react';
import { Unlock, Lock, ExternalLink, Sparkles, BookOpen, Layers, AlertCircle } from 'lucide-react';

export default function ResultCard({ paper, rank, onFindAlternatives }) {
  // Sanitize external URLs to only allow legitimate https:// links
  const safeOaUrl = paper.oa_url && paper.oa_url.startsWith('https://') ? paper.oa_url : null;
  const doiUrl = paper.doi ? `https://doi.org/${encodeURIComponent(paper.doi)}` : null;

  // Formatting author string (truncate if > 4 authors)
  const authorNames = Array.isArray(paper.authors)
    ? paper.authors.map(a => (typeof a === 'string' ? a : a.name || 'Unknown'))
    : ['Academic Authors'];
  const authorsText = authorNames.length > 4
    ? `${authorNames.slice(0, 3).join(', ')} et al.`
    : authorNames.join(', ');

  // Readability & Difficulty badge classes
  const diffLevel = paper.difficulty?.level || 'Intermediate';
  let diffClass = 'badge-diff-intermediate';
  if (diffLevel.toLowerCase().includes('foundational')) {
    diffClass = 'badge-diff-foundational';
  } else if (diffLevel.toLowerCase().includes('advanced')) {
    diffClass = 'badge-diff-advanced';
  }

  // Relevance percentage
  const relevancePercent = paper.relevance_score
    ? Math.round(paper.relevance_score * 100)
    : 85;

  return (
    <article className="result-card">
      {/* Visual Triage Badges Bar */}
      <div className="card-badges-row">
        {/* Semantic Relevance Badge */}
        <span className="badge badge-relevance" title="Semantic cosine similarity match">
          <Sparkles size={13} />
          <span>{relevancePercent}% Match</span>
        </span>

        {/* Open Access Status Badge */}
        {paper.is_open_access ? (
          <span className="badge badge-oa" title={paper.oa_source || 'Verified Open Access'}>
            <Unlock size={13} />
            <span>Open Access</span>
          </span>
        ) : (
          <span className="badge badge-paywalled" title="Requires subscription or paywall payment">
            <Lock size={13} />
            <span>Paywalled</span>
          </span>
        )}

        {/* Reading Difficulty Badge */}
        <span className={`badge ${diffClass}`} title={`Flesch-Kincaid Grade: ${paper.difficulty?.fk_grade || 'N/A'}`}>
          <Layers size={13} />
          <span>{diffLevel}</span>
        </span>

        {/* Paywall Fallback Indicator Badge */}
        {paper.is_paywall_fallback && (
          <span className="badge badge-fallback" title="Recommended because original queried paper was paywalled">
            <AlertCircle size={13} />
            <span>Open-Access Alternative</span>
          </span>
        )}
      </div>

      {/* Paper Title */}
      <h2 className="card-title">
        {rank}. {paper.title}
      </h2>

      {/* Paper Metadata */}
      <div className="card-metadata">
        <span>{authorsText}</span>
        {paper.year && (
          <>
            <span className="separator">•</span>
            <span>{paper.year}</span>
          </>
        )}
        {paper.venue && (
          <>
            <span className="separator">•</span>
            <span>{paper.venue}</span>
          </>
        )}
        {paper.citation_count !== undefined && paper.citation_count !== null && (
          <>
            <span className="separator">•</span>
            <span>{paper.citation_count.toLocaleString()} citations</span>
          </>
        )}
      </div>

      {/* Abstract */}
      <p className="card-abstract">
        {paper.abstract || 'No abstract preview available for this publication.'}
      </p>

      {/* Why Recommended / Explainability Box */}
      {paper.why_recommended && (
        <div className="card-why-box">
          <span className="card-why-title">Why recommended:</span>
          <span>{paper.why_recommended}</span>
        </div>
      )}

      {/* Actions & Links */}
      <div className="card-actions-row">
        <div>
          {safeOaUrl ? (
            <a
              href={safeOaUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="action-btn-link"
            >
              <Unlock size={14} />
              <span>Read Free PDF ({paper.oa_source || 'Open Access'})</span>
              <ExternalLink size={13} />
            </a>
          ) : !paper.is_paywall_fallback ? (
            <button
              type="button"
              className="action-btn-fallback"
              onClick={() => onFindAlternatives && onFindAlternatives(paper)}
              title="Run semantic paywall fallback to find freely accessible alternatives on this topic"
            >
              <Sparkles size={14} />
              <span>Find Free Alternatives</span>
            </button>
          ) : (
            <span className="doi-text" style={{ color: '#b45309' }}>
              Open-access alternative recommendation
            </span>
          )}
        </div>

        {doiUrl && (
          <a
            href={doiUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="doi-text"
            style={{ textDecoration: 'none' }}
            title={paper.is_open_access ? "Official DOI citation link" : "Official publisher page (requires subscription)"}
          >
            {paper.is_open_access ? "DOI: " : "Publisher (Paywalled): "} {paper.doi} ↗
          </a>
        )}
      </div>
    </article>
  );
}
