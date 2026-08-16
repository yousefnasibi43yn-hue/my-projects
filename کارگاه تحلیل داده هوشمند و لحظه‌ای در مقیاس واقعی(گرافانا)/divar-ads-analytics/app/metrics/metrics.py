"""
Prometheus metrics for the Divar Ads Analytics service.

VictoriaMetrics scrapes these via /metrics and stores them as time series.
All business KPIs use Prometheus exposition format — no separate event DB needed.
"""

from prometheus_client import Counter, Gauge, Histogram, Summary


# ── HTTP (RED Method) ────────────────────────────────────────────

http_requests_total = Counter(
    "divar_http_requests_total",
    "Total HTTP requests received",
    ["method", "path", "status"],
)

http_request_duration_seconds = Histogram(
    "divar_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0],
)

# ── Ad Business KPIs ─────────────────────────────────────────────

ad_views_total = Counter(
    "divar_ad_views_total",
    "Total classified ad page views",
    ["category", "city", "device_type"],
)

ad_posts_total = Counter(
    "divar_ad_posts_total",
    "Total new ads posted by sellers",
    ["category", "city", "condition"],
)

searches_total = Counter(
    "divar_searches_total",
    "Total search queries executed",
    ["category", "city"],
)

contacts_total = Counter(
    "divar_contacts_total",
    "Buyer contact actions (call or chat)",
    ["category", "city", "contact_type"],
)

favorites_total = Counter(
    "divar_favorites_total",
    "Ads saved to favorites",
    ["category", "city"],
)

ad_price_toman = Histogram(
    "divar_ad_price_toman",
    "Listed ad price distribution in Toman",
    ["category", "city"],
    buckets=[500_000, 1_000_000, 5_000_000, 10_000_000, 50_000_000, 100_000_000, 500_000_000, 2_000_000_000],
)

view_duration_seconds = Histogram(
    "divar_view_duration_seconds",
    "Time spent viewing an ad listing",
    ["category"],
    buckets=[3, 10, 30, 60, 120, 300, 600],
)

scroll_to_contact_total = Counter(
    "divar_scroll_to_contact_total",
    "Users who scrolled down to the contact section",
    ["category", "city"],
)
ad_edits_total = Counter(
    "divar_ad_edits_total",
    "Total number of ad edits by sellers",
    ["category", "city"]
)

ad_deletions_total = Counter(
    "divar_ad_deletions_total",
    "Total number of deleted ads",
    ["category", "city", "reason"]
)

ad_renewals_total = Counter(
    "divar_ad_renewals_total",
    "Total number of renewed ads",
    ["category", "city"]
)

ad_promotions_total = Counter(
    "divar_ad_promotions_total",
    "Total number of promoted ads",
    ["category", "city", "plan"]
)

chat_starts_total = Counter(
    "divar_chat_starts_total",
    "Total number of chat sessions started with sellers",
    ["category", "city"]
)

filter_usage_total = Counter(
    "divar_filter_usage_total",
    "Total usage of search filters",
    ["category", "city", "filter_type"]
)

search_to_view_conversion_total = Counter(
    "divar_search_to_view_conversion_total",
    "Total number of searches that resulted in ad views",
    ["category", "city"]
)

# ── Platform Health ──────────────────────────────────────────────

active_users_gauge = Gauge(
    "divar_active_users",
    "Current number of concurrent active users on the platform",
)

active_listings_gauge = Gauge(
    "divar_active_listings",
    "Estimated number of live classified ads",
)

search_results_gauge = Gauge(
    "divar_avg_search_results",
    "Average search results returned per query",
)

revenue_gauge = Gauge(
    "divar_estimated_revenue_toman",
    "Estimated daily promoted-ad revenue in Toman",
    ["plan"],
)

cache_hits_total = Counter(
    "divar_cache_hits_total",
    "Listing cache hit / miss counter",
    ["result"],
)

errors_total = Counter(
    "divar_errors_total",
    "Application errors by type and endpoint",
    ["type", "endpoint"],
)
divar_search_duration_seconds = Summary(
    "divar_search_duration_seconds",
    "Time spent processing search requests in seconds",
    ["category", "city"],
)
db_query_duration_seconds = Histogram(
    "divar_db_query_duration_seconds",
    "Database query duration in seconds",
    ["query_type"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0)
)

db_query_errors_total = Counter(
    "divar_db_query_errors_total",
    "Total number of database query errors",
    ["query_type", "error_type"]
)

external_api_requests_total = Counter(
    "divar_external_api_requests_total",
    "Total number of external API requests",
    ["service", "status"]
)

external_api_duration_seconds = Histogram(
    "divar_external_api_duration_seconds",
    "External API response duration in seconds",
    ["service"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0)
)

memory_usage_bytes = Gauge(
    "divar_memory_usage_bytes",
    "Current memory usage of the service in bytes"
)

background_jobs_total = Counter(
    "divar_background_jobs_total",
    "Total number of background jobs processed",
    ["job_type", "status"]
)
