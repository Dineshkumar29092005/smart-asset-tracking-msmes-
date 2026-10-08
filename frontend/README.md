# Frontend: Web Dashboard (Module 6)

The dashboard is where workers and managers search for assets and see where they were last seen.

**Tech:** HTML, CSS, JavaScript (no framework, no build step)

## Features

- Summary cards: total assets, available, missing, open alerts
- Search by asset name/ID, category, zone, status and date
- Table showing last seen location, last seen time and status
- Click an asset to see its movement history
- Alerts panel with a Resolve button
- Auto-refreshes every 10 seconds

## Files

```
frontend/
├── index.html        # page layout
├── css/
│   └── style.css     # navy/orange theme
└── js/
    └── app.js        # calls the backend /api endpoints
```

## How to run

The Flask backend serves this folder, so just start the backend:

```bash
cd ../backend
python seed_demo.py     # optional demo data
python app.py
```

Then open http://127.0.0.1:5000

> Opening `index.html` directly by double-click will not work, because the page needs the backend API.

## API endpoints used

`/api/stats`, `/api/assets/search`, `/api/assets/<id>/history`, `/api/alerts`, `/api/alerts/<id>/resolve`. See `backend/README.md` for details.

## Possible improvements

- Live camera feed panel (MJPEG stream from the backend)
- Charts for reports and analytics
- Login for workers and managers
- Mobile-friendly app and voice search (future scope from the case study)
