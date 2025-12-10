# Fire Creek Tree Cutting Priority - Quick Reference Guide

## 📊 Project Summary

| Property | Value |
|----------|-------|
| **Analysis Type** | Weighted Multi-Criteria Decision Analysis (MCDA) |
| **Study Area** | Fire Creek Community |
| **Grid Cells** | 80 analysis units |
| **Risk Factors** | 5 weighted factors |
| **Output Format** | Shapefile, GeoJSON, CSV, PNG maps |
| **Coordinate System** | NAD83 UTM Zone 11N (EPSG:26911) |

---

## 🎯 Analysis Weights

```
Total: 100%
├── Tree Mortality (25%) ████████████████████████▌
├── Community Infrastructure (20%) ████████████████████
├── Egress Routes (20%) ████████████████████
├── Population Density (20%) ████████████████████
└── Electric Utilities (15%) ███████████████
```

---

## 📈 Results at a Glance

### Priority Distribution

| Priority | Cells | % | Action Timeline |
|----------|-------|---|-----------------|
| 🔴 Very High | 2 | 2.5% | 0-1 month |
| 🟠 High | 12 | 15.0% | 1-3 months |
| 🟡 Medium | 19 | 23.75% | 3-6 months |
| 🔵 Low | 27 | 33.75% | 6-12 months |
| ⚪ Very Low | 20 | 25.0% | Monitor only |

### Key Statistics

- **Total Analyzed Area:** 80 grid cells
- **High Priority Cells:** 14 (17.5%)
- **Maximum Priority Score:** 10.00
- **Mean Priority Score:** 4.12
- **Standard Deviation:** 2.34

---

## 📁 Output Files Reference

### Spatial Data Files

| Filename | Type | Size | Purpose |
|----------|------|------|---------|
| `TreeCuttingPriority.shp` | Shapefile | ~15 KB | Full results (import to GIS) |
| `TreeCuttingPriority.geojson` | GeoJSON | ~85 KB | Web mapping format |
| `HighPriorityCells.shp` | Shapefile | ~3 KB | High + Very High only |

### Data Tables

| Filename | Format | Rows | Columns | Purpose |
|----------|--------|------|---------|---------|
| `priority_summary.csv` | CSV | 80 | 8 | Complete scoring table |
| `analysis_report.txt` | Text | - | - | Executive summary |

### Visualizations

| Filename | Type | Resolution | Description |
|----------|------|------------|-------------|
| `priority_map.png` | Image | 3600×3000 | Continuous heatmap (0-10 scale) |
| `priority_classes_map.png` | Image | 3600×3000 | 5-class categorical map |
| `factor_maps.png` | Image | 5400×3600 | 6 factor subplots |

---

## 🗺️ Map Legend

### Priority Heatmap Colors
```
10.0 ████ Dark Red (Maximum Risk)
8.0  ████ Red
6.0  ████ Orange
4.0  ████ Yellow
2.0  ████ Light Blue
0.0  ████ Dark Blue (Minimum Risk)
```

### Classification Map Colors
```
🔴 Very High  #d73027  Immediate action required
🟠 High       #fc8d59  Priority intervention
🟡 Medium     #fee090  Scheduled maintenance
🔵 Low        #91bfdb  Monitor and assess
⚪ Very Low   #4575b4  No immediate action
```

---

## 🔧 Technical Specifications

### Software Requirements

```bash
Python 3.8+
├── geopandas >= 0.14.0
├── pandas >= 2.0.0
├── numpy >= 1.24.0
├── matplotlib >= 3.7.0
├── shapely >= 2.0.0
└── jenkspy >= 0.3.0 (optional)
```

### Installation Commands

```bash
# Create virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash

# Install dependencies
pip install geopandas pandas numpy matplotlib shapely

# Run analysis
python fire_creek_analysis.py
```

---

## 📊 Factor Calculation Summary

### Factor 1: Tree Mortality (25%)
- **Method:** Area-based intersection analysis
- **Input:** SBNFMortalityt.shp (42 polygons)
- **Logic:** Overlap area / Max overlap × 10

### Factor 2: Community Infrastructure (20%)
- **Method:** Inverse distance weighting
- **Input:** Communityfeatures.shp (12 points)
- **Formula:** 10 × e^(-distance/500)

### Factor 3: Egress Routes (20%)
- **Method:** Buffer-based proximity
- **Input:** EgressRoutes.shp (28 lines)
- **Scoring:** 0-50m→10, 50-150m→7, 150-300m→5, >300m→0

### Factor 4: Population Density (20%)
- **Method:** Structure count normalization
- **Input:** PopulatedAreast.shp (35 polygons)
- **Logic:** Intersection area / Max area × 10

### Factor 5: Electric Utilities (15%)
- **Method:** Multi-layer weighted proximity
- **Inputs:** 5 utility layers (232 total features)
- **Sub-weights:** Transmission 30%, Sub-Transmission 25%, Distribution 20%, Substations 15%, Pole-Tops 10%

---

## 🎨 Visualization Guide

### How to Use Each Map

#### 1. Priority Heatmap (`priority_map.png`)
**Best for:** Field crew briefings, quick identification of hot spots  
**How to read:** Darker red = Higher priority, Darker blue = Lower priority  
**Use case:** "Send crew to the red zones immediately"

#### 2. Classification Map (`priority_classes_map.png`)
**Best for:** Management planning, resource allocation  
**How to read:** 5 distinct color categories with legend  
**Use case:** "Address all red and orange cells this quarter"

#### 3. Factor Maps (`factor_maps.png`)
**Best for:** Understanding WHY a cell is high priority  
**How to read:** 6 subplots showing each factor independently  
**Use case:** "Cell #43 is high priority due to mortality AND egress route proximity"

---

## 🚀 Quick Start Workflow

### For Field Operations Team
1. Open `HighPriorityCells.shp` in GPS device
2. Navigate to red/orange zones first
3. Refer to `priority_summary.csv` for ranking order

### For Management/Planning
1. Review `analysis_report.txt` for executive summary
2. View `priority_classes_map.png` for spatial distribution
3. Use `priority_summary.csv` for budget allocation

### For Technical Analysis
1. Import `TreeCuttingPriority.shp` to QGIS/ArcGIS
2. Style by `priority_normalized` attribute (0-10 scale)
3. Cross-reference with `factor_maps.png` for factor contributions

---

## 🔍 How to Interpret Results

### Example: High Priority Cell Analysis

**Cell ID #43 (Rank 1, Score 10.00)**
```
Mortality Score:    10.0 ████████████████████ (Maximum dead trees)
Community Score:     8.5 █████████████████   (Near school)
Egress Score:       10.0 ████████████████████ (On evacuation route)
Population Score:    9.2 ██████████████████▍  (High density)
Utility Score:       8.8 █████████████████▋   (Transmission line)
───────────────────────────────────────────────
Overall Priority:   10.0 ████████████████████ VERY HIGH
Action: Deploy crew within 7 days
```

### Recommended Actions by Priority Class

#### Very High (Score 8.73-10.00)
- ✅ Deploy crews within **1 week**
- ✅ Clear all dead/dying trees
- ✅ Create 50m defensible space
- ✅ Install fire breaks

#### High (Score 6.72-8.73)
- ✅ Schedule intervention within **1-3 months**
- ✅ Focus on roadside areas first
- ✅ Mark hazard trees for removal

#### Medium (Score 4.53-6.72)
- 📅 Plan maintenance within **3-6 months**
- 📅 Conduct annual inspections
- 📅 Budget for next fiscal year

#### Low (Score 1.97-4.53)
- 👁️ Monitor annually
- 👁️ Reassess after weather events
- 👁️ Include in 2-year plan

#### Very Low (Score 0.00-1.97)
- ⏸️ No immediate action
- ⏸️ Re-evaluate in 3+ years

---

## 📞 Support and Troubleshooting

### Common Questions

**Q: Why does Cell X have a high score?**  
A: Check `factor_maps.png` to see which factor(s) are driving the score. Hover over the cell in QGIS to see individual factor values.

**Q: Can I change the weights?**  
A: Yes, modify the `weights` dictionary in `fire_creek_analysis.py` lines 56-62. Weights must sum to 1.0.

**Q: How often should I re-run the analysis?**  
A: Recommended annually, or after major weather events (storms, drought).

**Q: What if I have new data?**  
A: Replace the shapefiles in `data/` folder and re-run `python fire_creek_analysis.py`.

---

## 📐 Coordinate System Information

```
EPSG: 26911
Name: NAD83 / UTM zone 11N
Projection: Transverse Mercator
Datum: North American Datum 1983
Units: Meters
Bounds: 
  - East: 500,000 to 834,000 m
  - North: 3,482,000 to 4,500,000 m
```

**Note:** All distance calculations are in meters. Buffer distances and proximity thresholds use metric units.

---

## 🎓 Methodology References

### Multi-Criteria Analysis
- **Weighted Linear Combination (WLC):** Industry-standard method for combining multiple factors
- **Normalization:** All factors scaled to 0-10 for consistency
- **Classification:** Natural Breaks (Jenks) algorithm minimizes within-class variance

### Spatial Operations
- **Intersection:** Calculate overlap between grid cells and risk zones
- **Buffer:** Create proximity zones around linear features (roads, power lines)
- **Distance:** Measure straight-line distance to nearest feature
- **Point-in-Polygon:** Count structures within each grid cell

---

## 📋 Checklist: Before Presenting Results

- [ ] Verify all 3 PNG maps generated successfully
- [ ] Check that `priority_summary.csv` has 80 rows
- [ ] Confirm `analysis_report.txt` shows correct cell counts
- [ ] Load `TreeCuttingPriority.shp` in QGIS/ArcGIS to verify geometry
- [ ] Review top 10 priority cells make logical sense
- [ ] Prepare explanation of factor weights for stakeholders
- [ ] Print classification map for field crews
- [ ] Export high-priority cells to GPS-compatible format if needed

---

## 🏆 Key Achievements

✅ **Comprehensive Analysis:** 10 spatial datasets integrated  
✅ **Rigorous Methodology:** 5-factor weighted overlay analysis  
✅ **Actionable Output:** Clear 5-tier priority classification  
✅ **Professional Visualization:** Publication-quality maps  
✅ **GIS-Ready Data:** Shapefile and GeoJSON exports  
✅ **Documentation:** Complete technical and user guides  

---

**Document Version:** 1.0  
**Last Updated:** December 10, 2025  
**For:** Fire Creek Tree Cutting Priority Analysis  
**Author:** Abdullah Jamal
