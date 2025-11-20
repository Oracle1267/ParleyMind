from flask import Flask, request, jsonify, render_template
import sqlite3
from pathlib import Path
from flask_cors import CORS
from backend.models import db, Bet, Leg, NCAABTeam, TeamDossier
from backend.utils.reddit_scheduler import start_reddit_scheduler
from backend.utils.ncaab_dossier_scheduler import start_ncaab_dossier_scheduler
from backend.utils.odds_fetcher import (
    get_cfb_odds,
    get_nfl_odds,
    get_ncaab_odds,
    get_nhl_odds,
)
from backend.utils.context_fetcher import get_team_injuries
from backend.utils.tradecore_bridge import get_team_signal
from backend.utils.sports_feed.feed_manager import get_feed_for_sport
from backend.utils.context_engine import get_team_context

app = Flask(__name__, static_folder="../static", static_url_path="/static")
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parlaymind.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
DB = Path(__file__).parent / "instance" / "parlaymind.db"




with app.app_context():
    db.create_all()

@app.get("/api/ncaab/dossier/<team>")
def api_dossier(team):
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("""
      SELECT team_name, efficiency_margin, reddit_sentiment, momentum_score, team_url
      FROM team_dossier WHERE team_name = ?;
    """, (team,))
    row = cur.fetchone(); con.close()
    if not row: return jsonify({"ok": False, "error": "not_found"}), 404
    keys = ["team_name","efficiency_margin","reddit_sentiment","momentum_score","team_url"]
    return jsonify({"ok": True, "dossier": dict(zip(keys, row))})
    
@app.route("/")
def home():
    return render_template("index.html")


print(">>> Running main.py from:", __file__)

print(">>> Registered routes before startup:")
with app.app_context():
    for rule in app.url_map.iter_rules():
        print("   ", rule)


#@app.route("/api/context/ai/<team>")
#def ai_context(team):
#   return jsonify(get_team_signal(team))


# --------------------------
# Core Bet Operations
# --------------------------
def _infer_market_type(desc):
    d = desc.lower()
    if "spread" in d or "+" in d or "-" in d:
        return "Spread"
    if "moneyline" in d or "ml" in d:
        return "Moneyline"
    if "over" in d or "under" in d or "total" in d:
        return "Total"
    return "Other"


@app.route("/api/bet", methods=["POST"])
def add_bet():
    data = request.json
    legs_data = data.get("legs", [])
    bet = Bet(
        bettor=data.get("bettor", "Me"),
        stake=data["stake"],
        parlay_odds=data["parlay_odds"],
        sport=data.get("sport", "CFB"),
        result=data.get("result", "pending"),
        payout=data.get("payout", 0),
        profit_boost=data.get("profit_boost", 0.0),
        num_legs=len(legs_data),
    )
    db.session.add(bet)
    for leg_data in legs_data:
        db.session.add(
            Leg(
                bet=bet,
                description=leg_data["desc"],
                odds=leg_data.get("odds", 0),
                market_type=_infer_market_type(leg_data["desc"]),
            )
        )
    db.session.commit()
    bet.update_profit()
    return jsonify({"status": "ok", "bet_id": bet.id})


@app.route("/api/bets", methods=["GET"])
def list_bets():
    bets = Bet.query.all()
    return jsonify(
        [
            {
                "id": b.id,
                "bettor": b.bettor,
                "sport": b.sport,
                "stake": b.stake,
                "parlay_odds": b.parlay_odds,
                "result": b.result,
                "payout": b.payout or 0.0,
            }
            for b in bets
        ]
    )


@app.route("/api/bet/<int:bet_id>", methods=["DELETE"])
def delete_bet(bet_id):
    bet = Bet.query.get(bet_id)
    if not bet:
        return jsonify({"error": "Bet not found"}), 404
    db.session.delete(bet)
    db.session.commit()
    return jsonify({"status": "deleted", "bet_id": bet_id})


# --------------------------
# Context + Analytics
# --------------------------
@app.route("/api/context/<sport>/<team>")
def api_team_context(sport, team):
    ctx = get_team_injuries(team_name=team, sport=sport)
    return jsonify(ctx)


@app.route("/api/context_batch", methods=["POST"])
def api_context_batch():
    data = request.get_json(force=True) or {}
    items = data.get("items", [])
    out = {}
    for it in items:
        sport = (it.get("sport") or "cfb").lower()
        team = it.get("team")
        if not team:
            continue
        key = f"{sport}|{team}"
        out[key] = get_team_injuries(team_name=team, sport=sport)
    return jsonify(out)


# --------------------------
# Odds Endpoints
# --------------------------
@app.route("/api/odds_ui/<sport>")
def odds_ui(sport):
    try:
        sport = sport.lower()
        if sport == "cfb":
            data = get_cfb_odds()
        elif sport == "nfl":
            data = get_nfl_odds()
        elif sport == "ncaab":
            data = get_ncaab_odds()
        elif sport == "nhl":
            data = get_nhl_odds()
        elif sport == "wncaab":
            data = get_wncaab_odds()
        elif sport == "volleyball":
            data = get_volleyball_odds()
        else:
            return jsonify({"error": f"Unsupported sport '{sport}'"}), 400


        def normalize_game(g):
            return {
                "id": g.get("id"),
                "home_team": g.get("home_team") or g.get("home"),
                "away_team": g.get("away_team") or g.get("away"),
                "commence_time": g.get("commence_time"),
                "bookmakers": g.get("bookmakers", []),
            }

        games = []
        for raw in data:
            g = normalize_game(raw)
            chosen = None
            for bm in g["bookmakers"]:
                if bm.get("key") == "fanduel":
                    chosen = bm
                    break
            if not chosen and g["bookmakers"]:
                chosen = g["bookmakers"][0]

            markets = []
            if chosen:
                for m in chosen.get("markets", []):
                    outcomes = [
                        {
                            "name": o.get("name"),
                            "price": o.get("price"),
                            "point": o.get("point"),
                        }
                        for o in m.get("outcomes", [])
                    ]
                    markets.append(
                        {
                            "bookmaker": chosen.get("title", "Unknown"),
                            "market": m.get("key"),
                            "outcomes": outcomes,
                        }
                    )

            games.append(
                {
                    "id": g["id"],
                    "home_team": g["home_team"],
                    "away_team": g["away_team"],
                    "commence_time": g["commence_time"],
                    "markets": markets,
                }
            )

        return jsonify(games)
    except Exception as e:
        import traceback

        print("⚠️ Error in odds_ui:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route("/api/stats/dashboard", methods=["GET"])
def stats_dashboard():
    bets = Bet.query.all()
    if not bets:
        return jsonify({"message": "no bets yet"})

    def safe_ratio(a, b): return round((a / b) * 100, 2) if b else 0

    total_bets = len(bets)
    total_wins = sum(1 for b in bets if b.result == "win")
    total_losses = sum(1 for b in bets if b.result == "loss")
    total_profit = sum(b.profit for b in bets)
    total_stake = sum(b.stake for b in bets)
    roi = safe_ratio(total_profit, total_stake)
    win_rate = safe_ratio(total_wins, total_wins + total_losses)

    # Bettor split
    bettors = {}
    for b in bets:
        if b.bettor not in bettors:
            bettors[b.bettor] = {"wins": 0, "losses": 0, "profit": 0, "count": 0}
        if b.result == "win": bettors[b.bettor]["wins"] += 1
        elif b.result == "loss": bettors[b.bettor]["losses"] += 1
        bettors[b.bettor]["profit"] += b.profit
        bettors[b.bettor]["count"] += 1

    bettor_stats = {
        k: {
            "win_rate": safe_ratio(v["wins"], v["wins"] + v["losses"]),
            "roi": safe_ratio(v["profit"], 10 * v["count"]),  # assume $10 stake
            "total_bets": v["count"]
        } for k, v in bettors.items()
    }

    # Sport stats
    sports = {}
    for b in bets:
        if b.sport not in sports:
            sports[b.sport] = {"profit": 0, "count": 0}
        sports[b.sport]["profit"] += b.profit
        sports[b.sport]["count"] += 1

    sport_roi = {
        s: safe_ratio(v["profit"], 10 * v["count"])
        for s, v in sports.items()
    }

    return jsonify({
        "total_bets": total_bets,
        "win_rate": win_rate,
        "roi": roi,
        "bettor_stats": bettor_stats,
        "sport_roi": sport_roi
    })
        
@app.route("/api/context/ai/<team>")
def ai_context(team):
    try:
        sport = request.args.get("sport", "cfb").lower()
        if sport not in ["cfb", "nfl", "ncaab", "nhl"]:
            sport = "cfb"
        context = get_team_context(team, sport)
        return jsonify(context)
    except Exception as e:
        print("⚠️ Error in ai_context:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/dossier/<team_name>", methods=["GET"])
def get_team_dossier(team_name):
    try:
        team = NCAABTeam.query.filter_by(name=team_name).first()
        if not team:
            return jsonify({"error": f"Team '{team_name}' not found"}), 404
        
        dossier = TeamDossier.query.filter_by(team_id=team.id).order_by(TeamDossier.snapshot_date.desc()).first()
        if not dossier:
            return jsonify({"error": f"No dossier found for {team_name}"}), 404
        
        from datetime import date
        injuries = [{"player": i.player_name, "status": i.status, "details": i.details} for i in dossier.injuries]
        recent_games = [{"opponent": g.opponent, "result": g.result, "score": g.score, "date": str(g.game_date)} for g in dossier.performance]
        upcoming_games = [{"opponent": g.opponent, "location": g.location, "date": str(g.game_date)} for g in dossier.schedule]
        
        return jsonify({
            "team": team.name,
            "snapshot_date": str(dossier.snapshot_date),
            "record": f"{dossier.wins}-{dossier.losses}",
            "reddit_mentions": dossier.reddit_mentions,
            "reddit_sentiment": dossier.reddit_sentiment,
            "active_injuries": dossier.active_injuries,
            "ppg": round(dossier.ppg, 1),
            "ppg_allowed": round(dossier.ppg_allowed, 1),
            "home_ppg": round(dossier.home_ppg, 1),
            "away_ppg": round(dossier.away_ppg, 1),
            "last_5_record": dossier.last_5_record,
            "injuries": injuries,
            "recent_games": recent_games,
            "upcoming_games": upcoming_games
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/dossiers", methods=["GET"])
def list_dossiers():
    try:
        from datetime import date
        teams = NCAABTeam.query.all()
        result = []
        
        for team in teams:
            dossier = TeamDossier.query.filter_by(team_id=team.id).order_by(TeamDossier.snapshot_date.desc()).first()
            if dossier:
                result.append({
                    "team": team.name,
                    "record": f"{dossier.wins}-{dossier.losses}",
                    "reddit_mentions": dossier.reddit_mentions,
                    "reddit_sentiment": dossier.reddit_sentiment,
                    "active_injuries": dossier.active_injuries,
                    "ppg": round(dossier.ppg, 1),
                    "ppg_allowed": round(dossier.ppg_allowed, 1),
                    "last_5_record": dossier.last_5_record,
                    "snapshot_date": str(dossier.snapshot_date)
                })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🧠 start background Reddit collector
try:
    start_reddit_scheduler()
except Exception as e:
    print(f"[INIT] Could not start Reddit scheduler: {e}")

try:
    start_ncaab_dossier_scheduler(app)
except Exception as e:
    print(f"[INIT] Could not start NCAAB dossier scheduler: {e}")


if __name__ == "__main__":
    app.run(debug=True, port=5200)
