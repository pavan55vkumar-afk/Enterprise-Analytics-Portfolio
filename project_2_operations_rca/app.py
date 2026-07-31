"""
app.py -- SLA Incident Responder (Streamlit dashboard)

WHAT THIS FILE DOES:
1. Reads tickets.csv (support tickets database)
2. Filters to at-risk tickets (75%+ SLA used)
3. For each ticket: offers two actions:
   a) Send first response (instant, fixed template, shows preview)
   b) Generate AI-drafted resolution update (after human works the ticket)
"""

import streamlit as st
import pandas as pd
from google import genai
from datetime import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ACCENT = "#2563EB"
ALERT = "#EA580C"
DARK = "#1E293B"
MUTED = "#64748B"
BG = "#FAFAFA"
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.facecolor": BG,
    "figure.facecolor": "white",
    "axes.edgecolor": "#CBD5E1",
    "axes.labelcolor": DARK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "text.color": DARK,
    "legend.frameon": False,
})

FIRST_RESPONSE_TEMPLATE = """Hi there,

Thank you for reaching out to us. We wanted to confirm that we've received your request and it's currently being worked on by our support team.

We understand your time is valuable, and we're actively looking into this. Someone from our team will follow up with you as soon as there's an update.

We appreciate your patience in the meantime.

Thank you,
Support Team"""


def send_real_email(sender, app_password, recipient, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, app_password)
        server.sendmail(sender, recipient, msg.as_string())


st.set_page_config(page_title="SLA Incident Responder", layout="wide", page_icon="🚨")

# --- light custom styling ---
st.markdown("""
<style>
    .main > div { padding-top: 1.2rem; }
    .ticket-card {
        border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;
        border-left: 5px solid #ccc; background: #fafafa; cursor: pointer;
    }
    .badge {
        display: inline-block; padding: 2px 9px; border-radius: 999px;
        font-size: 11px; font-weight: 700; color: white; margin-left: 6px;
    }
    .badge-breached { background: #d32f2f; }
    .badge-critical { background: #f57c00; }
    .badge-watch { background: #fbc02d; color: #4a3b00; }
    .kpi-box {
        border-radius: 10px; padding: 14px 10px; text-align: center;
        border: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚨 SLA Incident Responder")
st.caption("Auto-send fixed first response + AI-drafted resolution updates")

# --- session state ---
if "selected_ticket_id" not in st.session_state:
    st.session_state.selected_ticket_id = None
if "generated_draft" not in st.session_state:
    st.session_state.generated_draft = None
if "approval_history" not in st.session_state:
    st.session_state.approval_history = []
if "first_response_sent" not in st.session_state:
    st.session_state.first_response_sent = set()
if "show_first_response_preview" not in st.session_state:
    st.session_state.show_first_response_preview = {}

# --- STEP 1: read the database (generate it first if it doesn't exist yet) ---
def generate_tickets_if_missing():
    import os
    if os.path.exists("tickets.csv"):
        return
    import numpy as np
    from datetime import timedelta
    import random

    np.random.seed(42)
    random.seed(42)
    num_tickets = 1000

    ticket_ids = [f"TKT-{i+1:05d}" for i in range(num_tickets)]
    priorities = np.random.choice(['Low', 'Medium', 'High'], num_tickets, p=[0.3, 0.5, 0.2])
    categories = np.random.choice(
        ['Billing', 'Technical Support', 'Account Access', 'Delivery Issue'],
        num_tickets, p=[0.3, 0.3, 0.2, 0.2]
    )
    sla_map = {
        ('Billing', 'High'): 12, ('Billing', 'Medium'): 24, ('Billing', 'Low'): 48,
        ('Technical Support', 'High'): 8, ('Technical Support', 'Medium'): 24, ('Technical Support', 'Low'): 48,
        ('Account Access', 'High'): 4, ('Account Access', 'Medium'): 12, ('Account Access', 'Low'): 24,
        ('Delivery Issue', 'High'): 24, ('Delivery Issue', 'Medium'): 48, ('Delivery Issue', 'Low'): 72,
    }
    sla_limits = [sla_map.get((cat, pri), 24) for cat, pri in zip(categories, priorities)]

    now = datetime.now()
    created_ats = [now - timedelta(hours=random.randint(1, 2160)) for _ in range(num_tickets)]
    statuses = np.random.choice(['Open', 'In Progress', 'Resolved'], num_tickets, p=[0.3, 0.4, 0.3])
    elapsed_hours = [round(random.uniform(0, sla_limits[i] * 1.5), 1) for i in range(num_tickets)]

    resolved_ats = []
    for i, status in enumerate(statuses):
        if status == 'Resolved':
            resolved_ats.append((created_ats[i] + timedelta(hours=elapsed_hours[i])).strftime('%Y-%m-%d %H:%M:%S'))
        else:
            resolved_ats.append(None)

    sla_breaches = [1 if elapsed_hours[i] > sla_limits[i] else 0 for i in range(num_tickets)]
    csat_scores = [round(random.uniform(1.0, 5.0), 1) if s == 'Resolved' else None for s in statuses]

    out = pd.DataFrame({
        'ticket_id': ticket_ids,
        'created_at': [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in created_ats],
        'resolved_at': resolved_ats,
        'status': statuses,
        'priority': priorities,
        'category': categories,
        'sla_limit_hours': sla_limits,
        'elapsed_hours': elapsed_hours,
        'sla_breach': sla_breaches,
        'csat_score': csat_scores,
    })
    out.to_csv("tickets.csv", index=False)


@st.cache_data
def load_tickets():
    generate_tickets_if_missing()
    df = pd.read_csv("tickets.csv")
    df["sla_percent"] = (df["elapsed_hours"] / df["sla_limit_hours"] * 100).round(1)
    return df

df = load_tickets()

# --- sidebar controls ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    model_choice = st.selectbox(
        "Model",
        ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-flash-latest"],
        index=2,
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max tokens", 100, 500, 350, 50)
    threshold = st.slider("SLA warning threshold (%)", 50, 100, 75)

    st.divider()
    st.header("📧 Real email sending")
    st.caption("Uses Gmail SMTP with an App Password (not your normal Gmail password).")
    sender_email = st.text_input("Sender Gmail address", value="pavanwork111@gmail.com")
    sender_app_password = st.text_input("Gmail App Password", type="password")
    demo_recipient = st.text_input("Send to (recipient email)", value="pavanwork111@gmail.com")

# --- STEP 2 & 3: filter to warning tickets ---
warning_df = df[(df["sla_percent"] >= threshold) & (df["status"] != "Resolved")].copy()
warning_df = warning_df.sort_values("sla_percent", ascending=False)
breached_now = int((warning_df["sla_percent"] >= 100).sum())
critical_now = int(((warning_df["sla_percent"] >= 90) & (warning_df["sla_percent"] < 100)).sum())
compliance_rate = round(100 - (df["sla_breach"].sum() / len(df) * 100), 1)

# --- KPI header ---
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"<div class='kpi-box'><h2 style='margin:0'>{len(df)}</h2>"
                f"<span style='color:#666'>Total tickets</span></div>", unsafe_allow_html=True)
with k2:
    st.markdown(f"<div class='kpi-box' style='border-color:#fbc02d'><h2 style='margin:0;color:#b8860b'>{len(warning_df)}</h2>"
                f"<span style='color:#666'>At risk (≥{threshold}% SLA)</span></div>", unsafe_allow_html=True)
with k3:
    st.markdown(f"<div class='kpi-box' style='border-color:#d32f2f'><h2 style='margin:0;color:#d32f2f'>{breached_now}</h2>"
                f"<span style='color:#666'>Already breached</span></div>", unsafe_allow_html=True)
with k4:
    st.markdown(f"<div class='kpi-box' style='border-color:#2e7d32'><h2 style='margin:0;color:#2e7d32'>{compliance_rate}%</h2>"
                f"<span style='color:#666'>Overall SLA compliance</span></div>", unsafe_allow_html=True)

def severity(pct):
    if pct >= 100:
        return "#d32f2f", "🔴 BREACHED", "badge-breached"
    elif pct >= 90:
        return "#f57c00", "🟠 CRITICAL", "badge-critical"
    else:
        return "#fbc02d", "🟡 WATCH", "badge-watch"

st.write("")
tab_action, tab_insights = st.tabs(["🎫 Ticket Action Center", "📊 Insights & Analytics"])

with tab_action:
    col_list, col_detail = st.columns([1, 1.4])

    with col_list:
        st.subheader("Tickets at risk")
        st.caption(f"Sorted worst-first · {breached_now} breached · {critical_now} critical")

        if warning_df.empty:
            st.success("No tickets currently at risk. 🎉")
        else:
            for _, row in warning_df.head(30).iterrows():
                color, label, badge_class = severity(row["sla_percent"])
                is_selected = st.session_state.selected_ticket_id == row["ticket_id"]
                border = "3px solid #1a1a1a" if is_selected else f"5px solid {color}"

                st.markdown(
                    f"""<div class="ticket-card" style="border-left:{border}">
                        <b>{row['ticket_id']}</b>
                        <span class="badge {badge_class}">{label}</span><br>
                        <span style="color:#555;font-size:13px">{row['category']} · {row['priority']} priority</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
                st.progress(min(int(row["sla_percent"]), 100) / 100,
                            text=f"{row['sla_percent']:.0f}% of SLA window used")

                already_sent = row["ticket_id"] in st.session_state.first_response_sent
                btn_col1, btn_col2 = st.columns(2)

                if btn_col1.button("Select this ticket →", key=f"btn_{row['ticket_id']}", width="stretch"):
                    st.session_state.selected_ticket_id = row["ticket_id"]
                    st.session_state.generated_draft = None

                if already_sent:
                    btn_col2.button("✅ First response sent", key=f"sent_{row['ticket_id']}",
                                     width="stretch", disabled=True)
                else:
                    if btn_col2.button("📧 Send first response", key=f"auto_{row['ticket_id']}", width="stretch"):
                        st.session_state.show_first_response_preview[row["ticket_id"]] = True
                        st.rerun()

                # Show preview modal if triggered
                if st.session_state.show_first_response_preview.get(row["ticket_id"], False):
                    st.divider()
                    st.write("**Email preview:**")
                    st.text_area("First response template:", value=FIRST_RESPONSE_TEMPLATE, height=180, disabled=True)
                    col_a, col_b = st.columns(2)
                    if col_a.button("✅ Confirm & send", key=f"confirm_{row['ticket_id']}", width="stretch"):
                        if not sender_email or not sender_app_password or not demo_recipient:
                            st.error("Fill in sender email, App Password, and recipient in the sidebar first.")
                        else:
                            try:
                                send_real_email(
                                    sender_email, sender_app_password, demo_recipient,
                                    subject=f"We've received your request — Ticket {row['ticket_id']}",
                                    body=FIRST_RESPONSE_TEMPLATE,
                                )
                                st.session_state.first_response_sent.add(row["ticket_id"])
                                st.session_state.approval_history.append({
                                    "time": datetime.now().strftime("%H:%M:%S"),
                                    "ticket_id": row["ticket_id"],
                                    "type": "first_response",
                                    "draft": FIRST_RESPONSE_TEMPLATE,
                                })
                                st.session_state.show_first_response_preview[row["ticket_id"]] = False
                                st.success(f"Email actually sent to {demo_recipient} for {row['ticket_id']}.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Email send failed: {e}")
                    if col_b.button("❌ Cancel", key=f"cancel_{row['ticket_id']}", width="stretch"):
                        st.session_state.show_first_response_preview[row["ticket_id"]] = False
                        st.rerun()
                    st.divider()

                st.write("")

    with col_detail:
        st.subheader("Ticket detail & AI-drafted resolution update")

        if st.session_state.selected_ticket_id is None:
            st.info("👈 Click 'Select this ticket' on the left to see details and generate an update.")
        else:
            ticket = df[df["ticket_id"] == st.session_state.selected_ticket_id].iloc[0]
            color, label, _ = severity(ticket["sla_percent"])

            st.markdown(f"### {ticket['ticket_id']} &nbsp; <span style='color:{color}'>{label}</span>",
                        unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            c1.metric("Priority", ticket["priority"])
            c2.metric("Category", ticket["category"])
            c3.metric("SLA used", f"{ticket['sla_percent']:.0f}%")

            st.progress(min(int(ticket["sla_percent"]), 100) / 100)
            st.caption(f"Created: {ticket['created_at']}  ·  Elapsed: {ticket['elapsed_hours']:.1f}h "
                       f"of {ticket['sla_limit_hours']:.0f}h allowed")

            st.divider()

            # --- Generate AI draft for resolution update ---
            if st.button("✨ Generate resolution update", type="primary"):
                if not api_key:
                    st.error("Enter your Gemini API key in the sidebar first.")
                else:
                    with st.spinner("Gemini is drafting a response..."):
                        try:
                            client = genai.Client(api_key=api_key)
                            prompt = (
                                "You are a support manager writing a short update email to a customer "
                                "after working on their support ticket. This is NOT the first acknowledgment — "
                                "we already sent that. This is a status update as you actually resolve the issue.\n\n"
                                f"Ticket ID: {ticket['ticket_id']}\n"
                                f"Category: {ticket['category']}\n"
                                f"Priority: {ticket['priority']}\n"
                                f"Elapsed: {ticket['elapsed_hours']:.1f} of {ticket['sla_limit_hours']:.0f} hours "
                                f"({ticket['sla_percent']:.0f}% used)\n\n"
                                "Write the ACTUAL EMAIL TEXT ONLY -- start directly with a greeting like "
                                "'Hi there,' and end with a sign-off. Do NOT output a plan, outline, "
                                "bullet points, headers, or labels. Just the finished email a manager would copy and paste, "
                                "under 150 words. Sound professional but warm. Suggest next steps or closure if appropriate."
                            )
                            resp = client.models.generate_content(
                                model=model_choice,
                                contents=prompt,
                                config={
                                    "temperature": temperature,
                                    "max_output_tokens": max_tokens,
                                    "thinking_config": {"thinking_budget": 0},
                                },
                            )
                            st.session_state.generated_draft = resp.text
                        except Exception as e:
                            st.error(f"API error: {e}")

            # --- show draft, let human edit, log on approve ---
            if st.session_state.generated_draft:
                draft = st.text_area("📝 Draft resolution update (edit before approving):",
                                      value=st.session_state.generated_draft, height=180)
                b1, b2 = st.columns(2)
                if b1.button("✅ Approve & queue for sending", type="primary"):
                    st.session_state.approval_history.append({
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "ticket_id": ticket["ticket_id"],
                        "type": "resolution_update",
                        "draft": draft,
                    })
                    st.success(f"Resolution update approved for {ticket['ticket_id']}.")
                    st.session_state.generated_draft = None
                if b2.button("❌ Reject / discard draft"):
                    st.session_state.generated_draft = None
                    st.warning("Draft discarded.")

            if st.session_state.approval_history:
                st.divider()
                st.subheader("📋 Approved this session")
                for rec in reversed(st.session_state.approval_history[-5:]):
                    type_label = "First response" if rec["type"] == "first_response" else "Resolution update"
                    with st.expander(f"{rec['ticket_id']} ({type_label}) — {rec['time']}"):
                        st.text_area("", value=rec["draft"], height=140, disabled=True)

with tab_insights:
    st.subheader("Where SLA breaches actually come from")
    st.caption("Same underlying ticket data, aggregated to show the pattern instead of ticket-by-ticket detail.")

    resolved_df = df[df["status"] == "Resolved"].copy()

    if resolved_df.empty:
        st.info("No resolved tickets yet in this dataset to analyze.")
    else:
        cat_df = resolved_df.groupby("category").agg(
            volume=("ticket_id", "count"),
            avg_handling_time=("elapsed_hours", "mean"),
            sla_target=("sla_limit_hours", "first"),
            breach_count=("sla_breach", "sum"),
            avg_csat=("csat_score", "mean"),
        ).reset_index()
        cat_df["breach_rate_pct"] = (cat_df["breach_count"] / cat_df["volume"] * 100).round(1)

        bottleneck = cat_df.loc[cat_df["breach_rate_pct"].idxmax()]
        st.markdown(
            f"**Biggest bottleneck:** `{bottleneck['category']}` tickets breach {bottleneck['breach_rate_pct']:.0f}% "
            f"of the time — average handling time is {bottleneck['avg_handling_time']:.1f}h against a "
            f"{bottleneck['sla_target']:.0f}h target."
        )

        chart1, chart2 = st.columns(2)

        with chart1:
            pareto = cat_df.sort_values("breach_count", ascending=False)
            pareto["cumulative_pct"] = (pareto["breach_count"].cumsum() / pareto["breach_count"].sum() * 100)

            fig, ax1 = plt.subplots(figsize=(5.5, 4))
            ax1.bar(pareto["category"], pareto["breach_count"], color=ACCENT, alpha=0.85, width=0.55)
            ax1.set_ylabel("SLA breaches", fontweight="bold")
            ax1.set_xticks(range(len(pareto)))
            ax1.set_xticklabels(pareto["category"], rotation=20, ha="right")

            ax2 = ax1.twinx()
            ax2.plot(pareto["category"], pareto["cumulative_pct"], color=ALERT, marker="D", ms=5, linewidth=1.5)
            ax2.set_ylabel("Cumulative %", fontweight="bold")
            ax2.set_ylim(0, 110)

            ax1.set_title("SLA breaches by category", fontweight="bold", pad=12)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with chart2:
            csat_pivot = resolved_df.groupby(["category", "sla_breach"])["csat_score"].mean().unstack()
            csat_pivot.columns = ["SLA Met", "SLA Breached"] if 0 in csat_pivot.columns and 1 in csat_pivot.columns else csat_pivot.columns

            fig, ax = plt.subplots(figsize=(5.5, 4))
            x = range(len(csat_pivot))
            width = 0.35
            if "SLA Met" in csat_pivot.columns:
                ax.bar([i - width/2 for i in x], csat_pivot["SLA Met"], width, label="SLA Met", color=ACCENT)
            if "SLA Breached" in csat_pivot.columns:
                ax.bar([i + width/2 for i in x], csat_pivot["SLA Breached"], width, label="SLA Breached", color=ALERT)
            ax.set_xticks(list(x))
            ax.set_xticklabels(csat_pivot.index, rotation=20, ha="right")
            ax.set_ylabel("Avg CSAT (1-5)", fontweight="bold")
            ax.set_ylim(0, 5.5)
            ax.set_title("Customer satisfaction: met vs breached", fontweight="bold", pad=12)
            ax.legend()
            ax.grid(axis="y", linestyle=":", alpha=0.5, color="#CBD5E1")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        st.write("")
        st.markdown("**Ticket volume and SLA outcome over time**")

        df_trend = df.copy()
        df_trend["created_dt"] = pd.to_datetime(df_trend["created_at"])
        df_trend["week"] = df_trend["created_dt"].dt.to_period("W").astype(str)

        def outcome(row):
            if row["status"] != "Resolved":
                return "Open / In Progress"
            return "Resolved (Breached)" if row["sla_breach"] == 1 else "Resolved (Met)"

        df_trend["outcome"] = df_trend.apply(outcome, axis=1)
        weekly = df_trend.groupby(["week", "outcome"]).size().unstack(fill_value=0)
        cols_order = [c for c in ["Resolved (Met)", "Resolved (Breached)", "Open / In Progress"] if c in weekly.columns]
        weekly = weekly[cols_order]
        colors = {"Resolved (Met)": ACCENT, "Resolved (Breached)": ALERT, "Open / In Progress": "#CBD5E1"}

        fig, ax = plt.subplots(figsize=(11, 4))
        weekly.plot(kind="bar", stacked=True, color=[colors[c] for c in weekly.columns], ax=ax, width=0.65)
        ax.set_ylabel("Tickets", fontweight="bold")
        ax.set_xlabel("Week", fontweight="bold")
        ax.set_title("Ticket volume by week and outcome", fontweight="bold", pad=12)
        ax.legend(loc="upper left")
        ax.grid(axis="y", linestyle=":", alpha=0.5, color="#CBD5E1")
        plt.xticks(rotation=30, ha="right")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        st.write("")
        st.markdown("**Category breakdown**")
        display_df = cat_df[["category", "volume", "avg_handling_time", "sla_target", "breach_rate_pct", "avg_csat"]].copy()
        display_df.columns = ["Category", "Volume", "Avg handling (h)", "SLA target (h)", "Breach rate (%)", "Avg CSAT"]
        display_df = display_df.round(1)
        st.dataframe(display_df, width="stretch", hide_index=True)
