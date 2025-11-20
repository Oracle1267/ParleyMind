# 🧠 **ParleyMind — Project State**

**Date:** 2025-10-29  
**Version:** Alpha-0.5  
**Maintainer:** Nick Glanzer  

---

## 📦 Current Structure

**Directories**
```
parleymind/
│
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── templates/
│   │   └── index.html       ← main Parley Builder UI
│   └── utils/
│       ├── odds_fetcher.py  ← pulls live odds from The Odds API
│       └── tradecore_bridge.py (planned)
│
├── frontend/
│   └── index.html           ← legacy bet entry + tracker UI
│
└── parlaymind.db            ← SQLite database
```

---

## ✅ Current Functionality

| Feature | Description | Status |
|----------|--------------|--------|
| **Live Odds Feed (CFB)** | Pulls and renders real-time NCAA football odds (FanDuel) | ✅ Stable |
| **Parley Builder** | Multi-leg builder with combined-odds calculator and payout estimator | ✅ Stable |
| **Risk Meter** | Shows hit chance, EV, and visual probability bar | ✅ Working |
| **AI Coaching** | Provides structured text advice on leg balance, odds mix, and risk tier | ✅ Basic version |
| **Novice Mode** | Guided overlay tutorial (currently static) | ⚙️ Needs content |
| **TradeCore Bridge** | Placeholder for AI_TRADE_CORE signal injection | 🚧 Planned |
| **Bet Tracker / ROI system** | Legacy version (frontend/index.html) | 🕊️ Deprecated for now |

---

## 🧩 Planned Next Steps

### Phase 3 — Parley Builder Completion
1. **Multi-Sport Integration**
   - Add NFL, NBA, NCAAB, esports feeds to `odds_fetcher.py`.
   - Update `/api/odds_ui/<sport>` to handle all leagues.

2. **Data Enrichment**
   - Add `league`, `risk_flag`, and `bettor` columns to `Bet` model.
   - Allow tagging parlays as *Nick* or *Joe* for later comparative analysis.

3. **Contextual Coaching**
   - Expand coaching logic with deeper statistical context (momentum, variance, correlation).
   - Integrate with AI_TRADE_CORE once team injury & form signals are live.

4. **Persistence**
   - Implement `/api/save_parlay` and `/api/load_parlay` endpoints.
   - Enable export/import of parlays as JSON.

---

## ⚙️ Integration Targets

| System | Purpose | Connection Status |
|---------|----------|-------------------|
| **AI_TRADE_CORE** | Supplies normalized risk/strength indicators per team | Planned API Bridge |
| **The Odds API** | Primary odds data feed (FanDuel, DraftKings) | Active |
| **SQLite (parlaymind.db)** | Local storage for bets & parlays | Active |

---

## 🦯 Next Session Starting Point

- Begin by implementing **multi-sport odds fetching** (Step 1 of Phase 3).  
- Test `/api/odds_ui/nfl` and `/api/odds_ui/nba` for live data.  
- Once verified, extend frontend to switch between leagues via dropdown.

