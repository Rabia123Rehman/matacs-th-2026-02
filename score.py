"""Deterministic scoring. Input: extracted facts + criteria config. No AI, no randomness.
Usage: python score.py [facts.json] [criteria.json]  -> prints ranking.json content."""
import json, sys

def load(p): return json.load(open(p))

def score_one(f, c, best_price, best_weeks):
    w, p = c["weights"], c["params"]
    s = {}
    s["experience"] = w["experience"] * min(f["installs_100kw_5y"] / p["experience_full_marks_at"], 1)
    ok_price = f["price_cad"] is not None and f["price_cad"] <= c["budget_ceiling"]
    s["price"] = w["price"] * best_price / f["price_cad"] if ok_price else 0
    ok_time = f["weeks"] is not None and f["weeks"] <= c["max_weeks"]
    s["timeline"] = w["timeline"] * best_weeks / f["weeks"] if ok_time else 0
    s["warranty"] = w["warranty"] / 2 * (min(f["panel_years"] / p["panel_warranty_full_years"], 1)
                                         + min(f["workmanship_years"] / p["workmanship_full_years"], 1))
    items = p["team_items"]
    s["team"] = w["team"] * sum(bool(f[i]) for i in items) / len(items)
    return {k: round(v, 2) for k, v in s.items()}, round(sum(s.values()), 1)

def main(facts_path="facts.json", crit_path="criteria.json"):
    facts, c = load(facts_path), load(crit_path)
    elig = {k: v for k, v in facts.items() if all(v[m] for m in c["mandatory"])}
    inelig = {k: v for k, v in facts.items() if k not in elig}
    # baselines come only from eligible bids so a disqualified bid cannot distort the others
    best_price = min(v["price_cad"] for v in elig.values() if v["price_cad"] <= c["budget_ceiling"])
    best_weeks = min(v["weeks"] for v in elig.values() if v["weeks"] and v["weeks"] <= c["max_weeks"])
    scored = {}
    for k, v in elig.items():
        parts, total = score_one(v, c, best_price, best_weeks)
        scored[k] = (parts, total)
    ranked = sorted([k for k in scored
                     if not any(x.startswith("prompt_injection") for x in elig[k]["flags"])
                     and elig[k]["weeks"] is not None],
                    key=lambda k: (-scored[k][1], elig[k]["price_cad"], k))
    out = []
    for i, k in enumerate(ranked, 1):
        out.append({"proposal": k, "rank": i, "status": "ranked", "score": scored[k][1], "parts": scored[k][0]})
    for k in sorted(elig):
        if k not in ranked:
            out.append({"proposal": k, "rank": None, "status": "flagged", "score": None,
                        "provisional_score": scored[k][1], "parts": scored[k][0]})
    for k in sorted(inelig):
        out.append({"proposal": k, "rank": None, "status": "ineligible", "score": None})
    return out

if __name__ == "__main__":
    print(json.dumps(main(*sys.argv[1:]), indent=2))
