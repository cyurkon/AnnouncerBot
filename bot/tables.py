from bot.shared import db


class Player(db.Model):
    pid = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)
    attendance = db.relationship("Attendance", backref="player")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def is_admin(pid):
        if player := Player.query.filter_by(pid=pid).first():
            return player.admin
        return False


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
    status = db.Column(db.String)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.session.add(self)
        db.session.commit()
