"""
Agent 0: Enterprise Learning Agent (ELA)
==========================================
The "upstream" agent under audit. Produces training recommendations
for employees based on demographic + performance signals.

For the demo, this agent's logic is intentionally biased so the
downstream Foundry Sentinel can detect and surface the bias.
In production, the ELA would be a real ML model or rules engine —
the Sentinel doesn't need to know how it works internally.

Reasoning pattern: Rule-based scoring with demographic biases baked in
                   (simulating real-world biased ML models).
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_dataset() -> dict:
    with open(DATA_DIR / "synthetic_employees.json") as f:
        return json.load(f)


def get_employee(employee_id: str) -> dict:
    """Tool: retrieve employee record from synthetic enterprise data."""
    data = _load_dataset()
    for emp in data["employees"]:
        if emp["employee_id"] == employee_id:
            return emp
    return {"error": f"Employee {employee_id} not found"}


def list_all_employees() -> list:
    """Tool: list every employee under audit."""
    return _load_dataset()["employees"]


def list_all_recommendations() -> dict:
    """
    Returns the ELA's full set of training recommendations for the workforce.
    These are the candidate decisions the Sentinel will audit.
    """
    data = _load_dataset()
    return {
        "ela_version": "v1.0-biased-demo",
        "total_decisions": len(data["employees"]),
        "decisions": [
            {
                "employee_id": e["employee_id"],
                "employee_name": e["name"],
                "gender": e["gender"],
                "age_band": e["age_band"],
                "department": e["department"],
                "performance_score": e["performance_score"],
                "ela_recommendation": e["ela_recommendation"],
                "ela_confidence": e["ela_confidence"],
                "program_tier": data["training_programs"][e["ela_recommendation"]]["tier"],
                "career_impact": data["training_programs"][e["ela_recommendation"]]["career_impact"],
            }
            for e in data["employees"]
        ],
        "synthetic_note": "All ELA decisions are synthetic and contain deliberate bias patterns for demo.",
    }


def run() -> dict:
    """Run the Enterprise Learning Agent — returns full decision set."""
    return list_all_recommendations()


if __name__ == "__main__":
    result = run()
    print(f"ELA produced {result['total_decisions']} candidate decisions.")
    for d in result["decisions"][:5]:
        print(f"  {d['employee_id']} {d['employee_name']:20} → {d['ela_recommendation']}")
