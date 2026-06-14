"""
Agent 3: Transparency Agent
============================
Synthesises the Profiler's statistical findings and the Audit Agent's
ethical reasoning into a human-readable Responsible AI Summary for
HR, L&D, and compliance stakeholders.

Reasoning pattern: Synthesis → Counterfactual → Recommendation
  Step 1: Translate technical findings into plain-language insights
  Step 2: Generate counterfactual examples for each violation
  Step 3: Map mitigations to concrete next steps with priorities
  Step 4: Construct narrative summary suitable for non-technical readers
"""

from agents.agent2_audit import run as run_audit
from agents.agent1_profiler import run as run_profiler
from agents.agent0_ela import list_all_recommendations
from llm_client import synthesize_executive_verdict, is_llm_available


def _humanize_finding(violation: dict) -> dict:
    """Translate a technical violation into stakeholder language."""
    rule_id = violation["rule_id"]
    principles = ", ".join(p["name"] for p in violation["principles_violated"])

    explanations = {
        "R01": {
            "headline": "High performers being passed over for development opportunities",
            "plain_language": (
                "Some of our highest-performing employees are being routed "
                "to skill-maintenance training while lower-performing peers "
                "of a different gender are being placed in leadership tracks. "
                "This is the most direct form of growth-equity bias."
            ),
            "business_impact": (
                "Top talent attrition risk — these employees will notice the "
                "pattern. Likely contributor to gender gap in senior roles."
            ),
        },
        "R02": {
            "headline": "Gender disparity in leadership track assignment",
            "plain_language": (
                "The Enterprise Learning Agent is recommending leadership-track "
                "programs at a significantly higher rate for one gender than "
                "another, even controlling for performance."
            ),
            "business_impact": (
                "Direct legal exposure under EEOC and EU AI Act guidelines. "
                "Likely root cause for compensation and promotion gaps."
            ),
        },
        "R03": {
            "headline": "Age discrimination in 'Sunset Skills' allocation",
            "plain_language": (
                "Employees aged 50+ — including top performers — are being "
                "systematically routed to transition-tier ('Sunset Skills') "
                "programs. This pattern is a textbook age discrimination risk."
            ),
            "business_impact": (
                "ADEA exposure. Loss of institutional knowledge. Likely "
                "morale collapse if this pattern becomes visible internally."
            ),
        },
        "R04": {
            "headline": "High-impact decisions being made without sufficient confidence",
            "plain_language": (
                "Several career-affecting recommendations are being issued "
                "by the AI with confidence below 65%. Decisions of this "
                "consequence should not be made by AI alone."
            ),
            "business_impact": (
                "Regulatory risk under EU AI Act Article 14 (human oversight "
                "for high-risk AI systems)."
            ),
        },
        "R06": {
            "headline": "Performance-adjusted disparity persists across groups",
            "plain_language": (
                "Even after controlling for performance score, recommendation "
                "outcomes differ across demographic groups by more than the "
                "acceptable threshold. The model is using protected attributes "
                "as a hidden signal."
            ),
            "business_impact": (
                "Indicates the underlying model has learned demographic proxies. "
                "Will compound over time without intervention."
            ),
        },
    }

    expl = explanations.get(rule_id, {
        "headline": f"Rule {rule_id} violation",
        "plain_language": violation["rule_text"],
        "business_impact": "Review required.",
    })

    return {
        "rule_id": rule_id,
        "severity": violation["severity"],
        "principles_violated": principles,
        "headline": expl["headline"],
        "plain_language": expl["plain_language"],
        "business_impact": expl["business_impact"],
    }


def _generate_counterfactuals(violations: list, decisions: list) -> list:
    """
    For violations involving demographic disparities, generate "what-if"
    counterfactual examples.
    """
    counterfactuals = []
    for v in violations:
        if v["rule_id"] in ["R01", "R02"]:
            evidence = v.get("evidence", {})
            if v["rule_id"] == "R01" and "cross_pairs" in evidence:
                for pair in evidence["cross_pairs"][:2]:
                    counterfactuals.append({
                        "scenario": (
                            f"Employee {pair['higher_performer']} (higher performer) "
                            f"in {pair['department']} was assigned a maintenance program "
                            f"while {pair['lower_performer_promoted']} (lower performer, "
                            f"different gender) was placed on a leadership track."
                        ),
                        "what_if": (
                            "If the gender attribute were swapped while keeping all "
                            "other features constant, the recommendation would likely "
                            "flip — indicating gender, not merit, drove the decision."
                        ),
                        "violation": v["rule_id"],
                    })
            elif v["rule_id"] == "R02":
                evidence_rates = evidence.get("rates", {})
                counterfactuals.append({
                    "scenario": (
                        f"Across the full workforce, "
                        + " vs ".join(
                            f"{g} = {r['rate_pct']}%"
                            for g, r in evidence_rates.items()
                        )
                        + " are being placed in high-potential tracks."
                    ),
                    "what_if": (
                        "If gender were equally distributed in the input features, "
                        "the disparity would shrink to within the 20% tolerance."
                    ),
                    "violation": v["rule_id"],
                })
        elif v["rule_id"] == "R03":
            counterfactuals.append({
                "scenario": (
                    "Employees aged 50+ are being routed to 'Sunset Skills' "
                    "regardless of their performance score."
                ),
                "what_if": (
                    "If those same employees were aged 35–45 with identical "
                    "performance, the system would recommend leadership-track "
                    "programs instead."
                ),
                "violation": v["rule_id"],
            })
    return counterfactuals


def _prioritise_mitigations(mitigations: list) -> list:
    """Rank mitigations by effort/impact for the action plan."""
    effort_score = {"low": 1, "medium": 2, "high": 3}
    return sorted(
        mitigations,
        key=lambda m: effort_score.get(m.get("effort", "medium"), 2)
    )


def run(audit_report: dict = None, profiler_report: dict = None) -> dict:
    """
    Run the Transparency Agent.

    Returns: Responsible AI Summary for stakeholders.
    """
    if profiler_report is None:
        profiler_report = run_profiler()
    if audit_report is None:
        audit_report = run_audit(profiler_report)

    violations = audit_report["violations"]
    mitigations = audit_report["mitigations"]
    risk = audit_report["risk_assessment"]
    decisions = list_all_recommendations()["decisions"]

    # ── Step 1: Humanise each violation ────────────────────────────
    humanised = [_humanize_finding(v) for v in violations]

    # ── Step 2: Generate counterfactuals ──────────────────────────
    counterfactuals = _generate_counterfactuals(violations, decisions)

    # ── Step 3: Prioritise action plan ─────────────────────────────
    prioritised = _prioritise_mitigations(mitigations)
    action_plan = [
        {
            "priority": i + 1,
            "action": m["name"],
            "description": m["description"],
            "effort": m["effort"],
            "tradeoff": m["tradeoff"],
            "addresses_violations": m["applies_to_violations"],
        }
        for i, m in enumerate(prioritised)
    ]

    # ── Step 4: Build executive summary ────────────────────────────
    # Try LLM-powered synthesis first (Foundry IQ / GitHub Models)
    llm_verdict, verdict_source = synthesize_executive_verdict(
        risk_level=risk["level"],
        risk_score=risk["score"],
        violations=violations,
        principles_touched=audit_report["principles_touched"],
        counterfactuals=counterfactuals,
    )

    if llm_verdict:
        executive_verdict = llm_verdict
    elif risk["level"] == "CRITICAL":
        executive_verdict = (
            f"🛑 The Enterprise Learning Agent has been audited and assessed at "
            f"{risk['level']} ethical risk ({risk['score']}/100). "
            f"{len(violations)} rule violations were detected across "
            f"{len(audit_report['principles_touched'])} ethical principles. "
            "This system should NOT be deployed in its current form. "
            "Apply the priority mitigations below and re-audit before approval."
        )
    elif risk["level"] == "HIGH":
        executive_verdict = (
            f"⚠️ The ELA shows {risk['level']} ethical risk ({risk['score']}/100). "
            f"{len(violations)} violations detected. Remediation is required "
            f"before broader rollout — the human review workflow must be "
            f"strengthened and the listed mitigations applied."
        )
    elif risk["level"] == "MODERATE":
        executive_verdict = (
            f"📋 The ELA shows {risk['level']} ethical risk ({risk['score']}/100). "
            f"{len(violations)} minor concerns require review. Approval is "
            f"conditional on the mitigations being scheduled."
        )
    else:
        executive_verdict = (
            f"✅ The ELA is within acceptable ethical bounds "
            f"({risk['score']}/100). Continue monitoring."
        )

    # ── Step 5: Affected employees breakdown ───────────────────────
    affected = {"high_severity": [], "needs_review": []}
    for v in violations:
        if v["rule_id"] == "R01":
            evidence = v.get("evidence", {})
            for pair in evidence.get("cross_pairs", []):
                affected["high_severity"].append(pair["higher_performer"])
        elif v["rule_id"] == "R04":
            evidence = v.get("evidence", {})
            for eid in evidence.get("affected_employees", []):
                affected["needs_review"].append(eid)

    reasoning = (
        f"Synthesised {len(violations)} ethical violations from Audit Agent "
        f"into {len(humanised)} stakeholder-friendly explanations. "
        f"Generated {len(counterfactuals)} counterfactual scenarios to "
        f"illustrate causality. Prioritised {len(prioritised)} mitigation "
        f"strategies into a {len(action_plan)}-step action plan. "
        f"Identified {len(affected['high_severity'])} employees in high-severity "
        f"contexts requiring immediate human review."
    )

    return {
        "agent": "Transparency",
        "executive_verdict": executive_verdict,
        "risk_level": risk["level"],
        "risk_score": risk["score"],
        "deployment_decision": risk["verdict"],
        "humanised_findings": humanised,
        "counterfactual_scenarios": counterfactuals,
        "prioritised_action_plan": action_plan,
        "affected_employees": affected,
        "human_review_required": risk["level"] in ["CRITICAL", "HIGH"],
        "verdict_source": verdict_source,
        "llm_powered": verdict_source == "foundry_iq_llm",
        "reasoning": reasoning,
        "citation": (
            "Findings derived from Foundry IQ Ethics KG + Data Profiler stats. "
            "Executive verdict synthesised by Azure AI Foundry / GitHub Models "
            "(gpt-4o-mini) when GITHUB_TOKEN is configured. "
            "Human stakeholders make all final decisions."
        ),
    }


if __name__ == "__main__":
    result = run()
    print("\n=== RESPONSIBLE AI SUMMARY ===")
    print(result["executive_verdict"])
    print(f"\nHumanised findings: {len(result['humanised_findings'])}")
    for f in result["humanised_findings"]:
        print(f"  • {f['headline']}")
    print(f"\nAction plan: {len(result['prioritised_action_plan'])} items")
    for a in result["prioritised_action_plan"][:3]:
        print(f"  P{a['priority']}: {a['action']} ({a['effort']} effort)")
