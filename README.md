# PropIntel - Property Analysis Dashboard

A bilingual (Chinese/English) property investment and macro analysis dashboard for Singapore.

## Live Demo
- **Frontend:** [https://prop-intel.pages.dev/](https://prop-intel.pages.dev/)

## Features
- **Real-time Data:** Fetches from data.gov.sg and URA APIs.
- **Financial Modeling:** Dynamic acquisition cost, mortgage stress tests, and IRR analysis.
- **Macro Insights:** Market price gaps (Public vs Private), affordability trends, and population demand.
- **Land Intelligence:** Historical GLS (Government Land Sales) tracking and new launch benchmarks.
- **Amenities Engine:** Intelligent mapping of nearby schools, malls, and transport hubs.

## Tech Stack
- **Frontend:** Next.js 15, TypeScript, ECharts, Lucide React, CSS Modules.
- **Backend:** FastAPI (Python), SQLite, Pandas.
- **Deployment:** Cloudflare Pages (Static Export).

## Local Development

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```
*Make sure to set your `DATA_GOV_API_KEY` and `URA_ACCESS_KEY` in the `.env` file.*

### 2. Frontend Setup
```bash
npm install
npm run dev
```

### 3. Sync Data
```bash
python backend/scripts/fetch_data_gov.py
python backend/scripts/populate_land_data.py
```

## Deployment Info
The frontend is configured for **Static Export**. To deploy to Cloudflare Pages:
1. `npm run build`
2. `npx wrangler pages deploy out --project-name prop-intel`

*Note: The backend must be hosted separately and the API URL updated in the frontend if not running locally.*
