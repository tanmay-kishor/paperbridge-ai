# PaperBridge AI 🎓🌉

> **AI-assisted academic research paper discovery and recommendation platform.**  
> Mini Project — 5th Semester | B.Tech CSE / AI

PaperBridge AI helps students and researchers discover academic papers that:
1. **Match their research intent** via dense Sentence Transformer embeddings and cosine similarity (not just shallow keyword matching).
2. **Are legitimately accessible** via open-access discovery (Semantic Scholar + Unpaywall).
3. **Offer open-access fallbacks** if a target paper is paywalled, reusing semantic matching to find accessible alternatives.
4. **Match their reading level** through Flesch-Kincaid Grade Level and jargon-density analysis, classified into **Foundational**, **Intermediate**, and **Advanced**.

---

## 📁 Repository Structure

```
paperbridge-ai/
├── README.md               # Project overview, setup, and viva guide
├── .gitignore              # Ignores venv, node_modules, cache
├── LICENSE                 # MIT License
├── docs/                   # Team living documents (SOP compliance)
│   ├── decision-log.md     # Architectural and algorithmic decisions
│   ├── progress-tracker.md # Module status and ownership tracking
│   ├── test-log.md         # Empirical test queries and validation runs
│   ├── architecture.md     # System design, data flow, and contracts
│   ├── meeting-notes/      # Dated meeting minutes
│   └── paper/              # Academic paper drafts and outline
├── backend/                # Python / Flask API & ML Pipeline
│   ├── app.py              # Flask server entry point
│   ├── config.py           # Configuration & environment settings
│   ├── requirements.txt    # Python dependencies
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py       # API endpoints (/api/search, /api/health)
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── metadata.py     # Semantic Scholar API client & normalizer
│   │   ├── embeddings.py   # SentenceTransformer embeddings & cosine similarity
│   │   ├── open_access.py  # Unpaywall lookup & paywall fallback logic
│   │   ├── difficulty.py   # Readability & jargon density scorer
│   │   └── ranker.py       # Multi-signal recommendation ranker
│   └── tests/              # Unit and integration test suite
├── frontend/               # React (Vite) Web Application
│   ├── package.json
│   ├── vercel.json         # Vercel deployment routing configuration
│   ├── public/             # Static public assets
│   ├── src/
│   │   ├── App.jsx         # Main application container
│   │   ├── components/     # SearchBar, ResultCard, ResultsList
│   │   ├── pages/          # Home view
│   │   ├── api/client.js   # Backend API client with offline demo fallback
│   │   └── styles/         # Scannable, modern CSS design
│   └── README.md
├── prototype/              # Streamlit demo for quick prototyping & viva
│   └── streamlit_demo.py
└── data/                   # Offline datasets & test fixtures
    ├── sample_queries.json
    └── test_papers.json
```

---

## 🚀 Quick Start Guide

### 1. Backend Setup (Flask API)
```bash
cd backend
python -m pip install -r requirements.txt
python app.py
```
The Flask backend runs at `http://127.0.0.1:5000`.

### 2. Frontend Setup (React / Vite)
```bash
cd frontend
npm install
npm run dev
```
The React frontend runs at `http://localhost:5173`.

### 3. Optional Streamlit Demo
```bash
cd prototype
streamlit run streamlit_demo.py
```

---

## ☁️ Deployment Guide

### Deploying the Frontend to Vercel
1. Push your repository to GitHub.
2. Sign in to [Vercel](https://vercel.com) and click **"Add New Project"**.
3. Select your repository and set the **Root Directory** to `frontend`.
4. (Optional) Set the environment variable:
   - `VITE_API_BASE_URL`: URL of your deployed Flask backend (e.g. `https://paperbridge-api.onrender.com`).
   *Note: If no backend URL is set, the frontend automatically runs in interactive demo mode using cached benchmark queries!*
5. Click **Deploy**.

---

## 🔒 Security & Robustness Summary
- **Input Sanitization**: Query strings and DOIs are strictly validated and regex-checked.
- **SSRF Prevention**: External API calls target hardcoded whitelist endpoints.
- **XSS Protection**: React escapes all dynamic text; external links enforce `rel="noopener noreferrer"`.
- **Graceful Fallbacks**: If external academic APIs are rate-limited or offline, the system safely falls back to local sample datasets.
