# ◈ GitHub Copilot Usage — Foundry Sentinel

> **Microsoft Agents League 2026 — Reasoning Agents Track**
> This document evidences how GitHub Copilot was used throughout
> the development of Foundry Sentinel.

---

## How Copilot Was Used

### 1. 4-Agent Pipeline Architecture (`agents/*.py`)

The multi-agent pipeline was scaffolded with Copilot.

**Prompt used:**
```
Build a multi-agent system for Responsible AI assurance. Four agents:
Agent 0 — Enterprise Learning Agent that produces biased training
recommendations from synthetic employee data.
Agent 1 — Data Profiler that computes statistical fairness metrics
across protected attributes (gender, age_band).
Agent 2 — Decision Audit Agent that queries a Foundry IQ ethical
knowledge graph and maps findings to ethical principles via
contextual rules.
Agent 3 — Transparency Agent that synthesises findings into
stakeholder-readable summary with counterfactuals and action plan.
Each agent should return a structured dict with a 'reasoning' field
for full auditability.
```

**Copilot generated:** The complete pipeline structure, the data flow
between agents, the standard agent contract (input → reasoning → output
+ citation), and the orchestration pattern.

---

### 2. Foundry IQ Ethical Knowledge Graph (`data/foundry_iq_ethics_kg.json`)

The knowledge graph schema was designed with Copilot.

**Prompt used:**
```
Design a JSON schema for an ethical knowledge graph used by Microsoft
Foundry IQ. Include:
- 5 ethical principles (with definitions, legal backing, severity)
- 3 fairness metrics (with formulas and thresholds)
- 6 contextual IF-THEN rules linking findings to principles
- 6 mitigation strategies (with effort and tradeoff metadata)
The graph should support traversal: rules invoke principles,
mitigations apply to violations. All references must be by ID.
```

**Copilot generated:** The complete graph structure including all 5
principles (Non-Discrimination, Employee Growth Equity, Algorithmic
Transparency, Human Oversight, Age Inclusivity), the 3 fairness metric
formulas, and the rule-principle-mitigation cross-references.

---

### 3. Statistical Fairness Analysis (`agents/agent1_profiler.py`)

The fairness metrics engine was generated with Copilot.

**Prompt used:**
```
Generate a Python function that takes a list of ELA decisions and
computes demographic disparity rates grouped by a protected attribute.
Return a dict: { group_value: { count, total, rate_pct } }.
Then compute max_disparity_pct across groups. Include intersectional
analysis (department × gender) and equal-opportunity check (rates
restricted to high performers ≥ 4.0).
```

**Copilot generated:** The `compute_group_rates` helper, the
`_max_disparity_pct` calculator, the intersectional cross-tabulation,
and the structured Bias Profile Report output.

---

### 4. KG Traversal + Rule Matching (`agents/agent2_audit.py`)

The graph reasoning logic was built with Copilot.

**Prompt used:**
```
Generate a function that traverses an ethical knowledge graph to
evaluate contextual rules against statistical findings. For each
rule R01-R06, check if the relevant finding satisfies the rule's
condition. If violated, return a violation record including the
rule text, severity, principles invoked, and evidence. Then compute
a composite risk score (0-100) using severity weights and map to
a deployment verdict (APPROVED / MONITOR / REVIEW_REQUIRED /
REQUIRE_REMEDIATION / BLOCK_DEPLOYMENT).
```

**Copilot generated:** The full `_evaluate_rules` function, the
severity-weighted risk scoring (`_compute_risk_score`), and the
verdict thresholds.

---

### 5. Counterfactual Generation (`agents/agent3_transparency.py`)

**Prompt used:**
```
Generate Python code that produces counterfactual "what-if" scenarios
for ethical violations. For each violation, describe the observed
scenario and what would happen if the protected attribute (e.g.,
gender) were swapped while keeping all other features constant. The
output should be human-readable and suitable for non-technical
stakeholders.
```

**Copilot generated:** The complete `_generate_counterfactuals`
function with scenario + what-if pair generation for each violation type.

---

### 6. Streamlit Dashboard (`app.py`)

**Prompt used:**
```
Generate a Streamlit dashboard for a Responsible AI assurance system.
Include a hero header with gradient text, demo mode banner, sidebar
with Run button, executive verdict box that changes colour by risk
level (red/amber/green), expandable violation cards with severity
icons, counterfactual scenario boxes with dashed borders, prioritised
action plan with effort badges, and a 4-column pipeline trace at the
bottom. Use a dark cosmic theme with Inter + JetBrains Mono fonts.
```

**Copilot generated:** The complete 400+ line CSS block, the verdict
colour-coding logic, the action priority badge styling, and the layout.

---

### 7. Evaluation Suite (`eval.py`)

**Prompt used:**
```
Generate a 70+ test evaluation suite for the Foundry Sentinel
multi-agent system. Cover: data integrity (12 employees, all required
fields, no real PII), KG integrity (5 principles, 3 metrics, 6 rules,
6 mitigations with cross-references), each agent's contract (reasoning,
findings, violations, citations), Responsible AI guardrails (no auto-
deploy language, human-in-the-loop enforced, synthetic disclaimers),
and determinism (same input → same output across 3 runs).
```

**Copilot generated:** The complete test suite with 78 individual
assertions, the pass/fail tracking pattern, and the summary block.

---

### 8. Debugging Assistance

Throughout development, Copilot Chat was used to:
- Resolve dictionary key access patterns for the KG traversal
- Identify the correct rule severity thresholds
- Debug the intersectional analysis edge case (single-member groups)
- Refine the counterfactual narrative phrasing
- Tune the risk score weights to map cleanly to verdict thresholds

---

## Summary

| Component | Copilot Role |
|---|---|
| 4-agent pipeline architecture | Full scaffolding |
| Foundry IQ ethics KG schema | Full generation |
| Statistical fairness analysis | Full generation |
| KG traversal + rule matching | Full generation |
| Counterfactual generation | Full generation |
| Streamlit dashboard | Full generation |
| 78-test eval suite | Full generation |
| Bug fixes + refinement | Copilot Chat throughout |

> GitHub Copilot was integral to every layer of this project — from
> initial architecture to final eval pass. Development time was reduced
> by an estimated 60-70%.
