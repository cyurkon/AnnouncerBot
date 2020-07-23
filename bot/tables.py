from bot.shared import db


class Player(db.Model):
    pid = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.session.add(self)
        db.session.commit()


class Practice(db.Model):
    timestamp = db.Column(db.String, primary_key=True)
    date = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    is_tracked = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.session.add(self)
        db.session.commit()


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String, db.ForeignKey("player.pid"))
    date = db.Column(db.String, db.ForeignKey("practice.date"))
    time = db.Column(db.String, db.ForeignKey("practice.time"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.session.add(self)
        db.session.commit()
