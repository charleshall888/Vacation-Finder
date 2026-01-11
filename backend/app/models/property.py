from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Property(Base):
    __tablename__ = "properties"

    # Primary key: combination of source and external ID
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    source: Mapped[str] = mapped_column(String(50), index=True)  # airbnb, vrbo, vacasa, local
    name: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(1000))

    # Location
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    beach_walk_minutes: Mapped[int] = mapped_column(Integer, nullable=True)
    distance_from_origin_miles: Mapped[float] = mapped_column(Float, nullable=True)
    region: Mapped[str] = mapped_column(String(100), nullable=True)  # Gulf Coast FL, SC Coast, etc.

    # Specs
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[float] = mapped_column(Float, nullable=True)
    max_guests: Mapped[int] = mapped_column(Integer, nullable=True)

    # Pricing
    price_per_week: Mapped[float] = mapped_column(Float)
    cleaning_fee: Mapped[float] = mapped_column(Float, default=0.0)
    total_price: Mapped[float] = mapped_column(Float)

    # Quality
    review_score: Mapped[float] = mapped_column(Float, nullable=True)  # 0-5 scale
    review_count: Mapped[int] = mapped_column(Integer, default=0)

    # Amenities stored as JSON
    amenities: Mapped[dict] = mapped_column(JSON, default=dict)
    # Expected keys: has_full_kitchen, parking_spots, has_pool, has_hot_tub, pet_friendly

    # Photos stored as JSON array
    photos: Mapped[list] = mapped_column(JSON, default=list)

    # Meta
    verified: Mapped[bool] = mapped_column(Boolean, default=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Computed value score (updated when weights change)
    value_score: Mapped[float] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return f"<Property {self.id}: {self.name[:50]}... ({self.source})>"
