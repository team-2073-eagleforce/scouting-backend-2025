# Legacy Key Aliasing - Phase 4 Feature

## Problem Solved

When you rename a metric in `game_config.json`, old match data stored under the previous key name would be lost. Legacy key aliasing allows you to access old data using new metric names.

## How It Works

The `fetch_team_match_averages()` function now checks for a `legacy_keys` array in each metric definition. If the current key isn't found in the match data, it falls back to checking legacy keys.

### Example: Renaming a Metric

**Scenario**: You want to rename `climb` to `endgame_climb` for clarity.

**Old Data** (stored in database):
```json
{
  "climb": 3,
  "auto_L1": 2
}
```

**New Config** (`game_config.json`):
```json
{
  "key": "endgame_climb",
  "legacy_keys": ["climb"],
  "type": "number",
  "aggregation": "avg",
  "display_name": "Endgame Climb",
  "min": 0,
  "max": 12
}
```

**Result**: Rankings will show `endgame_climb` column, but the calculation pulls data from old `climb` key in existing matches.

---

## Usage

### Single Legacy Key
```json
{
  "key": "new_name",
  "legacy_keys": ["old_name"],
  ...
}
```

### Multiple Legacy Keys (tries in order)
```json
{
  "key": "current_name",
  "legacy_keys": ["previous_name", "original_name"],
  ...
}
```

### No Legacy Keys (new metric)
```json
{
  "key": "brand_new_metric",
  ...
}
```
(Omit `legacy_keys` field entirely)

---

## Implementation Details

**File**: `strategy/views.py` → `fetch_team_match_averages()`

**Logic**:
1. Loop through each metric in config
2. Try to get value from `match.data[current_key]`
3. If `None`, loop through `legacy_keys` and try each
4. Use first non-None value found
5. Calculate average/sum/percent as normal

**Code Snippet**:
```python
for metric in config['metrics']:
    key = metric['key']
    legacy_keys = metric.get('legacy_keys', [])
    
    for match in team_match_data:
        value = match.data.get(key)
        
        # Fallback to legacy keys
        if value is None and legacy_keys:
            for legacy_key in legacy_keys:
                value = match.data.get(legacy_key)
                if value is not None:
                    break
```

---

## Real-World Example

### Week 1: Initial Config
```json
{
  "key": "auto_coral",
  "display_name": "Auto Coral"
}
```

### Week 3: Realized we need to split by level
```json
{
  "key": "auto_coral_L1",
  "legacy_keys": ["auto_coral"],
  "display_name": "Auto Coral L1"
},
{
  "key": "auto_coral_L2",
  "display_name": "Auto Coral L2"
}
```

**Result**: 
- Old matches with `auto_coral` data will show up in `auto_coral_L1` column
- New matches collect both `auto_coral_L1` and `auto_coral_L2` separately
- No data loss!

---

## Best Practices

1. **Always add legacy_keys when renaming** - Never just change the key
2. **Keep legacy_keys forever** - Old data might exist from early season
3. **Document renames** - Add comment in config explaining the change
4. **Test after rename** - Verify old data still appears in rankings

---

## Testing

1. Create test match data with old key:
```python
Team_Match_Data.objects.create(
    team_number=2073,
    event="testing",
    match_number=1,
    scout_name="test",
    data={"old_metric_name": 5}
)
```

2. Update config with renamed metric:
```json
{
  "key": "new_metric_name",
  "legacy_keys": ["old_metric_name"],
  ...
}
```

3. Check rankings - should show value `5` under `new_metric_name` column

---

## Phase 4 Complete ✅

Legacy key aliasing is now implemented. The system is fully backward-compatible with renamed metrics.
