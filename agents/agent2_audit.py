"""
Agent 2: Decision Audit Agent
==============================
The Foundry IQ-powered ethical reasoner. Queries the Foundry IQ ethical
knowledge graph and maps the Data Profiler's findings to specific
ethical principles, contextual rules, and severity classifications.

Reasoning pattern: Graph Traversal → Rule Matching → Principle Mapping
  Step 1: Load ethical knowledge graph from Foundry IQ
  Step 2: For each finding from Profiler, traverse rules
  Step 3: Match findings to violated principles
  Step 4: Look up mitigation strategies for each violation
  Step 5: Compute composite ethical risk score
"""

import json
from pathlib import Path
from agents.agent1_profiler import run as run_profiler
from agents.agent0_ela import list_all_recommendations

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_kg() -> dict:
    with open(DATA_DIR / "foundry_iq_ethics_kg.json") as f:
        return json.load(f)


def query_kg_principle(principle_id: str) -> dict:
    """Tool: query Foundry IQ for a specific ethical principle."""
    kg = _load_kg()
    for p in kg["ethical_principles"]:
        if p["id"] == principle_id:
            return p
    return {}


def query_kg_rule(rule_id: str) -> dict:
    """Tool: query Foundry IQ for a contextual rule."""
    kg = _load_kg()
    for r in kg["contextual_rules"]:
        if r["id"] == rule_id:
            return r
    return {}


def query_kg_mitigations_for_violations(violation_ids: list) -> list:
    """Tool: retrieve mitigation strategies that apply to given violations."""
    kg = _load_kg()
    return [
        m for m in kg["mitigation_strategies"]
        if any(v in m["applies_to_violations"] for v in violation_ids)
    ]


def _evaluate_rules(findings: list, decisions: list, kg: dict) -> list:
    """
    Map Profiler findings to contextual rules in the KG.
    Returns list of violations.
    """
    violations = []

    finding_types = {f["type"]: f for f in findings}

    for rule in kg["contextual_rules"]:
        violated = False
        evidence = None

        if rule["id"] == "R02":
            # demographic parity > 20% in high_potential
            f = finding_types.get("demographic_parity_violation")
            if f and f["disparity_pct"] > 20:
                violated = True
                evidence = f

        elif rule["id"] == "R03":
            # age 50-59 systematically getting transition tier
            age_neg = finding_types.get("age_disparity_negative_signal")
            if age_neg:
                rates_50_59 = age_neg["rates"].get("50-59", {}).get("rate_pct", 0)
                if rates_50_59 >= 50:
                    violated = True
                    evidence = age_neg

        elif rule["id"] == "R04":
            # low confidence + high impact
            lc = finding_types.get("low_confidence_high_impact")
            if lc and lc["count"] > 0:
                violated = True
                evidence = lc

        elif rule["id"] == "R06":
            # performance-adjusted disparity
            eo = finding_types.get("equal_opportunity_violation")
            if eo and eo["disparity_pct"] > 10:
                violated = True
                evidence = eo

        elif rule["id"] == "R01":
            # high performer in maintenance while peer with lower perf in high-potential
            # Check cross-pairs
            hp_in_maintenance = [
                d for d in decisions
                if d["performance_score"] >= 4.0
                and d.get("program_tier") in ["maintenance", "support"]
            ]
            lp_in_high_pot = [
                d for d in decisions
                if d["performance_score"] < 4.2
                and d.get("career_impact") == "promotion_track"
            ]
            cross_pairs = []
            for high in hp_in_maintenance:
                for low in lp_in_high_pot:
                    if (high["department"] == low["department"]
                        and high["gender"] != low["gender"]
                        and high["performance_score"] >= low["performance_score"]):
                        cross_pairs.append({
                            "higher_performer": high["employee_id"],
                            "lower_performer_promoted": low["employee_id"],
                            "department": high["department"],
                        })
            if cross_pairs:
                violated = True
                evidence = {"cross_pairs": cross_pairs, "count": len(cross_pairs)}

        if violated:
            principles = [
                query_kg_principle(pid) for pid in rule["principles_invoked"]
            ]
            violations.append({
                "rule_id": rule["id"],
                "rule_text": rule["rule"],
                "severity": rule["severity"],
                "principles_violated": [
                    {"id": p["id"], "name": p["name"], "definition": p["definition"]}
                    for p in principles if p
                ],
                "evidence": evidence,
            })

    return violations


def _compute_risk_score(violations: list) -> dict:
    """Compute ethical risk score from violation set."""
    severity_weights = {"critical": 30, "high": 20, "medium": 10, "low": 5}
    score = sum(severity_weights.get(v["severity"], 5) for v in violations)
    score = min(score, 100)

    if score >= 70:
        level = "CRITICAL"
        verdict = "BLOCK_DEPLOYMENT"
    elif score >= 40:
        level = "HIGH"
        verdict = "REQUIRE_REMEDIATION"
    elif score >= 20:
        level = "MODERATE"
        verdict = "REVIEW_REQUIRED"
    elif score > 0:
        level = "LOW"
        verdict = "MONITOR"
    else:
        level = "NONE"
        verdict = "APPROVED"

    return {"score": score, "level": level, "verdict": verdict}


def run(profiler_report: dict = None) -> dict:
    """
    Run the Decision Audit Agent.

    Returns: Decision Audit Report with violations, principles, mitigations.
    """
    if profiler_report is None:
        profiler_report = run_profiler()

    decisions = list_all_recommendations()["decisions"]
    kg = _load_kg()
    findings = profiler_report["findings"]

    # ── Step 1: Evaluate all contextual rules ──────────────────────
    violations = _evaluate_rules(findings, decisions, kg)

    # ── Step 2: Compute risk score ─────────────────────────────────
    risk = _compute_risk_score(violations)

    # ── Step 3: Get applicable mitigation strategies ──────────────
    violation_ids = [v["rule_id"] for v in violations]
    mitigations = query_kg_mitigations_for_violations(violation_ids)

    # ── Step 4: Identify all principles touched ───────────────────
    principles_touched = set()
    for v in violations:
        for p in v["principles_violated"]:
            principles_touched.add(p["id"])

    # ── Reasoning ──────────────────────────────────────────────────
    reasoning = (
        f"Traversed Foundry IQ Ethics KG: {len(kg['contextual_rules'])} "
        f"contextual rules, {len(kg['ethical_principles'])} principles, "
        f"{len(kg['fairness_metrics'])} fairness metrics. "
        f"Evaluated {len(findings)} findings from Data Profiler against rule set. "
        f"Detected {len(violations)} rule violations across "
        f"{len(principles_touched)} ethical principles. "
        f"Composite ethical risk score: {risk['score']}/100 ({risk['level']}). "
        f"Recommended {len(mitigations)} mitigation strategies."
    )

    return {
        "agent": "Decision Audit",
        "kg_source": "Microsoft Foundry IQ — Ethical Reasoning Graph",
        "rules_evaluated": len(kg["contextual_rules"]),
        "violations_detected": len(violations),
        "violations": violations,
        "principles_touched": sorted(list(principles_touched)),
        "mitigations": mitigations,
        "risk_assessment": risk,
        "reasoning": reasoning,
        "citation": "Foundry IQ Ethics KG v1.0 — synthetic principles, rules, metrics",
    }


if __name__ == "__main__":
    result = run()
    print("\n=== DECISION AUDIT REPORT ===")
    print(result["reasoning"])
    print(f"\nViolations: {len(result['violations'])}")
    for v in result["violations"]:
        print(f"  [{v['severity'].upper()}] {v['rule_id']}: principles {[p['id'] for p in v['principles_violated']]}")
    print(f"\nRisk: {result['risk_assessment']['level']} ({result['risk_assessment']['score']}/100)")
    print(f"Verdict: {result['risk_assessment']['verdict']}")
    print(f"\nMitigation strategies: {len(result['mitigations'])}")
    for m in result["mitigations"]:
        print(f"  {m['id']}: {m['name']}")
