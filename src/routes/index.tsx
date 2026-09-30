import { createFileRoute } from "@tanstack/react-router";
import {
  ArrowUpRight,
  BookMarked,
  ChevronDown,
  FileSearch,
  Filter,
  History,
  Home,
  Moon,
  RotateCcw,
  Search,
  SlidersHorizontal,
  Sparkles,
  Sun,
} from "lucide-react";
import { useCallback, useEffect, useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import {
  searchPapers,
  getApiBaseUrl,
  type PaperResult,
  type PaperSearchResponse,
  type SearchMode,
} from "@/lib/paper-api";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "PaperBridge AI — Find research you can read" },
      {
        name: "description",
        content:
          "Discover relevant, legitimate open-access research papers matched to your reading level.",
      },
      { property: "og:title", content: "PaperBridge AI — Find research you can read" },
      {
        property: "og:description",
        content:
          "Semantic paper discovery, open-access checks, and clear reading difficulty in one research desk.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

const navItems = [
  { label: "Discover", icon: Home },
  { label: "Paper lookup", icon: FileSearch },
  { label: "Reading list", icon: BookMarked },
  { label: "Recent trails", icon: History },
];

function Mascot({
  compact = false,
  nocturnal = false,
}: {
  compact?: boolean;
  nocturnal?: boolean;
}) {
  return (
    <div
      className={`${compact ? "mascot mascot-compact" : "mascot"} ${
        nocturnal ? "mascot-owl" : "mascot-crow"
      }`}
      aria-label={
        nocturnal ? "Pico, the PaperBridge night owl" : "Pico, the PaperBridge research crow"
      }
    >
      {nocturnal ? (
        <svg viewBox="0 0 120 110" role="img" aria-hidden="true">
          <path className="owl-wing-left" d="M39 57C19 60 17 83 39 91c8 3 14-5 15-17" />
          <path className="owl-wing-right" d="M80 57c20 3 22 26 0 34-8 3-14-5-15-17" />
          <path
            className="owl-body"
            d="M35 39 26 21l22 10c8-5 17-5 25 0l21-10-8 19c8 15 6 42-9 52-12 8-32 7-43-6-10-13-8-34 1-47Z"
          />
          <path
            className="owl-face"
            d="M37 46c4-13 19-15 24-4 6-12 21-9 23 4 2 13-11 23-23 14-12 9-27-1-24-14Z"
          />
          <circle cx="49" cy="48" r="7" className="mascot-eye" />
          <circle cx="74" cy="48" r="7" className="mascot-eye" />
          <circle cx="50" cy="49" r="3" className="mascot-pupil" />
          <circle cx="73" cy="49" r="3" className="mascot-pupil" />
          <path d="m56 58 6 7 6-7Z" className="owl-beak" />
          <path d="M43 91 39 101m39-10 4 10M33 102h13m31 0h13" className="mascot-feet" />
          <path d="M46 76c10 7 20 7 30 0" className="owl-chest" />
        </svg>
      ) : (
        <svg viewBox="0 0 120 110" role="img" aria-hidden="true">
          <path className="mascot-wing-left" d="M34 54C15 55 10 73 26 82c10 5 20-3 24-12" />
          <path className="mascot-wing-right" d="M83 55c20 0 25 18 9 27-10 5-20-3-24-12" />
          <path
            d="M36 37c5-17 33-22 48-5 15 16 11 52-7 62-14 8-34 3-42-12-7-14-5-31 1-45Z"
            className="mascot-body"
          />
          <path d="M31 37 24 18l22 12M82 33l16-16-4 25" className="mascot-tuft" />
          <path d="m54 59 8 5-9 5" className="mascot-beak" />
          <circle cx="48" cy="51" r="9" className="mascot-eye" />
          <circle cx="73" cy="49" r="9" className="mascot-eye" />
          <circle cx="50" cy="52" r="3" className="mascot-pupil" />
          <circle cx="71" cy="50" r="3" className="mascot-pupil" />
          <path d="M43 90 38 101m40-11 4 11M32 102h13m32 0h13" className="mascot-feet" />
          <path d="M35 47c8-9 17-9 25 0m1-1c7-8 15-8 23 0" className="mascot-glasses" />
        </svg>
      )}
    </div>
  );
}

function formatPaperMeta(paper: PaperResult): string {
  const parts: string[] = [];
  if (paper.venue) parts.push(paper.venue);
  if (paper.year) parts.push(String(paper.year));
  if (paper.arxiv_id) parts.push(`arXiv:${paper.arxiv_id}`);
  else if (paper.doi) parts.push(`DOI ${paper.doi}`);
  if (typeof paper.citation_count === "number" && paper.citation_count > 0) {
    parts.push(`${paper.citation_count.toLocaleString()} citations`);
  }
  return parts.join(" · ") || "Academic Research Paper";
}

function PaperCard({ paper, index }: { paper: PaperResult; index: number }) {
  const isExact = Boolean(paper.is_exact_match);
  const isFallback = Boolean(paper.is_paywall_fallback);
  const isOA = Boolean(paper.is_open_access);

  const accessLabel = isExact
    ? "Exact match"
    : isFallback
      ? "Related work found"
      : isOA
        ? "Open access"
        : "No comparable copy";

  const accessClass = isExact
    ? "access-exact"
    : isFallback
      ? "access-related"
      : isOA
        ? "access-open"
        : "access-none";

  const matchPercent = Math.min(100, Math.max(0, Math.round((paper.relevance_score ?? 0.8) * 100)));
  const diffLevel = paper.difficulty?.level || "Intermediate";
  const authorsString = Array.isArray(paper.authors)
    ? paper.authors.join(", ")
    : String(paper.authors || "Unknown Author");

  const confidenceClass = paper.match_confidence
    ? `confidence-${paper.match_confidence.toLowerCase().replace(/\s+/g, "-")}`
    : "";

  return (
    <article className="paper-card" style={{ animationDelay: `${index * 90}ms` }}>
      <span className="result-number">{index + 1 < 10 ? `0${index + 1}` : index + 1}</span>
      <div className="paper-main">
        <div className="paper-meta">{formatPaperMeta(paper)}</div>
        <h3>{paper.title}</h3>
        <p className="authors">{authorsString}</p>
        <p className="abstract">{paper.abstract}</p>

        {/* Explainability note */}
        {paper.why_recommended ? (
          <div className={`note-strip ${!isOA && !isFallback ? "note-muted" : ""}`}>
            {paper.why_recommended}
          </div>
        ) : isFallback ? (
          <div className="note-strip">
            Pico found credible related open-access work after checking the paywalled paper.
          </div>
        ) : !isOA ? (
          <div className="note-strip note-muted">
            No related open-access work cleared the similarity and credibility checks.
          </div>
        ) : null}

        {/* Paywall fallback credibility signals */}
        {isFallback && (
          <div className="fallback-signals-row">
            {paper.match_confidence && (
              <span className={`confidence-badge ${confidenceClass}`}>
                {paper.match_confidence}
              </span>
            )}
            {paper.same_author_match && (
              <span className="fallback-tag author-tag">✦ same author</span>
            )}
            {typeof paper.bibliographic_overlap === "number" && paper.bibliographic_overlap > 0 && (
              <span className="fallback-tag overlap-tag">
                ✦ {paper.bibliographic_overlap} shared{" "}
                {paper.bibliographic_overlap === 1 ? "reference" : "references"}
              </span>
            )}
          </div>
        )}
      </div>

      <div className="paper-side">
        <span className={`access-stamp ${accessClass}`}>{accessLabel}</span>
        <div className="score-ring" aria-label={`${matchPercent}% semantic match`}>
          <strong>{matchPercent}%</strong>
          <span>match</span>
        </div>
        <div className="difficulty">
          <small>Reading level</small>
          <strong>{diffLevel}</strong>
          <div className={`level-bars level-${diffLevel.toLowerCase()}`}>
            <i />
            <i />
            <i />
          </div>
        </div>

        {paper.oa_url ? (
          <Button asChild variant="outline" className="sketch-button w-full">
            <a href={paper.oa_url} target="_blank" rel="noopener noreferrer">
              Read paper <ArrowUpRight />
            </a>
          </Button>
        ) : paper.doi ? (
          <Button asChild variant="outline" className="sketch-button w-full">
            <a href={`https://doi.org/${paper.doi}`} target="_blank" rel="noopener noreferrer">
              View details <ArrowUpRight />
            </a>
          </Button>
        ) : (
          <Button variant="outline" className="sketch-button w-full">
            View details <ArrowUpRight />
          </Button>
        )}
      </div>
    </article>
  );
}

function Index() {
  const [query, setQuery] = useState("citation-aware paper recommendations");
  const [submittedQuery, setSubmittedQuery] = useState("citation-aware paper recommendations");
  const [searchMode, setSearchMode] = useState<SearchMode>("topic");
  const [activeNav, setActiveNav] = useState("Discover");
  const [openOnly, setOpenOnly] = useState(false);
  const [difficulty, setDifficulty] = useState("Any level");
  const [publishedSpan, setPublishedSpan] = useState("Any time");
  const [isDark, setIsDark] = useState(false);

  // Search API lifecycle states
  const [isLoading, setIsLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [searchResponse, setSearchResponse] = useState<PaperSearchResponse | null>(null);

  useEffect(() => {
    const savedTheme = window.localStorage.getItem("paperbridge-theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    setIsDark(savedTheme ? savedTheme === "dark" : prefersDark);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDark);
    window.localStorage.setItem("paperbridge-theme", isDark ? "dark" : "light");
  }, [isDark]);

  const performSearch = useCallback(async (targetQuery: string, targetMode: SearchMode) => {
    const trimmed = targetQuery.trim();
    if (!trimmed) return;

    setIsLoading(true);
    setSearchError(null);
    setSubmittedQuery(trimmed);

    try {
      const response = await searchPapers({
        query: trimmed,
        mode: targetMode,
        limit: 10,
      });
      setSearchResponse(response);
    } catch (err: any) {
      console.error("[PaperBridge UI] Search error:", err);
      setSearchError(err?.message || "Failed to contact search backend service.");
      setSearchResponse({
        query: trimmed,
        mode: targetMode,
        total_results: 0,
        results: [],
        no_alternative_found: false,
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Run initial search on mount
  useEffect(() => {
    performSearch("citation-aware paper recommendations", "topic");
  }, [performSearch]);

  function submitSearch(event: FormEvent) {
    event.preventDefault();
    const trimmed = query.trim();
    const isDoi = trimmed.startsWith("10.") || trimmed.includes("doi.org/");
    const effectiveMode = isDoi ? "paper" : searchMode;
    if (isDoi && searchMode !== "paper") {
      setSearchMode("paper");
      setActiveNav("Paper lookup");
    }
    performSearch(trimmed, effectiveMode);
  }

  function switchMode(newMode: SearchMode) {
    setSearchMode(newMode);
    setActiveNav(newMode === "paper" ? "Paper lookup" : "Discover");
  }

  function handleNavClick(label: string) {
    setActiveNav(label);
    if (label === "Paper lookup") {
      setSearchMode("paper");
    } else if (label === "Discover") {
      setSearchMode("topic");
    }
  }

  function runTrailSearch(topic: string) {
    setQuery(topic);
    setSearchMode("topic");
    setActiveNav("Discover");
    performSearch(topic, "topic");
  }

  const rawResults = searchResponse?.results || [];

  // Reconcile exact match status for direct paper lookups
  const processedResults = rawResults.map((paper, idx) => {
    if (paper.is_exact_match !== undefined) return paper;
    if (
      searchMode === "paper" &&
      idx === 0 &&
      (paper.title.toLowerCase().includes(submittedQuery.toLowerCase()) ||
        submittedQuery.toLowerCase().includes(paper.title.toLowerCase()) ||
        (paper.doi && submittedQuery.includes(paper.doi)))
    ) {
      return { ...paper, is_exact_match: true };
    }
    return paper;
  });

  const visiblePapers = processedResults.filter((paper) => {
    if (openOnly && !paper.is_open_access) return false;
    if (difficulty !== "Any level" && paper.difficulty?.level !== difficulty) return false;
    if (publishedSpan !== "Any time" && typeof paper.year === "number") {
      if (publishedSpan === "Since 2021 (Last 5 yrs)" && paper.year < 2021) return false;
      if (publishedSpan === "Since 2016 (Last 10 yrs)" && paper.year < 2016) return false;
      if (publishedSpan === "Since 2011 (Last 15 yrs)" && paper.year < 2011) return false;
      if (publishedSpan === "Since 2006 (Last 20 yrs)" && paper.year < 2006) return false;
      if (publishedSpan === "Prior to 2011 (Classic works)" && paper.year >= 2011) return false;
    }
    return true;
  });

  const hasActiveFilters = openOnly || difficulty !== "Any level" || publishedSpan !== "Any time";
  const clearFilters = () => {
    setOpenOnly(false);
    setDifficulty("Any level");
    setPublishedSpan("Any time");
  };

  const isGenuineEmpty =
    searchResponse !== null &&
    !isLoading &&
    !searchError &&
    searchResponse.total_results === 0 &&
    !searchResponse.no_alternative_found;
  const isFilterEmpty =
    searchResponse !== null &&
    !isLoading &&
    searchResponse.total_results > 0 &&
    visiblePapers.length === 0;

  return (
    <main className="research-shell">
      <aside className="research-sidebar">
        <div className="brand-mark">
          <span>PB</span>
          <div>
            <strong>PaperBridge</strong>
            <small>AI research desk</small>
          </div>
        </div>
        <nav aria-label="Main navigation">
          {navItems.map(({ label, icon: Icon }) => (
            <Button
              key={label}
              variant="ghost"
              onClick={() => handleNavClick(label)}
              className={`nav-button ${activeNav === label ? "nav-active" : ""}`}
            >
              <Icon /> <span>{label}</span>
            </Button>
          ))}
        </nav>
        <div className="sidebar-divider" />
        <div className="topic-label">Pinned fields</div>
        <div className="topic-list">
          <button onClick={() => runTrailSearch("Machine learning")}>Machine learning</button>
          <button onClick={() => runTrailSearch("Computer vision")}>Computer vision</button>
          <button onClick={() => runTrailSearch("Natural language processing")}>NLP</button>
        </div>
        <div className="mascot-nook">
          <div className="speech-bubble">I traced the strongest citation paths!</div>
          <Mascot compact nocturnal={isDark} />
          <strong>Pico's {isDark ? "night note" : "field note"}</strong>
          <p>
            {isDark
              ? "Follow the brightest citation trails through the night."
              : "Start broad. Narrow with reading level after you see the landscape."}
          </p>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <span className="breadcrumb">RESEARCH DESK /</span>{" "}
            {searchMode === "paper" ? "PAPER LOOKUP" : "DISCOVER"}
          </div>
          <div className="topbar-actions">
            <div className="source-status">
              <span /> {getApiBaseUrl() ? "Academic sources ready (Live)" : "Academic sources ready (Demo)"}
            </div>
            <Button
              type="button"
              variant="outline"
              size="icon"
              className="theme-toggle"
              onClick={() => setIsDark((current) => !current)}
              aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
              title={isDark ? "Switch to light mode" : "Switch to dark mode"}
            >
              {isDark ? <Sun /> : <Moon />}
            </Button>
          </div>
        </header>

        <div className="search-section">
          <div className="night-sky" aria-hidden="true">
            <i className="moon moon-large" />
            <i className="moon moon-small" />
            <b className="star star-one">✦</b>
            <b className="star star-two">✧</b>
            <b className="star star-three">✦</b>
          </div>
          <div className="search-copy">
            <span className="eyebrow">
              <Sparkles /> FOR CURIOUS MINDS
            </span>
            <h1>
              Find papers that <em>meet you halfway.</em>
            </h1>
            <p>
              Search a topic or an existing paper. We'll rank what matters, check what you can
              access, and flag the reading level.
            </p>
          </div>
          <div className="mascot-stage">
            <div className="motion-line" />
            <Mascot nocturnal={isDark} />
            <span className="mascot-note">
              {isDark ? "Owl bridge the gap!" : "Let's bridge the gap!"}
            </span>
          </div>

          {/* Topic vs Paper Mode Toggle */}
          <div className="mode-toggle-group" role="tablist" aria-label="Search mode">
            <button
              type="button"
              role="tab"
              aria-selected={searchMode === "topic"}
              onClick={() => switchMode("topic")}
              className={`mode-pill ${searchMode === "topic" ? "mode-pill-active" : ""}`}
            >
              <Search className="w-3.5 h-3.5" /> Topic Search
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={searchMode === "paper"}
              onClick={() => switchMode("paper")}
              className={`mode-pill ${searchMode === "paper" ? "mode-pill-active" : ""}`}
            >
              <FileSearch className="w-3.5 h-3.5" /> Paper Title / DOI
            </button>
          </div>

          <form className="search-box" onSubmit={submitSearch}>
            <Search aria-hidden="true" />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              aria-label="Search papers"
              placeholder={
                searchMode === "paper"
                  ? "Paper title, DOI (e.g. 10.1145/...), or arXiv ID..."
                  : "Topic, keywords, or research field..."
              }
            />
            <Button type="submit" className="primary-sketch" disabled={isLoading}>
              {isLoading ? "Searching..." : "Search papers"} <ArrowUpRight />
            </Button>
          </form>

          <div className="quick-row">
            <span>Try a trail:</span>
            {["Graph neural networks", "Climate adaptation", "Medical imaging"].map((topic) => (
              <Button
                key={topic}
                variant="outline"
                size="sm"
                onClick={() => runTrailSearch(topic)}
                className="topic-chip"
              >
                {topic}
              </Button>
            ))}
          </div>
        </div>

        <section className="results-section">
          <div className="results-heading">
            <div>
              <span className="hand-label">
                {searchMode === "paper" ? "lookup target & related work for" : "best bridges for"}
              </span>
              <h2>“{submittedQuery}”</h2>
              <p>
                {isLoading
                  ? "Running citation-aware ranker..."
                  : `${visiblePapers.length} ranked papers · duplicates collapsed`}
              </p>
            </div>
            <Button variant="outline" className="filter-button">
              <SlidersHorizontal /> Refine <ChevronDown />
            </Button>
          </div>

          <div className="filter-board">
            <div className="filter-title">
              <Filter /> FILTER NOTES
            </div>
            <label>
              <input
                type="checkbox"
                checked={openOnly}
                onChange={(event) => setOpenOnly(event.target.checked)}
              />{" "}
              Open access only
            </label>
            <label>
              <span>Difficulty</span>
              <select value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
                <option>Any level</option>
                <option>Foundational</option>
                <option>Intermediate</option>
                <option>Advanced</option>
              </select>
            </label>
            <label>
              <span>Published</span>
              <select
                value={publishedSpan}
                onChange={(event) => setPublishedSpan(event.target.value)}
              >
                <option>Any time</option>
                <option>Since 2021 (Last 5 yrs)</option>
                <option>Since 2016 (Last 10 yrs)</option>
                <option>Since 2011 (Last 15 yrs)</option>
                <option>Since 2006 (Last 20 yrs)</option>
                <option>Prior to 2011 (Classic works)</option>
              </select>
            </label>
            <Button variant="ghost" className="clear-button" onClick={clearFilters}>
              Clear notes
            </Button>
          </div>

          {/* Results Area */}
          <div className="papers-list">
            {/* Paywalled original notification banner if triggered */}
            {searchResponse?.paywalled_original && (
              <div className="paywall-banner">
                <h4>Paywalled Paper Requested: {searchResponse.paywalled_original.title}</h4>
                <p>{searchResponse.paywalled_original.note}</p>
              </div>
            )}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="loading-indicator">
                Pico is tracing citation graphs and checking open-access repositories...
              </div>
            )}

            {/* Backend Connection Error Notice */}
            {searchError && (
              <div className="empty-state-card border-dashed border-amber-400/80 bg-amber-50/70 dark:bg-amber-950/30 dark:border-amber-700/60">
                <div className="empty-state-icon">
                  <Mascot compact nocturnal={isDark} />
                </div>
                <h3 className="text-amber-900 dark:text-amber-200">Backend Connection Notice</h3>
                <p className="empty-state-copy text-amber-800 dark:text-amber-300">
                  {searchError}
                </p>
                <div className="empty-trail-box">
                  <span className="empty-trail-label">Actions:</span>
                  <div className="quick-row justify-center mt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => performSearch(query, searchMode)}
                      className="sketch-button"
                    >
                      <RotateCcw className="w-3.5 h-3.5 mr-1" /> Retry Search
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Honest Empty-State Recovery UI (Requirement 3) */}
            {isGenuineEmpty && (
              <div className="empty-state-card">
                <div className="empty-state-icon">
                  <Mascot compact nocturnal={isDark} />
                </div>
                <h3>No papers found</h3>
                <p className="empty-state-copy">
                  No academic papers matched <strong>“{submittedQuery}”</strong>. Check the
                  spelling, try a broader topic, or explore one of the research trails below.
                </p>
                {hasActiveFilters && (
                  <Button variant="outline" onClick={clearFilters} className="sketch-button mt-2">
                    <RotateCcw className="w-3.5 h-3.5 mr-1" /> Try again without filters
                  </Button>
                )}
                <div className="empty-trail-box">
                  <span className="empty-trail-label">Try a trail:</span>
                  <div className="quick-row justify-center">
                    {["Graph neural networks", "Climate adaptation", "Medical imaging"].map(
                      (topic) => (
                        <Button
                          key={topic}
                          variant="outline"
                          size="sm"
                          onClick={() => runTrailSearch(topic)}
                          className="topic-chip"
                        >
                          {topic}
                        </Button>
                      ),
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Filter-empty State: papers found but local filters exclude all */}
            {isFilterEmpty && (
              <div className="empty-state-card">
                <h3>No papers match your filter criteria</h3>
                <p className="empty-state-copy">
                  Your search for <strong>“{submittedQuery}”</strong> returned{" "}
                  {searchResponse.total_results} papers, but none match your active filters (
                  {[
                    openOnly ? "Open access only" : null,
                    difficulty !== "Any level" ? difficulty : null,
                    publishedSpan !== "Any time" ? publishedSpan : null,
                  ]
                    .filter(Boolean)
                    .join(", ")}).
                </p>
                <Button variant="outline" onClick={clearFilters} className="sketch-button mt-3">
                  <RotateCcw className="w-3.5 h-3.5 mr-1" /> Try again without filters
                </Button>
              </div>
            )}

            {/* Active Result Cards */}
            {!isLoading &&
              visiblePapers.map((paper, index) => (
                <PaperCard key={paper.id || paper.title} paper={paper} index={index} />
              ))}
          </div>
        </section>
      </section>
    </main>
  );
}
