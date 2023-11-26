from app import db

class Timezones(db.Model):
    """
    Represents a store.
    """
    store_id = db.Column(db.Integer, primary_key=True)
    timezone_str = db.Column(db.String(20))
