from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bettor = db.Column(db.String(50), default="Joe")
    stake = db.Column(db.Float, nullable=False)
    parlay_odds = db.Column(db.Float, nullable=False)
    sport = db.Column(db.String(30), nullable=False)
    result = db.Column(db.String(10), default="pending")  # win/loss/pending
    payout = db.Column(db.Float, default=0.0)
    profit = db.Column(db.Float, default=0.0)
    num_legs = db.Column(db.Integer, default=0)
    avg_leg_odds = db.Column(db.Float, default=0.0)  # <--- NEW FIELD
    profit_boost = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    legs = db.relationship("Leg", backref="bet", cascade="all, delete-orphan")

    def update_profit(self):
        """Recalculate profit from payout and stake."""
        self.profit = round((self.payout or 0) - (self.stake or 0), 2)
        db.session.commit()

    def calc_avg_odds(self):
        """Compute the average odds per leg."""
        if not self.legs:
            return 0.0
        total = sum(abs(l.odds or 0) for l in self.legs)
        self.avg_leg_odds = round(total / len(self.legs), 2)
        db.session.commit()


class Leg(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bet_id = db.Column(db.Integer, db.ForeignKey("bet.id"), nullable=False)
    description = db.Column(db.String(200))
    odds = db.Column(db.Float)
    market_type = db.Column(db.String(50))


class NCAABTeam(db.Model):
    __tablename__ = "ncaab_team"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    espn_id = db.Column(db.String(50))
    conference = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    dossiers = db.relationship("TeamDossier", backref="team", cascade="all, delete-orphan")


class TeamDossier(db.Model):
    __tablename__ = "team_dossier"
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("ncaab_team.id"), nullable=False)
    snapshot_date = db.Column(db.Date, nullable=False)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    reddit_mentions = db.Column(db.Integer, default=0)
    reddit_sentiment = db.Column(db.String(20))
    key_players = db.Column(db.Text)
    active_injuries = db.Column(db.Integer, default=0)
    ppg = db.Column(db.Float, default=0.0)
    ppg_allowed = db.Column(db.Float, default=0.0)
    last_5_record = db.Column(db.String(20))
    streak = db.Column(db.String(20))
    home_ppg = db.Column(db.Float, default=0.0)
    away_ppg = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    injuries = db.relationship("Injury", backref="dossier", cascade="all, delete-orphan")
    performance = db.relationship("GamePerformance", backref="dossier", cascade="all, delete-orphan")
    schedule = db.relationship("GameSchedule", backref="dossier", cascade="all, delete-orphan")


class Injury(db.Model):
    __tablename__ = "injury"
    id = db.Column(db.Integer, primary_key=True)
    dossier_id = db.Column(db.Integer, db.ForeignKey("team_dossier.id"), nullable=False)
    player_name = db.Column(db.String(100))
    status = db.Column(db.String(50))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class GamePerformance(db.Model):
    __tablename__ = "game_performance"
    id = db.Column(db.Integer, primary_key=True)
    dossier_id = db.Column(db.Integer, db.ForeignKey("team_dossier.id"), nullable=False)
    opponent = db.Column(db.String(100))
    result = db.Column(db.String(10))
    score = db.Column(db.String(20))
    game_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class GameSchedule(db.Model):
    __tablename__ = "game_schedule"
    id = db.Column(db.Integer, primary_key=True)
    dossier_id = db.Column(db.Integer, db.ForeignKey("team_dossier.id"), nullable=False)
    opponent = db.Column(db.String(100))
    game_date = db.Column(db.Date)
    location = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
