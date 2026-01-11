from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_db
from ...models.property import Property
from ...schemas.property import PropertyResponse, PropertyListResponse

router = APIRouter()


@router.get("/", response_model=PropertyListResponse)
async def list_properties(
    skip: int = 0,
    limit: int = 50,
    source: str | None = None,
    min_bedrooms: int | None = None,
    max_price: float | None = None,
    sort_by: str = "value_score",
    db: AsyncSession = Depends(get_db),
):
    """List all cached properties with optional filtering."""
    query = select(Property)

    # Apply filters
    if source:
        query = query.where(Property.source == source)
    if min_bedrooms:
        query = query.where(Property.bedrooms >= min_bedrooms)
    if max_price:
        query = query.where(Property.total_price <= max_price)

    # Sorting
    if sort_by == "value_score":
        query = query.order_by(Property.value_score.desc().nullslast())
    elif sort_by == "price":
        query = query.order_by(Property.total_price.asc())
    elif sort_by == "reviews":
        query = query.order_by(Property.review_score.desc().nullslast())
    elif sort_by == "beach":
        query = query.order_by(Property.beach_walk_minutes.asc().nullslast())

    # Get total count
    count_query = select(func.count()).select_from(Property)
    if source:
        count_query = count_query.where(Property.source == source)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    properties = result.scalars().all()

    # Get last updated time
    last_updated_query = select(func.max(Property.last_updated))
    last_updated_result = await db.execute(last_updated_query)
    last_refreshed = last_updated_result.scalar()

    return PropertyListResponse(
        properties=[PropertyResponse.model_validate(p) for p in properties],
        total=total,
        last_refreshed=last_refreshed,
    )


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single property by ID."""
    query = select(Property).where(Property.id == property_id)
    result = await db.execute(query)
    property = result.scalar_one_or_none()

    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    return PropertyResponse.model_validate(property)


@router.delete("/{property_id}")
async def delete_property(
    property_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a property from cache."""
    query = select(Property).where(Property.id == property_id)
    result = await db.execute(query)
    property = result.scalar_one_or_none()

    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    await db.delete(property)
    await db.commit()

    return {"message": f"Property {property_id} deleted"}


@router.delete("/")
async def clear_all_properties(
    db: AsyncSession = Depends(get_db),
):
    """Clear all cached properties."""
    from sqlalchemy import delete

    await db.execute(delete(Property))
    await db.commit()

    return {"message": "All properties cleared"}
