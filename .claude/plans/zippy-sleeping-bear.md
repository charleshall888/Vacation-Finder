# Vacation Finder - Implementation Plan

## How to Use This Plan

1. **New session?** Read `CLAUDE.md` first for project context
2. **Find next session** below (first one marked ⬜)
3. **Run prerequisite check** before starting
4. **Complete all tasks** in the session
5. **Run verification** to confirm success
6. **Mark session ✅** when done

---

## Data Strategy: Claude + Perplexity Search

Instead of building fragile web scrapers, **Claude fetches data using Perplexity MCP**:

```
User: "Search for 8-bedroom beach houses in Destin FL for June 13-20"
  ↓
Claude: perplexity_search("Airbnb 8 bedroom beach house Destin FL June 2026")
  ↓
Claude: Gets structured results (title, URL, snippet for each listing)
  ↓
Claude: Extracts data and calls POST /api/properties for each
  ↓
Frontend: Displays all properties with value scoring
```

**Tools:**
| Tool | Purpose |
|------|---------|
| `perplexity_search` | Find listings - returns titles, URLs, snippets (up to 20 results) |
| `perplexity_ask` | Ask about beach areas, compare regions, get recommendations |
| `WebFetch` | Fetch full property page for detailed extraction if needed |

**Benefits:**
- No fragile Python scrapers to maintain
- Perplexity returns structured, ranked results
- Claude handles anti-bot measures naturally
- User controls exactly what gets added
- Works immediately

---

## Session Milestones (7 Sessions)

### Session 1: Backend Foundation ✅ COMPLETE
**Goal:** Working FastAPI server with database and Property model

**Prerequisite:** None (first session)

**Tasks Completed:**
- ✅ Create backend folder structure
- ✅ Set up FastAPI with CORS
- ✅ Create SQLite database with SQLAlchemy (async)
- ✅ Define Property and SearchConfig models
- ✅ Create Pydantic schemas
- ✅ Add health check endpoint
- ✅ Add properties and search route stubs

**Verified:** `curl http://localhost:8000/health` → `{"status":"healthy","service":"vacation-finder-api"}`

---

### Session 2: Frontend Scaffolding ⬜
**Goal:** Vue app displaying property cards with mock data

**Prerequisite Check:**
```bash
# Backend exists
ls /Users/charlie.hall/Workspaces/Vacation-Finder/backend/app/main.py && echo "✅ Backend exists"
# Node.js installed
node --version && echo "✅ Node.js OK"
```

**Tasks:**
1. Create Vue 3 + Vite + TypeScript project
   ```bash
   cd /Users/charlie.hall/Workspaces/Vacation-Finder
   npm create vite@latest frontend -- --template vue-ts
   cd frontend
   npm install
   npm install pinia vue-router axios
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   ```

2. Configure Tailwind CSS
   - Update `tailwind.config.js` with content paths
   - Add Tailwind directives to `src/style.css`

3. Create TypeScript types (`frontend/src/types/property.ts`)
   - Mirror backend Property schema exactly

4. Create PropertyCard component (`frontend/src/components/PropertyCard.vue`)
   - Photo display (first photo or placeholder)
   - Property name and source badge
   - Price per week + total price
   - Bedrooms, bathrooms, max guests
   - Beach walk time
   - Review score (stars) and count
   - Value score badge
   - "View Listing" button (opens URL)

5. Create ComparisonGrid component (`frontend/src/components/ComparisonGrid.vue`)
   - CSS Grid: 3-4 cards side-by-side on desktop
   - Stacks to 1 column on mobile
   - Empty state when no properties

6. Create mock data (`frontend/src/data/mockProperties.ts`)
   - 5-6 realistic beach house properties
   - Mix of sources (airbnb, vrbo)
   - Variety of prices, reviews, beach distances

7. Update App.vue
   - Import and display ComparisonGrid with mock data
   - Basic header with title

**Verification:**
```bash
cd /Users/charlie.hall/Workspaces/Vacation-Finder/frontend
npm run dev
# Open http://localhost:5173
# Should see property cards with mock data
```

**Files to Create:**
- `frontend/` (Vite scaffold)
- `frontend/src/types/property.ts`
- `frontend/src/components/PropertyCard.vue`
- `frontend/src/components/ComparisonGrid.vue`
- `frontend/src/data/mockProperties.ts`

**Files to Modify:**
- `frontend/tailwind.config.js`
- `frontend/src/style.css`
- `frontend/src/App.vue`

---

### Session 3: Frontend-Backend Integration ⬜
**Goal:** Frontend fetches and displays properties from backend API

**Prerequisite Check:**
```bash
# Backend runs
cd /Users/charlie.hall/Workspaces/Vacation-Finder/backend
source venv/bin/activate
uvicorn app.main:app --port 8000 &
sleep 2
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ Backend OK"

# Frontend runs
cd /Users/charlie.hall/Workspaces/Vacation-Finder/frontend
npm run dev &
sleep 3
curl -s http://localhost:5173 | grep -q "html" && echo "✅ Frontend OK"
pkill -f uvicorn; pkill -f vite
```

**Tasks:**
1. Add Create Property endpoint to backend
   - `POST /api/properties` - Create a new property
   - Accepts PropertyCreate schema
   - Returns created property
   - This is how Claude will add properties

2. Configure Vite proxy (`frontend/vite.config.ts`)
   ```typescript
   server: {
     proxy: {
       '/api': 'http://localhost:8000'
     }
   }
   ```

3. Create API service (`frontend/src/services/api.ts`)
   - `fetchProperties()` - GET /api/properties
   - `createProperty(data)` - POST /api/properties
   - `deleteProperty(id)` - DELETE /api/properties/{id}
   - Error handling with user-friendly messages

4. Create Pinia store (`frontend/src/stores/properties.ts`)
   - `properties` - array state
   - `loading` - boolean state
   - `lastUpdated` - timestamp
   - `fetchProperties()` action
   - `sortedByScore` computed

5. Create RefreshButton component (`frontend/src/components/RefreshButton.vue`)
   - Calls fetchProperties
   - Shows loading spinner
   - Displays "Last updated: X"

6. Update App.vue
   - Use Pinia store instead of mock data
   - Add RefreshButton
   - Fetch properties on mount

7. Seed database with mock properties (for testing)
   - Create `backend/app/scrapers/seed_data.py`
   - Add seed endpoint or startup logic

**Verification:**
```bash
# Start backend with seeded data
# Start frontend
# Properties appear automatically
# Refresh button works
```

**Files to Create:**
- `frontend/src/services/api.ts`
- `frontend/src/stores/properties.ts`
- `frontend/src/components/RefreshButton.vue`
- `backend/app/scrapers/seed_data.py`

**Files to Modify:**
- `frontend/vite.config.ts`
- `frontend/src/App.vue`
- `frontend/src/main.ts` (add Pinia)
- `backend/app/api/routes/properties.py` (add POST endpoint)

---

### Session 4: Scoring System ⬜
**Goal:** Properties ranked by weighted value score with adjustable sliders

**Prerequisite Check:**
```bash
# Frontend displays properties from backend
curl -s http://localhost:8000/api/properties/ | python3 -c "import sys,json; d=json.load(sys.stdin); print('✅' if d['total']>0 else '❌ No properties')"
```

**Tasks:**
1. Implement scoring service (`backend/app/services/scoring.py`)
   ```python
   DEFAULT_WEIGHTS = {
       "price": 0.30,      # Lower price = better
       "reviews": 0.25,    # Higher score * log(count) = better
       "beach": 0.20,      # Closer to beach = better
       "amenities": 0.15,  # More amenities = better
       "distance": 0.10    # Closer to origin = better
   }

   def calculate_score(property, weights, all_properties) -> float:
       # Normalize each factor to 0-100 scale
       # Apply weights
       # Return composite score 0-100
   ```

2. Add score calculation to property list endpoint
   - Accept weights as query params or from saved config
   - Calculate and return value_score for each property

3. Create ScoreSliders component (`frontend/src/components/ScoreSliders.vue`)
   - Range slider (0-100%) for each weight factor
   - Labels showing current percentage
   - Visual bar showing weight distribution
   - "Reset to Defaults" button
   - Weights must sum to 100%

4. Add weights to Pinia store
   - `weights` state object
   - `updateWeight(factor, value)` action
   - Persist to localStorage
   - Trigger re-fetch or recalculate on change

5. Update properties store
   - Include weights in fetch request
   - Re-sort when weights change

6. Update UI
   - Add ScoreSliders above or beside property grid
   - Show value score prominently on PropertyCard

**Verification:**
```bash
# Adjust price slider higher → cheaper properties rank higher
# Adjust beach slider higher → closer properties rank higher
# Weights persist after page refresh
```

**Files to Create:**
- `backend/app/services/scoring.py`
- `frontend/src/components/ScoreSliders.vue`

**Files to Modify:**
- `backend/app/api/routes/properties.py`
- `frontend/src/stores/properties.ts`
- `frontend/src/components/PropertyCard.vue`
- `frontend/src/App.vue`

---

### Session 5: Search Configuration UI ⬜
**Goal:** User can view and modify search parameters

**Prerequisite Check:**
```bash
# Scoring works
curl -s "http://localhost:8000/api/properties/?weights_price=0.5" | python3 -c "import sys,json; p=json.load(sys.stdin)['properties']; print('✅' if p else '❌')"
```

**Tasks:**
1. Create SearchConfig component (`frontend/src/components/SearchConfig.vue`)
   - **Origin**: City, State text inputs (default: Athens, GA)
   - **Dates**: Date pickers for check-in/out
   - **Bedrooms**: Min/Max number inputs (default: 7-9)
   - **Guests**: Number input (default: 12-16)
   - **Price**: Max price slider (default: $15,000)
   - **Beach**: Max walk time slider (default: 10 min)
   - **Amenities**: Checkboxes for required (full kitchen, parking 3+)
   - Collapsible panel (expanded/collapsed state)

2. Create searchConfig Pinia store (`frontend/src/stores/searchConfig.ts`)
   - All search parameters as state
   - Persist to localStorage
   - `resetToDefaults()` action

3. Backend: Save/load search config
   - Ensure POST /api/search/config works
   - GET /api/search/config returns current config

4. Connect UI to backend
   - Save config when user changes values
   - Load saved config on app start

5. Filter properties based on config
   - Backend filters by criteria
   - Or frontend filters cached results

**Verification:**
```bash
# Change bedroom filter → only matching properties show
# Reload page → settings persist
# Reset to defaults → original values restored
```

**Files to Create:**
- `frontend/src/components/SearchConfig.vue`
- `frontend/src/stores/searchConfig.ts`

**Files to Modify:**
- `frontend/src/App.vue`
- `backend/app/api/routes/search.py`

---

### Session 6: Property Import Features ⬜
**Goal:** Easy ways to add properties to the database

**Prerequisite Check:**
```bash
# POST endpoint works
curl -X POST http://localhost:8000/api/properties/ \
  -H "Content-Type: application/json" \
  -d '{"id":"test_1","source":"manual","name":"Test","url":"http://example.com","bedrooms":8,"price_per_week":10000,"total_price":10500}' \
  | grep -q "test_1" && echo "✅ Create works"
```

**Tasks:**
1. Create AddPropertyForm component (`frontend/src/components/AddPropertyForm.vue`)
   - Manual entry form with all fields
   - Source dropdown (airbnb, vrbo, vacasa, other)
   - URL input
   - Price, bedrooms, bathrooms, guests
   - Review score and count
   - Beach walk minutes
   - Amenity checkboxes
   - Photo URL input
   - Submit → POST to API

2. Create ImportFromUrl component (`frontend/src/components/ImportFromUrl.vue`)
   - Paste Airbnb/VRBO URL
   - "Import" button
   - Backend attempts to fetch and parse
   - Pre-fills form with extracted data
   - User confirms and saves

3. Backend: URL import endpoint
   - `POST /api/properties/import-url`
   - Accepts URL, attempts to extract property data
   - Uses httpx + basic parsing (best effort)
   - Returns extracted data for confirmation

4. Add "Add Property" button to UI
   - Opens modal with AddPropertyForm
   - Or opens ImportFromUrl first

5. Delete property feature
   - Delete button on PropertyCard
   - Confirmation dialog
   - Removes from database

**Note:** The primary way to add properties is asking Claude:
> "Search Airbnb for 8-bedroom beach houses in Destin FL and add them"

Claude will use WebSearch, extract data, and call POST /api/properties.

**Verification:**
```bash
# Add property manually → appears in list
# Paste Airbnb URL → data extracted → save works
# Delete property → removed from list
```

**Files to Create:**
- `frontend/src/components/AddPropertyForm.vue`
- `frontend/src/components/ImportFromUrl.vue`

**Files to Modify:**
- `backend/app/api/routes/properties.py` (import-url endpoint)
- `frontend/src/App.vue`
- `frontend/src/components/PropertyCard.vue` (delete button)

---

### Session 7: Polish & Error Handling ⬜
**Goal:** Production-ready user experience

**Prerequisite Check:**
```bash
# Core features work
# Properties display, scoring works, can add/delete
```

**Tasks:**
1. Loading states
   - Skeleton loaders for property cards
   - Button loading spinners
   - Page-level loading indicator

2. Error handling
   - API error messages displayed to user
   - Retry buttons on failure
   - Offline detection

3. Empty states
   - "No properties yet" with call-to-action
   - "No matches" when filters exclude all

4. Responsive design
   - Mobile-friendly property cards
   - Collapsible sidebar for config/sliders
   - Touch-friendly controls

5. Visual polish
   - Consistent spacing and typography
   - Source badges (Airbnb=red, VRBO=blue, etc.)
   - Hover states and transitions
   - Value score visualization (progress bar or badge)

6. Performance
   - Debounce slider inputs
   - Lazy load images
   - Minimize re-renders

7. Final testing
   - Full flow: add properties → adjust weights → compare
   - Test on mobile
   - Test error scenarios

**Verification:**
```bash
# Full end-to-end flow works smoothly
# Looks good on mobile
# Errors are handled gracefully
```

---

## Quick Reference

### Start Backend
```bash
cd /Users/charlie.hall/Workspaces/Vacation-Finder/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Start Frontend (after Session 2)
```bash
cd /Users/charlie.hall/Workspaces/Vacation-Finder/frontend
npm run dev
```

### Test API
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/properties/
curl -X POST http://localhost:8000/api/properties/ -H "Content-Type: application/json" -d '{"id":"test","source":"airbnb","name":"Beach House","url":"http://airbnb.com/rooms/123","bedrooms":8,"price_per_week":12000,"total_price":12500}'
```

### Ask Claude to Add Properties
```
"Search Airbnb for 8-bedroom beach houses in Destin, FL
 for June 13-20, 2026, under $15k, and add the top 5 to my database"
```

Claude will:
1. Use `perplexity_search` to find matching listings
2. Extract property data from results
3. Use `WebFetch` if more details needed
4. Call `POST /api/properties` for each property
5. Confirm what was added

---

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /health | Health check |
| GET | /api/properties/ | List all properties |
| GET | /api/properties/{id} | Get single property |
| POST | /api/properties/ | **Create property** (Claude uses this) |
| DELETE | /api/properties/{id} | Delete property |
| POST | /api/properties/import-url | Import from Airbnb/VRBO URL |
| GET | /api/search/config | Get search configuration |
| POST | /api/search/config | Save search configuration |
