# Find My Next Home - Setup Guide

## Project Overview
A Jupyter notebook-based tool to scrape property listings and visualize them on interactive maps using Folium.

## Environment Setup

### Package Manager: UV
This project uses `uv` instead of `pip` for faster dependency management.

- **UV Installation Location**: `/home/yuntong/snap/code/214/.local/bin/uv`
- **Symlink Location**: `~/.local/bin/uv`

### Dependencies
All dependencies are managed in `pyproject.toml`:
- `homeharvest` - Property scraping from realtor.com
- `folium` - Interactive map visualization
- `pandas` - Data manipulation
- `jupyter` - Notebook support
- `ipykernel` - Jupyter kernel

### Installation Commands
```bash
# Install dependencies
uv sync

# Add new packages
uv add <package-name>

# Remove packages
uv remove <package-name>

# List installed packages
uv pip list

# Run Python scripts
uv run python main.py
```

## Running the Notebook

### Option 1: VS Code (Recommended)
1. Install the Jupyter extension in VS Code
2. Open `main.ipynb`
3. Select the `.venv` Python kernel
4. Run cells with ▶ button or `Shift+Enter`

### Option 2: Jupyter in Browser
```bash
jupyter notebook
# or
jupyter lab
```

## Property Data Schema

### Column Names (varies by listing type)
The API returns different column names depending on listing type:
- **For Sale listings**: `list_price`
- **Sold listings**: `sold_price`
- **Some listings**: `price`

### Key Columns
- `latitude`, `longitude` - Property coordinates
- `list_price` / `sold_price` / `price` - Property price
- `beds` - Number of bedrooms
- `full_baths` - Number of full bathrooms
- `permalink` - Used to extract address display
- `property_url` - Link to listing
- `mls`, `mls_id` - MLS information

### Common Issues
**KeyError: ['price']** - The price column name varies. The notebook now auto-detects which price column is available (`list_price`, `sold_price`, or `price`).

## Scraping Parameters

### Location Examples
```python
location="Westchester County, NY"
location="San Diego, CA"
location="Brooklyn, NY"
```

### Listing Types
```python
listing_type="for_sale"   # Active listings
listing_type="sold"        # Recently sold
listing_type="for_rent"    # Rental listings
listing_type="pending"     # Pending sales
```

### Time Range
```python
past_days=30   # Last 30 days
past_days=60   # Last 60 days
past_days=90   # Last 90 days
# Omit past_days to get all available listings
```

## Customization

### Map Settings
- **Zoom level**: Adjust `zoom_start` (11 for counties, 12 for cities, 13+ for neighborhoods)
- **Map center**: Automatically calculated from property coordinates
- **Markers**: Each property shown with address, price, beds, baths

### Data Filtering
Current filters remove properties missing:
- `latitude` or `longitude`
- Price (whichever column is present)
- Optional: `full_baths`

Modify in the "Clean and Prepare Data for Mapping" cell.

## File Outputs
- `results.csv` - All scraped property data in CSV format
- Interactive map displayed in notebook

## Troubleshooting

### uv command not found
```bash
# Use full path
/home/yuntong/snap/code/214/.local/bin/uv --version

# Or add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Kernel not found in VS Code
1. Install Jupyter extension
2. Click "Select Kernel" in top right
3. Choose the `.venv` Python environment

### No properties displayed on map
1. Check if scraping returned results (`Found X properties`)
2. Verify coordinates exist after cleaning
3. Check browser console for JavaScript errors

## Notes
- The notebook auto-detects which price column is available
- Address display is extracted from the `permalink` field
- All markers are clickable with detailed property information
- Links open property listings in new tabs
