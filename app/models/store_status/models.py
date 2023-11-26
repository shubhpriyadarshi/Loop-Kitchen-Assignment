from app import db

class StoreStatus(db.Model):
    """
    Represents the status of a store at a given timestamp.
    """
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer)
    timestamp_utc = db.Column(db.DateTime)
    status = db.Column(db.String(10), nullable=False)
