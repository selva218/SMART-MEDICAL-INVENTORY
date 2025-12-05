from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    batch = db.Column(db.String(80), nullable=True)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    unit = db.Column(db.String(20), default="pcs")
    expiry_date = db.Column(db.Date, nullable=True)
    threshold = db.Column(db.Integer, default=5)
    notes = db.Column(db.String(300), nullable=True)

    def is_expired(self):
        return self.expiry_date and self.expiry_date < date.today()

    def days_to_expiry(self):
        if not self.expiry_date:
            return None
        delta = self.expiry_date - date.today()
        return delta.days
