from app import db

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staffname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    clicked = db.Column(db.Integer, default=0)
    submitted = db.Column(db.Integer, default=0)
    confidence = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Staff {}>'.format(self.staffname)