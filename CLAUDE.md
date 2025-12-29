# CLAUDE.md - AI Assistant Guide for find-my-next-home

## Project Overview

**find-my-next-home** is a Python-based property search and commute analysis tool that helps users find homes based on proximity and commute time to Grand Central Terminal (NYC). The project combines:

- **Property scraping** from realtor.com using the homeharvest library
- **Commute time calculation** using Metro-North Railroad GTFS data and OSRM routing
- **Interactive visualization** with Folium maps showing properties color-coded by commute time

### Primary Use Case
Find properties in Westchester County, NY (or other locations) that are within a reasonable commute to Grand Central Terminal, factoring in both driving time to the nearest Metro-North station and train time to GCT.

## Repository Structure

```
find-my-next-home/
├── main.py                      # Standalone Python script version
├── main.ipynb                   # Jupyter notebook (primary interface)
├── check_lirr.py                # LIRR train schedule checker (bonus utility)
├── pyproject.toml               # UV package manager configuration
├── uv.lock                      # UV lockfile for reproducible installs
├── .python-version              # Python version specification
├── README.md                    # (Currently empty)
├── SETUP.md                     # Detailed setup and usage guide
├── gtfsmnr/                     # Metro-North GTFS (transit) data
│   ├── stops.txt                # Station locations and IDs
│   ├── stop_times.txt           # Train schedules
│   ├── routes.txt               # Train routes
│   ├── trips.txt                # Trip definitions
│   ├── shapes.txt               # Route geometries
│   ├── calendar_dates.txt       # Service calendar
│   ├── transfers.txt            # Transfer information
│   ├── agency.txt               # Agency information
│   └── notes.txt                # Additional notes
├── station_train_times.csv      # Pre-computed fastest train times (generated)
└── results.csv                  # Scraped property data (generated)
```

## Tech Stack

### Core Technologies
- **Python**: 3.12+ (specified in `.python-version`)
- **Package Manager**: `uv` (fast, modern replacement for pip)
- **Primary Interface**: Jupyter notebooks (VS Code or browser)

### Key Dependencies (from `pyproject.toml`)
- `homeharvest` - Property scraping from realtor.com
- `folium` - Interactive Leaflet.js map generation
- `pandas` - Data manipulation and analysis
- `jupyter` - Notebook support
- `ipykernel` - Jupyter kernel integration
- `requests` - HTTP requests (for OSRM routing API)

### External APIs Used
- **OSRM** (Open Source Routing Machine) - Free routing service, NO API key needed
  - Endpoint: `http://router.project-osrm.org/route/v1/driving/`
  - Used for drive time calculations to stations
- **realtor.com** - Property data (via homeharvest library)

## Data Flow

### 1. Property Scraping Flow
```
homeharvest.scrape_property()
  ↓
Raw property DataFrame (66 columns)
  ↓
Filter: Remove rows missing lat/lon/price
  ↓
properties_clean DataFrame
```

### 2. Commute Calculation Flow
```
Load station_train_times.csv (pre-computed)
  ↓
For each property:
  ↓
  Calculate distance to all stations
  ↓
  Select top 5 nearest stations
  ↓
  Query OSRM for actual drive time
  ↓
  Calculate total_commute = drive + train + buffer (5min)
  ↓
  Select station with BEST total commute
  ↓
Add commute columns to properties_clean
  ↓
Filter: Keep only properties ≤ MAX_COMMUTE_MINUTES
  ↓
properties_filtered DataFrame
```

### 3. Visualization Flow
```
properties_filtered DataFrame
  ↓
Create Folium map centered on property cluster
  ↓
Add markers:
  - Grand Central (red star)
  - Metro-North stations (purple train icons)
  - Properties (green/orange/blue homes)
  ↓
Display interactive map in notebook
```

## Key Files and Their Purposes

### main.ipynb (Primary Interface)
The Jupyter notebook is the main interface for users. It contains:
- **Cell 0-1**: Documentation markdown
- **Cell 2**: Library imports
- **Cell 3-4**: API key setup notes (not needed - OSRM is free)
- **Cell 5-6**: Property scraping with configurable parameters
- **Cell 7-8**: Data preview and column inspection
- **Cell 9-13**: Commute calculation with station selection logic
- **Cell 14-15**: Debug utilities for testing specific addresses
- **Cell 16-17**: Map visualization with color-coded markers

### main.py (Standalone Script)
Simplified version for command-line use:
- Scrapes properties
- Cleans data
- Generates basic Folium map
- **Note**: Uses `sold_price` hardcoded (less flexible than notebook)

### check_lirr.py (Bonus Utility)
Separate utility for checking LIRR (Long Island Rail Road) train times to Grand Central:
- Uses GTFS-realtime Protocol Buffer feed
- Requires `google.transit` protobuf library
- Not integrated with main property search

### station_train_times.csv (Generated Data)
Pre-computed fastest train times from each Metro-North station to Grand Central:
- Columns: `stop_id`, `stop_name`, `stop_lat`, `stop_lon`, `fastest_train_minutes`
- Generated from gtfsmnr GTFS data
- Calculated using morning rush hour trains (7-9 AM)
- **Important**: Only generated once; reuse for performance

### results.csv (Generated Data)
Complete scraped property data:
- All 66 columns from homeharvest API
- Raw data before filtering/cleaning
- Can be reloaded for analysis without re-scraping

## Development Workflows

### Initial Setup
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies
uv sync

# Verify installation
uv pip list
```

### Running the Notebook
**Option 1: VS Code (Recommended)**
1. Install Jupyter extension
2. Open `main.ipynb`
3. Select `.venv` kernel from top-right selector
4. Run cells with Shift+Enter or ▶ button

**Option 2: Browser**
```bash
uv run jupyter notebook
# or
uv run jupyter lab
```

### Running the Standalone Script
```bash
uv run python main.py
```

### Adding New Dependencies
```bash
uv add <package-name>
# Example: uv add numpy
```

### Removing Dependencies
```bash
uv remove <package-name>
```

## Important Conventions and Patterns

### 1. Price Column Handling
**CRITICAL**: The homeharvest API returns different price column names based on listing type:
- `list_price` - For active "for_sale" listings
- `sold_price` - For "sold" listings
- `price` - Fallback for some listings

**Pattern to follow**:
```python
# Auto-detect which price column exists
price_col = 'list_price' if 'list_price' in properties.columns else \
            'sold_price' if 'sold_price' in properties.columns else 'price'
```

### 2. Station Selection Strategy
The code uses a **total commute optimization** strategy, NOT just "nearest station":

1. Calculate straight-line distance to all stations
2. Filter to top 5 nearest stations
3. Get actual OSRM drive times for these candidates
4. Apply sanity check: reject drive times < 2 min if distance > 0.5 miles
5. Calculate: `total_commute = drive + train + walking_buffer`
6. Select station with BEST total commute time

**Why**: A slightly farther station may have faster trains, resulting in shorter total commute.

### 3. OSRM API Usage
**Rate limiting**: Small delay (0.05s) between requests to be respectful
**Fallback**: If OSRM fails, use distance-based estimate: `(miles / 40) * 60`
**Sanity check**: OSRM sometimes returns unrealistic times (e.g., 3 min for 5 miles); detect and use estimate instead

### 4. Data Cleaning Pattern
Always clean data in this order:
1. Remove rows missing `latitude` or `longitude`
2. Remove rows missing price column
3. Optionally remove rows missing other critical fields (beds, baths)

### 5. Map Color Coding
Properties are color-coded by total commute time:
- **Green**: ≤ 45 minutes total
- **Orange**: 46-60 minutes total
- **Blue**: > 60 minutes (if included)

### 6. GTFS Data Usage
The `gtfsmnr/` directory contains static GTFS data for Metro-North Railroad:
- **stops.txt**: Station locations (lat/lon) and IDs
- **stop_times.txt**: Detailed train schedules (departure/arrival times per stop)
- **trips.txt**: Trip definitions (route, service, direction)
- **routes.txt**: Route information

**Important**: The pre-computation cell (Cell 12) parses this data ONCE to create `station_train_times.csv`. Don't re-run unless GTFS data is updated.

## Common Tasks and How to Approach Them

### Task: Change Search Location
**File**: `main.ipynb`, Cell 6
```python
properties = scrape_property(
    location="New Location, STATE",  # Change this
    listing_type="for_sale",
    past_days=30
)
```

### Task: Adjust Commute Time Threshold
**File**: `main.ipynb`, Cell 13
```python
MAX_COMMUTE_MINUTES = 60  # Change this value
```

### Task: Change Listing Type (For Sale, Sold, Rent)
**File**: `main.ipynb`, Cell 6
```python
listing_type="for_sale"   # or "sold", "for_rent", "pending"
```

### Task: Adjust Map Zoom Level
**File**: `main.ipynb`, Cell 17
```python
m = folium.Map(location=[center_lat, center_lon], zoom_start=10)  # Change zoom_start
```
- 9: Wide county view
- 10: County view (default)
- 11: Multi-town view
- 12: City view
- 13+: Neighborhood view

### Task: Add New Property Filters
**Location**: After properties_clean creation, before commute calculation
**Pattern**:
```python
# Example: Filter to only 3+ bedroom properties
properties_clean = properties_clean[properties_clean['beds'] >= 3]
```

### Task: Debug Specific Property's Station Selection
**Use**: Debug cell (Cell 15)
- Change `debug_address` variable to partial address
- Run cell to see top 5 station candidates and selection logic

### Task: Update GTFS Data
1. Download new GTFS data from MTA
2. Replace files in `gtfsmnr/` directory
3. Delete `station_train_times.csv`
4. Run Cell 12 to regenerate pre-computed times

### Task: Add New Map Marker Information
**File**: `main.ipynb`, Cell 17
**Location**: The `popup_parts` list construction
```python
popup_parts.append(f"<b>New Field:</b> {row['column_name']}")
```

## Common Pitfalls and How to Avoid Them

### 1. KeyError: 'price' or 'sold_price' or 'list_price'
**Problem**: Hardcoding a price column name
**Solution**: Use the auto-detection pattern shown in "Price Column Handling"

### 2. Empty results.csv or No Properties Found
**Causes**:
- Invalid location string
- No properties match criteria in past_days
- Network error during scraping

**Solution**:
- Verify location string matches realtor.com format: "City, STATE" or "County, STATE"
- Increase `past_days` or remove it entirely
- Check for error messages in scraping output

### 3. OSRM Returning Unrealistic Drive Times
**Problem**: OSRM sometimes returns 1-3 minute drive times for 5+ mile distances
**Solution**: Already handled! The code includes sanity check:
```python
if drive_time < MIN_DRIVE_TO_STATION and distance > 0.5:
    drive_time = estimated_drive  # Use fallback
```

### 4. No Properties After Commute Filtering
**Problem**: `MAX_COMMUTE_MINUTES` is too restrictive
**Solution**:
- Increase `MAX_COMMUTE_MINUTES`
- Check `properties_clean['commute_minutes'].describe()` to see distribution
- Adjust search location to areas closer to Metro-North

### 5. Missing station_train_times.csv
**Problem**: File not generated yet
**Solution**: Run Cell 12 once to generate it from GTFS data

### 6. Kernel Not Found in VS Code
**Problem**: VS Code can't find the `.venv` Python environment
**Solution**:
1. Install Jupyter extension in VS Code
2. Click "Select Kernel" in top-right of notebook
3. Choose "Python Environments..."
4. Select the `.venv` environment

### 7. OSRM API Timing Out or Failing
**Problem**: External API not responding
**Solution**: Code already falls back to distance estimates:
```python
if drive_time is None:
    drive_time = (distance / 40) * 60  # Estimate at 40 mph
```

### 8. Map Not Displaying in Notebook
**Causes**:
- Browser JavaScript disabled
- No properties in filtered results
- Folium version incompatibility

**Solution**:
- Check browser console for errors
- Verify `len(properties_filtered) > 0`
- Try regenerating with `m.save('map.html')` and open in browser

## Code Quality Guidelines

### When Making Changes

1. **Don't hardcode values that vary by listing type** (especially price columns)
2. **Preserve the station selection strategy** - it's optimized for total commute, not just distance
3. **Maintain the sanity checks** - OSRM and external APIs can return bad data
4. **Keep the pre-computation pattern** - Don't re-parse GTFS data on every run
5. **Use meaningful variable names** - Follow existing patterns (e.g., `properties_clean`, `properties_filtered`)
6. **Add progress indicators** for long-running operations (e.g., "Processed X/Y properties")

### Testing Changes

When modifying the code:

1. **Test with small data first**: Use `past_days=1` to get fewer properties
2. **Test the debug cell**: Verify station selection logic on known addresses
3. **Check edge cases**: Properties very far from stations, properties with missing data
4. **Verify map markers**: Ensure color coding, popups, and tooltips still work

### Documentation

- **Update SETUP.md** if changing workflow or dependencies
- **Add markdown cells** in notebook for new features
- **Use docstrings** for new functions
- **Keep this CLAUDE.md up to date** with structural changes

## Data Schema Reference

### Property DataFrame Columns (66 total from homeharvest)

**Critical columns**:
- `latitude`, `longitude` - Property coordinates (required for mapping)
- `list_price` / `sold_price` / `price` - Property price (varies by listing_type)
- `beds` - Number of bedrooms
- `full_baths`, `half_baths` - Bathroom counts
- `permalink` - Used to extract display address
- `property_url` - Link to listing
- `formatted_address`, `full_street_line` - Full address strings
- `city`, `state`, `zip_code` - Location components

**Additional useful columns**:
- `sqft` - Square footage
- `year_built` - Construction year
- `days_on_mls` - Days on market
- `status`, `mls_status` - Listing status
- `lot_sqft` - Lot size
- `price_per_sqft` - Calculated price per sqft
- `hoa_fee` - HOA fees
- `tax`, `tax_history` - Property taxes
- `agent_*`, `broker_*`, `office_*` - Contact information

**All columns** (reference):
```
property_url, property_id, listing_id, permalink, mls, mls_id, status,
mls_status, text, style, formatted_address, full_street_line, street,
unit, city, state, zip_code, beds, full_baths, half_baths, sqft,
year_built, days_on_mls, list_price, list_price_min, list_price_max,
list_date, pending_date, sold_price, last_sold_date, last_sold_price,
last_status_change_date, last_update_date, assessed_value,
estimated_value, tax, tax_history, new_construction, lot_sqft,
price_per_sqft, latitude, longitude, neighborhoods, county, fips_code,
stories, hoa_fee, parking_garage, agent_id, agent_name, agent_email,
agent_phones, agent_mls_set, agent_nrds_id, broker_id, broker_name,
builder_id, builder_name, office_id, office_mls_set, office_name,
office_email, office_phones, nearby_schools, primary_photo, alt_photos
```

### Station Train Times Schema
**File**: `station_train_times.csv`

Columns:
- `stop_id` - Metro-North station ID (matches gtfsmnr/stops.txt)
- `stop_name` - Station name (e.g., "White Plains", "Tarrytown")
- `stop_lat` - Station latitude
- `stop_lon` - Station longitude
- `fastest_train_minutes` - Fastest train time from this station to Grand Central (during morning rush)

## Environment and Tools

### Python Version
- **Required**: Python 3.12+
- **Specified in**: `.python-version`
- **Why**: Modern Python features, better performance

### UV Package Manager
- **Installation**: See SETUP.md
- **Location**: Typically `~/.local/bin/uv`
- **Advantages**: 10-100x faster than pip, better dependency resolution
- **Key commands**:
  - `uv sync` - Install all dependencies
  - `uv add <pkg>` - Add new package
  - `uv remove <pkg>` - Remove package
  - `uv pip list` - List installed packages
  - `uv run <cmd>` - Run command in venv

### Virtual Environment
- **Location**: `.venv/` (created by uv)
- **Activation**: Not needed with `uv run`
- **Manual activation**: `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows)

## Git Workflow

### Branches
- Work on feature branches starting with `claude/` prefix
- Branch naming: `claude/descriptive-name-sessionid`
- Always push to designated branch (specified in task context)

### Commits
- Write clear, descriptive commit messages
- Focus on "why" not "what"
- Example: "Optimize station selection to minimize total commute" not "Change station loop"

### Before Committing
1. Verify code runs without errors
2. Test with at least one property search
3. Check that map renders correctly
4. Ensure no hardcoded personal paths or API keys

## Performance Considerations

### Current Performance Characteristics
- **Property scraping**: 1-5 seconds for 30-day search
- **GTFS pre-computation**: 30-60 seconds (run once)
- **Commute calculation**: ~10-15 seconds per 100 properties
- **Map rendering**: Instant in notebook

### Optimization Opportunities
If asked to improve performance:

1. **Batch OSRM requests**: Currently sequential with 0.05s delay
2. **Cache OSRM results**: Store drive times for property-station pairs
3. **Parallel processing**: Use multiprocessing for commute calculations
4. **Reduce OSRM calls**: Use distance-based filtering before OSRM queries
5. **Optimize GTFS parsing**: Use chunked reading for large files

### Don't Optimize Prematurely
- Current performance is acceptable for typical use (100-500 properties)
- Only optimize if user reports slowness or handles 1000+ properties

## Troubleshooting Guide for AI Assistants

### User Reports: "No properties found"
**Check**:
1. Is the location string valid? (Format: "City, STATE")
2. Are there actually properties in that area on realtor.com?
3. Is `past_days` too restrictive?
4. Check for network errors in scraping output

### User Reports: "Map is blank"
**Check**:
1. `len(properties_filtered)` - Are there properties after filtering?
2. Browser console errors
3. Are latitude/longitude values valid (not NaN)?
4. Try saving map: `m.save('debug_map.html')`

### User Reports: "Wrong station selected"
**Check**:
1. Use debug cell (Cell 15) with the property address
2. Verify OSRM drive times are realistic
3. Check if sanity check is triggering (< 2 min for > 0.5 mi)
4. Review top 5 candidates to see total commute calculations

### User Reports: "Commute times seem wrong"
**Check**:
1. Verify `WALKING_BUFFER_MINUTES` is set (default 5)
2. Check if train times are from `station_train_times.csv`
3. Verify OSRM is returning actual drive times, not estimates
4. Confirm total = drive + train + buffer

### User Reports: "Can't install dependencies"
**Check**:
1. Is `uv` installed? (`uv --version`)
2. Is Python 3.12+ available? (`python --version`)
3. Try: `uv sync --reinstall`
4. Check `uv.lock` exists

## Future Enhancement Ideas

If users request new features, these are natural extensions:

1. **Multiple destinations**: Support commute to multiple offices/locations
2. **Reverse commute**: Find properties near specific stations
3. **School districts**: Add school rating overlays
4. **Price trends**: Show price history using `last_sold_price`
5. **Favorite properties**: Add ability to mark/save favorite listings
6. **Email alerts**: Notify when new properties match criteria
7. **Comparison tool**: Side-by-side comparison of selected properties
8. **Walking distance filter**: Only show properties within walking distance of stations
9. **Multi-modal routing**: Include walking/biking to station
10. **Rental yield analysis**: For investment properties

## Security and Privacy Notes

### No API Keys Required
- OSRM is completely free and requires no authentication
- homeharvest scrapes public data from realtor.com
- No sensitive data is stored

### Data Privacy
- `results.csv` contains publicly available listing data
- No personal information is collected
- All data is stored locally

### Safe Practices
- Don't commit API keys if any are added later
- Don't commit personal search criteria to public repos
- Be respectful of OSRM API with rate limiting (0.05s delay)

## Summary: Quick Reference for AI Assistants

**Primary Language**: Python 3.12+
**Primary Interface**: Jupyter Notebook (`main.ipynb`)
**Package Manager**: `uv`
**Main Libraries**: homeharvest, folium, pandas
**External APIs**: OSRM (free routing, no key needed)
**Data Sources**: realtor.com (via homeharvest), Metro-North GTFS

**Most Common Tasks**:
1. Change search location → Cell 6
2. Adjust commute threshold → Cell 13
3. Debug station selection → Cell 15
4. Modify map visualization → Cell 17

**Critical Patterns**:
- Auto-detect price column (varies by listing type)
- Optimize for total commute (drive + train), not just distance
- Pre-compute GTFS data once, reuse
- Sanity-check OSRM drive times
- Provide progress indicators for long operations

**Files to Know**:
- `main.ipynb` - Main user interface
- `main.py` - Standalone script version
- `station_train_times.csv` - Pre-computed train times
- `results.csv` - Scraped property data
- `gtfsmnr/` - Transit schedule data
- `SETUP.md` - User documentation
- `CLAUDE.md` - This file (AI assistant guide)

---

**Last Updated**: 2025-12-29
**Repository**: find-my-next-home
**Maintained for**: Claude Code and other AI assistants
