# Dynamic Config System - Implementation Summary

## ✅ Phase 1 & 2 Complete: Foundation Built

### What Was Done

#### 1. Models Cleaned (`teams/models.py`)
- **Teams Model**: Removed 15 hardcoded pit scouting fields → Added `pit_data` JSONField
- **Team_Match_Data Model**: Removed 20+ game-specific columns → Added `data` JSONField
- **Anchor Fields Preserved**:
  - `team_number`, `event`, `match_number`, `scout_name`, `quantifier`
  - `start_pos`, `comment`
  - `is_broken`, `is_disabled`, `is_tipped`
- **Removed**: `auto_path` (as requested)
- **Updated**: `unique_together` now includes `scout_name` to allow multiple scouts per match

#### 2. Config Loader Created (`utils.py`)
- **Hot-Reload**: Checks file modification timestamp on every request
- **Smart Cache**: Loads config once, reloads only when file changes
- **Validation**: Built-in type checking and min/max validation
- **Thread-Safe**: Singleton pattern with lock

#### 3. Game Config Created (`game_config.json`)
- **18 Metrics**: All 2025 Reefscape scoring elements
- **15 Pit Questions**: Robot specifications and capabilities
- **Validation Rules**: Min/max constraints on all numeric fields
- **Categories**: auto, teleop, endgame, subjective
- **Types Supported**: number, boolean, text, select, multiselect, textarea

#### 4. Scanner View Rewritten (`scanner/views.py`)
- **Dynamic Ingestion**: Loops through config metrics instead of hardcoded fields
- **Validation**: Checks data types and ranges before saving
- **Error Handling**: Returns specific validation errors to scouts
- **Data Bucket**: All game metrics stored in `data` JSONField

#### 5. Strategy Views Rewritten (`strategy/views.py`)
- **Dynamic Calculator**: `fetch_team_match_averages()` loops through config
- **Aggregation Support**: avg, sum, percent calculations
- **Composite Metrics**: Auto-calculates totals (auto_total, teleop_total, total)
- **No Hardcoded Math**: All calculations driven by config

#### 6. Database Migration (`teams/migrations/0007_dynamic_config_system.py`)
- Removes all hardcoded columns
- Adds JSONField buckets
- Updates constraints
- Ready to run (requires Django environment)

---

## 🎯 How It Works

### Data Flow
1. **Scout scans QR code** → POST to `/scanner/`
2. **Scanner view loads config** → Validates incoming data
3. **Loops through metrics** → Extracts values, type-converts, validates
4. **Saves to database** → Anchor fields + `data` bucket
5. **Strategy views query** → Dynamically calculate averages from `data` JSONField

### Hot-Reload Mechanism
```python
# Every request checks:
current_modified = os.path.getmtime('game_config.json')
if self._last_modified != current_modified:
    self._config = self._load_config()  # Reload
```

### Validation Example
```json
{
  "key": "auto_L1",
  "type": "number",
  "min": 0,
  "max": 12
}
```
→ Scanner rejects values outside 0-12 range

---

## 🚀 Next Steps (Phase 3 & 4)

### Phase 3: Frontend Updates Needed
1. **Update `rankings.html`**:
   - Loop through `config.metrics` to generate table headers
   - Display values from dynamic result dict

2. **Update `pit_scouting.html`**:
   - Loop through `config.pit_questions`
   - Generate form fields based on type (text, select, multiselect, etc.)

3. **Update `teams/views.py`**:
   - Rewrite `pit_scouting()` view to save to `pit_data` JSONField
   - Pass config to template

4. **Update `team_page.html`**:
   - Display match data from `data` JSONField
   - Remove auto_path visualization

### Phase 4: Testing
1. Run migration: `python manage.py migrate teams`
2. Start server
3. Edit `game_config.json` → Add test metric
4. Refresh page → Verify new column appears
5. Submit test data → Verify validation works

---

## 📋 Config Structure Reference

### Metric Definition
```json
{
  "key": "metric_name",           // Database key
  "type": "number|boolean",       // Data type
  "category": "auto|teleop|...",  // UI grouping
  "aggregation": "avg|sum|percent", // Calculation method
  "display_name": "Human Name",   // UI label
  "min": 0,                       // Validation (optional)
  "max": 100                      // Validation (optional)
}
```

### Pit Question Definition
```json
{
  "key": "question_key",
  "type": "text|number|select|multiselect|textarea",
  "display_name": "Question Label",
  "options": ["Option1", "Option2"],  // For select/multiselect
  "required": true,                   // Optional
  "min": 0,                           // For numbers
  "max": 100
}
```

---

## ⚠️ Important Notes

1. **Data Wipe**: Old data will be lost when migration runs (as requested)
2. **Scout Name**: Now part of unique constraint - multiple scouts can submit same match
3. **Auto Path**: Completely removed (can be re-added as special metric if needed)
4. **Performance**: JSONField queries are slower - consider adding GIN index if needed
5. **Frontend**: Still needs updates to display dynamic data

---

## 🔧 To Add a New Metric

1. Edit `game_config.json`:
```json
{
  "key": "coolness_factor",
  "type": "number",
  "category": "subjective",
  "aggregation": "avg",
  "display_name": "Coolness",
  "min": 1,
  "max": 10
}
```

2. **That's it!** No code changes needed.
3. Scanner will accept it, validate it, store it
4. Strategy will calculate averages for it
5. (Frontend needs update to display it)

---

## 🎉 Success Criteria Met

✅ Models stripped of hardcoded logic  
✅ Config file created with validation  
✅ Scanner view dynamically ingests data  
✅ Strategy view dynamically calculates  
✅ Hot-reload implemented (timestamp check)  
✅ Migration created  
✅ Multi-select stored as arrays  
✅ Anchor fields preserved  

**Ready for Phase 3: Frontend Updates**
