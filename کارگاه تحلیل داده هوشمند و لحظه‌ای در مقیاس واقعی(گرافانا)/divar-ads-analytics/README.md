# Divar Ads Analytics — Classified Ads Monitoring Tutorial

> A complete tutorial project that simulates a **Divar.ir-style classified ads marketplace** with real-time analytics. Demonstrates **Grafana + VictoriaMetrics + Python + Docker Compose** — a single time-series database for both business KPIs and application metrics.

---

## How This Relates to `netflix-watch-analytics`

| Aspect | netflix-watch-analytics | divar-ads-analytics |
|--------|-------------------------|---------------------|
| Domain | Video streaming (Netflix) | Classified ads (Divar.ir) |
| Business events | Watch sessions, genres, buffering | Ad views, posts, searches, contacts |
| Time-series DB | **InfluxDB** (Flux queries) | **VictoriaMetrics** (PromQL) |
| App metrics | Prometheus (separate service) | Same `/metrics` endpoint → VM |
| Grafana datasources | 2 (InfluxDB + Prometheus) | 1 (VictoriaMetrics) |
| Stack complexity | 4 containers | 3 containers |

**Key takeaway**: VictoriaMetrics is Prometheus-compatible. Your Python app exposes standard Prometheus metrics; VictoriaMetrics scrapes them directly — no separate InfluxDB or Prometheus needed for this tutorial.

---

## Architecture

```
                    ┌──────────────────────────────────────┐
                    │       Grafana (Port 8795)            │
                    │                                      │
                    │   Divar Ads Analytics Dashboard      │
                    │   (25 panels, PromQL queries)        │
                    │              │                       │
                    └──────────────┼───────────────────────┘
                                   │ PromQL / MetricsQL
                    ┌──────────────▼───────────────────────┐
                    │   VictoriaMetrics (Port 8428)        │
                    │                                      │
                    │   - Scrapes /metrics every 3s        │
                    │   - Stores all time series           │
                    │   - 7-day retention                  │
                    └──────────────┬───────────────────────┘
                                   │ scrape
                    ┌──────────────▼───────────────────────┐
                    │   FastAPI App (Port 8010)            │
                    │                                      │
                    │   POST /api/ads/view                 │
                    │   POST /api/ads/post                 │
                    │   POST /api/search                   │
                    │   POST /api/contact                  │
                    │   GET  /metrics                      │
                    │   Background Simulator               │
                    └──────────────────────────────────────┘
```

---

## Quick Start

```bash
cd divar-ads-analytics

# Start the full stack
docker compose up --build

# Wait ~20 seconds for VictoriaMetrics to start scraping

# Open Grafana
# http://localhost:8795
# Login: admin / admin

# Dashboard auto-loads:
# "Divar Ads Analytics — Real-Time Classified Ads Dashboard"
```

---

## Services & Ports

| Service           | Port  | Purpose                              |
|-------------------|-------|--------------------------------------|
| FastAPI App       | 8010  | REST API + `/metrics` + simulator    |
| VictoriaMetrics   | 8428  | Time-series DB + scraper             |
| Grafana           | 8795  | Dashboards (maps to container 3000)  |

---

## Project Structure

```
divar-ads-analytics/
├── app/
│   ├── main.py                 # FastAPI app, middleware, lifespan
│   ├── simulator.py            # Background traffic generator
│   ├── api/routes.py           # REST endpoints
│   ├── models/schemas.py       # Pydantic models
│   ├── services/ad_service.py  # Business logic + metric updates
│   ├── db/vm_client.py         # VictoriaMetrics query client
│   └── metrics/metrics.py      # All Prometheus metric definitions
├── grafana/provisioning/
│   ├── datasources/datasources.yml
│   └── dashboards/
│       ├── dashboard.yml
│       └── divar-dashboard.json
├── victoriametrics/scrape.yml  # VM scrape config
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Simulated Divar.ir Events

The background simulator generates realistic classified-ads traffic:

| Event | Description | Example categories |
|-------|-------------|-------------------|
| **Ad view** | User opens a listing | real-estate, vehicles, electronics |
| **Ad post** | Seller publishes new ad | home-appliances, services, jobs |
| **Search** | User searches listings | apartment search, car listings |
| **Contact** | Call or chat with seller | call (60%), chat (40%) |

Iranian cities with weighted distribution: Tehran (38%), Isfahan, Mashhad, Shiraz, etc.

---

## API Examples

### Record an ad view
```bash
curl -X POST http://localhost:8010/api/ads/view \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_42",
    "ad_id": "ad_123456",
    "ad_title": "Apartment 85sqm",
    "category": "real-estate",
    "city": "tehran",
    "price_toman": 4500000000,
    "condition": "new",
    "device_type": "phone",
    "view_duration_seconds": 45.2,
    "scrolled_to_contact": true
  }'
```

### Get stats (queries VictoriaMetrics)
```bash
curl http://localhost:8010/api/stats
```

### Prometheus metrics
```bash
curl http://localhost:8010/metrics
```

---

## VictoriaMetrics Metrics

All metrics use the `divar_` prefix. Example PromQL:

```promql
sum(rate(divar_ad_views_total[1m]))
topk(5, sum by (category) (increase(divar_ad_views_total[1h])))
```

Browse VictoriaMetrics UI: http://localhost:8428/vmui

---

## Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11 | Application |
| FastAPI | 0.104 | Web framework |
| VictoriaMetrics | 1.97 | Time-series database |
| Grafana | 10.2 | Dashboards |
| prometheus_client | 0.19 | Metric instrumentation |
| Docker Compose | — | Orchestration |
