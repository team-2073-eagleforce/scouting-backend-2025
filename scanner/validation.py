"""
Shared validation utilities for scanner data
"""

def validate_scan_data(scan_data):
    """
    Validate scan data with comprehensive checks
    Returns tuple (is_valid, errors_list)
    """
    errors = []
    
    # Required fields validation
    required_fields = {
        'teamNumber': 'Team number',
        'matchNumber': 'Match number', 
        'name': 'Scout name',
        'comp_code': 'Competition code'
    }
    
    for field, display_name in required_fields.items():
        if field not in scan_data or not str(scan_data[field]).strip():
            errors.append(f"{display_name} is required")
    
    # Team number validation
    try:
        team_num = int(scan_data.get('teamNumber', 0))
        if team_num <= 0 or team_num > 99999:
            errors.append("Team number must be between 1 and 99999")
    except (ValueError, TypeError):
        errors.append("Team number must be a valid integer")
    
    # Match number validation
    try:
        match_num = int(scan_data.get('matchNumber', 0))
        if match_num <= 0 or match_num > 999:
            errors.append("Match number must be between 1 and 999")
    except (ValueError, TypeError):
        errors.append("Match number must be a valid integer")
    
    # Scout name validation
    name = str(scan_data.get('name', '')).strip()
    if len(name) < 2:
        errors.append("Scout name must be at least 2 characters")
    elif len(name) > 32:
        errors.append("Scout name cannot exceed 32 characters")
    
    # Competition code validation
    comp_code = str(scan_data.get('comp_code', '')).strip()
    if len(comp_code) < 3:
        errors.append("Competition code must be at least 3 characters")
    elif len(comp_code) > 16:
        errors.append("Competition code cannot exceed 16 characters")
    
    # Validate numeric fields with reasonable bounds
    numeric_fields = {
        'startPos': (0, 4),
        'driverRanking': (1, 5),
        'defenseRanking': (1, 5),
        'endClimb': (0, 4)
    }
    
    for field, (min_val, max_val) in numeric_fields.items():
        if field in scan_data:
            try:
                val = int(scan_data[field])
                if val < min_val or val > max_val:
                    errors.append(f"{field} must be between {min_val} and {max_val}")
            except (ValueError, TypeError):
                errors.append(f"{field} must be a valid integer")
    
    # Validate boolean-like fields
    boolean_fields = ['isBroken', 'isDisabled', 'isTipped']
    for field in boolean_fields:
        if field in scan_data:
            try:
                val = int(scan_data[field])
                if val not in [0, 1]:
                    errors.append(f"{field} must be 0 or 1")
            except (ValueError, TypeError):
                errors.append(f"{field} must be 0 or 1")
    
    return len(errors) == 0, errors

def sanitize_scan_data(scan_data):
    """
    Sanitize and normalize scan data
    """
    sanitized = {}
    
    # Copy and sanitize string fields
    string_fields = ['name', 'comp_code', 'comment']
    for field in string_fields:
        if field in scan_data:
            sanitized[field] = str(scan_data[field]).strip()
    
    # Handle quantifier with default
    sanitized['quantifier'] = str(scan_data.get('quantifier', 'Prac')).strip() or 'Prac'
    
    # Copy and validate numeric fields
    numeric_fields = [
        'teamNumber', 'matchNumber', 'startPos', 'missed_auto',
        'autoLeave', 'autoNet', 'autoProcessor', 'autoRemoved',
        'autoL1', 'autoL2', 'autoL3', 'autoL4',
        'telenet', 'teleProcessor', 'teleRemoved', 
        'teleL1', 'teleL2', 'teleL3', 'teleL4',
        'endClimb', 'driverRanking', 'defenseRanking',
        'isBroken', 'isDisabled', 'isTipped'
    ]
    
    for field in numeric_fields:
        if field in scan_data:
            try:
                sanitized[field] = int(scan_data[field])
            except (ValueError, TypeError):
                sanitized[field] = 0
    
    # Handle special fields
    if 'autoPath' in scan_data:
        sanitized['autoPath'] = scan_data['autoPath'] if isinstance(scan_data['autoPath'], list) else []
    
    return sanitized