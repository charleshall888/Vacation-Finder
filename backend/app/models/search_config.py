from datetime import date, datetime
from sqlalchemy import String, Float, Integer, Date, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class SearchConfig(Base):
    __tablename__ = "search_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Origin location
    origin_city: Mapped[str] = mapped_column(String(100))
    origin_state: Mapped[str] = mapped_column(String(50))
    origin_latitude: Mapped[float] = mapped_column(Float, nullable=True)
    origin_longitude: Mapped[float] = mapped_column(Float, nullable=True)

    # Distance
    max_distance_miles: Mapped[int] = mapped_column(Integer)

    # Property requirements
    min_bedrooms: Mapped[int] = mapped_column(Integer)
    max_bedrooms: Mapped[int] = mapped_column(Integer)
    min_guests: Mapped[int] = mapped_column(Integer, nullable=True)

    # Pricing
    max_price_per_week: Mapped[float] = mapped_column(Float)

    # Dates
    date_start: Mapped[date] = mapped_column(Date)
    date_end: Mapped[date] = mapped_column(Date)

    # Beach proximity
    max_beach_walk_minutes: Mapped[int] = mapped_column(Integer)

    # Required amenities stored as JSON array
    required_amenities: Mapped[list] = mapped_column(JSON, default=list)
    # Example: ["full_kitchen", "parking_3plus"]

    # Scoring weights stored as JSON
    scoring_weights: Mapped[dict] = mapped_column(
        JSON,
        default=lambda: {
            "price": 0.30,
            "reviews": 0.25,
            "beach": 0.20,
            "amenities": 0.15,
            "distance": 0.10,
        },
    )

    # Meta
    name: Mapped[str] = mapped_column(String(100), nullable=True)  # Optional saved search name
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<SearchConfig {self.id}: {self.origin_city}, {self.origin_state}>"
