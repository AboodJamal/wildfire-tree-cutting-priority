# Fire Creek Tree Cutting Priority Analysis

<p align="center">
  <img src="docs/priority_map.png" alt="Priority Map Visualization" width="800"/>
</p>

## Assignment

> **Task:** Identify and prioritize areas for tree cutting to reduce wildfire risk in Fire Creek community.
>
> **Analysis Method:** Weighted Multi-Criteria Decision Analysis (MCDA)
>
> **Selection Criteria:**
> 1. **Tree Mortality (25%)** - Areas with high concentrations of dead/dying trees
> 2. **Community Infrastructure (20%)** - Proximity to schools, fire stations, and essential facilities
> 3. **Egress Routes (20%)** - Road networks critical for evacuation
> 4. **Population Density (20%)** - Residential areas with higher structure density
> 5. **Electric Utilities (15%)** - Power infrastructure vulnerable to tree falls
>
> **Tools:** Python (GeoPandas, Matplotlib) + GIS Spatial Analysis

---

## Project Overview

This project uses **spatial multi-criteria analysis** to prioritize tree cutting operations in Fire Creek based on wildfire risk factors. The solution combines multiple spatial datasets through weighted overlay analysis to identify high-priority intervention zones.

### Objective

Determine which grid cells require **immediate tree cutting intervention** based on:
- Tree mortality rates and dead vegetation concentration
- Proximity to critical community infrastructure
- Accessibility via evacuation routes
- Population exposure and structure density
- Electric utility infrastructure vulnerability

---

## Analysis Framework

### Methodology: Weighted Linear Combination (WLC)

For each grid cell, a priority score is calculated using:

```
Priority Score = (0.25 × Mortality) + (0.20 × Community) + 
                 (0.20 × Egress) + (0.20 × Population) + 
                 (0.15 × Utilities)
```

### Weight Rationale

| Factor | Weight | Justification |
|--------|--------|---------------|
| **Tree Mortality** | 25% | Dead trees are the primary fuel source for wildfires |
| **Community Infrastructure** | 20% | Essential facilities require maximum protection |
| **Egress Routes** | 20% | Clear evacuation routes save lives |
| **Population Density** | 20% | More people = higher risk exposure |
| **Electric Utilities** | 15% | Power lines can ignite fires and lose critical services |

---

## Data Inventory

### Input Datasets

Located in the `data/` directory:

| Dataset | Type | Features | Description |
|---------|------|----------|-------------|
| `CuttingGrids.shp` | Polygon | 80 | Analysis grid cells (study area subdivision) |
| `SBNFMortalityt.shp` | Polygon | 42 | Southern Bark Beetle mortality zones |
| `Communityfeatures.shp` | Point | 12 | Schools, fire stations, community centers |
| `EgressRoutes.shp` | Line | 28 | Primary and secondary evacuation roads |
| `PopulatedAreast.shp` | Polygon | 35 | Residential zones with structure density |
| `Transmission.shp` | Line | 8 | High-voltage transmission lines |
| `SubTransmission.shp` | Line | 15 | Sub-transmission power lines |
| `DistCircuits.shp` | Line | 156 | Distribution circuits (local power) |
| `Substations.shp` | Point | 3 | Electrical substations |
| `PoleTopSubs.shp` | Point | 45 | Pole-mounted transformers |

### Coordinate System

| Property | Value |
|----------|-------|
| **CRS** | NAD83 / UTM Zone 11N |
| **EPSG** | 26911 |
| **Units** | Meters |
| **Projection** | Universal Transverse Mercator |

---

## Analysis Pipeline

### Step 1: Data Loading and Projection

All 10 shapefiles are loaded and reprojected to a common coordinate system (NAD83 UTM 11N) to ensure accurate spatial calculations.

```python
# All layers reprojected to match CuttingGrids CRS
self.cutting_grid = gpd.read_file("CuttingGrids.shp")
self.tree_mortality = gpd.read_file("SBNFMortalityt.shp").to_crs(base_crs)
# ... (8 more layers)
```

### Step 2: Factor Scoring (Normalized 0-10)

Each grid cell receives a score for each of the 5 factors:

#### Factor 1: Tree Mortality Score
- **Method:** Calculate area of overlap between grid cells and mortality polygons
- **Normalization:** Linear scale 0-10 (highest overlap = 10)
- **Logic:** More dead trees = Higher fire fuel load

```python
mortality_overlap = grid_cell.intersection(mortality_zones).area
mortality_score = normalize(mortality_overlap, 0, max_overlap) * 10
```

#### Factor 2: Community Infrastructure Score
- **Method:** Inverse distance weighting to nearest community facility
- **Normalization:** Exponential decay (closer = higher score)
- **Logic:** Protect schools, fire stations, and community centers

```python
min_distance = min(distance(grid_cell, facility) for facility in community_features)
community_score = 10 * exp(-min_distance / decay_factor)
```

#### Factor 3: Egress Route Score
- **Method:** Proximity to evacuation roads with buffer analysis
- **Normalization:** Distance-based decay function
- **Logic:** Keep escape routes clear of falling trees

```python
if ST_Intersects(grid_cell, egress_buffer_50m):
    egress_score = 10
elif ST_DWithin(grid_cell, egress_routes, 150m):
    egress_score = 5 - 7 (distance-based)
else:
    egress_score = 0
```

#### Factor 4: Population Density Score
- **Method:** Structure density calculation within grid cell
- **Normalization:** Linear scale based on structure count
- **Logic:** Protect areas where more people live

```python
structure_count = count(structures WITHIN grid_cell)
population_score = normalize(structure_count, 0, max_structures) * 10
```

#### Factor 5: Electric Utilities Score
- **Method:** Combined proximity to all 5 utility types
- **Weights:** Transmission (30%), Sub-Transmission (25%), Distribution (20%), Substations (15%), Pole-Tops (10%)
- **Logic:** Prevent tree-caused power outages and electrical fires

```python
utility_score = (0.30 * transmission_proximity +
                 0.25 * subtransmission_proximity +
                 0.20 * distribution_proximity +
                 0.15 * substation_proximity +
                 0.10 * poletop_proximity)
```

### Step 3: Weighted Overlay

Combine all factor scores using predetermined weights:

```python
priority_score = (0.25 * mortality_score +
                  0.20 * community_score +
                  0.20 * egress_score +
                  0.20 * population_score +
                  0.15 * utility_score)
```

### Step 4: Classification

Grid cells are classified into 5 priority classes using Natural Breaks (Jenks) classification:

| Class | Score Range | Action Required |
|-------|-------------|-----------------|
| **Very High** | 8.73 - 10.00 | Immediate intervention (within 1 month) |
| **High** | 6.72 - 8.73 | Priority action (within 3 months) |
| **Medium** | 4.53 - 6.72 | Scheduled maintenance (within 6 months) |
| **Low** | 1.97 - 4.53 | Monitor and assess (annual review) |
| **Very Low** | 0.00 - 1.97 | No immediate action required |

---

## Results Summary

### Priority Distribution

| Priority Class | Cell Count | Percentage | Action Timeline |
|----------------|------------|------------|-----------------|
| **Very High** | 2 | 2.5% | **Immediate** (0-1 month) |
| **High** | 12 | 15.0% | **Soon** (1-3 months) |
| **Medium** | 19 | 23.75% | **Scheduled** (3-6 months) |
| **Low** | 27 | 33.75% | **Monitor** (6-12 months) |
| **Very Low** | 20 | 25.0% | **No action** (>12 months) |
| **Total** | **80** | **100%** | - |

### Top 10 Highest Priority Cells

| Rank | Priority Score | Class | Dominant Factors |
|------|----------------|-------|------------------|
| 1 | 10.00 | Very High | All factors critical |
| 2 | 8.73 | Very High | High mortality + egress |
| 3 | 7.55 | High | Community + utilities |
| 4 | 7.38 | High | Population + mortality |
| 5 | 7.31 | High | Egress + utilities |
| 6 | 7.24 | High | Mortality + community |
| 7 | 7.20 | High | Population + egress |
| 8 | 7.14 | High | Utilities + mortality |
| 9 | 6.74 | High | Community + population |
| 10 | 6.72 | High | Egress + mortality |

### Key Findings

1. **2 cells require immediate attention** - These represent critical risk zones where multiple high-risk factors converge
2. **14 cells (17.5%) are High or Very High priority** - Should be addressed within 3 months
3. **Geographic clustering** - High-priority cells concentrate near populated areas along main roads
4. **Utility corridors** - Transmission line corridors show elevated risk due to tree mortality
5. **Evacuation route vulnerability** - Main egress routes traverse multiple high-risk zones

---

## Visualization Outputs

### 1. Priority Heatmap (`priority_map.png`)

<p align="center">
  <img src="docs/priority_map.png" alt="Priority Heatmap" width="700"/>
</p>

**Description:** Continuous color gradient showing priority scores (0-10). Red indicates highest priority, blue indicates lowest.

**Usage:** Quick visual identification of hot spots for field crews.

---

### 2. Priority Classification Map (`priority_classes_map.png`)

<p align="center">
  <img src="docs/priority_classes_map.png" alt="Priority Classes" width="700"/>
</p>

**Description:** Categorical map showing 5 priority classes with distinct colors.

**Usage:** Management planning and resource allocation by priority tier.

---

### 3. Factor Analysis Map (`factor_maps.png`)

<p align="center">
  <img src="docs/factor_maps.png" alt="Factor Analysis" width="700"/>
</p>

**Description:** Small-multiple visualization showing individual factor scores for each grid cell.

**Usage:** Understanding which factors drive high priority in specific areas.

---

## Output Files

### Spatial Outputs (GIS-Ready)

| File | Format | Description | Use Case |
|------|--------|-------------|----------|
| `TreeCuttingPriority.shp` | Shapefile | Full results with all scores | Import to ArcGIS/QGIS |
| `TreeCuttingPriority.geojson` | GeoJSON | Web-compatible format | Web mapping applications |
| `HighPriorityCells.shp` | Shapefile | Filtered High + Very High cells only | Field crew GPS devices |

### Tabular Outputs

| File | Format | Description |
|------|--------|-------------|
| `priority_summary.csv` | CSV | Complete scoring table (80 rows) |
| `analysis_report.txt` | Text | Executive summary and statistics |

### Visualization Outputs

| File | Format | Description |
|------|--------|-------------|
| `priority_map.png` | Image | Continuous heatmap visualization |
| `priority_classes_map.png` | Image | Categorical classification map |
| `factor_maps.png` | Image | Individual factor analysis (6 subplots) |

---

## Technical Implementation

### Software Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Language** | Python | 3.8+ |
| **Spatial Analysis** | GeoPandas | 0.14+ |
| **Data Processing** | Pandas | 2.0+ |
| **Numerical Computing** | NumPy | 1.24+ |
| **Visualization** | Matplotlib | 3.7+ |
| **Geometry Operations** | Shapely | 2.0+ |

### Key Spatial Functions Used

| Function | Purpose | Example |
|----------|---------|---------|
| `ST_Intersection()` | Calculate overlap area | Mortality zone coverage |
| `ST_Distance()` | Measure proximity | Distance to community features |
| `ST_Buffer()` | Create proximity zones | Egress route buffers |
| `ST_Within()` | Point-in-polygon test | Structures within grid cells |
| `ST_Intersects()` | Spatial overlap test | Utility line crossings |

### Performance Optimizations

- **Spatial Indexing:** All GeoDataFrames use R-tree spatial index
- **CRS Pre-projection:** Single reprojection at data load (not per operation)
- **Vectorized Operations:** NumPy arrays for scoring calculations
- **Progressive Filtering:** Early elimination of non-intersecting geometries

---

## Project Structure

```
tree-cutting-priority/
├── data/                           # Input data directory
│   ├── CuttingGrids.shp           # 80 analysis grid cells
│   ├── SBNFMortalityt.shp         # Tree mortality zones
│   ├── Communityfeatures.shp      # Community infrastructure
│   ├── EgressRoutes.shp           # Evacuation routes
│   ├── PopulatedAreast.shp        # Residential areas
│   ├── Transmission.shp           # Power transmission lines
│   ├── SubTransmission.shp        # Sub-transmission lines
│   ├── DistCircuits.shp           # Distribution circuits
│   ├── Substations.shp            # Electrical substations
│   └── PoleTopSubs.shp            # Pole-mounted transformers
├── output/                         # Analysis results
│   ├── TreeCuttingPriority.shp    # Full results shapefile
│   ├── TreeCuttingPriority.geojson # GeoJSON export
│   ├── HighPriorityCells.shp      # High priority subset
│   ├── priority_summary.csv       # Complete scoring table
│   ├── analysis_report.txt        # Text summary report
│   ├── priority_map.png           # Heatmap visualization
│   ├── priority_classes_map.png   # Classification map
│   └── factor_maps.png            # Factor analysis subplots
├── docs/                           # Documentation assets
│   ├── priority_map.png           # README images
│   ├── priority_classes_map.png
│   └── factor_maps.png
├── fire_creek_analysis.py          # Main analysis script (721 lines)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── TECHNICAL_REPORT.md                     # Detailed technical documentation
```

---

## Getting Started

### Prerequisites

- **Python 3.8+** (Anaconda recommended)
- **GeoPandas** with all dependencies (GDAL, Fiona, Shapely)
- **Matplotlib** for visualization
- **NumPy** and **Pandas** for data processing

### Installation

```bash
# Clone or download the project
cd tree-cutting-priority

# Create virtual environment (recommended)
python -m venv .venv
source .venv/Scripts/activate  # On Windows Git Bash
# .venv\Scripts\activate       # On Windows CMD
# source .venv/bin/activate    # On Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Running the Analysis

```bash
# Activate virtual environment
source .venv/Scripts/activate

# Run the complete analysis
python fire_creek_analysis.py

# Expected runtime: 2-5 minutes
# Output: All files will be generated in output/ directory
```

### Viewing Results

**Option 1: View in QGIS**
1. Open QGIS
2. Add Vector Layer → `output/TreeCuttingPriority.shp`
3. Style by `priority_class` attribute (Categorized)
4. Color scheme: Dark Red (Very High) → Blue (Very Low)

**Option 2: View in ArcGIS**
1. Add Data → `output/TreeCuttingPriority.shp`
2. Symbology → Unique Values → `priority_class`
3. Apply red-to-blue color ramp

**Option 3: View in Python**
```python
import geopandas as gpd
import matplotlib.pyplot as plt

# Load results
results = gpd.read_file('output/TreeCuttingPriority.shp')

# Plot
results.plot(column='priority_normalized', legend=True, 
             figsize=(10, 8), cmap='RdYlGn_r')
plt.title('Fire Creek Tree Cutting Priority')
plt.show()
```

---

## Methodology Validation

### Sensitivity Analysis

The weight allocation was validated through sensitivity testing:

| Scenario | Mortality | Community | Egress | Population | Utilities | Result Stability |
|----------|-----------|-----------|--------|------------|-----------|------------------|
| **Base** | 25% | 20% | 20% | 20% | 15% | - |
| Equal Weights | 20% | 20% | 20% | 20% | 20% | 92% cells unchanged |
| Mortality Focus | 40% | 15% | 15% | 15% | 15% | 87% cells unchanged |
| Population Focus | 15% | 15% | 15% | 40% | 15% | 89% cells unchanged |

**Conclusion:** Top 20% priority cells remain consistent across weight variations, indicating robust methodology.

---

## Recommendations

### Immediate Actions (Next 30 Days)
- **Deploy crews to 2 Very High priority cells** immediately
- **Conduct field verification** of top 5 priority cells
- **Clear 50m buffer** along primary egress routes in high-priority zones

### Short-Term Actions (1-3 Months)
- **Address all 12 High priority cells** with systematic tree removal
- **Install emergency fire breaks** in cells scoring >7.0
- **Update mortality data** with ground-truthing surveys

### Long-Term Planning (6-12 Months)
- **Monitor Medium priority cells** quarterly
- **Re-run analysis** annually with updated data
- **Integrate weather data** (wind patterns, precipitation) for dynamic risk modeling
- **Expand analysis** to adjacent communities using same methodology

---

## Key Learnings

1. **Multi-Criteria Analysis Power** - Combining diverse factors reveals risk patterns invisible in single-factor analysis
2. **Weight Sensitivity** - Mortality and egress factors have highest influence on final prioritization
3. **Spatial Clustering** - High-priority cells cluster along populated corridors and utility rights-of-way
4. **Data Quality Matters** - Accurate mortality data is critical; field verification recommended
5. **Actionable Output** - Classification into 5 tiers enables clear resource allocation decisions

---

## Author

**Abdullah Jamal**  
Spatial Data Analysis Course  
Fourth Year, First Term  
Fire Creek Tree Cutting Priority Analysis using Multi-Criteria GIS

---

## License

This project is for educational purposes as part of spatial data analysis coursework.

---

**Last Updated:** December 10, 2025  
**Analysis Version:** 1.0  
**Data Snapshot Date:** 2025
