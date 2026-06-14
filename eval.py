"""
Foundry Sentinel — Evaluation Suite
=====================================
Tests all 4 agents, the Foundry IQ knowledge graph, the full pipeline,
edge cases, and Responsible AI guardrails.

Run with: python eval.py
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.agent0_ela import (
    run as run_ela,
    get_employee,
    list_all_employees,
)
from agents.agent1_profiler import (
    run as run_profiler,
    compute_group_rates,
)
from agents.agent2_audit import (
    run as run_audit,
    query_kg_principle,
    query_kg_rule,
    query_kg_mitigations_for_violations,
)
from agents.agent3_transparency import run as run_transparency

PASS = "✅ PASS"
FAIL = "❌ FAIL"
results = []


def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append({"test": name, "status": status, "detail": detail})
    print(f"  {status}  {name}" + (f" — {detail}" if detail else ""))
    return condition


# ── DATA INTEGRITY ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("DATA INTEGRITY — Synthetic Dataset")
print("=" * 60)

DATA_DIR = Path(__file__).parent / "data"

with open(DATA_DIR / "synthetic_employees.json") as f:
    employees_data = json.load(f)

with open(DATA_DIR / "foundry_iq_ethics_kg.json") as f:
    kg_data = json.load(f)

check("synthetic_employees.json loads", True)
check("foundry_iq_ethics_kg.json loads", True)

employees = employees_data["employees"]
check("12 synthetic employees", len(employees) == 12, f"found {len(employees)}")

# Required fields on every employee
required_fields = [
    "employee_id", "name", "gender", "age_band",
    "tenure_years", "department", "performance_score",
    "ela_recommendation", "ela_confidence",
]
all_have_fields = all(
    all(f in e for f in required_fields) for e in employees
)
check("All employees have required fields", all_have_fields)

# Synthetic ID format
all_synthetic_ids = all(e["employee_id"].startswith("E-") for e in employees)
check("All employee IDs use synthetic format", all_synthetic_ids)

# No real PII
emp_str = json.dumps(employees_data)
no_real_pii = (
    "@gmail" not in emp_str.lower()
    and "@yahoo" not in emp_str.lower()
    and "@hotmail" not in emp_str.lower()
)
check("No real email domains in dataset", no_real_pii)

# KG integrity
check("KG has 5 ethical principles",
      len(kg_data["ethical_principles"]) == 5,
      f"found {len(kg_data['ethical_principles'])}")
check("KG has 3 fairness metrics",
      len(kg_data["fairness_metrics"]) == 3)
check("KG has 6 contextual rules",
      len(kg_data["contextual_rules"]) == 6)
check("KG has 6 mitigation strategies",
      len(kg_data["mitigation_strategies"]) == 6)

# Each rule references at least one principle
for rule in kg_data["contextual_rules"]:
    check(
        f"Rule {rule['id']} invokes valid principles",
        len(rule["principles_invoked"]) > 0,
    )

# Each mitigation maps to at least one violation
for m in kg_data["mitigation_strategies"]:
    check(
        f"Mitigation {m['id']} maps to violations",
        len(m["applies_to_violations"]) > 0,
    )


# ── AGENT 0: ELA ────────────────────────────────────────────────
print("\n" + "=" * 60)
print("AGENT 0 — Enterprise Learning Agent")
print("=" * 60)

ela_result = run_ela()
check("ELA produces decisions", ela_result["total_decisions"] == 12)
check("ELA decisions have all required fields",
      all("ela_recommendation" in d and "ela_confidence" in d
          and "career_impact" in d
          for d in ela_result["decisions"]))

# Get specific employee
emp = get_employee("E-001")
check("get_employee retrieves valid employee",
      emp["name"] == "Alex Chen")

# Missing employee
missing = get_employee("E-999")
check("get_employee handles missing entity",
      "error" in missing)

# Verify deliberate bias exists in data (for demo)
gender_in_hp = {}
for d in ela_result["decisions"]:
    g = d["gender"]
    if g not in gender_in_hp:
        gender_in_hp[g] = {"hp": 0, "total": 0}
    gender_in_hp[g]["total"] += 1
    if d["career_impact"] == "promotion_track":
        gender_in_hp[g]["hp"] += 1
male_hp_pct = (gender_in_hp["Male"]["hp"] /
               gender_in_hp["Male"]["total"] * 100)
female_hp_pct = (gender_in_hp["Female"]["hp"] /
                 gender_in_hp["Female"]["total"] * 100)
check(
    "Demo dataset contains gender disparity",
    abs(male_hp_pct - female_hp_pct) > 20,
    f"Male: {male_hp_pct:.0f}% vs Female: {female_hp_pct:.0f}%",
)


# ── AGENT 1: PROFILER ───────────────────────────────────────────
print("\n" + "=" * 60)
print("AGENT 1 — Data Profiler")
print("=" * 60)

profiler_result = run_profiler(ela_result)

check("Profiler returns reasoning",
      bool(profiler_result.get("reasoning")))
check("Profiler reasoning > 100 chars",
      len(profiler_result["reasoning"]) > 100)
check("Profiler returns findings",
      isinstance(profiler_result["findings"], list))

# Should find at least 3 critical/high findings
critical_or_high = [
    f for f in profiler_result["findings"]
    if f["severity"] in ("critical", "high")
]
check(
    "Profiler detects ≥3 critical/high findings",
    len(critical_or_high) >= 3,
    f"found {len(critical_or_high)}",
)

# Specific finding types
finding_types = {f["type"] for f in profiler_result["findings"]}
check("Profiler detects demographic parity violation",
      "demographic_parity_violation" in finding_types)
check("Profiler detects age disparity",
      "age_disparity_negative_signal" in finding_types)
check("Profiler detects low-confidence high-impact",
      "low_confidence_high_impact" in finding_types)

# Citation
check("Profiler output is cited",
      "Foundry IQ" in profiler_result["citation"])

# Group rate computation
rates = compute_group_rates(
    ela_result["decisions"], "gender", lambda d: d["career_impact"] == "promotion_track"
)
check("compute_group_rates returns valid dict", "Male" in rates and "Female" in rates)
check("Group rates have count, total, rate_pct",
      all("count" in v and "total" in v and "rate_pct" in v
          for v in rates.values()))


# ── AGENT 2: DECISION AUDIT ─────────────────────────────────────
print("\n" + "=" * 60)
print("AGENT 2 — Decision Audit (Foundry IQ)")
print("=" * 60)

audit_result = run_audit(profiler_result)

check("Audit returns reasoning",
      bool(audit_result.get("reasoning")))
check("Audit returns violations",
      isinstance(audit_result["violations"], list))

# Expect multiple violations given the biased dataset
check("Audit detects ≥3 violations",
      len(audit_result["violations"]) >= 3,
      f"found {len(audit_result['violations'])}")

# Verify violations reference rule IDs and principles
for v in audit_result["violations"]:
    check(
        f"Violation {v['rule_id']} has principles",
        len(v["principles_violated"]) > 0,
    )

# Risk assessment
check("Risk score 0-100",
      0 <= audit_result["risk_assessment"]["score"] <= 100)
check("Risk level present",
      audit_result["risk_assessment"]["level"] in
      ["NONE", "LOW", "MODERATE", "HIGH", "CRITICAL"])
check("Risk verdict present",
      audit_result["risk_assessment"]["verdict"] in
      ["APPROVED", "MONITOR", "REVIEW_REQUIRED",
       "REQUIRE_REMEDIATION", "BLOCK_DEPLOYMENT"])

# Given heavy bias, should be CRITICAL or HIGH
check(
    "Risk assessed as CRITICAL or HIGH for biased data",
    audit_result["risk_assessment"]["level"] in ("CRITICAL", "HIGH"),
    f"got {audit_result['risk_assessment']['level']}",
)

# Mitigations returned
check("Audit returns ≥3 mitigations",
      len(audit_result["mitigations"]) >= 3)

# KG queries work
p01 = query_kg_principle("P01")
check("query_kg_principle works", p01.get("name") == "Non-Discrimination")

r02 = query_kg_rule("R02")
check("query_kg_rule works", r02.get("id") == "R02")

mits = query_kg_mitigations_for_violations(["R02", "R03"])
check("query_kg_mitigations_for_violations works",
      len(mits) > 0)


# ── AGENT 3: TRANSPARENCY ───────────────────────────────────────
print("\n" + "=" * 60)
print("AGENT 3 — Transparency")
print("=" * 60)

trans_result = run_transparency(audit_result, profiler_result)

check("Transparency returns reasoning",
      bool(trans_result.get("reasoning")))
check("Transparency returns executive verdict",
      bool(trans_result.get("executive_verdict")))
check("Executive verdict > 100 chars",
      len(trans_result["executive_verdict"]) > 100)
check("Humanised findings present",
      len(trans_result["humanised_findings"]) >= 3)

# Each humanised finding has all required fields
for h in trans_result["humanised_findings"]:
    check(
        f"Humanised finding {h['rule_id']} complete",
        all(k in h for k in
            ["headline", "plain_language", "business_impact"]),
    )

# Counterfactuals
check("Counterfactual scenarios generated",
      len(trans_result["counterfactual_scenarios"]) > 0)

# Action plan
check("Prioritised action plan ≥3 items",
      len(trans_result["prioritised_action_plan"]) >= 3)

# Each action has priority + tradeoff
for a in trans_result["prioritised_action_plan"]:
    check(
        f"Action P{a['priority']} ({a['action']}) is complete",
        all(k in a for k in
            ["action", "description", "effort", "tradeoff"]),
    )

# Human review required
check("Human review flag set on CRITICAL/HIGH risk",
      trans_result["human_review_required"])


# ── RESPONSIBLE AI GUARDRAILS ───────────────────────────────────
print("\n" + "=" * 60)
print("RESPONSIBLE AI — Safety & Integrity Checks")
print("=" * 60)

# Every agent output cited
all_cited = all(
    bool(r.get("citation"))
    for r in [profiler_result, audit_result, trans_result]
)
check("All agent outputs cite their source", all_cited)

# No autonomous deployment language
trans_str = json.dumps(trans_result)
no_auto_deploy = (
    "auto-deploy" not in trans_str.lower()
    and "automatically apply" not in trans_str.lower()
)
check("No autonomous deployment language", no_auto_deploy)

# Human-in-the-loop enforced
check("Human review required on CRITICAL/HIGH",
      trans_result["human_review_required"] is True)

# Synthetic disclaimers present
check("Synthetic disclaimer in dataset",
      "synthetic" in employees_data["description"].lower())
check("Synthetic disclaimer in KG",
      "synthetic" in kg_data["synthetic_disclaimer"].lower())


# ── DETERMINISM ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("DETERMINISM — Reproducibility Check")
print("=" * 60)

r1 = run_ela()
r2 = run_ela()
check("ELA deterministic", r1 == r2)

p1 = run_profiler(r1)
p2 = run_profiler(r2)
check("Profiler deterministic",
      p1["disparity_summary"] == p2["disparity_summary"])

a1 = run_audit(p1)
a2 = run_audit(p2)
check("Audit deterministic",
      a1["risk_assessment"] == a2["risk_assessment"])


# ── SUMMARY ─────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("EVALUATION SUMMARY")
print("=" * 60)

passed = sum(1 for r in results if r["status"] == PASS)
failed = sum(1 for r in results if r["status"] == FAIL)
total = len(results)
score = round(passed / total * 100) if total > 0 else 0

print(f"\n  Total Tests : {total}")
print(f"  Passed      : {passed}")
print(f"  Failed      : {failed}")
print(f"  Score       : {score}%")

if failed > 0:
    print(f"\n  Failed Tests:")
    for r in results:
        if r["status"] == FAIL:
            print(f"    ❌ {r['test']} — {r['detail']}")

print(f"\n  {'🏆 ALL TESTS PASSED' if failed == 0 else '⚠️  SOME TESTS FAILED'}")
print("=" * 60)
