"""
Sequentially executes ParleyMind data collection agents.
Usage:
    python -m backend.run_agents
"""

import importlib

AGENTS = [
    "backend.agents.reddit_collector_sports_v2",
    "backend.agents.odds_fetcher",
]

def main():
    print("=== Running ParleyMind Agent Stack ===")
    for mod_name in AGENTS:
        try:
            print(f"[RUN] {mod_name}")
            mod = importlib.import_module(mod_name)
            if hasattr(mod, "run"):
                mod.run()
            else:
                print(f"[WARN] {mod_name} has no 'run()' entry.")
        except Exception as e:
            print(f"[ERR] {mod_name}: {e}")
    print("=== All agents completed ===")

if __name__ == "__main__":
    main()
