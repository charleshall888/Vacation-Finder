# Vacation Finder - Claude Project Guide

> **START HERE**: This file is the entry point for every Claude session on this project.

## Quick Start for New Sessions

### 1. Check Current Status
```bash
# Run these to understand project state:
ls -la backend/app/          # Backend structure exists?
ls -la frontend/src/ 2>/dev/null || echo "Frontend not created yet"
```

### 2. Read the Plan
The full implementation plan is at **`PLAN.md`** - read it to see:
- Which sessions are complete (✅) vs pending (⬜)
- Prerequisite checks for each session
- Exact files to create/modify
- Verification steps

### 3. User Commands
- **"Start Session N"** - Begin working on Session N
- **"Continue"** - Resume the last in-progress session
- **"Status"** - Show what's complete and what's next

---

## Project Overview

A vacation rental aggregator that searches Airbnb, VRBO, Vacasa, and local agencies for beach house rentals, displaying them in a comparable card UI with weighted scoring.

**Use Case**: Find 7-9 bedroom beach houses within 7 hours of Athens, GA for a family reunion in June 2026.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Vue 3 Frontend                        │   │
│  │   PropertyCards │ ComparisonGrid │ ScoreSliders      │   │
│  └─────────────────────────┬───────────────────────────┘   │
│                            │ HTTP                           │
│                            ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend                          │   │
│  │   /api/properties │ /api/search │ /api/config        │   │
│  └─────────────────────────┬───────────────────────────┘   │
│                            │                                 │
│              ┌─────────────┴─────────────┐                  │
│              ▼                           ▼                   │
│  ┌───────────────────┐       ┌───────────────────┐         │
│  │   SQLite Cache    │       │     Scrapers      │         │
│  │   (properties)    │       │ Airbnb│VRBO│etc   │         │
│  └───────────────────┘       └───────────────────┘         │
└─────────────────────────────────────────────────────────────┘

DATA FLOW:
1. User clicks "Refresh" in frontend
2. Backend scrapers fetch from rental sites
3. Results normalized to Property model
4. Stored in SQLite cache
5. Frontend displays with scoring
```

## Tech Stack

| Layer | Technology | Status |
|-------|------------|--------|
| Backend | Python 3.14 + FastAPI | ✅ Session 1 |
| Database | SQLAlchemy + SQLite | ✅ Session 1 |
| Frontend | Vue 3 + Vite + TypeScript | ⬜ Session 2 |
| State | Pinia | ⬜ Session 2 |
| Styling | Tailwind CSS | ⬜ Session 2 |

## Data Strategy: Claude + Perplexity Search

Instead of fragile web scrapers, **Claude fetches property data using Perplexity**:

```
User: "Search for beach houses in Destin FL and add them"
  ↓
Claude: perplexity_search → structured results with URLs
  ↓
Claude: Extracts data (name, price, bedrooms, URL)
  ↓
Claude: POST /api/properties for each property
  ↓
Frontend: Displays properties with value scoring
```

**Tools used:**
- `perplexity_search` - Find listings (returns titles, URLs, snippets)
- `perplexity_ask` - Follow-up questions about areas/properties
- `WebFetch` - Get full details from a property URL if needed

**To add properties, ask Claude:**
> "Search Airbnb for 8-bedroom beach houses in Destin, FL for June 13-20, under $15k, and add the top 5"

## Directory Structure

```
Vacation-Finder/
├── CLAUDE.md              # THIS FILE - read first every session
├── SPECIFICATION.md       # Detailed requirements
├── .claude/plans/         # Session tracking
│   └── plan.md
├── backend/               # ✅ Created in Session 1
│   ├── venv/              # Python virtual environment
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py        # FastAPI entry point
│   │   ├── config.py      # Settings
│   │   ├── database.py    # Async SQLite
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── api/routes/    # Endpoints
│   │   ├── services/      # Business logic
│   │   └── scrapers/      # Data fetchers
│   └── tests/
└── frontend/              # ⬜ Created in Session 3
    └── src/
        ├── components/
        ├── views/
        ├── stores/
        └── services/
```

## Running the Project

### Backend (after Session 1)
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
# Test: curl http://localhost:8000/health
```

### Frontend (after Session 3)
```bash
cd frontend
npm run dev
# Opens: http://localhost:5173
```

---

## Session Progress (7 Sessions)

| # | Session | Status | Prerequisite |
|---|---------|--------|--------------|
| 1 | Backend Foundation | ✅ | N/A |
| 2 | Frontend Scaffolding | ⬜ | Backend exists |
| 3 | Frontend-Backend Integration | ⬜ | Session 2 complete |
| 4 | Scoring System | ⬜ | Session 3 complete |
| 5 | Search Configuration UI | ⬜ | Session 4 complete |
| 6 | Property Import Features | ⬜ | Session 3 complete |
| 7 | Polish & Error Handling | ⬜ | All previous complete |

**See full plan**: `PLAN.md`

---

## Key Models

### Property (backend/app/models/property.py)
```python
id: str              # "airbnb_12345"
source: str          # airbnb, vrbo, vacasa, local
name: str
url: str
bedrooms: int
bathrooms: float
price_per_week: float
total_price: float   # includes fees
review_score: float  # 0-5
beach_walk_minutes: int
amenities: dict      # {has_full_kitchen, parking_spots, has_pool...}
value_score: float   # computed ranking
```

### SearchConfig (backend/app/models/search_config.py)
```python
origin_city: str     # "Athens"
origin_state: str    # "GA"
max_distance_miles: int
min_bedrooms: int
max_bedrooms: int
max_price_per_week: float
date_start: date
date_end: date
max_beach_walk_minutes: int
required_amenities: list[str]
scoring_weights: dict
```

## Default Search Criteria

- **Origin**: Athens, GA
- **Distance**: 400 miles (~7 hour drive)
- **Bedrooms**: 7-9
- **Guests**: 12-16 people
- **Budget**: $15,000/week
- **Beach**: < 10 min walk
- **Required**: Full kitchen, 3+ parking spots
- **Dates**: June 13-20, 2026 OR June 27-July 4, 2026

## Scoring Weights (User Adjustable)

| Factor | Default | Calculation |
|--------|---------|-------------|
| Price | 30% | Lower = better |
| Reviews | 25% | score × log(count+1) |
| Beach | 20% | Closer = better |
| Amenities | 15% | Pool, hot tub bonuses |
| Distance | 10% | Closer to origin = better |

---

## Code Conventions

- Async/await for all database operations
- Pydantic for request/response validation
- Type hints on all functions
- Source field identifies data origin
- Properties without reviews from Airbnb/VRBO are excluded
- Local agency properties: verified=False
