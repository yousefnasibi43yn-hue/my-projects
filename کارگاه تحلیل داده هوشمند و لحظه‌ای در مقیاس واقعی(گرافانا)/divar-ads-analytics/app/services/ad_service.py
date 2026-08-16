"""
Business logic for Divar-style classified ad events.

Events are recorded as Prometheus metrics — VictoriaMetrics scrapes /metrics
and stores all time series for Grafana dashboards.
"""

import random

from app.metrics.metrics import (
 ad_views_total,
    ad_posts_total,
    searches_total,
    contacts_total,
    favorites_total,
    ad_price_toman,
    view_duration_seconds,
    scroll_to_contact_total,
    cache_hits_total,
    errors_total,
    ad_edits_total,
    ad_deletions_total,
    ad_renewals_total,
    ad_promotions_total,
    chat_starts_total,
    filter_usage_total,
    search_to_view_conversion_total,
    db_query_duration_seconds,
    db_query_errors_total,
    external_api_requests_total,
    external_api_duration_seconds,
    memory_usage_bytes,
    background_jobs_total,
    divar_search_duration_seconds,
)


_current_active_users = 0
_current_active_listings = 125_000


def record_ad_view(event_data: dict) -> bool:
    try:
        ad_views_total.labels(
            category=event_data["category"],
            city=event_data["city"],
            device_type=event_data["device_type"],
        ).inc()

        view_duration_seconds.labels(category=event_data["category"]).observe(
            event_data["view_duration_seconds"]
        )

        ad_price_toman.labels(
            category=event_data["category"],
            city=event_data["city"],
        ).observe(event_data["price_toman"])

        if event_data.get("scrolled_to_contact"):
            scroll_to_contact_total.labels(
                category=event_data["category"],
                city=event_data["city"],
            ).inc()

        if random.random() < 0.08:
            favorites_total.labels(
                category=event_data["category"],
                city=event_data["city"],
            ).inc()

        if random.random() < 0.78:
            cache_hits_total.labels(result="hit").inc()
        else:
            cache_hits_total.labels(result="miss").inc()

        return True
    except Exception as exc:
        errors_total.labels(type="record_error", endpoint="/api/ads/view").inc()
        print(f"Error recording ad view: {exc}")
        return False


def record_ad_post(event_data: dict) -> bool:
    try:
        ad_posts_total.labels(
            category=event_data["category"],
            city=event_data["city"],
            condition=event_data["condition"],
        ).inc()

        ad_price_toman.labels(
            category=event_data["category"],
            city=event_data["city"],
        ).observe(event_data["price_toman"])

        global _current_active_listings
        _current_active_listings += 1
        from app.metrics.metrics import active_listings_gauge
        active_listings_gauge.set(_current_active_listings)

        return True
    except Exception as exc:
        errors_total.labels(type="record_error", endpoint="/api/ads/post").inc()
        print(f"Error recording ad post: {exc}")
        return False


def record_search(event_data: dict) -> bool:
    try:
        searches_total.labels(
            category=event_data["category"],
            city=event_data["city"],
        ).inc()

        divar_search_duration_seconds.labels(
            category=event_data["category"],
            city=event_data["city"],
        ).observe(random.uniform(0.2, 1.5))

        return True
    except Exception as exc:
        errors_total.labels(type="record_error", endpoint="/api/search").inc()
        print(f"Error recording search: {exc}")
        return False



def record_contact(event_data: dict) -> bool:
    try:
        contacts_total.labels(
            category=event_data["category"],
            city=event_data["city"],
            contact_type=event_data["contact_type"],
        ).inc()
        return True
    except Exception as exc:
        errors_total.labels(type="record_error", endpoint="/api/contact").inc()
        print(f"Error recording contact: {exc}")
        return False


def update_active_users(count: int):
    global _current_active_users
    _current_active_users = count
    from app.metrics.metrics import active_users_gauge
    active_users_gauge.set(count)


def get_active_users() -> int:
    return _current_active_users


def update_search_results(avg_results: float):
    from app.metrics.metrics import search_results_gauge
    search_results_gauge.set(avg_results)


def update_revenue(plans: dict):
    from app.metrics.metrics import revenue_gauge
    for plan_name, amount in plans.items():
        revenue_gauge.labels(plan=plan_name).set(amount)


def get_active_listings() -> int:
    return _current_active_listings

def record_ad_edit(category: str, city: str):
    ad_edits_total.labels(category=category, city=city).inc()


def record_ad_deletion(category: str, city: str, reason: str):
    ad_deletions_total.labels(category=category, city=city, reason=reason).inc()


def record_ad_renewal(category: str, city: str):
    ad_renewals_total.labels(category=category, city=city).inc()


def record_ad_promotion(category: str, city: str, plan: str):
    ad_promotions_total.labels(category=category, city=city, plan=plan).inc()


def record_chat_start(category: str, city: str):
    chat_starts_total.labels(category=category, city=city).inc()


def record_filter_usage(category: str, city: str, filter_type: str):
    filter_usage_total.labels(category=category, city=city, filter_type=filter_type).inc()


def record_search_to_view_conversion(category: str, city: str):
    search_to_view_conversion_total.labels(category=category, city=city).inc()

def record_db_query_duration(query_type: str, duration: float):
    db_query_duration_seconds.labels(query_type=query_type).observe(duration)


def record_db_query_error(query_type: str, error_type: str):
    db_query_errors_total.labels(query_type=query_type, error_type=error_type).inc()


def record_external_api_request(service: str, status: str):
    external_api_requests_total.labels(service=service, status=status).inc()


def record_external_api_duration(service: str, duration: float):
    external_api_duration_seconds.labels(service=service).observe(duration)


def update_memory_usage(memory_bytes: float):
    memory_usage_bytes.set(memory_bytes)


def record_background_job(job_type: str, status: str):
    background_jobs_total.labels(job_type=job_type, status=status).inc()
