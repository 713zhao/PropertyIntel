# Backend Deployment Guide (Fly.io)

This guide will help you deploy the FastAPI backend for PropIntel to Fly.io.

## Prerequisites
1. [Fly.io CLI](https://fly.io/docs/hands-on/install-flyctl/) installed and logged in (`fly auth login`).
2. You are in the `backend/` directory of the project.

## Deployment Steps

### 1. Create a Volume for Persistent Data
Since the project uses SQLite, we need a persistent volume so your data isn't lost when the server restarts.
```bash
fly volumes create prop_intel_data --region sin --size 1
```
*(Select `1GB` when prompted, which is more than enough for the SQLite DB)*

### 2. Set Up Environment Secrets
You need to set your API keys on Fly.io so the backend can fetch live data.
```bash
fly secrets set DATA_GOV_API_KEY=your_key_here URA_ACCESS_KEY=your_key_here
```

### 3. Deploy the App
```bash
fly deploy
```
*Note: If the app name `prop-intel-backend` is already taken, edit the `app` field in `fly.toml` first.*

### 4. Populate Data (One-time)
Once the app is live, you can SSH into the machine to run the initial data population scripts:
```bash
fly ssh console
# Inside the console:
python scripts/fetch_data_gov.py
python scripts/populate_land_data.py
exit
```

## Update Frontend
After deployment, your backend will be at `https://prop-intel-backend.fly.dev`. 

1. Update your frontend code (fetch calls) to point to this URL.
2. In `next.config.ts`, if you are using static export for Cloudflare, make sure you replace any relative `/api/` calls with the full absolute URL if needed, OR configure your Cloudflare Pages to proxy to this Fly.io URL.

### Recommended: Updating Frontend URLs
Search for `fetch('/api/` in your `src/` folder and update it to `fetch('https://prop-intel-backend.fly.dev/api/`.
