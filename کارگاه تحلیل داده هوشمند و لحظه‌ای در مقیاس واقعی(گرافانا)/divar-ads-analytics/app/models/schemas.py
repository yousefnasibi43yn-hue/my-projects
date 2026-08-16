"""Pydantic v2 schemas for Divar-style classified ads events."""

from pydantic import BaseModel, Field
from typing import Optional


class AdViewEvent(BaseModel):
    """A user viewing a classified ad listing."""

    user_id: str = Field(..., min_length=1, max_length=50)
    ad_id: str = Field(..., min_length=1, max_length=50)
    ad_title: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=50)
    city: str = Field(..., min_length=1, max_length=50)
    price_toman: int = Field(..., ge=0)
    condition: str = Field(..., pattern="^(new|used|like_new)$")
    device_type: str = Field(..., pattern="^(phone|tablet|desktop|mobile_web)$")
    view_duration_seconds: float = Field(..., ge=0)
    scrolled_to_contact: bool = Field(default=False)
    timestamp: Optional[str] = Field(default=None)


class AdPostEvent(BaseModel):
    """A seller posting a new classified ad."""

    seller_id: str = Field(..., min_length=1, max_length=50)
    ad_id: str = Field(..., min_length=1, max_length=50)
    ad_title: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=50)
    city: str = Field(..., min_length=1, max_length=50)
    price_toman: int = Field(..., ge=0)
    condition: str = Field(..., pattern="^(new|used|like_new)$")
    has_image: bool = Field(default=True)
    timestamp: Optional[str] = Field(default=None)


class SearchEvent(BaseModel):
    """A user searching for ads."""

    user_id: str = Field(..., min_length=1, max_length=50)
    query: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=50)
    city: str = Field(..., min_length=1, max_length=50)
    results_count: int = Field(..., ge=0)
    timestamp: Optional[str] = Field(default=None)


class ContactEvent(BaseModel):
    """A buyer contacting a seller (call / chat)."""

    user_id: str = Field(..., min_length=1, max_length=50)
    ad_id: str = Field(..., min_length=1, max_length=50)
    category: str = Field(..., min_length=1, max_length=50)
    city: str = Field(..., min_length=1, max_length=50)
    contact_type: str = Field(..., pattern="^(call|chat)$")
    timestamp: Optional[str] = Field(default=None)


class AdStats(BaseModel):
    """Aggregated ad platform statistics."""

    total_ad_views: int
    total_new_ads: int
    total_searches: int
    total_contacts: int
    avg_view_duration: float
    avg_price_toman: float
