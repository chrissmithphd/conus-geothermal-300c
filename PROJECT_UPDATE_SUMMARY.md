# Project Update Summary - September 15, 2026

## ✅ Completed Tasks

### 1. Coal Power Plant Overlay Analysis

**Question:** Which coal plants could be converted to geothermal?

**Answer:** Only 23 of 340 plants (7%) have accessible geothermal resources.

**Key Findings:**
- 22 of 23 accessible plants are in the western US
- Eastern US: 1 of 290 plants accessible (<1%)
- Best candidates:
  - Centralia, WA: 1,460 MW, 6.2 km depth (LARGEST)
  - Huntington, UT: 1,016 MW, 6.7 km depth
  - Boardman, OR: 642 MW, 7.0 km depth (RETIRED - immediate opportunity)

**Deliverables:**
- ✅ `plots/coal_plants_geothermal_overlay.png` - CONUS-wide map
- ✅ `plots/coal_plants_western_zoom.png` - Western states detail
- ✅ `data/processed/coal_plants_with_geothermal.csv` - All 340 plants matched
- ✅ `data/processed/coal_geothermal_top_candidates.csv` - Top 50 ranked
- ✅ `COAL_GEOTHERMAL_ANALYSIS.md` - Comprehensive analysis document

---

### 2. Energy Generation Potential Analysis

**Question:** How much electricity could be generated instead of just area coverage?

**Answer:** 3,000 GW with proven drilling (≤7 km), 10,342 GW with frontier drilling (≤10 km).

**Key Findings:**
- **3,000 GW at ≤7 km depth** = 2.3× total US electricity capacity
- **10,342 GW at ≤10 km depth** = 8.0× total US electricity capacity
- Could replace all US coal+gas (696 GW) and still have 9× capacity remaining
- Moving from 7 km to 10 km drilling capability = **3.4× capacity increase**

**Power Density by Temperature:**
- Conventional (150-200°C): 10-15 MW/km²
- Superhot (300-400°C): 30-40 MW/km²
- Supercritical (>374°C): 25-35 MW/km² (IDDP-2 demonstrated 45 MW from single well!)

**Deliverables:**
- ✅ `ENERGY_GENERATION_RESEARCH.md` - Research on geothermal power output
- ✅ `data/processed/energy_generation_potential.csv` - Capacity calculations
- ✅ `ENERGY_SUMMARY.md` - Executive summary with tables
- ✅ `calculate_energy_potential.py` - Analysis script

---

## 📊 Summary Tables

### Energy Potential by Depth (Typical Development Scenario)

| Depth Bin | Area (km²) | Temperature | Potential Capacity | % of US Total |
|-----------|-----------|-------------|-------------------|---------------|
| 5-6 km | 16,285 | 350°C | 114 GW | 9% |
| 6-7 km | 412,296 | 325°C | 2,886 GW | 224% |
| 7-8 km | 32,000 | 325°C | 224 GW | 17% |
| 8-10 km | 1,016,841 | 325°C | 7,118 GW | 553% |
| **Total ≤10 km** | **1,477,468** | **—** | **10,342 GW** | **804%** |

### Coal Plants by Geothermal Depth

| Depth Category | # Plants | Total Capacity | Best Candidates |
|----------------|----------|----------------|-----------------|
| **6-7 km** | 5 | 4,228 MW | Centralia WA, Huntington UT, Boardman OR |
| **7-8 km** | 2 | 1,893 MW | Craig CO, Hayden CO |
| **8-10 km** | 16 | 11,574 MW | Navajo AZ (retired), San Juan NM (retired) |
| **>10 km** | 317 | 249,195 MW | Entire eastern US coal fleet |

---

## 📁 New Files Created

### Analysis Scripts
- `analyze_coal_geothermal_overlay.py` - Matches coal plants to geothermal grid
- `create_coal_overlay_map.py` - Generates overlay visualizations
- `calculate_energy_potential.py` - Calculates MW/GW capacity from area

### Data Files
- `data/raw/coal_plants/eia_coal_plants.csv` - 340 US coal plants from EIA Form 860
- `data/processed/coal_plants_with_geothermal.csv` - Plants matched to geothermal depth
- `data/processed/coal_geothermal_top_candidates.csv` - Ranked conversion candidates
- `data/processed/energy_generation_potential.csv` - Capacity by depth bin

### Visualizations
- `plots/coal_plants_geothermal_overlay.png` - CONUS map with all coal plants
- `plots/coal_plants_western_zoom.png` - Western states detail map

### Documentation
- `COAL_GEOTHERMAL_ANALYSIS.md` - Full coal plant analysis (17 pages)
- `ENERGY_GENERATION_RESEARCH.md` - Geothermal power output research
- `ENERGY_SUMMARY.md` - Energy generation potential summary
- `COAL_PLANTS_SUMMARY.md` - Coal plant data acquisition summary

---

## 🎯 Key Insights

### 1. Geographic Reality Check
**The eastern US coal fleet (235 GW) has essentially zero accessible geothermal conversion potential.** Only 1 of 290 eastern plants sits on ≤10 km resources. Coal-to-geothermal is a **western US story only**.

### 2. The Resource Is Enormous
**3,000 GW with proven drilling** is enough to:
- Replace all US coal (180 GW) **17 times over**
- Replace all US coal+gas (696 GW) **4 times over**
- Power the entire US electricity system (1,287 GW) **2.3 times over**

### 3. Drilling Depth Is Everything
Going from 7 km to 10 km drilling capability **triples** the accessible capacity (3,000 GW → 10,342 GW). This single technology improvement is worth **7,342 GW** of additional capacity.

### 4. Technology Demonstration Matters
**IDDP-2 in Iceland demonstrated 45 MW from a single supercritical well** at 427°C. That's **10× the output of a conventional geothermal well** and **4× the output of a large wind turbine**. If this can be replicated commercially, it changes everything.

### 5. Coal Conversion Is Real But Limited
Only 23 coal plants have accessible geothermal, but they include some large, strategic sites:
- **Centralia, WA (1,460 MW)** - Largest accessible operating plant
- **Navajo, AZ (2,409 MW)** - Largest retired plant with accessible geothermal
- **Boardman, OR (642 MW)** - Already retired, infrastructure available now

---

## 🚀 Recommended Next Steps

### Immediate (This Week)
1. ⬜ **Update README.md** with energy generation tables (replace area-only stats)
2. ⬜ **Add coal overlay maps** to README and index.html
3. ⬜ **Commit and push** all new analysis to GitHub

### Short-Term (Next Month)
4. ⬜ **Interactive coal overlay map** (Plotly version for GitHub Pages)
5. ⬜ **Energy calculator tool** - "How much capacity at X km depth?"
6. ⬜ **Regional breakdowns** - State-by-state energy potential

### Long-Term (Future Projects)
7. ⬜ **Transmission analysis** - Distance from resources to demand centers
8. ⬜ **Economic modeling** - LCOE estimates for different depth/temperature scenarios
9. ⬜ **Environmental overlay** - Protected lands, water availability, seismic risk
10. ⬜ **Drilling technology roadmap** - What R&D is needed to reach 10 km commercially?

---

## 📈 Impact Statement

This analysis transforms the project from **"here's where the hot rocks are"** to **"here's how much clean energy America could generate."**

**Before:**
- "83% of CONUS requires >10 km drilling"
- Focused on area coverage percentages
- Hard to grasp the scale

**After:**
- "3,000 GW available with proven drilling—that's 17× US coal capacity"
- Focused on actual electricity generation potential
- Immediate impact comparison to existing grid

The coal overlay adds a **real-world conversion pathway** that connects abstract geothermal potential to actual power plants, workers, and communities.

---

## 🎓 What We Learned

1. **Supercritical geothermal is a game-changer:** 45 MW per well vs 4 MW for conventional
2. **The resource is not the bottleneck:** 10,000+ GW is available
3. **Drilling technology is the bottleneck:** Need to get from 5 km (easy) to 10 km (hard) commercially
4. **Geography matters:** Western US has the resources; eastern US has the demand
5. **Coal conversion is limited but strategic:** 23 plants, but they're in the right places (West)

---

**Analysis Date:** September 15, 2026  
**Total Analysis Time:** ~6 hours (research, coding, visualization, documentation)  
**Lines of Code:** ~800 (3 new Python scripts)  
**Data Processed:** 535k geothermal cells + 340 coal plants = 535,340 records  
**New Insights:** 🔥 3,000 GW of clean baseload power waiting to be unlocked 🔥
