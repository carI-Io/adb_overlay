# Flood Hazard Map Processing — Methodology README

## Overview

This repository contains the scripts used to process and merge flood hazard vector and raster layers from two Italian national sources — **ISPRA** (Istituto Superiore per la Protezione e la Ricerca Ambientale) and multiple **ADB** (Autorità di Bacino Distrettuale) districts — into a single unified hazard map. The pipeline applies hierarchical overlay logic to avoid double-counting overlapping flood zones, standardises attribute schemas, and uploads the final products to a PostGIS database.

---

## Data Sources

### ISPRA — National Flood Hazard Mosaic (2020)

The ISPRA dataset is a national-scale vector mosaic of flood hazard zones derived from the Piano di Gestione del Rischio Alluvioni (PGRA). It provides three hazard classes organised by return period probability:

| Layer code | Probability class | Nominal return period |
|-----------|------------------|-----------------------|
| H | High probability | ~30–50 yr RP |
| M | Medium probability | ~100–200 yr RP |
| L | Low probability | ~200–500 yr RP |

**Input shapefiles:**
- `HPH_Mosaicatura_ISPRA_2020_premerge.shp`
- `MPH_Mosaicatura_ISPRA_2020_premerge.shp`
- `LPH_Mosaicatura_ISPRA_2020_premerge.shp`

### ADB — District Flood Hazard Plans

Each ADB district provides its own hazard vector data at higher spatial resolution. Districts processed in this pipeline:

| Script | District | Source dataset |
|--------|----------|---------------|
| `adb_po_overlay.py` | ADB Po (Alpi Occidentali, PO valley) | `AA_pda2025_H/M/L.shp` |
| `adb_am_overlay.py` | ADB Alto Adriatico / Alpi Marittime | `ADB-AM_2026_merge_cum_prob_RP.shp` |
| `adb_as_overlay.py` | ADB Alpi Settentrionali / Alps | `PIANIFICAZIONE_SIT_PGRA_ITC_FLUVIAL_cum_prob_RP.shp` |
| `adb_ao_overlay.py` | ADB Appennino Occidentale (Valle d'Aosta) | `Tiranti_TR30/100/300_HPH/MPH/LPH_premerge.shp` |
| `adb_overlay.py` | ADB Appennino Centrale, Sicilia, Sardegna | ISPRA clipped to district boundaries |

### ADB Po PGRA 2027 — Water Depth Rasters

A separate raster pipeline processes flood depth (water height in metres) data from the ADB Po PGRA 2027 plan, for the low-probability scenario (TR500):

- Input: collections of `.tif` tiles per hazard scenario (H, M, L)
- Output: a single merged GeoTIFF at 5 m resolution in EPSG:3035

---

## Pipeline Architecture

```
ISPRA national vectors                  ADB district vectors
         │                                       │
         ▼                                       ▼
  ispra_overlay.py               adb_*_overlay.py / adb_overlay.py
  (standalone ISPRA H>M>L)       (clip to district + H>M>L overlay)
         │                                       │
         └──────────────┬────────────────────────┘
                        ▼
              adb_overlay.py (final merge)
              ispra_adb_2026 (unified vector output)
                        │
                        ▼
                 PostGIS / GCS Bucket
```

For the Po raster depth data:

```
adb_po_pgra_2027_l/*.tif (raw tiles)
         │
         ▼
adbpo_pgra2027.py  →  reproject tiles to EPSG:3035 @ 5 m
         │
         ▼
adbpo_pgra2027_merge.py  →  merge tiles via VRT + pixel-level max
         │
         ▼
adbpo_pgra2027_milano.py  →  integrate higher-res Milano TR500 raster
         │
         ▼
adpo_pgra2027_milano_to_db.py  →  upload to PostGIS (raster2pgsql, chunked)
```

---

## Step-by-step Methodology

### Stage 1 — ISPRA standalone overlay (`ispra_overlay.py`)

This script processes the national ISPRA mosaic independently, before any ADB merging.

**Steps:**

1. **Load** the three ISPRA shapefiles (H, M, L) with GeoPandas.
2. **Fix invalid geometries** by applying `buffer(0)` to each layer — a standard Shapely trick to repair self-intersections.
3. **Hierarchical difference — M minus H:**
   A spatial-index-accelerated `fast_difference()` function is used instead of the naive `gpd.overlay(..., how='difference')`. For each polygon in M, only candidate polygons from H within the bounding-box intersection are tested. Polygons in M that are fully within H are discarded; partially overlapping ones are trimmed.
4. **Hierarchical difference — L minus (H ∪ M):**
   H and the trimmed M are first concatenated into a combined `H_M` GeoDataFrame. The same fast difference is then applied to L against `H_M`.
5. **Final concatenation:** H (untouched) + M_trimmed + L_trimmed are stacked into a single GeoDataFrame and written to disk.

**Output:** `HPH_Mosaicatura_ISPRA_2020_H_M_L/`

---

### Stage 2 — ADB Po overlay (`adb_po_overlay.py`)

The ADB Po dataset requires an extra pre-processing step because the source shapefiles contain many disconnected polygons per return period that need dissolving before overlay.

**Steps:**

1. **Load** H, M, L shapefiles for the Po district.
2. **Graph-based topological dissolve** (`dissolve_touching_by_rp()`):
   - Applied independently per RP value.
   - A spatial index (R-tree via `gdf.sindex`) identifies candidate polygon pairs.
   - A NetworkX undirected graph is built: each polygon is a node; an edge is added if two polygons touch or intersect.
   - Connected components of this graph are identified; all polygons in a component are unioned into a single geometry (`union_all()`).
   - This avoids dissolving across RP boundaries and prevents over-merging.
3. **Hierarchical overlay** (same H > M > L logic as ISPRA stage):
   - `gpd.overlay(M_dissolved, H_dissolved, how='difference')`
   - `gpd.overlay(L_dissolved, H_M_combined, how='difference')`
4. **Geometry validation** (`filter_valid_geoms()`): polygons with area ≤ 0.25 m² or empty geometries are discarded to eliminate artefacts introduced by topology operations.
5. **Save** intermediate H_dissolved, M_overlay, L_overlay and combined final file.

**Output:** `AA_pda2025_H_dissolved2/`, `AA_pda2025_M_overlay/`, `AA_pda2025_L_overlay/`, `AA_pda2025_H_M_L/`

---

### Stage 3 — ADB AM and AS overlay (`adb_am_overlay.py`, `adb_as_overlay.py`)

Both AM (Alpi Marittime) and AS (Appennino Settentrionale / Alps) districts provide a single pre-merged shapefile with an `RP` attribute already encoding return period. These do not require a hierarchical difference — only the graph-based dissolve is needed to unify touching polygons within each RP class.

**Steps:**

1. **Load** the single merged shapefile.
2. **Graph-based topological dissolve** per RP value (same `dissolve_touching_by_rp()` as Stage 2).
3. **Save** the dissolved result.

**Outputs:** `ADB-AM_2026_merge_RP_overlay/`, `ADB-AS_2026_merge_RP_overlay/`

---

### Stage 4 — ADB AO overlay (`adb_ao_overlay.py`)

The Valle d'Aosta / Appennino Occidentale district uses Tiranti method data at return periods TR30, TR100, TR300.

**Steps:**

1. **Load** three separate shapefiles and assign `RP` values (30, 100, 300) manually since the source files do not carry that attribute.
2. **Hierarchical overlay** without pre-dissolve (source polygons are already clean):
   - `gpd.overlay(M, H, how='difference')`
   - `gpd.overlay(L, H_M_combined, how='difference')`
3. **Save** M_overlay, L_overlay, and the combined `ADB_AO_Tiranti` file.

**Output:** `ADB_AO_Tiranti/`

---

### Stage 5 — Multi-district ADB + ISPRA integration (`adb_overlay.py`)

This is the central integration script that combines all ADB district outputs with the ISPRA national mosaic.

**Steps:**

1. **Load** the three ISPRA shapefiles and three ADB district boundary shapefiles:
   - `delimitazione_distretto_ADB_Sardegna.shp`
   - `delimitazione_distretto_ADB_Sicilia.shp`
   - `delimitazione_distretto_ADB_App_Centrale.shp`
2. **CRS harmonisation:** All district boundary files are reprojected to match the CRS of the ISPRA H layer.
3. **`process_adb()` function** — runs for each district (SI, SA, AC):
   - Clips ISPRA H, M, L layers to the district boundary using `gpd.clip()`.
   - Assigns standardised `RP` values: H→20, M→100, L→200.
   - Assigns an `adb` string identifier.
   - Retains only columns `[RP, adb, geometry]`.
   - Runs full hierarchical overlay: `M_clean = overlay(M, H, difference)`, then `L_clean = overlay(L, HM_valid, difference)`.
   - Applies `filter_valid_geoms()` (area ≥ 0.25 m²) after each overlay step.
   - Returns a final 3-class GeoDataFrame.
4. **Per-district outputs** are saved individually (`ispra_adbsi`, `ispra_adbsa`, `ispra_adbac`).
5. **All three districts are concatenated** into `ispra_adb_ac_si_sa`.
6. **Final merge with the ADB Po / AM / AS / AO pre-processed dataset** (`ADB_merged`):
   - The `ADB_merged` file is an earlier-stage product containing the processed outputs from Stages 2–4.
   - It is concatenated with `ispra_adb_ac_si_sa`.
7. **Write** `ispra_adb_2026` — the unified national flood hazard vector map.

**Output:** `ispra_adb_2026/`

---

### Stage 6 — ADB Po depth raster pipeline (`adbpo_pgra2027.py`)

Separate from the vector pipeline, this stage processes flood water-depth rasters from the PGRA 2027 plan for the low-probability scenario (TR500).

**Steps:**

1. **Discover all input `.tif` tiles** in the source folder.
2. **Reproject each tile** to EPSG:3035 at 5 m resolution using `rasterio.warp.reproject()` with bilinear resampling. Output tiles are written as `float32` with nodata = -9999, DEFLATE-compressed, and tiled for efficient I/O.
3. **Build a GDAL Virtual Raster (VRT)** from all reprojected tiles using `gdal.BuildVRT()`. This avoids physically mosaicking the entire dataset in memory.
4. **Translate the VRT to a single GeoTIFF** at EPSG:3035 using `gdal.Translate()` with DEFLATE compression, BIGTIFF, and tiled output.

**Output:** `adbpo_pgra2027_l_merged_3035_5m.tif`

---

### Stage 7 — Milano TR500 raster integration (`adbpo_pgra2027_milano.py`)

A higher-resolution water depth raster specifically covering the Milan metropolitan area is merged into the ADB Po raster from Stage 6.

**Steps:**

1. **Open** both the ADB Po merged raster and the Milano TR500 raster.
2. **Compute the window** in the ADB Po raster grid that corresponds to the spatial extent of the Milano raster, using `rasterio.windows.from_bounds()`.
3. **Load only the Milan footprint** from the ADB Po raster (windowed read) to keep memory usage bounded.
4. **Pixel-level merge logic:**
   - Where both rasters have valid data: `np.maximum(adb_value, milano_value)` — the higher flood depth is retained.
   - Where only Milano has data (ADB Po is nodata): Milano value is used.
   - Where only ADB Po has data: ADB Po value is retained (by construction, since the base raster is written first).
5. **Write output:** The entire ADB Po base raster is first copied block-by-block to the output file; then the Milan window is overwritten with the merged values. This block-by-block writing avoids loading the full raster into memory.

**Output:** `adbpo_pgra2027_l_merged_milano_tr500_3035_2m.tif`

---

### Stage 8 — PostGIS ingestion

Two strategies are available for loading the final rasters into the PostGIS database.

#### `load_raster.sh` — single-pass load

Wraps `raster2pgsql` for a full raster file:

```bash
raster2pgsql -s <EPSG> -I -C -M <FILE> -t <TILE_SIZE> public.<TABLE> | psql ...
```

Flags: `-I` creates a GiST spatial index, `-C` adds raster constraints, `-M` vacuum-analyses after load.

#### `load_raster_chuncks.sh` — chunked load with retry

Used for very large rasters that exceed single-transaction limits. The script:

1. Reads raster pixel dimensions via `gdalinfo`.
2. Splits the raster into 2000×2000-pixel spatial chunks using `gdal_translate -srcwin`.
3. Loads each chunk with `raster2pgsql` in append mode (`-a`), with up to 3 retries per chunk.
4. Creates a GiST index on `ST_ConvexHull(rast)` after all chunks are loaded.

#### `adpo_pgra2027_milano_to_db.py` — Python-based multi-environment loader

Wraps the `raster2pgsql | psql` pipeline in Python via `subprocess.run()`, with:
- Support for multiple deployment environments (dev, prod, webgis) via environment variable suffixes.
- Automatic PostGIS extension and version verification before load.
- Configurable tile size (default `128x128`).

---

## Orchestration

### `run.sh`

Runs the ADB Po standalone pipeline (used for earlier AA pda2025 data):

```bash
conda activate ccpy4
python -m adb_clip
gsutil -m cp -r ... gs://cc-geodata-bucket/
```

### `run_adbs.sh`

Runs the full multi-district ADB + ISPRA integration (Stage 5) and uploads the result to GCS:

```bash
python -m adb_overlay
gsutil -m cp -r ispra_adb_2026 gs://cc-geodata-bucket/
```

Earlier per-district scripts (`adb_am_overlay`, `adb_as_overlay`, `adb_ao_overlay`, `ispra_overlay`) are preserved as commented-out lines and can be re-run individually.

### `run_adbpo_pgra2027.sh`

Runs the PGRA 2027 Milano check / raster pipeline.

---

## Attribute Schema (final vector output)

All features in `ispra_adb_2026` conform to the following schema:

| Field | Type | Description |
|-------|------|-------------|
| `RP` | Integer | Return period in years (20, 30, 100, 200, 300, 500) |
| `adb` | String | Source district code (e.g. `SI`, `SA`, `AC`, `PO`, `AM`, `AS`, `AO`) |
| `geometry` | Polygon / MultiPolygon | Flood hazard zone (EPSG matches ISPRA source) |

---

## Coordinate Reference Systems

| Dataset | Native CRS | Processing CRS |
|---------|-----------|----------------|
| ISPRA vectors | As distributed (typically EPSG:32632 or EPSG:4326) | Harmonised to ISPRA H CRS at runtime |
| ADB district vectors | Various | Reprojected to ISPRA H CRS via `.to_crs()` |
| ADB Po depth rasters | Various national CRS | EPSG:3035 (ETRS89-LAEA), 5 m resolution |
| PostGIS storage | — | EPSG:3035 |

---

## Geometry Validity and Artefact Removal

Throughout the pipeline, geometry validity is enforced at multiple points:

- **`buffer(0)`** is applied when loading any layer and after every overlay, to repair self-intersections without altering shape.
- **`filter_valid_geoms(min_area=0.25 m²)`** removes slivers and empty geometries introduced by topology operations.
- **`keep_geom_type=False`** is passed to `gpd.overlay()` to retain geometry collections when polygon clips produce lower-dimensional results; these are then filtered by polygon-type checks where needed.

---

## Dependencies

| Library | Purpose |
|---------|---------|
| `geopandas` | Vector I/O, spatial overlay, clip |
| `shapely` | Geometry operations (buffer, difference, union) |
| `networkx` | Connected-component graph for topological dissolve |
| `pandas` | DataFrame concatenation |
| `rasterio` | Raster I/O, reprojection, windowed read/write |
| `gdal` / `osgeo` | VRT building, raster translation, gdalinfo |
| `numpy` | Pixel-level array operations |
| `tqdm` | Progress reporting for long iterations |
| `sqlalchemy` | DB connection verification |
| `raster2pgsql` | CLI tool (PostGIS) for raster ingestion |
| `psql` | CLI tool for DB communication |
| `gsutil` | GCS upload |

Environment: Conda environment `ccpy4` (Python 3.x with PostGIS extension).