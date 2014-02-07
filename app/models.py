from . import db


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    fb_id = db.Column(db.String, nullable=False)
    accepted = db.Column(db.Boolean, default=False, nullable=False)
    creation = db.Column(db.DateTime, nullable=False)
    last_activity = db.Column(db.DateTime, nullable=False)
    sended_matches = db.relationship('Match',
                                     backref='sender',
                                     lazy='dynamic',
                                     primaryjoin='Match.sender_id == User.id')
    received_matches = db.relationship('Match',
                                       backref='receiver',
                                       lazy='dynamic',
                                       primaryjoin='Match.receiver_id == User.id')


class Match(db.Model):
    __tablename__ = "match"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    drawing_id = db.Column(db.Integer, db.ForeignKey('drawing.id'), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    last_activity = db.Column(db.DateTime, nullable=False)


class DrawingCategory(db.Model):
    __tablename__ = "drawing_category"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    drawings = db.relationship('Drawing',
                               backref='category',
                               lazy='dynamic')


class Drawing(db.Model):
    __tablename__ = "drawing"
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('drawing_category.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    matches = db.relationship('Match',
                              backref='drawing',
                              lazy='dynamic')
