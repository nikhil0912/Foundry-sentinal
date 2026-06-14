"""
Agent 1: Data Profiler Agent
=============================
Performs statistical and semantic analysis on the input data and the
ELA's candidate decisions. Computes fairness metrics across protected
attributes (gender, age_band) and highlights disparities.

Reasoning pattern: Statistical Audit — Compute → Compare → Flag
  Step 1: Group employees by protected attribute
  Step 2: Compute selection rates per group for high-impact decisions
  Step 3: Compare against fairness metric thresholds from Foundry IQ
  Step 4: Build structured Bias Profile Report for downstream agents
"""

import json
from pathlib import Path
from agents.agent0_ela import list_all_recommendations

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_kg() -> dict:
    """Load Foundry IQ ethical knowledge graph."""
    with open(DATA_DIR / "foundry_iq_ethics_kg.json") as f:
        return json.load(f)


def _is_high_potential(decision: dict) -> bool:
    """A decision is 'high-potential' if it carries promotion impact."""
    return decision.get("career_impact") == "promotion_track"


def _is_negative_signal(decision: dict) -> bool:
    """A decision is a 'negative signal' if it carries phase-out impact."""
    return decision.get("career_impact") == "negative_signal"


def _is_high_performer(decision: dict) -> bool:
    return decision.get("performance_score", 0) >= 4.0


def compute_group_rates(decisions: list, group_key: str, value_predicate) -> dict:
    """
    Compute the rate at which value_predicate(d) is True, broken down by group_key.
    Returns: { group_value: { count: n, total: m, rate_pct: x } }
    """
    by_group = {}
    for d in decisions:
        g = d[group_key]
        if g not in by_group:
            by_group[g] = {"count": 0, "total": 0}
        by_group[g]["total"] += 1
        if value_predicate(d):
            by_group[g]["count"] += 1
    for g in by_group:
        t = by_group[g]["total"]
        c = by_group[g]["count"]
        by_group[g]["rate_pct"] = round(c / t * 100, 1) if t else 0
    return by_group


def _max_disparity_pct(rates: dict) -> float:
    """Find the largest disparity between any two groups."""
    pcts = [v["rate_pct"] for v in rates.values()]
    if len(pcts) < 2:
        return 0.0
    return round(max(pcts) - min(pcts), 1)


def run(candidate_decisions: dict = None) -> dict:
    """
    Run the Data Profiler.

    Returns: Bias Profile Report (structured, machine-readable).
    """
    if candidate_decisions is None:
        candidate_decisions = list_all_recommendations()

    decisions = candidate_decisions["decisions"]
    kg = _load_kg()

    # ── Step 1: Gender disparity in high-potential allocation ──────
    gender_hp_rates = compute_group_rates(
        decisions, "gender", _is_high_potential
    )
    gender_hp_disparity = _max_disparity_pct(gender_hp_rates)

    # ── Step 2: Age disparity in negative-signal allocation ────────
    age_neg_rates = compute_group_rates(
        decisions, "age_band", _is_negative_signal
    )
    age_neg_disparity = _max_disparity_pct(age_neg_rates)

    # ── Step 3: Equal opportunity check (among high performers) ────
    hp_decisions = [d for d in decisions if _is_high_performer(d)]
    eo_gender_rates = compute_group_rates(
        hp_decisions, "gender", _is_high_potential
    )
    eo_gender_disparity = _max_disparity_pct(eo_gender_rates)

    # ── Step 4: Department × gender intersection ───────────────────
    intersectional = {}
    for d in decisions:
        key = f"{d['department']} | {d['gender']}"
        if key not in intersectional:
            intersectional[key] = {"count": 0, "total": 0}
        intersectional[key]["total"] += 1
        if _is_high_potential(d):
            intersectional[key]["count"] += 1
    for k in intersectional:
        t = intersectional[k]["total"]
        intersectional[k]["rate_pct"] = round(
            intersectional[k]["count"] / t * 100, 1
        ) if t else 0

    # ── Step 5: Low-confidence decision count ──────────────────────
    low_confidence = [
        d for d in decisions
        if d.get("ela_confidence", 1.0) < 0.65
        and d.get("career_impact") in ["promotion_track", "negative_signal"]
    ]

    # ── Step 6: Compile findings ───────────────────────────────────
    findings = []
    if gender_hp_disparity > 20:
        findings.append({
            "id": "F01",
            "type": "demographic_parity_violation",
            "attribute": "gender",
            "decision_class": "high_potential",
            "disparity_pct": gender_hp_disparity,
            "threshold_pct": 20,
            "rates": gender_hp_rates,
            "severity": "critical",
        })
    if age_neg_disparity > 20:
        findings.append({
            "id": "F02",
            "type": "age_disparity_negative_signal",
            "attribute": "age_band",
            "decision_class": "negative_signal",
            "disparity_pct": age_neg_disparity,
            "threshold_pct": 20,
            "rates": age_neg_rates,
            "severity": "critical",
        })
    if eo_gender_disparity > 15:
        findings.append({
            "id": "F03",
            "type": "equal_opportunity_violation",
            "attribute": "gender",
            "decision_class": "high_potential_among_high_performers",
            "disparity_pct": eo_gender_disparity,
            "threshold_pct": 15,
            "rates": eo_gender_rates,
            "severity": "high",
        })
    if low_confidence:
        findings.append({
            "id": "F04",
            "type": "low_confidence_high_impact",
            "attribute": "ela_confidence",
            "decision_class": "high_impact",
            "count": len(low_confidence),
            "affected_employees": [d["employee_id"] for d in low_confidence],
            "severity": "high",
        })

    # ── Reasoning narrative (auditable) ────────────────────────────
    reasoning = (
        f"Analysed {len(decisions)} ELA decisions across "
        f"{len(set(d['gender'] for d in decisions))} gender groups and "
        f"{len(set(d['age_band'] for d in decisions))} age bands. "
        f"Gender disparity in high-potential track: {gender_hp_disparity}%. "
        f"Age disparity in negative-signal track: {age_neg_disparity}%. "
        f"Equal-opportunity disparity among high performers: {eo_gender_disparity}%. "
        f"Low-confidence high-impact decisions: {len(low_confidence)}. "
        f"Total findings: {len(findings)}."
    )

    return {
        "agent": "Data Profiler",
        "input_decision_count": len(decisions),
        "fairness_metrics_evaluated": ["M01", "M02", "M03"],
        "disparity_summary": {
            "gender_in_high_potential": {
                "rates": gender_hp_rates,
                "disparity_pct": gender_hp_disparity,
            },
            "age_in_negative_signal": {
                "rates": age_neg_rates,
                "disparity_pct": age_neg_disparity,
            },
            "equal_opportunity_gender": {
                "rates": eo_gender_rates,
                "disparity_pct": eo_gender_disparity,
            },
        },
        "intersectional_analysis": intersectional,
        "findings": findings,
        "low_confidence_decisions": [
            {"employee_id": d["employee_id"], "confidence": d["ela_confidence"]}
            for d in low_confidence
        ],
        "reasoning": reasoning,
        "citation": "Fairness metrics defined in Foundry IQ Ethics KG (M01–M03)",
    }


if __name__ == "__main__":
    result = run()
    print("\n=== DATA PROFILER REPORT ===")
    print(result["reasoning"])
    print(f"\nFindings: {len(result['findings'])}")
    for f in result["findings"]:
        print(f"  [{f['severity'].upper()}] {f['id']}: {f['type']}")
