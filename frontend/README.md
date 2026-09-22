# PaperBridge AI Frontend (React + Vite)

This frontend client implements the user-interface tier of PaperBridge AI, engineered around the Nielsen Norman Group scannability principles for academic search.

## Setup & Running Locally

```bash
# 1. Install dependencies
npm.cmd install

# 2. Run local dev server
npm.cmd run dev
```

The application will start at `http://localhost:5173`.

## Environment Variables

Create `.env.local` inside `frontend/` if connecting to an external or custom backend port:

```env
VITE_API_BASE_URL=http://127.0.0.1:5000
```

## Vercel Deployment

Deploying to Vercel is seamless:
1. Connect your GitHub repository in the Vercel dashboard.
2. Set the **Root Directory** to `frontend`.
3. Framework Preset: **Vite**.
4. (Optional) Set `VITE_API_BASE_URL` to your hosted Flask backend URL.
5. Click **Deploy**. If the backend URL is not provided, the frontend will automatically function in interactive preview mode with benchmark datasets.
