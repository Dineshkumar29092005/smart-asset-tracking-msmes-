# Database: Asset Memory Database (Module 4)

Stores every asset's identity, last seen location, timestamp and history, so the dashboard can answer "where is it?" instantly.

**Tech:** SQLite (prototype) / MySQL (production)

## Main Table: `assets`

| Column | Example |
|--------|---------|
| asset_id | A001 |
| asset_name | Spanner |
| category | Tool |
| camera_id | Camera-01 |
| zone | Zone A |
| last_seen_time | 25-05-2025 10:30:15 |
| status | Available |

## Tables

| Table | Purpose |
|-------|---------|
| `assets` | One row per asset with its latest known state |
| `cameras` | Registered cameras |
| `zones` | Zones within each camera view |
| `asset_history` | Every location change with timestamp |
| `alerts` | Missing, idle and unauthorized-removal alerts |

## Relationships (ER summary)

```
cameras 1 --- * zones
zones   1 --- * assets
assets  1 --- * asset_history
assets  1 --- * alerts
```

Full SQL is in [`schema.sql`](schema.sql).
