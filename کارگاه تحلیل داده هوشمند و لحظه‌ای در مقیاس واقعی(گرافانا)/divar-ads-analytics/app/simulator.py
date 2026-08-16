"""
Background simulator for Divar-style classified ads traffic.

Generates realistic ad views, posts, searches, and contact events so the
Grafana dashboard has live data immediately after docker compose up.
"""

import asyncio
import random
import string

from app.services.ad_service import (
    record_ad_view,
    record_ad_post,
    record_search,
    record_contact,
    update_active_users,
    update_search_results,
    update_revenue,
    record_ad_edit,
    record_ad_deletion,
    record_ad_renewal,
    record_ad_promotion,
    record_chat_start,
    record_filter_usage,
    record_search_to_view_conversion,
    record_db_query_duration,
    record_db_query_error,
    record_external_api_request,
    record_external_api_duration,
    update_memory_usage,
    record_background_job,
)


CATEGORIES = [
    "real-estate",
    "vehicles",
    "electronics",
    "home-appliances",
    "services",
    "jobs",
    "personal",
    "leisure",
]

CITIES = ["tehran", "isfahan", "mashhad", "shiraz", "tabriz", "karaj", "ahvaz", "qom"]
CITY_WEIGHTS = [0.38, 0.12, 0.10, 0.08, 0.08, 0.10, 0.07, 0.07]

DEVICES = ["phone", "tablet", "desktop", "mobile_web"]
DEVICE_WEIGHTS = [0.55, 0.08, 0.22, 0.15]

CONDITIONS = ["new", "used", "like_new"]
CONDITION_WEIGHTS = [0.15, 0.65, 0.20]

SAMPLE_ADS = [
    {"title": "آپارتمان ۸۵ متری نوساز در سعادت‌آباد", "category": "real-estate", "price": 4_500_000_000},
    {"title": "پژو ۲۰۶ تیپ ۲ مدل ۹۸", "category": "vehicles", "price": 680_000_000},
    {"title": "آیفون ۱۵ پرو ۲۵۶ گیگ", "category": "electronics", "price": 62_000_000},
    {"title": "یخچال ساید بای سامسونگ", "category": "home-appliances", "price": 38_000_000},
    {"title": "نقاش ساختمان با ۱۰ سال سابقه", "category": "services", "price": 0},
    {"title": "استخدام فروشنده فروشگاه پوشاک", "category": "jobs", "price": 0},
    {"title": "مبل راحتی ۷ نفره", "category": "personal", "price": 18_000_000},
    {"title": "دوچرخه کوهستان", "category": "leisure", "price": 12_000_000},
    {"title": "ویلا ۲۰۰ متری در شمال", "category": "real-estate", "price": 8_000_000_000},
    {"title": "تویوتا کرولا ۲۰۱۹", "category": "vehicles", "price": 1_850_000_000},
    {"title": "لپ‌تاپ لنوو ThinkPad", "category": "electronics", "price": 28_000_000},
    {"title": "ماشین لباسشویی ال‌جی ۸ کیلو", "category": "home-appliances", "price": 22_000_000},
]

SEARCH_QUERIES = [
    "آپارتمان شمال تهران",
    "پژو ۲۰۶",
    "آیفون",
    "یخچال",
    "استخدام",
    "مبل",
    "دوچرخه",
    "ویلا",
    "پراید",
    "لپتاپ",
]


def _random_ad_id() -> str:
    return "ad_" + "".join(random.choices(string.digits, k=6))


def _generate_view_event() -> dict:
    ad = random.choice(SAMPLE_ADS)
    city = random.choices(CITIES, weights=CITY_WEIGHTS, k=1)[0]
    duration = random.expovariate(1 / 45)
    duration = min(duration, 600)

    return {
        "user_id": f"user_{random.randint(1, 500)}",
        "ad_id": _random_ad_id(),
        "ad_title": ad["title"],
        "category": ad["category"],
        "city": city,
        "price_toman": ad["price"] or random.randint(500_000, 50_000_000),
        "condition": random.choices(CONDITIONS, weights=CONDITION_WEIGHTS, k=1)[0],
        "device_type": random.choices(DEVICES, weights=DEVICE_WEIGHTS, k=1)[0],
        "view_duration_seconds": round(duration, 2),
        "scrolled_to_contact": random.random() < 0.35,
    }


def _generate_post_event() -> dict:
    ad = random.choice(SAMPLE_ADS)
    city = random.choices(CITIES, weights=CITY_WEIGHTS, k=1)[0]

    return {
        "seller_id": f"seller_{random.randint(1, 300)}",
        "ad_id": _random_ad_id(),
        "ad_title": ad["title"],
        "category": ad["category"],
        "city": city,
        "price_toman": ad["price"] or random.randint(1_000_000, 100_000_000),
        "condition": random.choices(CONDITIONS, weights=CONDITION_WEIGHTS, k=1)[0],
        "has_image": random.random() < 0.92,
    }


def _generate_search_event() -> dict:
    category = random.choice(CATEGORIES)
    city = random.choices(CITIES, weights=CITY_WEIGHTS, k=1)[0]

    return {
        "user_id": f"user_{random.randint(1, 500)}",
        "query": random.choice(SEARCH_QUERIES),
        "category": category,
        "city": city,
        "results_count": random.randint(0, 120),
    }


def _generate_contact_event() -> dict:
    ad = random.choice(SAMPLE_ADS)
    city = random.choices(CITIES, weights=CITY_WEIGHTS, k=1)[0]

    return {
        "user_id": f"user_{random.randint(1, 500)}",
        "ad_id": _random_ad_id(),
        "category": ad["category"],
        "city": city,
        "contact_type": random.choices(["call", "chat"], weights=[0.6, 0.4], k=1)[0],
    }


async def start_simulator():
    """Main simulator loop — runs as a background asyncio task."""
    await asyncio.sleep(6)
    print("Divar Ads Simulator started — generating classified ads traffic...")

    base_revenue = {
        "ladder": 250_000,
        "urgent": 180_000,
        "featured": 420_000,
    }

    event_count = 0

    while True:
        try:
            num_events = random.choices([2, 3, 4, 5], weights=[0.25, 0.30, 0.30, 0.15], k=1)[0]

            for _ in range(num_events):
                roll = random.random()
                if roll < 0.55:
                    record_ad_view(_generate_view_event())
                elif roll < 0.72:
                    record_search(_generate_search_event())
                elif roll < 0.85:
                    record_ad_post(_generate_post_event())
                else:
                    record_contact(_generate_contact_event())
                event_count += 1

            active = random.randint(80, 1200)
            update_active_users(active)
            update_search_results(round(random.uniform(15, 85), 1))

            for plan, base in base_revenue.items():
                update_revenue({plan: round(base * random.uniform(0.95, 1.08))})

            if event_count % 30 == 0:
                print(f"Simulated {event_count} events | Active users: {active}")

        except Exception as exc:
            print(f"Simulator error: {exc}")

        await asyncio.sleep(random.uniform(1.0, 2.5))
def simulate_ad_edits():
    categories = ["real-estate", "vehicles", "electronics"]
    cities = ["tehran", "mashhad", "shiraz"]

    for _ in range(random.randint(5, 15)):
        category = random.choice(categories)
        city = random.choice(cities)
        record_ad_edit(category, city)


def simulate_ad_deletions():
    categories = ["real-estate", "vehicles", "electronics"]
    cities = ["tehran", "mashhad", "shiraz"]
    reasons = ["sold", "expired", "user_removed"]

    for _ in range(random.randint(2, 8)):
        category = random.choice(categories)
        city = random.choice(cities)
        reason = random.choice(reasons)
        record_ad_deletion(category, city, reason)


def simulate_ad_renewals():
    categories = ["real-estate", "vehicles", "electronics"]
    cities = ["tehran", "mashhad", "shiraz"]

    for _ in range(random.randint(3, 10)):
        category = random.choice(categories)
        city = random.choice(cities)
        record_ad_renewal(category, city)


def simulate_ad_promotions():
    categories = ["real-estate", "vehicles", "electronics"]
    cities = ["tehran", "mashhad", "shiraz"]
    plans = ["silver", "gold", "vip"]

    for _ in range(random.randint(2, 7)):
        category = random.choice(categories)
        city = random.choice(cities)
        plan = random.choice(plans)
        record_ad_promotion(category, city, plan)


def simulate_chat_starts():
    categories = ["real-estate", "vehicles", "electronics"]
    cities = ["tehran", "mashhad", "shiraz"]

    for _ in range(random.randint(5, 20)):
        category = random.choice(categories)
        city = random.choice(cities)
        record_chat_start(category, city)


def simulate_filter_usage():
    categories = ["real-estate", "vehicles", "electronics"]
    cities = ["tehran", "mashhad", "shiraz"]
    filter_types = ["price", "city", "category", "has_photo"]

    for _ in range(random.randint(10, 25)):
        category = random.choice(categories)
        city = random.choice(cities)
        filter_type = random.choice(filter_types)
        record_filter_usage(category, city, filter_type)


def simulate_search_to_view_conversion():
    categories = ["real-estate", "vehicles", "electronics"]
    cities = ["tehran", "mashhad", "shiraz"]

    for _ in range(random.randint(5, 15)):
        category = random.choice(categories)
        city = random.choice(cities)
        record_search_to_view_conversion(category, city)
def simulate_db_metrics():
    query_types = ["insert_ad", "search_ads", "update_ad", "delete_ad"]
    error_types = ["timeout", "connection", "syntax"]

    for _ in range(random.randint(5, 15)):
        query_type = random.choice(query_types)
        duration = round(random.uniform(0.001, 0.8), 4)
        record_db_query_duration(query_type, duration)

    for _ in range(random.randint(0, 3)):
        query_type = random.choice(query_types)
        error_type = random.choice(error_types)
        record_db_query_error(query_type, error_type)


def simulate_external_api_metrics():
    services = ["sms", "payment", "maps"]
    statuses = ["success", "failed"]

    for _ in range(random.randint(3, 10)):
        service = random.choice(services)
        status = random.choice(statuses)
        duration = round(random.uniform(0.02, 1.5), 4)

        record_external_api_request(service, status)
        record_external_api_duration(service, duration)


def simulate_memory_usage():
    memory_bytes = random.randint(150_000_000, 450_000_000)
    update_memory_usage(memory_bytes)


def simulate_background_jobs():
    job_types = ["sync_stats", "cleanup_ads", "generate_report"]
    statuses = ["success", "failed"]

    for _ in range(random.randint(2, 6)):
        job_type = random.choice(job_types)
        status = random.choice(statuses)
        record_background_job(job_type, status)
