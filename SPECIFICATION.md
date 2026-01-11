# Vacation Finder - Project Specification

## Overview

A flexible vacation rental aggregator that searches multiple platforms to find and compare beach house rentals. Built with Python backend and Vue frontend, designed for reuse across different vacation searches.

## Current Search Criteria (Parameterized)

| Parameter | Value |
|-----------|-------|
| **Bedrooms** | 7-9 |
| **Group Size** | 12-16 people |
| **Location Origin** | Athens, Georgia, USA |
| **Max Distance** | ~400 mile radius (≈7 hours drive) |
| **Target Regions** | Gulf Coast FL, SC Coast, GA Coast (all within range) |
| **Budget** | $15,000/week |
| **Date Options** | June 13-20, 2026 OR June 27 - July 4, 2026 |
| **Beach Proximity** | < 10 minute walk |

## Required Amenities (Deal-Breakers)

- Full kitchen (essential for cooking for large group)
- Parking for 3+ vehicles (multiple families driving separately)

## Data Sources

### Primary (API Integration)
1. **Airbnb** - via MCP or unofficial API
2. **VRBO/HomeAway** - Expedia Group API

### Secondary
3. **Vacasa** - Professional property management
4. **Local Rental Agencies** - Auto-discovered per target beach region

### Data Source Rules
- Airbnb/VRBO: Exclude listings with no reviews OR unclear beach distance
- Local agencies: May lack reviews; include with "unverified" flag
- Vacasa: Include all matching properties (professionally managed = reliable)

## Architecture

### Backend (Python)

```
vacation-finder/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── search.py       # Search endpoints
│   │   │   ├── properties.py   # Property details
│   │   │   └── config.py       # Search config CRUD
│   │   └── app.py
│   ├── scrapers/
│   │   ├── base.py             # Abstract scraper interface
│   │   ├── airbnb.py
│   │   ├── vrbo.py
│   │   ├── vacasa.py
│   │   └── local_agencies.py   # Auto-discovery + scraping
│   ├── services/
│   │   ├── distance.py         # Radius calculation from origin
│   │   ├── scoring.py          # Weighted value scoring
│   │   ├── normalization.py    # Standardize data across sources
│   │   └── discovery.py        # Find local rental agencies
│   ├── models/
│   │   ├── property.py         # Unified property model
│   │   └── search_config.py    # Saved search parameters
│   └── database/
│       └── sqlite.py           # Local SQLite for caching results
```

### Frontend (Vue)

```
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchConfig.vue      # Parameter inputs
│   │   │   ├── PropertyCard.vue      # Individual property display
│   │   │   ├── ComparisonView.vue    # Side-by-side 3-4 cards
│   │   │   ├── ScoreSliders.vue      # Adjustable weight controls
│   │   │   └── RefreshButton.vue     # Manual data refresh trigger
│   │   ├── views/
│   │   │   ├── SearchView.vue
│   │   │   └── ResultsView.vue
│   │   └── stores/
│   │       ├── properties.js
│   │       └── searchConfig.js
```

## Core Features

### 1. Unified Property Model

All sources normalized to:

```python
@dataclass
class Property:
    id: str
    source: str                  # airbnb, vrbo, vacasa, local
    name: str
    url: str

    # Location
    address: str
    beach_walk_minutes: int      # Required < 10
    distance_from_origin_miles: float
    region: str                  # "Gulf Coast FL", "SC Coast", etc.

    # Specs
    bedrooms: int
    bathrooms: float
    max_guests: int

    # Pricing
    price_per_week: float
    cleaning_fee: float
    total_price: float           # All-in cost

    # Quality
    review_score: float | None   # 0-5 scale, None for unverified
    review_count: int

    # Amenities
    has_full_kitchen: bool       # Required
    parking_spots: int           # Required >= 3
    has_pool: bool
    has_hot_tub: bool
    pet_friendly: bool

    # Meta
    verified: bool               # Has reviews + clear beach distance
    photos: list[str]
    last_updated: datetime
```

### 2. Weighted Scoring System

Default weights (user-adjustable via sliders):

| Factor | Default Weight | Calculation |
|--------|---------------|-------------|
| Price | 30% | Inverse of total_price (lower = better) |
| Reviews | 25% | review_score * log(review_count + 1) |
| Beach Proximity | 20% | Inverse of beach_walk_minutes |
| Amenities | 15% | Bonus points for pool, hot tub, etc. |
| Drive Distance | 10% | Inverse of distance_from_origin |

```python
def calculate_value_score(property: Property, weights: dict) -> float:
    scores = {
        'price': normalize_inverse(property.total_price, min_price, max_price),
        'reviews': normalize(property.review_score * log(property.review_count + 1)),
        'beach': normalize_inverse(property.beach_walk_minutes, 0, 10),
        'amenities': calculate_amenity_score(property),
        'distance': normalize_inverse(property.distance_from_origin_miles, 0, 400)
    }
    return sum(scores[k] * weights[k] for k in weights)
```

### 3. Comparison UI

Side-by-side card layout showing 3-4 properties:

```
┌─────────────────┬─────────────────┬─────────────────┐
│  🏠 Property A  │  🏠 Property B  │  🏠 Property C  │
│  ─────────────  │  ─────────────  │  ─────────────  │
│  [Photo]        │  [Photo]        │  [Photo]        │
│                 │                 │                 │
│  $14,200 total  │  $13,800 total  │  $15,000 total  │
│  ⭐ 4.9 (127)   │  ⭐ 4.7 (89)    │  ⭐ 4.8 (203)   │
│  🚶 4 min walk  │  🚶 7 min walk  │  🚶 2 min walk  │
│  🛏️ 8 bed/6 bath│  🛏️ 7 bed/5 bath│  🛏️ 9 bed/7 bath│
│  🚗 5.2 hrs     │  🚗 6.1 hrs     │  🚗 4.8 hrs     │
│                 │                 │                 │
│  ✅ Kitchen     │  ✅ Kitchen     │  ✅ Kitchen     │
│  ✅ 4 parking   │  ✅ 3 parking   │  ✅ 5 parking   │
│  ✅ Pool        │  ❌ No pool     │  ✅ Pool        │
│                 │                 │                 │
│  VALUE: 87/100  │  VALUE: 79/100  │  VALUE: 91/100  │
│  [View Listing] │  [View Listing] │  [View Listing] │
└─────────────────┴─────────────────┴─────────────────┘

[Weight Sliders]
Price:     ████████░░ 30%
Reviews:   █████░░░░░ 25%
Beach:     ████░░░░░░ 20%
Amenities: ███░░░░░░░ 15%
Distance:  ██░░░░░░░░ 10%

[🔄 Refresh Data]
```

### 4. Data Refresh Strategy

- **No automatic refresh** - data fetched only on manual trigger
- Refresh button triggers parallel scraping of all sources
- Loading state shows progress per source
- Results cached in SQLite until next refresh
- Last updated timestamp displayed prominently

## Local Agency Discovery

For each target beach region, the system will:

1. Search for "[region] beach house rentals"
2. Identify local property management companies
3. Attempt to scrape their listings
4. Flag as "unverified" (no standardized reviews)

Target regions to scan:
- **Gulf Coast FL**: Destin, Panama City Beach, 30A, Pensacola
- **SC Coast**: Hilton Head, Myrtle Beach, Kiawah, Isle of Palms
- **GA Coast**: Tybee Island, Jekyll Island, St. Simons Island

## API Integrations

### MCP Integrations (Preferred)
- **Airbnb MCP** - If available, use for structured API access
- **Mapping MCP** - For distance calculations if needed

### Direct APIs / Scraping
- VRBO: Expedia Rapid API or scraping
- Vacasa: Direct scraping (no public API)
- Local agencies: Per-site scraping with rate limiting

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Distance calculation | Approximate radius (~400mi) | Faster, no mapping API dependency |
| Data freshness | Manual refresh only | User controls when to query, avoids stale data surprises |
| Database | SQLite | Simple, local, no infrastructure needed |
| Property filtering | Exclude incomplete (except local) | Quality over quantity for major platforms |
| Collaboration | None | Single user, no sharing features |

## Out of Scope (V1)

- Price drop alerts
- Email notifications
- Multi-user collaboration
- Map view
- Booking through the app (links to source only)

## Success Criteria

1. Aggregates properties from 4+ sources into unified view
2. Correctly filters by all criteria (bedrooms, distance, price, beach proximity, amenities)
3. Scores and ranks properties by configurable weighted formula
4. Displays top options in easy-to-compare card format
5. Works for any search parameters, not just current vacation

## Next Steps

1. Set up Python + Vue project structure
2. Implement Airbnb scraper/MCP integration first
3. Build unified property model and SQLite storage
4. Create Vue frontend with search config and card display
5. Add VRBO, Vacasa scrapers
6. Implement local agency discovery
7. Add scoring system with adjustable weights
