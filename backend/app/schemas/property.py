from datetime import date, datetime
from pydantic import BaseModel, Field


# --- Amenities Schema ---
class AmenitiesSchema(BaseModel):
    has_full_kitchen: bool = False
    parking_spots: int = 0
    has_pool: bool = False
    has_hot_tub: bool = False
    pet_friendly: bool = False


# --- Property Schemas ---
class PropertyBase(BaseModel):
    source: str
    name: str
    url: str

    # Location
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    beach_walk_minutes: int | None = None
    distance_from_origin_miles: float | None = None
    region: str | None = None

    # Specs
    bedrooms: int
    bathrooms: float | None = None
    max_guests: int | None = None

    # Pricing
    price_per_week: float
    cleaning_fee: float = 0.0
    total_price: float

    # Quality
    review_score: float | None = None
    review_count: int = 0

    # Amenities
    amenities: dict = Field(default_factory=dict)

    # Photos
    photos: list[str] = Field(default_factory=list)

    # Meta
    verified: bool = True


class PropertyCreate(PropertyBase):
    id: str


class PropertyResponse(PropertyBase):
    id: str
    last_updated: datetime
    value_score: float | None = None

    class Config:
        from_attributes = True


class PropertyListResponse(BaseModel):
    properties: list[PropertyResponse]
    total: int
    last_refreshed: datetime | None = None


# --- Scoring Weights Schema ---
class ScoringWeights(BaseModel):
    price: float = Field(0.30, ge=0, le=1)
    reviews: float = Field(0.25, ge=0, le=1)
    beach: float = Field(0.20, ge=0, le=1)
    amenities: float = Field(0.15, ge=0, le=1)
    distance: float = Field(0.10, ge=0, le=1)


# --- Search Config Schemas ---
class SearchConfigBase(BaseModel):
    # Origin
    origin_city: str = "Athens"
    origin_state: str = "GA"
    origin_latitude: float | None = None
    origin_longitude: float | None = None

    # Distance
    max_distance_miles: int = 400

    # Property requirements
    min_bedrooms: int = 7
    max_bedrooms: int = 9
    min_guests: int | None = 12

    # Pricing
    max_price_per_week: float = 15000.0

    # Dates
    date_start: date
    date_end: date

    # Beach proximity
    max_beach_walk_minutes: int = 10

    # Required amenities
    required_amenities: list[str] = Field(default_factory=lambda: ["full_kitchen", "parking_3plus"])

    # Scoring weights
    scoring_weights: ScoringWeights = Field(default_factory=ScoringWeights)

    # Name (optional)
    name: str | None = None


class SearchConfigCreate(SearchConfigBase):
    pass


class SearchConfigResponse(SearchConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Search Request/Response ---
class SearchRequest(BaseModel):
    config: SearchConfigCreate | None = None
    use_cached: bool = True


class RefreshResponse(BaseModel):
    message: str
    properties_found: int
    sources_searched: list[str]
    duration_seconds: float
