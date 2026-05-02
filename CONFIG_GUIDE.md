# Game Configuration Guide

Complete guide to creating and maintaining `game_config.json` for FRC scouting seasons.

## Table of Contents
1. [Overview](#overview)
2. [Configuration Structure](#configuration-structure)
3. [Root Level Fields](#root-level-fields)
4. [Metrics Configuration](#metrics-configuration)
5. [Pit Questions Configuration](#pit-questions-configuration)
6. [Legacy Key Aliasing](#legacy-key-aliasing)
7. [Best Practices](#best-practices)
8. [Real-World Example: 2025 Reefscape](#real-world-example-2025-reefscape)
9. [Common Pitfalls](#common-pitfalls)
10. [Migration Guide](#migration-guide)

---

## Overview

The `game_config.json` file is the heart of the dynamic scouting system. It defines:
- What data to collect during matches
- How to display and aggregate that data
- Pit scouting questions
- Team branding

**Key Benefits:**
-  ✓ No code changes needed for new seasons
-  ✓ Hot-reload: Changes apply instantly without restart
-  ✓ Data retention: Rename metrics without losing historical data
-  ✓ Validation: Automatic type and range checking

---

## Configuration Structure

```json
{
  "version": "2025_reefscape",
  "home_team": 2073,
  "year": 2025,
  "app_name": "EagleScout",
  "team_name": "EagleForce",
  "metrics": [...],
  "pit_questions": [...]
}
```

---

## Root Level Fields

### `version` (string, required)
Unique identifier for this configuration. Use format: `YEAR_GAMENAME`

```json
"version": "2025_reefscape"
```

**Best Practice:** Update this when making major changes to track configuration history.

### `home_team` (integer, required)
Your FRC team number. Used for TBA API calls.

```json
"home_team": 2073
```

### `year` (integer, required)
Competition year. Used for TBA API event fetching.

```json
"year": 2025
```

### `app_name` (string, optional)
Application name displayed in navbar and page titles.

```json
"app_name": "EagleScout"
```

**Default:** "Scouting System"

### `team_name` (string, optional)
Your team name for branding.

```json
"team_name": "EagleForce"
```

**Default:** "Team"

---

## Metrics Configuration

Metrics define what data scouts collect during matches. Each metric becomes a column in rankings and a field in the scanner.

### Metric Structure

```json
{
  "key": "auto_leave",
  "type": "number",
  "category": "auto",
  "aggregation": "avg",
  "display_name": "Auto Leave",
  "min": 0,
  "max": 1,
  "legacy_keys": []
}
```

### Field Definitions

#### `key` (string, required)
Unique identifier for this metric. Used in database and code.

**Rules:**
- Use snake_case (lowercase with underscores)
- Be descriptive but concise
- Never change without using `legacy_keys`

**Examples:**
```json
"key": "auto_leave"        //  ✓ Good
"key": "teleL1"            //  ✓ Good
"key": "autoLeave"         //  ✗ Bad (camelCase)
"key": "al"                //  ✗ Bad (too short)
```

#### `type` (string, required)
Data type for validation.

**Options:**
- `"number"` - Integer or decimal values
- `"boolean"` - True/false values

```json
"type": "number"
```

#### `category` (string, required)
Groups metrics for organization.

**Common Categories:**
- `"auto"` - Autonomous period
- `"teleop"` - Teleoperated period
- `"endgame"` - End game actions
- `"subjective"` - Scout opinions (driver skill, defense)

```json
"category": "auto"
```

#### `aggregation` (string, required)
How to calculate team averages.

**Options:**
- `"avg"` - Average across all matches
- `"sum"` - Total across all matches
- `"percent"` - Percentage (0-100)

```json
"aggregation": "avg"
```

**When to use each:**
- `avg`: Most scoring metrics (points, game pieces)
- `sum`: Cumulative stats (total penalties)
- `percent`: Success rates (climb success rate)

#### `display_name` (string, required)
Human-readable name shown in UI.

```json
"display_name": "Auto Leave"
```

**Best Practice:** Use title case and be descriptive.

#### `min` / `max` (number, optional)
Validation bounds for number types.

```json
"min": 0,
"max": 12
```

**Best Practice:** Set realistic bounds based on game rules. For 2025 Reefscape, max coral is 12 (6 per robot × 2 robots).

#### `legacy_keys` (array, optional)
Previous names for this metric. Enables renaming without data loss.

```json
"legacy_keys": ["climb", "old_climb"]
```

**See [Legacy Key Aliasing](#legacy-key-aliasing) for details.**

---

## Pit Questions Configuration

Pit questions define the pit scouting form. Each question becomes a form field.

### Question Structure

```json
{
  "key": "drivetrain",
  "type": "select",
  "display_name": "Drivetrain Type",
  "options": ["Swerve", "Tank", "Mecanum", "Other"],
  "required": true
}
```

### Field Definitions

#### `key` (string, required)
Unique identifier. Same rules as metric keys.

#### `type` (string, required)
Form input type.

**Options:**
- `"text"` - Single-line text input
- `"number"` - Numeric input with validation
- `"select"` - Dropdown (single choice)
- `"multiselect"` - Checkboxes (multiple choices)
- `"textarea"` - Multi-line text input
- `"boolean"` - Checkbox (yes/no)

#### `display_name` (string, required)
Label shown above the input field.

#### `options` (array, required for select/multiselect)
Available choices for select and multiselect types.

```json
"options": ["Swerve", "Tank", "Mecanum", "Other"]
```

#### `required` (boolean, optional)
Whether the field must be filled.

```json
"required": true
```

**Default:** false

#### `min` / `max` (number, optional for number type)
Validation bounds for numeric inputs.

```json
"min": 0,
"max": 125
```

### Question Type Examples

**Text Input:**
```json
{
  "key": "intake_design",
  "type": "text",
  "display_name": "Intake Design"
}
```

**Number Input:**
```json
{
  "key": "weight",
  "type": "number",
  "display_name": "Weight (lbs)",
  "min": 0,
  "max": 125
}
```

**Dropdown (Single Choice):**
```json
{
  "key": "drivetrain",
  "type": "select",
  "display_name": "Drivetrain Type",
  "options": ["Swerve", "Tank", "Mecanum", "Other"],
  "required": true
}
```

**Checkboxes (Multiple Choice):**
```json
{
  "key": "scoring_locations",
  "type": "multiselect",
  "display_name": "Scoring Locations",
  "options": ["L1", "L2", "L3", "L4", "Net", "Processor"]
}
```

**Text Area:**
```json
{
  "key": "additional_info",
  "type": "textarea",
  "display_name": "Additional Notes"
}
```

**Boolean (Checkbox):**
```json
{
  "key": "has_vision",
  "type": "boolean",
  "display_name": "Has Vision System"
}
```

---

## Legacy Key Aliasing

Legacy keys allow you to rename metrics mid-season without losing historical data.

### Problem Scenario

Week 1: You name a metric `"climb"`
```json
{
  "key": "climb",
  "display_name": "Climb"
}
```

Week 3: You realize it should be more specific
```json
{
  "key": "endgame_climb",
  "display_name": "Endgame Climb"
}
```

**Without legacy keys:** All Week 1-2 data is lost! ✗ DATA LOST

**With legacy keys:** All data is preserved! ✓ DATA PRESERVED

### Solution: Add Legacy Keys

```json
{
  "key": "endgame_climb",
  "legacy_keys": ["climb"],
  "type": "number",
  "category": "endgame",
  "aggregation": "avg",
  "display_name": "Endgame Climb",
  "min": 0,
  "max": 12
}
```

### How It Works

When calculating averages, the system:
1. Looks for data under `"endgame_climb"` (current key)
2. If not found, checks `"climb"` (legacy key)
3. Uses whichever is found

**Result:** Old data (stored as "climb") and new data (stored as "endgame_climb") both appear in rankings.

### Multiple Legacy Keys

You can have multiple legacy keys if you renamed something multiple times:

```json
{
  "key": "endgame_climb_points",
  "legacy_keys": ["endgame_climb", "climb", "hang"],
  "display_name": "Endgame Climb Points"
}
```

**Order matters:** System checks from left to right, uses first match.

### When to Use Legacy Keys

 ✓ **Use when:**
- Renaming a metric mid-season
- Consolidating similar metrics
- Fixing typos in metric names

 ✗ **Don't use when:**
- Starting a new season (clean slate)
- Metric meaning changed significantly
- Creating a brand new metric

---

## Best Practices

### 1. Plan Your Metrics Before the Season

**Do:**
- Watch game reveal carefully
- Identify all scoring actions
- Consider autonomous vs teleop
- Think about endgame

**Example Planning (2025 Reefscape):**
```
Autonomous:
- Leave starting zone (0-1)
- Score coral in reef (L1-L4)
- Score algae in net
- Score algae in processor
- Remove coral from reef

Teleop:
- Same scoring as auto
- More pieces possible

Endgame:
- Climb (0-12 points)
```

### 2. Use Consistent Naming Conventions

**Prefixes:**
- `auto_` - Autonomous actions
- `tele` - Teleop actions (no underscore for historical reasons)
- `endgame_` - Endgame actions

**Examples:**
```json
"auto_leave"      //  ✓ Consistent
"auto_L1"         //  ✓ Consistent
"teleL1"          //  ✓ Consistent (historical)
"climb"           //  ✓ Endgame implied
```

### 3. Set Realistic Min/Max Values

**Based on game rules:**
```json
{
  "key": "auto_L1",
  "min": 0,
  "max": 12,  // 6 coral per robot × 2 robots in auto
  "display_name": "Auto L1"
}
```

**Prevents data entry errors:**
- Scout accidentally enters 120 instead of 12
- System rejects it before saving

### 4. Group Related Metrics

**Keep categories organized:**
```json
// All auto metrics together
{"key": "auto_leave", "category": "auto"},
{"key": "auto_L1", "category": "auto"},
{"key": "auto_L2", "category": "auto"},

// All teleop metrics together
{"key": "teleL1", "category": "teleop"},
{"key": "teleL2", "category": "teleop"},

// All endgame metrics together
{"key": "climb", "category": "endgame"}
```

### 5. Include Subjective Metrics

**Driver skill and defense are valuable:**
```json
{
  "key": "driver_ranking",
  "type": "number",
  "category": "subjective",
  "aggregation": "avg",
  "display_name": "Driver Skill",
  "min": 1,
  "max": 5
},
{
  "key": "defense_ranking",
  "type": "number",
  "category": "subjective",
  "aggregation": "avg",
  "display_name": "Defense",
  "min": 1,
  "max": 5
}
```

**Use 1-5 scale:**
- 1 = Poor
- 3 = Average
- 5 = Excellent

### 6. Keep Pit Questions Practical

**Ask questions that help with alliance selection:**

 ✓ **Good Questions:**
- Drivetrain type (affects speed/defense)
- Scoring locations (what can they do?)
- Auto capabilities (reliable auto?)
- Climb capability (endgame points?)

 ✗ **Bad Questions:**
- Favorite color (irrelevant)
- Team motto (not strategic)
- Number of mentors (doesn't affect performance)

### 7. Use Multiselect for Capabilities

**Instead of multiple yes/no questions:**
```json
//  ✗ Bad: Multiple boolean questions
{"key": "can_score_L1", "type": "boolean"},
{"key": "can_score_L2", "type": "boolean"},
{"key": "can_score_L3", "type": "boolean"},
{"key": "can_score_L4", "type": "boolean"}

//  ✓ Good: One multiselect
{
  "key": "scoring_locations",
  "type": "multiselect",
  "options": ["L1", "L2", "L3", "L4", "Net", "Processor"]
}
```

### 8. Test Your Config Before Competition

**Validation checklist:**
1. Add a test metric
2. Refresh rankings page
3. Verify it appears immediately (hot-reload)
4. Remove test metric
5. Verify it disappears

**If hot-reload doesn't work:**
- Check JSON syntax (use JSONLint.com)
- Check file permissions
- Restart server as last resort

---

## Real-World Example: 2025 Reefscape

Let's break down the 2025 Reefscape configuration and explain the reasoning.

### Game Overview

**Scoring Objects:**
- Coral (orange) - Placed in reef levels (L1-L4)
- Algae (green) - Scored in net or processor

**Reef Levels:**
- L1: Lowest, easiest
- L2-L3: Middle levels
- L4: Highest, hardest

**Scoring Locations:**
- Reef (L1-L4)
- Net (algae only)
- Processor (algae only)

**Endgame:**
- Climb on cage (shallow or deep)
- Points based on position

### Metric Decisions

#### Auto Leave
```json
{
  "key": "auto_leave",
  "type": "number",
  "category": "auto",
  "aggregation": "avg",
  "display_name": "Auto Leave",
  "min": 0,
  "max": 1
}
```

**Why:**
- Binary: Either left (1) or didn't (0)
- Average tells us reliability (0.8 = 80% success rate)
- Min/max prevents invalid entries

#### Scoring Metrics (L1-L4)
```json
{
  "key": "auto_L1",
  "type": "number",
  "category": "auto",
  "aggregation": "avg",
  "display_name": "Auto L1",
  "min": 0,
  "max": 12
}
```

**Why:**
- Separate metric for each level (different difficulty)
- Max 12: Game rules limit (6 coral × 2 robots)
- Average shows typical performance

#### Net and Processor
```json
{
  "key": "auto_net",
  "type": "number",
  "category": "auto",
  "aggregation": "avg",
  "display_name": "Auto Net",
  "min": 0,
  "max": 12
}
```

**Why:**
- Algae-specific scoring locations
- Separate from reef scoring
- Helps identify algae specialists

#### Removed Coral
```json
{
  "key": "auto_removed",
  "type": "number",
  "category": "auto",
  "aggregation": "avg",
  "display_name": "Auto Removed",
  "min": 0,
  "max": 12
}
```

**Why:**
- Defensive action (removing opponent coral)
- Valuable for strategy
- Separate from scoring

#### Teleop Metrics
```json
{
  "key": "teleL1",
  "type": "number",
  "category": "teleop",
  "aggregation": "avg",
  "display_name": "Teleop L1",
  "min": 0,
  "max": 50
}
```

**Why:**
- Higher max (50) than auto (12)
- More time = more pieces
- Same structure as auto for consistency

#### Climb
```json
{
  "key": "climb",
  "type": "number",
  "category": "endgame",
  "aggregation": "avg",
  "display_name": "Climb",
  "min": 0,
  "max": 12
}
```

**Why:**
- Points vary by position (shallow vs deep)
- Average shows typical endgame points
- Critical for close matches

#### Subjective Ratings
```json
{
  "key": "driver_ranking",
  "type": "number",
  "category": "subjective",
  "aggregation": "avg",
  "display_name": "Driver Skill",
  "min": 1,
  "max": 5
}
```

**Why:**
- 1-5 scale is intuitive
- Average gives overall impression
- Helps with tiebreakers in alliance selection

### Pit Question Decisions

#### Drivetrain
```json
{
  "key": "drivetrain",
  "type": "select",
  "display_name": "Drivetrain Type",
  "options": ["Swerve", "Tank", "Mecanum", "Other"],
  "required": true
}
```

**Why:**
- Single choice (can't have multiple drivetrains)
- Required (fundamental robot characteristic)
- Affects speed, defense, maneuverability

#### Dimensions
```json
{
  "key": "weight",
  "type": "number",
  "display_name": "Weight (lbs)",
  "min": 0,
  "max": 125
},
{
  "key": "length",
  "type": "number",
  "display_name": "Length (inches)",
  "min": 0,
  "max": 48
}
```

**Why:**
- Weight max 125: FRC rule
- Length/width max 48: Starting configuration rule
- Helps predict pushing power and maneuverability

#### Capabilities (Multiselect)
```json
{
  "key": "scoring_locations",
  "type": "multiselect",
  "display_name": "Scoring Locations",
  "options": ["L1", "L2", "L3", "L4", "Net", "Processor"]
}
```

**Why:**
- Robots can score in multiple locations
- Quick visual of capabilities
- Helps with role assignment (high scorer vs ground game)

#### Cage Positions
```json
{
  "key": "cage_positions",
  "type": "multiselect",
  "display_name": "Cage Positions",
  "options": ["Shallow", "Deep"]
}
```

**Why:**
- Multiselect: Some robots can do both
- Critical for endgame planning
- Deep = more points but harder

#### Boolean Questions
```json
{
  "key": "under_shallow",
  "type": "select",
  "display_name": "Can Go Under Shallow Reef?",
  "options": ["Yes", "No"]
}
```

**Why:**
- Select instead of boolean for consistency
- Important for navigation strategy
- Affects positioning options

---

## Common Pitfalls

### 1. Changing Keys Without Legacy Keys

**Problem:**
```json
// Week 1
{"key": "climb"}

// Week 3 (renamed without legacy_keys)
{"key": "endgame_climb"}
```

**Result:** All Week 1-2 data disappears from rankings! ✗ DATA LOST

**Solution:**
```json
{
  "key": "endgame_climb",
  "legacy_keys": ["climb"]
}
```

### 2. Invalid JSON Syntax

**Problem:**
```json
{
  "key": "auto_leave",
  "type": "number",  //  ✗ Trailing comma
}
```

**Result:** Config fails to load, app breaks!

**Solution:** Use a JSON validator (JSONLint.com) before saving.

### 3. Unrealistic Min/Max Values

**Problem:**
```json
{
  "key": "auto_L1",
  "min": 0,
  "max": 999  //  ✗ Way too high
}
```

**Result:** Doesn't catch data entry errors (scout enters 120 instead of 12).

**Solution:** Set realistic bounds based on game rules.

### 4. Too Many Metrics

**Problem:**
- 50+ metrics
- Scouts overwhelmed
- Data quality suffers

**Solution:**
- Focus on strategic metrics
- Combine similar actions
- Aim for 15-25 metrics

### 5. Vague Display Names

**Problem:**
```json
{"display_name": "L1"}  //  ✗ L1 what? Auto? Teleop?
```

**Solution:**
```json
{"display_name": "Auto L1"}  //  ✓ Clear
```

### 6. Wrong Aggregation Type

**Problem:**
```json
{
  "key": "climb",
  "aggregation": "sum"  //  ✗ Inflates scores
}
```

**Result:** Team with 10 matches shows 120 climb points (12 × 10) instead of 12 average.

**Solution:** Use `"avg"` for most metrics.

### 7. Missing Required Fields

**Problem:**
```json
{
  "key": "auto_leave",
  "type": "number"
  //  ✗ Missing category, aggregation, display_name
}
```

**Result:** Errors in rankings or scanner.

**Solution:** Always include all required fields.

---

## Migration Guide

### Starting a New Season

**Step 1: Copy Previous Config**
```bash
cp game_config.json game_config_2024.json  # Backup
```

**Step 2: Update Root Fields**
```json
{
  "version": "2026_newgame",  // Update
  "year": 2026,               // Update
  "home_team": 2073,          // Keep
  "app_name": "EagleScout",   // Keep
  "team_name": "EagleForce"   // Keep
}
```

**Step 3: Clear Old Metrics**
```json
"metrics": []  // Start fresh
```

**Step 4: Add New Game Metrics**
Watch game reveal, identify scoring actions, add metrics.

**Step 5: Update Pit Questions**
Keep universal questions (drivetrain, weight), update game-specific ones.

### Mid-Season Changes

**Adding a Metric:**
```json
// Just add to the array
{
  "key": "new_metric",
  "type": "number",
  "category": "teleop",
  "aggregation": "avg",
  "display_name": "New Metric",
  "min": 0,
  "max": 10
}
```

**Renaming a Metric:**
```json
{
  "key": "new_name",
  "legacy_keys": ["old_name"],  // Add this!
  "type": "number",
  "category": "teleop",
  "aggregation": "avg",
  "display_name": "New Name",
  "min": 0,
  "max": 10
}
```

**Removing a Metric:**
```json
// Just delete it from the array
// Historical data is preserved in database
```

---

## Quick Reference

### Metric Template
```json
{
  "key": "metric_name",
  "type": "number",
  "category": "auto|teleop|endgame|subjective",
  "aggregation": "avg|sum|percent",
  "display_name": "Display Name",
  "min": 0,
  "max": 100,
  "legacy_keys": []
}
```

### Pit Question Templates

**Text:**
```json
{"key": "name", "type": "text", "display_name": "Label"}
```

**Number:**
```json
{"key": "name", "type": "number", "display_name": "Label", "min": 0, "max": 100}
```

**Dropdown:**
```json
{"key": "name", "type": "select", "display_name": "Label", "options": ["A", "B"]}
```

**Checkboxes:**
```json
{"key": "name", "type": "multiselect", "display_name": "Label", "options": ["A", "B"]}
```

**Text Area:**
```json
{"key": "name", "type": "textarea", "display_name": "Label"}
```

**Boolean:**
```json
{"key": "name", "type": "boolean", "display_name": "Label"}
```

---

## Testing Your Configuration

### Pre-Competition Checklist

- [ ] JSON syntax is valid (use JSONLint.com)
- [ ] All metrics have required fields
- [ ] Min/max values are realistic
- [ ] Display names are clear
- [ ] Categories are consistent
- [ ] Aggregation types are correct
- [ ] Pit questions cover key capabilities
- [ ] Hot-reload works (add test metric, refresh, remove)

### During Competition

- [ ] Monitor for data entry errors
- [ ] Check if scouts are confused by any metrics
- [ ] Verify rankings calculations look correct
- [ ] Be ready to add metrics if needed
- [ ] Use legacy keys if renaming

---

## Rankings Configuration

The `rankings` array controls which columns appear in the rankings table, their display names, and whether they're sortable.

### Rankings Column Structure

```json
{
  "key": "autoScore",
  "display_name": "Auto Score",
  "sortable": true
}
```

### Field Definitions

#### `key` (string, required)
Must match either:
- A metric `key` from the `metrics` array (e.g., `"autoScore"`)
- An anchor field: `"team_number"`, `"autoLeave"`, `"driverRanking"`, `"defenseRanking"`
- A computed field: `"totalPass"`, `"totalShooting"` (see below)

#### `display_name` (string, required)
Column header text shown in the rankings table.

#### `sortable` (boolean, optional)
Whether users can sort the table by this column. Default: false.

#### `computed` (boolean, optional)
Mark as `true` for derived columns that are calculated from other metrics, not stored directly.

### Computed Fields

These are calculated automatically in the rankings view:

| Key | Formula | Description |
|-----|---------|-------------|
| `totalPass` | `autoPass + telePass` | Combined passing |
| `totalShooting` | `autoScore + teleScore` | Combined scoring |
| `totalTotal` | `totalShooting + totalPass` | Everything combined |

### Anchor Fields

These are stored as dedicated database columns (not in the dynamic `data` JSONField):

| Key | Description | Notes |
|-----|-------------|-------|
| `team_number` | FRC team number | Always first column |
| `autoLeave` | Left starting zone in auto | 0 or 1 |
| `driverRanking` | Subjective driver skill | 0-5 scale |
| `defenseRanking` | Subjective defense rating | 0-5 scale |
| `start_pos` | Starting position | 0-5 |

Anchor fields are averaged only across non-zero values (so unrated matches don't drag down the average).

### Example Rankings Configuration

```json
"rankings": [
  {"key": "team_number",      "display_name": "Team #",            "sortable": true},
  {"key": "autoLeave",        "display_name": "Auto Leave",        "sortable": true},
  {"key": "autoScore",        "display_name": "Auto Score",        "sortable": true},
  {"key": "autoPass",         "display_name": "Auto Pass",         "sortable": true},
  {"key": "teleScore",        "display_name": "Teleop Score",      "sortable": true},
  {"key": "telePass",         "display_name": "Teleop Pass",       "sortable": true},
  {"key": "driverRanking",    "display_name": "Driver Ranking",    "sortable": true},
  {"key": "defenseRanking",   "display_name": "Defense",           "sortable": true},
  {"key": "totalPass",        "display_name": "Total Pass",        "sortable": true, "computed": true},
  {"key": "totalShooting",    "display_name": "Total Score",       "sortable": true, "computed": true}
]
```

### How Rankings Columns Connect to Config

The sort dropdown and table columns are **driven by the `rankings` array**. When you add a new metric to `metrics` and want it visible in rankings:

1. Add the metric to `metrics` (for data collection and aggregation)
2. Add a matching entry to `rankings` (for display in the table)
3. Set `"sortable": true` if users should be able to sort by it

If you add a metric to `metrics` but NOT to `rankings`, it will still be collected and stored, but won't appear in the rankings table. It will still appear on team pages and in the dashboard.

---

## Match Exclusion System

Scouts and strategists can **hide individual matches** from rankings averages. This is useful for excluding inaccurate data, broken robot matches, or outliers.

### How It Works

1. **Team Page**: Each match row has a "Hide" button. Clicking it dims the row (opacity 0.5, strikethrough) and saves the exclusion to the user's session.
2. **Rankings Page**: The match detail modal also has ✕/✓ buttons to exclude/include matches. After toggling, the page reloads with recalculated averages.
3. **Session-Based**: Exclusions are stored in the user's browser session, NOT in the database. This means:
   - Each user has their own set of exclusions
   - Exclusions don't affect other users
   - Exclusions are lost when the user logs out or the session expires
   - This is intentional — different strategists may want different exclusion sets

### What Gets Excluded

- Only matches with `match_number < 100` are counted in rankings averages (this is a hardcoded filter to exclude practice/test matches)
- Hidden matches are excluded from the average calculation but remain visible (dimmed) in the UI
- The `match_count` in rankings reflects the number of matches actually counted

### Important Notes

- Hiding a match on the team page takes effect on the rankings page on the next page load
- The "X matches hidden from rankings" badge on the team page shows the total across ALL teams, not just the current team
- To clear all exclusions, log out and log back in

---

## How Config Changes Affect the Running System

### What Happens Instantly (Hot-Reload)

The `ConfigLoader` checks the file modification time on every request. These changes apply immediately without server restart:

| Change | Effect |
|--------|--------|
| Add a metric to `metrics` | New column appears in team pages, dashboard, scanner starts collecting it |
| Remove a metric from `metrics` | Column disappears from views, existing data preserved in DB |
| Change `display_name` | Labels update everywhere |
| Change `min`/`max` | Validation bounds update for new scans |
| Add/remove `rankings` columns | Rankings table columns update |
| Change `pit_questions` | Pit scouting form updates |
| Change `app_name`/`team_name` | Branding updates |

### What Does NOT Change

| Change | What Stays the Same |
|--------|-------------------|
| Rename a metric `key` (without `legacy_keys`) | Old data becomes invisible — it's still in the DB under the old key but nothing reads it |
| Change `aggregation` type | Only affects new calculations, not stored data |
| Remove a metric | Data stays in the `Team_Match_Data.data` JSONField forever |
| Change pit question `options` | Existing pit data keeps old values — filters won't match if option names changed |

### The Pit Data Trap

**This is the most common source of bugs.** If you change pit question option values mid-season:

```json
// Before: options were ["Hood", "Turret", "Static"]
// After:  options are  ["Drum", "Turret", "Single Static", "None"]
```

Teams scouted before the change still have `"Hood"` and `"Static"` in their `pit_data`. The rankings pit filters only show the NEW options, so those teams become invisible to filters.

**Fix:** Run a data migration to update old values:
```python
# In Django shell (python3 manage.py shell)
from teams.models import Teams

MIGRATION = {'Hood': 'Single Static', 'Static': 'Single Static'}

for team in Teams.objects.filter(pit_scout_status=True):
    pd = team.pit_data or {}
    shooter = pd.get('Shooter')
    if isinstance(shooter, list):
        new = [MIGRATION.get(v, v) for v in shooter]
        if new != shooter:
            pd['Shooter'] = new
            team.pit_data = pd
            team.save()
            print(f'Updated team {team.team_number}: {shooter} -> {new}')
```

### Computed Fields Are Hardcoded

The computed fields (`totalPass`, `totalShooting`, `totalTotal`) are calculated in `strategy/views.py`, not from the config. If you change the metric keys they depend on (e.g., rename `autoScore` to `auto_score`), the computed fields will break because they reference the old key names.

**Current formulas in `strategy/views.py`:**
```python
stats['totalPass']     = autoPass + telePass
stats['totalShooting'] = autoScore + teleScore
stats['totalTotal']    = totalShooting + totalPass
```

If you rename these metrics, update the formulas in `rankings()` in `strategy/views.py`.

---

## Season Transition Checklist

When starting a new FRC season:

### Before Kickoff
- [ ] Back up current `game_config.json` as `game_config_YEAR.json`
- [ ] Back up the database (match data, pit data, picklists)
- [ ] Update `version`, `year` in config

### After Game Reveal
- [ ] Watch the game reveal and read the manual
- [ ] Identify all scoring actions (auto, teleop, endgame)
- [ ] Draft `metrics` array — aim for 8-15 metrics
- [ ] Draft `pit_questions` — keep universal ones (drivetrain, weight, dimensions), add game-specific ones
- [ ] Draft `rankings` array — decide which columns to show and which are sortable
- [ ] Validate JSON syntax
- [ ] Test with a practice scan

### Before First Competition
- [ ] Verify scanner QR format matches metric keys
- [ ] Test pit scouting form on mobile
- [ ] Test rankings page loads correctly
- [ ] Test dashboard with a real TBA event
- [ ] Verify all sort options work
- [ ] Train scouts on what each metric means

### During Competition
- [ ] Monitor for data quality issues
- [ ] Use match exclusion to hide bad data
- [ ] If renaming a metric, ALWAYS use `legacy_keys`
- [ ] If changing pit question options, run a data migration for existing data
- [ ] Check rankings filters still work after any config change

### Mid-Season Config Changes
- [ ] Never change a metric `key` without `legacy_keys`
- [ ] Never change pit question `options` without migrating existing data
- [ ] Test the change on the rankings page immediately after saving
- [ ] Verify pit filters still return expected results

---

## Support

For questions or issues:
- Check this guide first
- Review the 2025 Reefscape example above or the JSON example file as a reference
- Test changes in a development environment
- Ask team leadership for clarification

**Remember:** The config file is powerful but requires careful planning. Take time to debate, design, and improve it well before your first competition starts!
