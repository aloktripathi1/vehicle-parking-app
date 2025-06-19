from datetime import datetime
from pytz import timezone

def utc_to_ist(utc_dt):
    if utc_dt is None:  # this will convert utc datetime into ist datetime
        return None
    if utc_dt.tzinfo is None: 
        utc_dt = timezone('UTC').localize(utc_dt)
    ist = timezone('Asia/Kolkata')
    return utc_dt.astimezone(ist)

def format_ist_datetime(utc_dt, format='%Y-%m-%d %H:%M'):
    if utc_dt is None: 
        return 'N/A'
    ist_dt = utc_to_ist(utc_dt)
    return ist_dt.strftime(format) 