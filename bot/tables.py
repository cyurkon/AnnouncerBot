from bot.shared import db, POINTS


class Attendance(db.Model):
    pid = db.Column(db.String, db.ForeignKey("player.pid"), primary_key=True)
    date = db.Column(db.String, db.ForeignKey("practice.date"), primary_key=True)
    time = db.Column(db.String, db.ForeignKey("practice.time"), primary_key=True)
    status = db.Column(db.String)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.session.add(self)
        db.session.commit()


class Player(db.Model):
    pid = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)
    num_activities = db.Column(db.Integer, nullable=False, default=0)
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

    def get_practice_points(self):
        practice_points = 0
        records = self.attendance
        for record in records:
            practice_points += POINTS[record.status]
        return practice_points

    def get_power_level(self):
        return self.get_practice_points() + 0.5 * self.num_activities


class Practice(db.Model):
    timestamp = db.Column(db.String, primary_key=True)
    date = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    is_tracked = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.session.add(self)
        db.session.commit()
