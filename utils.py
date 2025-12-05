from datetime import date, timedelta
from models import Medicine, db

def check_expired_and_near_expiry(days_threshold=30):
    expired = []
    near = []
    today = date.today()
    threshold_date = today + timedelta(days=days_threshold)
    meds = Medicine.query.all()
    for m in meds:
        if m.expiry_date:
            if m.expiry_date < today:
                expired.append(m)
            elif m.expiry_date <= threshold_date:
                days_left = (m.expiry_date - today).days
                near.append((m, days_left))
    return {'expired': expired, 'near_expiry': near}

def check_low_stock():
    return Medicine.query.filter(Medicine.quantity <= Medicine.threshold).all()
