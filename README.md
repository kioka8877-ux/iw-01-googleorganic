# IW-01 GoogleOrganic — Standalone

> Google organic search results — JSON clean, no tracking.
> Part of the PERTURABO Iron Warriors fleet.

## Deploy on Render

1. Sign up on https://render.com (with Google)
2. New → Web Service → Connect this repo
3. Render auto-detects `render.yaml`
4. Click Deploy
5. Your API is live at `https://iw-01-googleorganic.onrender.com`

## Endpoints

- `GET /search?q=test` — Google organic search
- `GET /health` — Health check
- `GET /docs` — Swagger UI

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```
