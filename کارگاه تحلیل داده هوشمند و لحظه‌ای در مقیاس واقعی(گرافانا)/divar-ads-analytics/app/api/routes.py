"""
API routes for the Divar Ads Analytics service.

Endpoints mirror a classified-ads platform like divar.ir:
  POST /api/ads/view     — Record an ad page view
  POST /api/ads/post     — Record a new ad listing
  POST /api/search       — Record a search query
  POST /api/contact      — Record buyer contact (call/chat)
  GET  /api/stats        — Aggregated stats from VictoriaMetrics
  GET  /api/active       — Current active user count
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    AdViewEvent,
    AdPostEvent,
    SearchEvent,
    ContactEvent,
    AdStats,
)
from app.services.ad_service import (
    record_ad_view,
    record_ad_post,
    record_search,
    record_contact,
    get_active_users,
)
from app.db.vm_client import query_instant, extract_scalar

router = APIRouter()


@router.post("/ads/view", status_code=201, summary="Record an ad view")
async def create_ad_view(event: AdViewEvent):
    """Record a user viewing a classified ad listing."""
    if not record_ad_view(event.model_dump()):
        raise HTTPException(status_code=503, detail="Failed to record ad view")
    return {"status": "recorded", "ad_id": event.ad_id, "ad_title": event.ad_title}


@router.post("/ads/post", status_code=201, summary="Record a new ad post")
async def create_ad_post(event: AdPostEvent):
    """Record a seller posting a new classified ad."""
    if not record_ad_post(event.model_dump()):
        raise HTTPException(status_code=503, detail="Failed to record ad post")
    return {"status": "recorded", "ad_id": event.ad_id, "category": event.category}


@router.post("/search", status_code=201, summary="Record a search query")
async def create_search(event: SearchEvent):
    """Record a user search on the platform."""
    if not record_search(event.model_dump()):
        raise HTTPException(status_code=503, detail="Failed to record search")
    return {"status": "recorded", "query": event.query, "results_count": event.results_count}


@router.post("/contact", status_code=201, summary="Record buyer contact")
async def create_contact(event: ContactEvent):
    """Record a buyer contacting a seller via call or chat."""
    if not record_contact(event.model_dump()):
        raise HTTPException(status_code=503, detail="Failed to record contact")
    return {"status": "recorded", "ad_id": event.ad_id, "contact_type": event.contact_type}


@router.get("/stats", response_model=AdStats, summary="Get platform statistics")
async def get_stats():
    """
    Get aggregated statistics from VictoriaMetrics (last 1 hour).

    Uses PromQL instant queries against the VictoriaMetrics API.
    """
    try:
        views = extract_scalar(await query_instant("sum(increase(divar_ad_views_total[1h]))"))
        posts = extract_scalar(await query_instant("sum(increase(divar_ad_posts_total[1h]))"))
        searches = extract_scalar(await query_instant("sum(increase(divar_searches_total[1h]))"))
        contacts = extract_scalar(await query_instant("sum(increase(divar_contacts_total[1h]))"))
        avg_duration = extract_scalar(
            await query_instant(
                "sum(rate(divar_view_duration_seconds_sum[1h])) "
                "/ sum(rate(divar_view_duration_seconds_count[1h]))"
            )
        )
        avg_price = extract_scalar(
            await query_instant(
                "sum(rate(divar_ad_price_toman_sum[1h])) "
                "/ sum(rate(divar_ad_price_toman_count[1h]))"
            )
        )

        return AdStats(
            total_ad_views=int(views),
            total_new_ads=int(posts),
            total_searches=int(searches),
            total_contacts=int(contacts),
            avg_view_duration=round(avg_duration, 2),
            avg_price_toman=round(avg_price, 0),
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"VictoriaMetrics query error: {exc}") from exc


@router.get("/active", summary="Get active user count")
async def get_active():
    """Get the current number of concurrent active users."""
    return {"active_users": get_active_users()}
