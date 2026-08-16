"""Generate valid Grafana dashboard JSON for Divar Ads Analytics."""

import json
from pathlib import Path

DS = {"type": "prometheus", "uid": "victoriametrics"}


def panel(id_, title, ptype, x, y, w, h, **extra):
    p = {
        "id": id_,
        "title": title,
        "type": ptype,
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "datasource": DS,
    }
    p.update(extra)
    return p


def row(id_, title, y):
    return {
        "id": id_,
        "title": title,
        "type": "row",
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": y},
        "collapsed": False,
        "panels": [],
    }


dashboard = {
    "uid": "divar-ads-analytics",
    "title": "Divar Ads Analytics — Real-Time Classified Ads Dashboard",
    "tags": ["divar", "classified-ads", "victoriametrics"],
    "timezone": "browser",
    "schemaVersion": 39,
    "version": 1,
    "refresh": "5s",
    "time": {"from": "now-30m", "to": "now"},
    "templating": {"list": []},
    "annotations": {"list": []},
    "panels": [
        row(1, "Overview", 0),
        panel(2, "Active Users", "stat", 0, 1, 4, 5,
              targets=[{"expr": "divar_active_users", "refId": "A", "instant": True}]),
        panel(3, "Ad Views (1h)", "stat", 4, 1, 4, 5,
              targets=[{"expr": "sum(increase(divar_ad_views_total[1h]))", "refId": "A", "instant": True}]),
        panel(4, "New Ads Posted (1h)", "stat", 8, 1, 4, 5,
              targets=[{"expr": "sum(increase(divar_ad_posts_total[1h]))", "refId": "A", "instant": True}]),
        panel(5, "Searches (1h)", "stat", 12, 1, 4, 5,
              targets=[{"expr": "sum(increase(divar_searches_total[1h]))", "refId": "A", "instant": True}]),
        panel(6, "Contacts (1h)", "stat", 16, 1, 4, 5,
              targets=[{"expr": "sum(increase(divar_contacts_total[1h]))", "refId": "A", "instant": True}]),
        panel(7, "Active Listings", "stat", 20, 1, 4, 5,
              targets=[{"expr": "divar_active_listings", "refId": "A", "instant": True}]),
        row(10, "Real-Time Activity", 6),
        panel(11, "Ad Views Over Time", "timeseries", 0, 7, 12, 8,
              targets=[{"expr": "sum(rate(divar_ad_views_total[1m]))", "legendFormat": "views/sec", "refId": "A"}]),
        panel(12, "Concurrent Active Users", "timeseries", 12, 7, 12, 8,
              targets=[{"expr": "divar_active_users", "legendFormat": "users", "refId": "A"}]),
        panel(13, "Searches vs Contacts", "timeseries", 0, 15, 12, 8,
              targets=[
                  {"expr": "sum(rate(divar_searches_total[1m]))", "legendFormat": "searches/sec", "refId": "A"},
                  {"expr": "sum(rate(divar_contacts_total[1m]))", "legendFormat": "contacts/sec", "refId": "B"},
              ]),
        panel(14, "New Ads Posted Over Time", "timeseries", 12, 15, 12, 8,
              targets=[{"expr": "sum(rate(divar_ad_posts_total[1m]))", "legendFormat": "posts/sec", "refId": "A"}]),
        row(20, "Category and City Analytics", 23),
        panel(21, "Ad Views by Category", "piechart", 0, 24, 8, 8,
              targets=[{"expr": "sum by (category) (increase(divar_ad_views_total[1h]))", "legendFormat": "{{category}}", "refId": "A", "instant": True}]),
        panel(22, "Ad Views by City", "barchart", 8, 24, 8, 8,
              targets=[{"expr": "topk(8, sum by (city) (increase(divar_ad_views_total[1h])))", "legendFormat": "{{city}}", "refId": "A", "instant": True}]),
        panel(23, "Contacts by Type", "piechart", 16, 24, 8, 8,
              targets=[{"expr": "sum by (contact_type) (increase(divar_contacts_total[1h]))", "legendFormat": "{{contact_type}}", "refId": "A", "instant": True}]),
        panel(24, "New Ads by Category", "barchart", 0, 32, 12, 8,
              targets=[{"expr": "sum by (category) (increase(divar_ad_posts_total[1h]))", "legendFormat": "{{category}}", "refId": "A", "instant": True}]),
        panel(25, "Avg Ad Price by Category (Toman)", "barchart", 12, 32, 12, 8,
              targets=[{"expr": "sum by (category) (rate(divar_ad_price_toman_sum[1h])) / sum by (category) (rate(divar_ad_price_toman_count[1h]))", "legendFormat": "{{category}}", "refId": "A", "instant": True}]),
        row(30, "User Behavior", 40),
        panel(31, "Device Type Distribution", "piechart", 0, 41, 8, 7,
              targets=[{"expr": "sum by (device_type) (increase(divar_ad_views_total[1h]))", "legendFormat": "{{device_type}}", "refId": "A", "instant": True}]),
        panel(32, "Scroll to Contact Rate", "timeseries", 8, 41, 8, 7,
              targets=[{"expr": "sum(rate(divar_scroll_to_contact_total[1m]))", "legendFormat": "scroll/sec", "refId": "A"}]),
        panel(33, "Favorites Added", "timeseries", 16, 41, 8, 7,
              targets=[{"expr": "sum(rate(divar_favorites_total[1m]))", "legendFormat": "favorites/sec", "refId": "A"}]),
        row(40, "API Performance", 48),
        panel(41, "API Request Rate", "timeseries", 0, 49, 12, 7,
              targets=[
                  {"expr": 'sum(rate(divar_http_requests_total{status=~"2.."}[1m]))', "legendFormat": "2xx", "refId": "A"},
                  {"expr": 'sum(rate(divar_http_requests_total{status=~"5.."}[1m]))', "legendFormat": "5xx", "refId": "B"},
              ]),
        panel(42, "API Latency P95", "timeseries", 12, 49, 12, 7,
              targets=[{"expr": "histogram_quantile(0.95, sum(rate(divar_http_request_duration_seconds_bucket[1m])) by (le))", "legendFormat": "p95", "refId": "A"}]),
        row(50, "Revenue and Platform Health", 56),
        panel(51, "Promoted Ad Revenue (Toman/day)", "barchart", 0, 57, 8, 7,
              targets=[{"expr": "divar_estimated_revenue_toman", "legendFormat": "{{plan}}", "refId": "A", "instant": True}]),
        panel(52, "Cache Hit Rate", "gauge", 8, 57, 8, 7,
              targets=[{"expr": 'sum(rate(divar_cache_hits_total{result="hit"}[5m])) / sum(rate(divar_cache_hits_total[5m])) * 100', "refId": "A", "instant": True}]),
        panel(53, "Error Rate", "timeseries", 16, 57, 8, 7,
              targets=[{"expr": "sum(rate(divar_errors_total[1m]))", "legendFormat": "errors/sec", "refId": "A"}]),
    ],
}

out = Path(__file__).resolve().parents[1] / "grafana" / "provisioning" / "dashboards" / "divar-dashboard.json"
out.write_text(json.dumps(dashboard, indent=2), encoding="utf-8")
print(f"Wrote {out}")
