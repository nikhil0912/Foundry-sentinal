# 🛡️ Foundry Sentinel — Judge Demo Guide

> **Microsoft Agents League 2026 · Reasoning Agents Track**
> Estimated demo time: **3 minutes**

This guide walks judges through the full Responsible AI audit pipeline. Everything runs locally — no Azure credentials, no setup beyond `pip install`.

---

## ⚡ 60-Second Quick Start

```bash
git clone https://github.com/nikhil0912/foundry-sentinel
cd foundry-sentinel
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` — you'll see the Foundry Sentinel dashboard with the demo mode banner.

---

## 🎬 Demo Path — The Full Audit

| Step | Action | What to look for |
|---|---|---|
| 1 | Click **▶️ Run Full Sentinel Pipeline** in the sidebar | All 4 agents execute in <50ms |
| 2 | Read the **Executive Verdict** at the top | **🛑 CRITICAL (100/100)** — Sentinel blocks deployment |
| 3 | Scroll to **Agent 1 — Data Profiler** | Gender disparity: ~66%, Age disparity: ~50% |
| 4 | Expand findings (F01-F04) | Each finding has severity + threshold |
| 5 | Scroll to **Agent 2 — Decision Audit** | 5 rule violations across 4 ethical principles |
| 6 | Click any violation (e.g. **R02**) | See the full Foundry IQ rule + principles touched |
| 7 | Scroll to **Agent 3 — Transparency** | Plain-language headlines for HR/L&D stakeholders |
| 8 | Read the **Counterfactual Scenarios** | "What if gender were swapped?" — illustrates causality |
| 9 | Review the **Prioritised Action Plan** | 5 mitigations ranked by effort with tradeoffs |
| 10 | Check **Employees Requiring Immediate Review** | Specific employee IDs flagged for human review |
| 11 | Scroll to **Pipeline Trace** | Per-agent timing + full auditability |

---

## 🧪 Run the Evaluation Suite

```bash
python eval.py
```

**Expected output:** `78/78 tests passing, 100% score`

---

## 🎯 What Judges Should Notice

### Foundry IQ as Ethical Knowledge Graph (NOT Document Retrieval)

This is the **central innovation**. Open `data/foundry_iq_ethics_kg.json` to inspect:

- 5 ethical principles with legal backing
- 3 fairness metrics with formulas and thresholds
- 6 contextual IF-THEN rules that link findings to principles
- 6 mitigation strategies with effort/tradeoff metadata

The Decision Audit Agent **traverses this graph** to perform principle-based reasoning — every violation cites the exact rule and principle it touches.

### Multi-Step Reasoning Across 4 Agents

Each agent enriches the downstream context:

```
ELA decisions
   → Profiler computes statistical disparities
      → Audit maps stats to ethical rule violations
         → Transparency synthesises into stakeholder action plan
```

This is genuine multi-step reasoning — challenging for a single monolithic agent.

### Counterfactual "What-If" Analysis

Agent 3 generates concrete counterfactual scenarios for each violation:

> *"If this employee's gender were swapped while keeping all other features constant, the recommendation would likely flip — indicating gender, not merit, drove the decision."*

This is exactly the kind of explainability the EU AI Act demands.

### Human-in-the-Loop Enforced

The system **never auto-deploys decisions**. It produces analysis, surfaces violations, suggests mitigations — and explicitly hands off to HR + Compliance.

---

## 🛡️ Responsible AI Guardrails Demonstrated

| Guardrail | How It's Enforced |
|---|---|
| **No real PII** | All employee data synthetic with `E-001` style IDs |
| **All outputs cited** | Each agent has a `citation` field referencing Foundry IQ KG |
| **Human review required** | `human_review_required: true` on CRITICAL/HIGH risk |
| **No autonomous deployment** | `deployment_decision: BLOCK_DEPLOYMENT` on violations |
| **Auditability** | Every agent has a `reasoning` field, full trace logged |
| **Determinism** | Same input → same output (proven in eval suite) |

---

## 🧭 Reasoning Patterns

| Agent | Pattern | Why It Matters |
|---|---|---|
| **Profiler** | Statistical Audit (Compute → Compare → Flag) | Detects what humans miss in volume |
| **Audit** | KG Traversal → Rule Match → Principle Mapping | Brings legal/ethical reasoning into the loop |
| **Transparency** | Synthesis → Counterfactual → Action Plan | Makes findings actionable for non-technical stakeholders |

---

## 🔍 The Bias Pattern in Demo Data

The synthetic dataset deliberately contains these patterns for the audit to catch:

| Pattern | Affected Group | What Sentinel Detects |
|---|---|---|
| Male high performers routed to leadership | Female high performers | **R01** — Growth Equity Violation |
| 4 of 6 males in leadership track, 0 of 6 females | All female employees | **R02** — Demographic Parity Violation |
| 50+ age group routed to "Sunset Skills" | David Kim, Sarah Brennan | **R03** — Age Discrimination |
| Multiple decisions made with confidence < 0.65 | Several employees | **R04** — Human Oversight Violation |

The Sentinel catches **all four** without ever being told what to look for — just by traversing the Foundry IQ ethics graph.

---

## 📂 Repo Structure

```
foundry-sentinel/
├── app.py                          # Streamlit dashboard
├── eval.py                         # 78-test evaluation suite
├── architecture.html               # Architecture diagram
├── banner.html                     # Project banner
├── README.md
├── DEMO.md                         # This guide
├── copilot_usage.md                # GitHub Copilot documentation
├── requirements.txt
├── .gitignore
├── .streamlit/config.toml
├── agents/
│   ├── agent0_ela.py
│   ├── agent1_profiler.py
│   ├── agent2_audit.py
│   └── agent3_transparency.py
└── data/
    ├── synthetic_employees.json
    └── foundry_iq_ethics_kg.json
```

---

*All data is synthetic. Built entirely with GitHub Copilot for the Agents League 2026 hackathon.*
*⚠️ This system supports human decision-making — humans make all final calls.*
