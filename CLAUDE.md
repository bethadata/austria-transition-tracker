# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Austria Transition Tracker** is a static dashboard that collects and visualizes energy transition and emissions data for Austria. It combines:
- A **Jekyll-based static site** (in `docs/`) hosted on GitHub Pages
- **Python backend services** (in `services/`) that scrape data and generate interactive Plotly charts
- **Automated data pipelines** that run on a schedule to fetch latest data and update the dashboard

The project tracks multiple sectors: Agriculture, Buildings, Energy & Industry, Transport, Waste, Fluorinated Gases, and LULUCF (land use).

## Tech Stack

- **Frontend**: Jekyll (Ruby-based static site generator) with Minima theme
- **Backend**: Python 3.11+ with Poetry for dependency management
- **Data Visualization**: Plotly (interactive HTML charts)
- **Data Sources**: Eurostat API, Statistics Austria, Umweltbundesamt (manual imports)
- **Data Processing**: pandas, numpy
- **Automation**: FastAPI + APScheduler for scheduled dashboard builds

## Architecture & Data Flow

### Directory Structure

```
services/
├── config.py           # BASEPATH configuration (must be set per machine)
├── config_example.py   # Template for config.py — copy and set BASEPATH
├── main.py             # FastAPI scheduler (runs full pipeline daily at 00:01 Vienna time)
├── scrape_data.py      # Orchestrates data downloads
├── create_charts.py    # Orchestrates chart generation (calls plot/plot_all.py)
├── publish_github.py   # Commits and pushes changes to GitHub
├── source/             # Data downloaders (Eurostat, E-control, etc.)
├── plot/               # Chart generation modules
│   ├── plot_all.py     # Calls all sector plot() functions
│   ├── plot_single.py  # Shared plotting: plot_single_go() and plot_with_toggle()
│   ├── plot_buildings.py
│   ├── plot_emissions_sectors.py
│   ├── plot_agriculture.py
│   ├── plot_transport.py
│   ├── plot_industry.py
│   ├── plot_waste.py
│   ├── plot_energy.py
│   ├── plot_energy_balance.py
│   ├── plot_fossil_fuels.py
│   ├── plot_fluorinated_gases.py
│   ├── plot_lulucf.py
│   ├── plot_food_consumption.py
│   ├── plot_car_brands.py
│   └── utils/          # Data filtering per source type
│       ├── filter.py                       # Eurostat filtering
│       ├── filter_statistik_austria.py
│       ├── filter_national_inventory.py
│       ├── filter_unfcc.py
│       ├── filter_econtrol.py
│       └── filter_fossil_extrapolation.py
└── data_raw/           # Raw downloaded data

docs/                   # Jekyll static site
├── _config.yml
├── assets/
│   ├── data_charts/    # Generated JSON files used by Plotly charts
│   └── images/
├── _includes/          # Generated HTML chart embeds + shared partials
└── _layouts/           # Jekyll templates
```

### Data Pipeline Flow

1. **Scrape** (`scrape_data.py` → `source/*.py`)
   - Downloads Eurostat data via API (cached in `data_raw/eurostat/`)
   - Downloads E-control electricity data
   - Some sources require manual downloads into `data_raw/` (see below)

2. **Process & Visualize** (`create_charts.py` → `plot/plot_all.py` → `plot/*.py`)
   - Each sector has a dedicated plot module with a `plot()` function
   - Plot modules call `filter_*` utilities from `utils/` to process raw data
   - `plot_single.py` provides `plot_single_go()` and `plot_with_toggle()` for chart creation
   - Charts are saved as **both**:
     - **JSON** → `docs/assets/data_charts/*.json` (loaded by Plotly via JavaScript)
     - **HTML** → `docs/_includes/*.html` (embedded in Jekyll pages)

3. **Deploy** (`publish_github.py`)
   - Commits and pushes to GitHub; GitHub Pages serves the `docs/` folder

4. **Schedule** (`main.py`)
   - APScheduler: `misfire_grace_time=3600`, `coalesce=True`, `max_instances=1`

## Key Concepts

### Chart Data Structure

```python
data_plot = {
    "data": {
        "Series Name": {
            "x": [datetime objects],
            "y": [float values]
        }
    },
    "meta": {
        "code": "eurostat_code",
        "uncertainty": {"Series Name": [error arrays]},  # optional
        "areas": ["Series Name"]  # for stacked area charts
    }
}
```

### Chart Types

- `plot_type="line"` — default time series
- `plot_type="area"` — stacked areas for composition
- `plot_type="area_neg"` — stacked areas with negative values (e.g., LULUCF carbon sink)
- `plot_with_toggle()` — multiple visualization modes (bar, area, line)

### Filter Utilities

`plot/utils/` provides per-source filtering functions that all return `data_plot`:
- `filter_eurostat_monthly()` / `filter_eurostat_yearly()`
- `filter_statistik_austria()`, `filter_national_inventory()`, `filter_unfcc()`, `filter_econtrol()`

## Common Development Tasks

### Setup

```bash
# Python backend (from services/):
cp config_example.py config.py   # then set BASEPATH to absolute path of this repo
poetry install

# Jekyll site (from docs/):
bundle install
bundle exec jekyll serve         # local dev at localhost:4000
```

### Run Pipeline

```bash
# From services/:
python scrape_data.py    # download latest data only
python create_charts.py  # regenerate all charts from current data
python main.py           # full pipeline: scrape + charts + publish + start scheduler
```

### Add a New Chart

1. Create `services/plot/plot_<theme>.py` with a `plot()` function
2. Use `filter_*` from `utils/` to load and process data into `data_plot`
3. Call `plot_single_go()` or `plot_with_toggle()` with a `filename` (no extension; both JSON and HTML are generated)
4. Add the call to `plot_all()` in `services/plot/plot_all.py`
5. Add a Jekyll page (e.g., `docs/<theme>.md`) and embed: `{% include AT_timeseries_<filename>.html %}`

### Manual Data Sources

Some sources require manual download; update the corresponding `filter_*` function if paths change:
- **Statistics Austria**: save to `services/data_raw/statistik_austria/`
- **Umweltbundesamt NIR**: save to `services/data_raw/nir/`
- **Umweltbundesamt Klimadashboard**: save to `services/data_raw/uba_klimadashboard/`

### Configuration

`config.py` has a single variable: `BASEPATH` — absolute path to the dashboard root. It is git-ignored; use `config_example.py` as a template. All data savers and chart generators derive their paths from this.
