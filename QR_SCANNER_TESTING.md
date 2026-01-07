# QR Scanner Testing Guide

Complete guide to testing the QR code scanner functionality before and during competition.

## Table of Contents
1. [Pre-Competition Testing](#pre-competition-testing)
2. [Test Data Generation](#test-data-generation)
3. [Scanner Validation](#scanner-validation)
4. [Common Issues](#common-issues)
5. [Competition Day Checklist](#competition-day-checklist)

---

## Pre-Competition Testing

### Step 1: Verify Configuration

**Check game_config.json:**
```bash
# Validate JSON syntax
python3 -c "import json; json.load(open('game_config.json'))"
```

**Expected output:** No errors

**If errors:** Use JSONLint.com to find syntax issues

### Step 2: Create Test QR Code

**Manual Test Data (JSON format):**
```json
{
  "team_number": 2073,
  "match_number": 1,
  "scout_name": "TestScout",
  "quantifier": "Quals",
  "start_pos": 2,
  "auto_leave": 1,
  "auto_L1": 2,
  "auto_L2": 1,
  "auto_L3": 0,
  "auto_L4": 0,
  "auto_net": 1,
  "auto_processor": 0,
  "auto_removed": 0,
  "teleL1": 5,
  "teleL2": 3,
  "teleL3": 2,
  "teleL4": 1,
  "telenet": 2,
  "teleProcessor": 1,
  "teleRemoved": 0,
  "climb": 6,
  "driver_ranking": 4,
  "defense_ranking": 3,
  "comment": "Test match",
  "is_broken": false,
  "is_disabled": false,
  "is_tipped": false
}
```

**Generate QR Code:**
1. Go to https://www.qr-code-generator.com/
2. Select "Text" type
3. Paste the JSON above
4. Download QR code image
5. Print or display on phone

### Step 3: Test Scanner Flow

**Access Scanner:**
```
http://localhost:8000/scanner/
```

**Test Steps:**
1. Click "Start Scanner" button
2. Allow camera permissions
3. Point camera at test QR code
4. Verify data appears in preview
5. Click "Submit Data"
6. Check for success message

**Expected Result:**
- QR code scans successfully
- Data preview shows all fields
- Submit succeeds with green success message
- No errors in browser console (F12)

### Step 4: Verify Database Storage

**Check data was saved:**
```bash
python3 manage.py shell
```

```python
from teams.models import Team_Match_Data

# Get the test match
match = Team_Match_Data.objects.filter(
    team_number=2073,
    match_number=1,
    scout_name="TestScout"
).first()

# Verify data
print(f"Team: {match.team_number}")
print(f"Match: {match.match_number}")
print(f"Scout: {match.scout_name}")
print(f"Data: {match.data}")

# Check specific values
print(f"Auto L1: {match.data.get('auto_L1')}")
print(f"Climb: {match.data.get('climb')}")
```

**Expected Output:**
```
Team: 2073
Match: 1
Scout: TestScout
Data: {'auto_leave': 1, 'auto_L1': 2, ...}
Auto L1: 2
Climb: 6
```

### Step 5: Verify Rankings Display

**Check rankings page:**
```
http://localhost:8000/strategy/rankings/?comp=testing
```

**Verify:**
- Team 2073 appears in table
- All metric columns show data
- Values match what you scanned
- Averages calculate correctly

---

## Test Data Generation

### Python Script to Generate Test QR Codes

Create `generate_test_qr.py`:

```python
#!/usr/bin/env python3
import json
import qrcode
from pathlib import Path

def generate_test_match(team_number, match_number, scout_name):
    """Generate realistic test match data"""
    data = {
        "team_number": team_number,
        "match_number": match_number,
        "scout_name": scout_name,
        "quantifier": "Quals",
        "start_pos": 2,
        "auto_leave": 1,
        "auto_L1": 2,
        "auto_L2": 1,
        "auto_L3": 0,
        "auto_L4": 0,
        "auto_net": 1,
        "auto_processor": 0,
        "auto_removed": 0,
        "teleL1": 5,
        "teleL2": 3,
        "teleL3": 2,
        "teleL4": 1,
        "telenet": 2,
        "teleProcessor": 1,
        "teleRemoved": 0,
        "climb": 6,
        "driver_ranking": 4,
        "defense_ranking": 3,
        "comment": f"Test match {match_number}",
        "is_broken": False,
        "is_disabled": False,
        "is_tipped": False
    }
    
    # Convert to JSON string
    json_str = json.dumps(data)
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(json_str)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save
    filename = f"test_qr_team{team_number}_match{match_number}.png"
    img.save(filename)
    print(f"Generated: {filename}")

# Generate test QR codes
generate_test_match(2073, 1, "TestScout1")
generate_test_match(2073, 2, "TestScout2")
generate_test_match(254, 1, "TestScout1")
```

**Install dependencies:**
```bash
pip install qrcode[pil]
```

**Run:**
```bash
python3 generate_test_qr.py
```

### Online QR Generator (No Code)

**Quick Test:**
1. Copy test JSON from Step 2
2. Go to https://www.qr-code-generator.com/
3. Paste JSON
4. Download QR code
5. Test immediately

---

## Scanner Validation

### Validation Checklist

**Data Validation:**
- [ ] Min/max values enforced (try entering 999 for auto_L1)
- [ ] Required fields checked
- [ ] Invalid JSON rejected
- [ ] Type validation works (string in number field)

**Scanner Functionality:**
- [ ] Camera permissions requested
- [ ] QR code detected quickly (< 2 seconds)
- [ ] Multiple scans work without refresh
- [ ] Data preview shows all fields
- [ ] Submit button works
- [ ] Success/error messages display

**Database Integration:**
- [ ] Data saves to correct table
- [ ] JSONField stores dynamic data
- [ ] Anchor fields saved correctly
- [ ] Duplicate detection works (same team/match/scout)

**Rankings Integration:**
- [ ] Scanned data appears in rankings
- [ ] Averages calculate correctly
- [ ] Legacy keys work (if applicable)
- [ ] Hot-reload shows new data

### Test Edge Cases

**1. Invalid QR Code:**
```json
{"invalid": "data"}
```
**Expected:** Error message, data not saved

**2. Missing Required Fields:**
```json
{
  "team_number": 2073
  // Missing match_number, scout_name, etc.
}
```
**Expected:** Validation error

**3. Out of Range Values:**
```json
{
  "team_number": 2073,
  "match_number": 1,
  "auto_L1": 999  // Max is 12
}
```
**Expected:** Validation error

**4. Duplicate Scan:**
Scan same QR code twice
**Expected:** Either update existing or show duplicate warning

**5. Special Characters in Comment:**
```json
{
  "comment": "Robot broke! @#$%^&*()"
}
```
**Expected:** Saves correctly, displays properly

---

## Common Issues

### Issue 1: Camera Not Working

**Symptoms:**
- Black screen
- "Camera not found" error
- Permission denied

**Solutions:**
1. Check browser permissions (Settings > Privacy > Camera)
2. Use HTTPS (required for camera access)
3. Try different browser (Chrome recommended)
4. Check if another app is using camera
5. Restart browser

**Test:**
```
https://localhost:8000/scanner/
```
Note: HTTPS required for camera API

### Issue 2: QR Code Not Scanning

**Symptoms:**
- Scanner sees QR but doesn't read
- Takes very long to scan
- Never detects QR code

**Solutions:**
1. Increase QR code size (print larger)
2. Improve lighting
3. Hold camera steady
4. Clean camera lens
5. Reduce QR code complexity (less data)

**Test:**
Generate simple QR with minimal data

### Issue 3: Data Not Saving

**Symptoms:**
- Success message but no data in database
- Error in browser console
- 500 server error

**Solutions:**
1. Check server logs: `python3 manage.py runserver`
2. Verify database connection
3. Check migrations: `python3 manage.py migrate`
4. Verify JSON format matches config

**Debug:**
```bash
# Check server logs
tail -f /var/log/scouting.log

# Test database connection
python3 manage.py shell
>>> from teams.models import Team_Match_Data
>>> Team_Match_Data.objects.count()
```

### Issue 4: Validation Errors

**Symptoms:**
- "Invalid data" error
- Specific field errors
- Type mismatch errors

**Solutions:**
1. Check game_config.json min/max values
2. Verify data types match config
3. Ensure all required fields present
4. Check for typos in field names

**Debug:**
```python
from utils import config_loader
config = config_loader.get_config()

# Check metric definitions
for metric in config['metrics']:
    print(f"{metric['key']}: {metric['type']} ({metric.get('min')}-{metric.get('max')})")
```

### Issue 5: Rankings Not Updating

**Symptoms:**
- Data in database but not in rankings
- Old data showing
- Averages incorrect

**Solutions:**
1. Hard refresh browser (Ctrl+Shift+R)
2. Check competition code matches
3. Verify quantifier (Quals/Playoff/Practice)
4. Check for JavaScript errors (F12 console)

**Debug:**
```python
from teams.models import Team_Match_Data

# Check what data exists
matches = Team_Match_Data.objects.filter(
    team_number=2073,
    event="testing"
)
print(f"Found {matches.count()} matches")
for m in matches:
    print(f"Match {m.match_number}: {m.data}")
```

---

## Competition Day Checklist

### Before Competition

**Setup:**
- [ ] Server running and accessible
- [ ] Database backed up
- [ ] game_config.json finalized
- [ ] Test QR codes generated
- [ ] Scanner tested on competition network
- [ ] Multiple devices tested (tablets, phones)
- [ ] Backup devices charged

**Network:**
- [ ] WiFi credentials distributed
- [ ] Server IP address documented
- [ ] Firewall allows connections
- [ ] HTTPS certificate valid (if using)

**Training:**
- [ ] Scouts trained on scanner
- [ ] Backup paper forms available
- [ ] Data entry person assigned
- [ ] Troubleshooting guide printed

### During Competition

**Per Match:**
- [ ] Scouts scan QR codes
- [ ] Verify data appears in rankings
- [ ] Check for missing matches
- [ ] Monitor for errors

**Periodic Checks:**
- [ ] Database backup every hour
- [ ] Check server logs for errors
- [ ] Verify all scouts submitting data
- [ ] Compare match count to schedule

**Troubleshooting:**
- [ ] Have backup paper forms ready
- [ ] Designate tech support person
- [ ] Keep test QR codes handy
- [ ] Monitor server performance

### After Competition

**Data Validation:**
- [ ] Export all data
- [ ] Check for missing matches
- [ ] Verify data quality
- [ ] Backup database

**Review:**
- [ ] Note any issues encountered
- [ ] Update documentation
- [ ] Improve config for next event

---

## Quick Test Script

Save as `test_scanner.sh`:

```bash
#!/bin/bash

echo "QR Scanner Test Suite"
echo "===================="

# Test 1: Config validation
echo "Test 1: Validating game_config.json..."
python3 -c "import json; json.load(open('game_config.json'))" && echo "✓ Config valid" || echo "✗ Config invalid"

# Test 2: Database connection
echo "Test 2: Testing database connection..."
python3 manage.py shell -c "from teams.models import Team_Match_Data; print('✓ Database connected')" || echo "✗ Database error"

# Test 3: Server running
echo "Test 3: Checking if server is running..."
curl -s http://localhost:8000/scanner/ > /dev/null && echo "✓ Server running" || echo "✗ Server not running"

# Test 4: Check migrations
echo "Test 4: Checking migrations..."
python3 manage.py showmigrations | grep "\[ \]" && echo "✗ Unapplied migrations" || echo "✓ All migrations applied"

echo "===================="
echo "Test complete!"
```

**Run:**
```bash
chmod +x test_scanner.sh
./test_scanner.sh
```

---

## Support

**If scanner issues persist:**
1. Check browser console (F12) for JavaScript errors
2. Check server logs for Python errors
3. Verify game_config.json matches scouting app format
4. Test with minimal QR code (fewer fields)
5. Try different device/browser
6. Contact team leadership

**Emergency Fallback:**
- Use paper scouting forms
- Manual data entry via admin panel
- Post-competition data import

---

## Summary

**Minimum Testing Required:**
1. Generate test QR code with all metrics
2. Scan QR code successfully
3. Verify data in database
4. Check rankings display
5. Test one edge case (invalid data)

**Time Required:** 15-30 minutes

**When to Test:**
- After any config changes
- Before each competition
- After server updates
- When adding new scouts/devices

**Remember:** Better to find issues during testing than during competition!
