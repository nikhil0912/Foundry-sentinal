"""
Foundry Sentinel — Streamlit Demo UI
======================================
Multi-Agent Responsible AI Assurance for Enterprise Learning
Microsoft Agents League 2026 · Reasoning Agents Track

Run with: streamlit run app.py
"""

import streamlit as st
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.agent0_ela import run as run_ela, get_employee
from agents.agent1_profiler import run as run_profiler
from agents.agent2_audit import run as run_audit
from agents.agent3_transparency import run as run_transparency

# ── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Foundry Sentinel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────
st.markdown(
    """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .stApp {
    background: radial-gradient(ellipse at top, #15151f 0%, #0a0a0f 100%);
  }

  #MainMenu, footer { visibility: hidden; }
  .stDeployButton { display: none; }

  .fs-hero {
    background: linear-gradient(135deg, rgba(167,139,250,0.08) 0%, rgba(74,222,128,0.05) 100%);
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 14px;
    padding: 22px 30px;
    margin-bottom: 18px;
  }
  .fs-title {
    font-size: 32px;
    font-weight: 700;
    background: linear-gradient(135deg, #c7d2fe 0%, #a78bfa 50%, #4ade80 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .fs-subtitle {
    color: #94a3b8;
    font-size: 14px;
    margin: 6px 0 0 0;
  }
  .fs-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 14px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.04em;
    margin-right: 6px;
    margin-top: 12px;
  }
  .badge-foundry {
    background: rgba(167,139,250,0.15);
    border: 1px solid rgba(167,139,250,0.4);
    color: #a78bfa;
  }
  .badge-rai {
    background: rgba(74,222,128,0.12);
    border: 1px solid rgba(74,222,128,0.3);
    color: #4ade80;
  }
  .badge-enterprise {
    background: rgba(251,191,36,0.12);
    border: 1px solid rgba(251,191,36,0.3);
    color: #fbbf24;
  }
  .badge-copilot {
    background: rgba(96,165,250,0.12);
    border: 1px solid rgba(96,165,250,0.3);
    color: #60a5fa;
  }

  .demo-banner {
    background: linear-gradient(90deg, rgba(74,222,128,0.07) 0%, rgba(167,139,250,0.07) 100%);
    border: 1px solid rgba(74,222,128,0.25);
    border-radius: 10px;
    padding: 11px 18px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .agent-card {
    background: rgba(20,20,32,0.6);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 14px;
  }

  .verdict-critical {
    background: linear-gradient(90deg, rgba(239,68,68,0.15) 0%, rgba(239,68,68,0.05) 100%);
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 14px 0;
  }
  .verdict-high {
    background: linear-gradient(90deg, rgba(251,191,36,0.15) 0%, rgba(251,191,36,0.05) 100%);
    border-left: 4px solid #fbbf24;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 14px 0;
  }
  .verdict-low {
    background: linear-gradient(90deg, rgba(74,222,128,0.15) 0%, rgba(74,222,128,0.05) 100%);
    border-left: 4px solid #4ade80;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 14px 0;
  }

  .principle-tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    background: rgba(167,139,250,0.15);
    border: 1px solid rgba(167,139,250,0.3);
    color: #a78bfa;
    font-size: 10px;
    font-weight: 600;
    margin: 2px 4px 2px 0;
  }

  .counterfactual-box {
    background: rgba(15,15,30,0.8);
    border: 1px dashed rgba(167,139,250,0.4);
    border-radius: 10px;
    padding: 14px 18px;
    margin: 10px 0;
    font-family: 'Inter', sans-serif;
  }

  .action-step {
    background: rgba(20,20,32,0.5);
    border: 1px solid rgba(99,102,241,0.1);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
  }
  .action-priority {
    display: inline-block;
    padding: 3px 9px;
    border-radius: 12px;
    background: rgba(96,165,250,0.15);
    border: 1px solid rgba(96,165,250,0.3);
    color: #60a5fa;
    font-size: 11px;
    font-weight: 700;
    margin-right: 8px;
  }
</style>
""",
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────
st.markdown(
    """
<div class="fs-hero">
  <h1 class="fs-title">🛡️ Foundry Sentinel</h1>
  <p class="fs-subtitle">
    Multi-Agent Responsible AI Assurance for Enterprise Learning
    · Microsoft Foundry IQ · Reasoning Agents Track
  </p>
  <div>
    <span class="fs-badge badge-foundry">⬡ Foundry IQ</span>
    <span class="fs-badge badge-rai">🛡️ Responsible AI</span>
    <span class="fs-badge badge-enterprise">◆ Reasoning Agents</span>
    <span class="fs-badge badge-copilot">◈ GitHub Copilot</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Demo Mode Banner ──────────────────────────────────────────
st.markdown(
    """
<div class="demo-banner">
  <span style="font-size: 15px;">🟢</span>
  <div style="flex: 1;">
    <span style="color:#4ade80; font-weight:600; font-size:12px;
          letter-spacing:0.05em; text-transform:uppercase;">Demo Mode</span>
    <span style="color:#94a3b8; font-size:12px; margin-left:10px;">
      Running fully offline · All employee data is synthetic ·
      Foundry IQ Ethics KG pre-loaded · No credentials required
    </span>
  </div>
  <span style="font-family: 'JetBrains Mono', monospace; color:#475569; font-size:11px;">
    v1.0 · 4 agents · 6 ethical rules · 6 mitigations
  </span>
</div>
""",
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ Sentinel Control")
    st.markdown("---")
    st.markdown("#### Audit Target")
    st.info(
        "**Enterprise Learning Agent v1.0**\n\n"
        "Producing training recommendations for "
        "12 synthetic employees across Engineering "
        "and Product departments."
    )
    st.markdown("#### Run Audit")
    run_btn = st.button(
        "▶️ Run Full Sentinel Pipeline",
        type="primary",
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("#### Knowledge Source")
    st.markdown(
        """
<div style="font-size:12px; color:#94a3b8;">
⬡ <b style="color:#a78bfa">Foundry IQ Ethics KG</b><br>
• 5 ethical principles<br>
• 3 fairness metrics<br>
• 6 contextual rules<br>
• 6 mitigation strategies<br><br>
⚠️ All data is <b>synthetic</b> — for demo only.
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("#### Reasoning Patterns")
    st.markdown(
        """
<div style="font-size:11px; color:#64748b; line-height:1.7;">
<b style="color:#94a3b8;">Agent 1:</b> Statistical Audit<br>
<b style="color:#94a3b8;">Agent 2:</b> KG Traversal → Rule Match<br>
<b style="color:#94a3b8;">Agent 3:</b> Synthesis + Counterfactual<br>
</div>
""",
        unsafe_allow_html=True,
    )

# ── Main Content ──────────────────────────────────────────────
if run_btn:
    with st.spinner("Running 4-agent Responsible AI assurance pipeline..."):
        # ── Agent 0: ELA ──────────────────────────────────────
        t0 = time.time()
        ela_result = run_ela()
        ela_ms = round((time.time() - t0) * 1000)

        # ── Agent 1: Profiler ─────────────────────────────────
        t = time.time()
        profiler_result = run_profiler(ela_result)
        prof_ms = round((time.time() - t) * 1000)

        # ── Agent 2: Decision Audit (Foundry IQ) ──────────────
        t = time.time()
        audit_result = run_audit(profiler_result)
        audit_ms = round((time.time() - t) * 1000)

        # ── Agent 3: Transparency ─────────────────────────────
        t = time.time()
        trans_result = run_transparency(audit_result, profiler_result)
        trans_ms = round((time.time() - t) * 1000)

        total_ms = round((time.time() - t0) * 1000)

    # ── EXECUTIVE VERDICT ─────────────────────────────────────
    risk_class = "verdict-critical" if trans_result["risk_level"] == "CRITICAL" else (
        "verdict-high" if trans_result["risk_level"] in ["HIGH", "MODERATE"] else "verdict-low"
    )
    st.markdown(
        f"""
<div class="{risk_class}">
  <div style="font-size:11px; letter-spacing:2px; color:#94a3b8;
       text-transform:uppercase; margin-bottom:6px;">
    🛡️ Foundry Sentinel — Executive Verdict
  </div>
  <div style="font-size:16px; color:#e2e8f0; line-height:1.6;">
    {trans_result['executive_verdict']}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # ── Top-line Metrics ──────────────────────────────────────
    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    with col_a:
        st.metric("Risk Score", f"{trans_result['risk_score']}/100")
    with col_b:
        st.metric("Risk Level", trans_result["risk_level"])
    with col_c:
        st.metric("Violations", len(audit_result["violations"]))
    with col_d:
        st.metric("Decisions Audited", ela_result["total_decisions"])
    with col_e:
        st.metric("Pipeline Time", f"{total_ms}ms")

    st.divider()

    # ── Agent 1: Bias Profile Report ──────────────────────────
    st.markdown("### 📊 Agent 1 — Data Profiler")
    st.caption(
        "**Reasoning pattern:** Statistical Audit — "
        "Compute → Compare → Flag"
    )

    col1, col2 = st.columns(2)
    ds = profiler_result["disparity_summary"]
    with col1:
        st.markdown("**Gender Disparity — High-Potential Track**")
        gd = ds["gender_in_high_potential"]
        for grp, info in gd["rates"].items():
            st.write(
                f"• **{grp}**: {info['rate_pct']}% "
                f"({info['count']}/{info['total']})"
            )
        st.error(
            f"⚠ Disparity: **{gd['disparity_pct']}%** — "
            f"threshold: 20%"
        )

    with col2:
        st.markdown("**Age Disparity — Negative-Signal Track**")
        ad = ds["age_in_negative_signal"]
        for grp, info in ad["rates"].items():
            st.write(
                f"• **{grp}**: {info['rate_pct']}% "
                f"({info['count']}/{info['total']})"
            )
        st.error(
            f"⚠ Disparity: **{ad['disparity_pct']}%** — "
            f"threshold: 20%"
        )

    st.markdown("**🔍 Findings**")
    for f in profiler_result["findings"]:
        sev_color = (
            "🔴" if f["severity"] == "critical" else "🟡"
        )
        st.write(f"{sev_color} **{f['id']}** — {f['type']} (severity: {f['severity']})")

    with st.expander("View Agent 1 Reasoning"):
        st.info(profiler_result["reasoning"])
        st.caption(f"📎 {profiler_result['citation']}")
        st.caption(f"⏱️ Completed in {prof_ms}ms")

    st.divider()

    # ── Agent 2: Decision Audit Report ────────────────────────
    st.markdown("### ⚖️ Agent 2 — Decision Audit Agent")
    st.caption(
        "**Foundry IQ Integration:** Queries ethical knowledge graph · "
        "Maps findings to principles · Computes risk score"
    )

    col_x, col_y, col_z = st.columns(3)
    with col_x:
        st.metric(
            "KG Rules Evaluated",
            audit_result["rules_evaluated"],
        )
    with col_y:
        st.metric(
            "Violations Detected",
            audit_result["violations_detected"],
        )
    with col_z:
        st.metric(
            "Principles Touched",
            len(audit_result["principles_touched"]),
        )

    st.markdown("**📜 Foundry IQ Ethical Rule Violations**")
    for v in audit_result["violations"]:
        sev_icon = {
            "critical": "🔴",
            "high": "🟡",
            "medium": "🟠",
            "low": "🟢",
        }.get(v["severity"], "⚪")

        with st.expander(
            f"{sev_icon} **{v['rule_id']}** — "
            f"Severity: {v['severity'].upper()} · "
            f"Principles: {', '.join(p['id'] for p in v['principles_violated'])}"
        ):
            st.markdown(f"**Rule:** {v['rule_text']}")
            st.markdown("**Principles Violated:**")
            for p in v["principles_violated"]:
                st.markdown(
                    f"<span class='principle-tag'>{p['id']} · "
                    f"{p['name']}</span>",
                    unsafe_allow_html=True,
                )
                st.caption(p["definition"])

    with st.expander("View Agent 2 Reasoning"):
        st.info(audit_result["reasoning"])
        st.caption(f"📎 {audit_result['citation']}")
        st.caption(f"⏱️ Completed in {audit_ms}ms")

    st.divider()

    # ── Agent 3: Responsible AI Summary ───────────────────────
    st.markdown("### 📝 Agent 3 — Transparency Agent")
    st.caption(
        "**Reasoning pattern:** Synthesis → Counterfactual → "
        "Prioritised Action Plan"
    )

    st.markdown("#### 🎯 Findings for Stakeholders")
    for h in trans_result["humanised_findings"]:
        with st.expander(f"📌 {h['headline']} (severity: {h['severity']})"):
            st.markdown(f"**Plain language:** {h['plain_language']}")
            st.markdown(f"**Business impact:** {h['business_impact']}")
            st.markdown(f"**Principles violated:** {h['principles_violated']}")

    st.markdown("#### 🔄 Counterfactual 'What-If' Scenarios")
    for i, cf in enumerate(trans_result["counterfactual_scenarios"], 1):
        st.markdown(
            f"""
<div class="counterfactual-box">
  <div style="font-size:11px; color:#a78bfa; font-weight:600;
       letter-spacing:1px; margin-bottom:6px;">
    SCENARIO {i} · {cf['violation']}
  </div>
  <div style="color:#cbd5e1; font-size:13px; margin-bottom:8px;">
    <b>Observed:</b> {cf['scenario']}
  </div>
  <div style="color:#a78bfa; font-size:13px;">
    <b>What if:</b> {cf['what_if']}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("#### 📋 Prioritised Action Plan")
    for a in trans_result["prioritised_action_plan"]:
        eff_color = {
            "low": "#4ade80",
            "medium": "#fbbf24",
            "high": "#ef4444",
        }.get(a["effort"], "#94a3b8")
        st.markdown(
            f"""
<div class="action-step">
  <span class="action-priority">P{a['priority']}</span>
  <b style="color:#e2e8f0;">{a['action']}</b>
  <span style="float:right; font-size:11px; color:{eff_color};
        font-weight:600; text-transform:uppercase;">
    {a['effort']} effort
  </span>
  <div style="color:#94a3b8; font-size:12px; margin-top:6px;">
    {a['description']}
  </div>
  <div style="color:#64748b; font-size:11px; margin-top:4px;
       font-style:italic;">
    Tradeoff: {a['tradeoff']}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    if trans_result["human_review_required"]:
        st.warning(
            "🛑 **Human review required.** This system should not be deployed "
            "in its current form without HR + Compliance sign-off."
        )

    if trans_result["affected_employees"]["high_severity"]:
        st.markdown("#### 👥 Employees Requiring Immediate Review")
        for eid in trans_result["affected_employees"]["high_severity"]:
            emp = get_employee(eid)
            st.write(
                f"• **{eid}** — {emp.get('name', 'Unknown')} "
                f"({emp.get('department', '?')}, "
                f"perf: {emp.get('performance_score', '?')})"
            )

    with st.expander("View Agent 3 Reasoning"):
        st.info(trans_result["reasoning"])
        st.caption(f"📎 {trans_result['citation']}")
        st.caption(f"⏱️ Completed in {trans_ms}ms")

    # ── Pipeline Trace ────────────────────────────────────────
    st.divider()
    st.markdown("### 🔍 Pipeline Trace — Full Auditability")
    st.caption(
        f"Total pipeline time: **{total_ms}ms** · "
        f"4 agents · deterministic · synthetic data"
    )

    trace_cols = st.columns(4)
    trace_data = [
        ("Agent 0", "Enterprise Learning Agent", ela_ms, "12 decisions"),
        ("Agent 1", "Data Profiler", prof_ms, f"{len(profiler_result['findings'])} findings"),
        ("Agent 2", "Decision Audit (Foundry IQ)", audit_ms, f"{audit_result['violations_detected']} violations"),
        ("Agent 3", "Transparency", trans_ms, f"{len(trans_result['prioritised_action_plan'])} actions"),
    ]
    for col, (name, full, ms, out) in zip(trace_cols, trace_data):
        with col:
            st.markdown(
                f"""
<div style="background:rgba(20,20,32,0.6);
     border:1px solid rgba(99,102,241,0.15);
     border-radius:10px; padding:14px;">
  <div style="font-size:10px; color:#94a3b8;
       letter-spacing:1px; text-transform:uppercase;">{name}</div>
  <div style="font-size:13px; color:#e2e8f0;
       font-weight:600; margin:4px 0;">{full}</div>
  <div style="font-size:11px; color:#64748b;">{out}</div>
  <div style="font-size:11px; color:#a78bfa;
       font-family:'JetBrains Mono', monospace; margin-top:4px;">
    {ms}ms
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

else:
    st.info(
        "👈 Click **▶️ Run Full Sentinel Pipeline** to audit the "
        "Enterprise Learning Agent against Foundry IQ ethical principles."
    )

    st.markdown(
        """
### What Foundry Sentinel Does

Foundry Sentinel is a multi-agent system that audits other AI agents for
**bias, fairness, and ethical compliance** before their decisions affect
real employees. It uses **Microsoft Foundry IQ** as an active ethical
knowledge graph — not just document retrieval, but principle-based reasoning.

#### The 4-Agent Pipeline

| Agent | Role | Reasoning Pattern |
|---|---|---|
| **Agent 0: ELA** | The system under audit — produces (biased) training recommendations | Rule-based |
| **Agent 1: Data Profiler** | Statistical bias detection across protected attributes | Statistical Audit |
| **Agent 2: Decision Audit** | Foundry IQ knowledge graph traversal → ethical rule matching | KG Traversal → Rule Match |
| **Agent 3: Transparency** | Synthesises findings into stakeholder-ready Responsible AI Summary | Synthesis → Counterfactual |

#### Foundry IQ as the Creative Nucleus

The Foundry IQ Ethics KG contains:
- **5 ethical principles** (Non-Discrimination, Employee Growth Equity, Algorithmic Transparency, Human Oversight, Age Inclusivity)
- **3 fairness metrics** (Demographic Parity, Equal Opportunity, Performance-Adjusted Disparity)
- **6 contextual rules** mapping findings → principle violations
- **6 mitigation strategies** with effort/tradeoff metadata

The Decision Audit Agent **queries and traverses this graph** to perform
active ethical reasoning — moving Foundry IQ beyond document retrieval
into principle-based inference.

#### Try It

Click the button in the sidebar to run the full audit pipeline.
The system will surface a CRITICAL violation pattern in the demo data —
exactly what Foundry Sentinel is designed to catch.
"""
    )

# ── Footer ────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
<div style="display:flex; justify-content:space-between;
     align-items:center; padding:12px 0;
     font-size:11px; color:#475569;">
  <div>🛡️ FOUNDRY SENTINEL · MICROSOFT AGENTS LEAGUE 2026 · REASONING AGENTS TRACK</div>
  <div>Built with GitHub Copilot · All data synthetic · For demonstration only</div>
</div>
""",
    unsafe_allow_html=True,
)
