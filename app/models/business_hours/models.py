from app import db
class BusinessHours(db.Model):
    """
    Represents the business hours of a store for a given day of the week.
    """
    store_id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, primary_key=True)
    start_time_local = db.Column(db.Time, primary_key=True)
    end_time_local = db.Column(db.Time, nullable=False)
