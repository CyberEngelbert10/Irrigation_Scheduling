# Zambian Agriculture Reference
## Field Model Data Choices

**Purpose:** Reference data for dropdown choices in Field Management forms  
**Last Updated:** October 7, 2025

---

## Zambian Provinces (Regions)

### Primary Agricultural Regions:
1. **Lusaka** - Capital region, mixed farming, urban agriculture
2. **Central Province** - Zambia's maize belt, commercial farming hub
3. **Southern Province** - Cattle ranching and maize production
4. **Eastern Province** - Maize, cotton, tobacco, groundnuts
5. **Copperbelt** - Urban farming, vegetables, peri-urban agriculture
6. **Northern Province** - Cassava, beans, finger millet
7. **Western Province** - Rice cultivation, cassava, fishing
8. **Luapula** - Fish farming, cassava, vegetables
9. **Muchinga** - Beans, maize, groundnuts
10. **North-Western** - Cassava, maize, forest products

### Climate Zones:
- **Region I** (Southern, Western): Semi-arid, 600-800mm annual rainfall
- **Region II** (Central, Eastern, Lusaka): Sub-humid, 800-1000mm rainfall
- **Region III** (Northern, Luapula, Muchinga, North-Western): Humid, 1000-1500mm+ rainfall

---

## Crop Types (Supported by AI Model)

### Major Crops:
1. **Maize** (Zea mays)
   - Most important staple crop in Zambia
   - Grown in all provinces
   - Rain-fed and irrigated varieties
   - Growing season: 120-150 days

2. **Wheat** (Triticum aestivum)
   - Grown in Southern and Central provinces
   - Mainly irrigated crop
   - Growing season: 90-120 days
   - Cool season crop (May-September)

3. **Rice** (Oryza sativa)
   - Western Province (Barotse plains)
   - Luapula Province
   - Requires flooded/paddy conditions
   - Growing season: 120-150 days

4. **Tomatoes** (Solanum lycopersicum)
   - High-value vegetable crop
   - Grown near urban areas
   - Requires regular irrigation
   - Growing season: 70-90 days

5. **Potatoes** (Solanum tuberosum)
   - Eastern and Northern provinces
   - Cool season crop
   - Growing season: 90-120 days

6. **Cotton** (Gossypium spp.)
   - Eastern, Southern, Central provinces
   - Rain-fed crop
   - Growing season: 150-180 days

### Future Expansion (Not in Current Model):
- Groundnuts (peanuts)
- Sorghum
- Finger millet
- Sunflower
- Soybeans
- Cassava

---

## Soil Types (Common in Zambia)

### Primary Soil Classifications:
1. **Clay**
   - High water retention
   - Slow drainage
   - Common in valleys and dambo areas
   - Suitable for: Rice, maize (with drainage)

2. **Loam**
   - Best agricultural soil
   - Good water retention and drainage
   - Suitable for: Most crops, ideal for vegetables

3. **Sandy**
   - Fast drainage
   - Low water retention
   - Requires more frequent irrigation
   - Suitable for: Groundnuts, cassava, early maturing crops

4. **Silty**
   - Moderate water retention
   - Prone to erosion
   - Suitable for: Most crops with proper management

### Soil Fertility Zones:
- **High Fertility:** Luapula, Northern (high organic matter)
- **Medium Fertility:** Central, Eastern, Copperbelt
- **Low Fertility:** Southern, Western (sandy soils)

---

## Irrigation Methods (Common in Zambia)

### 1. **Drip Irrigation**
- Most water-efficient (90-95% efficiency)
- Suitable for: Vegetables, tomatoes, high-value crops
- Initial cost: High
- Running cost: Low
- Best for: Small-scale commercial farms

### 2. **Sprinkler Irrigation**
- Medium efficiency (70-85%)
- Suitable for: Maize, wheat, potatoes
- Initial cost: Medium-High
- Running cost: Medium
- Best for: Medium to large-scale farms

### 3. **Flood/Furrow Irrigation**
- Low efficiency (40-60%)
- Suitable for: Rice, maize, wheat
- Initial cost: Low
- Running cost: Low
- Best for: Traditional farming, rice paddies

### 4. **Rain-fed** (No irrigation)
- Zero irrigation cost
- Dependent on seasonal rainfall
- Suitable for: Maize, cotton (in high rainfall regions)
- Risk: High (drought vulnerability)

---

## Seasons in Zambia

### 1. **Dry Season** (May - October)
- **Cool Dry:** May - August (15-25°C)
- **Hot Dry:** September - October (25-35°C)
- No rainfall
- Irrigation required for all crops
- Ideal for: Wheat, winter vegetables

### 2. **Wet Season** (November - April)
- **Main Rainy Season:** December - March
- 80-90% of annual rainfall occurs
- High humidity (70-90%)
- Ideal for: Maize, rice, cotton, most crops
- Challenge: Disease and pest pressure

### 3. **Transition Periods**
- **October - November:** Pre-rains, hot and humid
- **April - May:** Post-rains, cooling down

---

## Weather Parameters (for AI Model)

### Temperature
- **Cool Season:** 15-25°C (May-August)
- **Hot Season:** 25-35°C (September-November)
- **Rainy Season:** 20-30°C (December-April)

### Humidity
- **Dry Season:** 20-40%
- **Wet Season:** 60-90%

### Rainfall
- **Annual Average:** 600-1500mm (varies by region)
- **Rainy Days:** 60-100 days per year
- **Peak Months:** December, January, February

### Wind Speed
- **Average:** 5-15 km/h
- **Peak (September):** 15-25 km/h

---

## Data Sources

1. **Zambia Meteorological Department** - Weather data
2. **Ministry of Agriculture, Zambia** - Crop calendars and zones
3. **IAPRI (Indaba Agricultural Policy Research Institute)** - Agricultural statistics
4. **FAO Zambia** - Irrigation and water management data

---

## Usage in Application

### Field Model Choices:
```python
REGION_CHOICES = [
    ('lusaka', 'Lusaka'),
    ('central', 'Central Province'),
    ('southern', 'Southern Province'),
    ('eastern', 'Eastern Province'),
    ('copperbelt', 'Copperbelt'),
    ('northern', 'Northern Province'),
    ('western', 'Western Province'),
    ('luapula', 'Luapula'),
    ('muchinga', 'Muchinga'),
    ('northwestern', 'North-Western'),
]

CROP_CHOICES = [
    ('maize', 'Maize'),
    ('wheat', 'Wheat'),
    ('rice', 'Rice'),
    ('tomatoes', 'Tomatoes'),
    ('potatoes', 'Potatoes'),
    ('cotton', 'Cotton'),
]

SOIL_CHOICES = [
    ('clay', 'Clay'),
    ('loam', 'Loam'),
    ('sandy', 'Sandy'),
    ('silty', 'Silty'),
]

IRRIGATION_CHOICES = [
    ('drip', 'Drip Irrigation'),
    ('sprinkler', 'Sprinkler Irrigation'),
    ('flood', 'Flood/Furrow Irrigation'),
    ('rainfed', 'Rain-fed (No Irrigation)'),
]

SEASON_CHOICES = [
    ('dry', 'Dry Season'),
    ('wet', 'Wet Season'),
]
```

---

**Note:** This reference will be used to populate dropdown choices in the Field Management forms to ensure data consistency for AI model predictions.
