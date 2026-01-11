from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_db
from ...models.search_config import SearchConfig
from ...schemas.property import (
    SearchConfigCreate,
    SearchConfigResponse,
    SearchRequest,
    RefreshResponse,
    PropertyListResponse,
    PropertyResponse,
    ScoringWeights,
)
from ...models.property import Property

router = APIRouter()


@router.get("/config", response_model=SearchConfigResponse | None)
async def get_current_config(
    db: AsyncSession = Depends(get_db),
):
    """Get the current/most recent search configuration."""
    query = select(SearchConfig).order_by(SearchConfig.updated_at.desc()).limit(1)
    result = await db.execute(query)
    config = result.scalar_one_or_none()

    if not config:
        return None

    return SearchConfigResponse.model_validate(config)


@router.post("/config", response_model=SearchConfigResponse)
async def create_or_update_config(
    config: SearchConfigCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create or update search configuration."""
    # Create new config
    db_config = SearchConfig(
        origin_city=config.origin_city,
        origin_state=config.origin_state,
        origin_latitude=config.origin_latitude,
        origin_longitude=config.origin_longitude,
        max_distance_miles=config.max_distance_miles,
        min_bedrooms=config.min_bedrooms,
        max_bedrooms=config.max_bedrooms,
        min_guests=config.min_guests,
        max_price_per_week=config.max_price_per_week,
        date_start=config.date_start,
        date_end=config.date_end,
        max_beach_walk_minutes=config.max_beach_walk_minutes,
        required_amenities=config.required_amenities,
        scoring_weights=config.scoring_weights.model_dump(),
        name=config.name,
    )

    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)

    return SearchConfigResponse.model_validate(db_config)


@router.post("/", response_model=PropertyListResponse)
async def search_properties(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Search for properties based on configuration.

    If use_cached=True, returns cached results.
    If use_cached=False or no cache exists, triggers a fresh search.
    """
    # For now, just return cached properties
    # Real scraping will be added in Session 2
    query = select(Property).order_by(Property.value_score.desc().nullslast())
    result = await db.execute(query)
    properties = result.scalars().all()

    return PropertyListResponse(
        properties=[PropertyResponse.model_validate(p) for p in properties],
        total=len(properties),
        last_refreshed=properties[0].last_updated if properties else None,
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_data(
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a fresh data fetch from all sources.

    This will be implemented in Session 2 with actual scraper integration.
    For now, returns a placeholder response.
    """
    # Placeholder - actual scraping will be added in Session 2
    return RefreshResponse(
        message="Refresh functionality will be implemented with scraper integration",
        properties_found=0,
        sources_searched=[],
        duration_seconds=0.0,
    )


@router.post("/score")
async def recalculate_scores(
    weights: ScoringWeights,
    db: AsyncSession = Depends(get_db),
):
    """
    Recalculate value scores for all properties with new weights.

    This will be fully implemented in Session 5.
    """
    # Placeholder - scoring will be added in Session 5
    return {
        "message": "Score recalculation will be implemented in Session 5",
        "weights": weights.model_dump(),
    }
