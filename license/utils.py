import hashlib
from django.utils import timezone
from datetime import timedelta

def generate_api_token(secret, dt=None):
    """
    Generate a SHA256 token based on secret and hourly timestamp.
    Format: SHA256(secret + YYYYMMDDHH)
    """
    if dt is None:
        dt = timezone.now()
    
    # Format: 2023121912 (YearMonthDayHour)
    time_str = dt.strftime('%Y%m%d%H')
    data = f"{secret}{time_str}"
    return hashlib.sha256(data.encode()).hexdigest()

def verify_api_token(token, secret):
    """
    Verify if the provided token matches the current or previous hour's token.
    (Previous hour check handles clock drift/overlaps)
    """
    if not token or not secret:
        return False
        
    now = timezone.now()
    
    # Check current hour
    current_token = generate_api_token(secret, now)
    if token == current_token:
        return True
        
    # Check previous hour
    previous_hour = now - timedelta(hours=1)
    previous_token = generate_api_token(secret, previous_hour)
    if token == previous_token:
        return True
        
    return False
