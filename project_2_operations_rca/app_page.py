import streamlit as st
import pandas as pd
from google import genai
from datetime import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
import plotly.express as px
import plotly.graph_objects as go

INDIGO = "#4F46E5"
TEAL = "#0D9488"
ORANGE = "#EA580C"
RED = "#DC2626"
SLATE = "#94A3B8"

PLOTLY_LAYOUT = dict(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(248,250,255,0.7)",
    font=dict(color="#334155", size=12),
    margin=dict(l=10, r=10, t=48, b=10),
)

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


def severity(pct):
    if pct >= 100:
        return RED, "🔴 BREACHED", "badge-breached"
    elif pct >= 90:
        return ORANGE, "🟠 CRITICAL", "badge-critical"
    else:
        return "#D97706", "🟡 WATCH", "badge-watch"


def show_page():
    # --- session state (must be initialized before anything reads it) ---
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

    st.markdown("""
    <div class="hero" style="padding:24px 30px;">
        <h1 style="font-size:1.6rem;">🚨 SLA Incident Responder</h1>
        <p>Reactive operations: catch tickets <i>before</i> they breach — template first response, AI-drafted updates, human approval.</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        df = load_tickets()
    except Exception:
        st.warning("Ticket data couldn't be loaded. Refreshing usually resolves this — the dataset regenerates automatically.")
        return

    api_key = st.session_state.get("gemini_key", "")
    model_choice = st.session_state.get("gemini_model", "gemini-flash-latest")
    temperature = st.session_state.get("temperature", 0.3)
    max_tokens = st.session_state.get("max_tokens", 450)
    threshold = st.session_state.get("threshold", 75)
    use_claude = st.session_state.get("use_claude", False)
    claude_key = st.session_state.get("claude_key", "")
    claude_model = st.session_state.get("claude_model", "claude-haiku-4-5-20251001")

    sender_email = st.session_state.get("sender_email", "pavanwork111@gmail.com")
    sender_app_password = st.session_state.get("sender_app_password", "")
    demo_recipient = st.session_state.get("demo_recipient", "pavanwork111@gmail.com")

    warning_df = df[(df["sla_percent"] >= threshold) & (df["status"] != "Resolved")].copy()
    warning_df = warning_df.sort_values("sla_percent", ascending=False)
    breached_now = int((warning_df["sla_percent"] >= 100).sum())
    critical_now = int(((warning_df["sla_percent"] >= 90) & (warning_df["sla_percent"] < 100)).sum())
    compliance_rate = round(100 - (df["sla_breach"].sum() / len(df) * 100), 1)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"<div class='kpi-card'><h2>{len(df)}</h2>"
                    f"<span>Total tickets</span></div>", unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='kpi-card' style='border-top-color:#D97706'><h2 style='color:#D97706'>{len(warning_df)}</h2>"
                    f"<span>At risk (≥{threshold}% SLA)</span></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='kpi-card' style='border-top-color:{RED}'><h2 style='color:{RED}'>{breached_now}</h2>"
                    f"<span>Already breached</span></div>", unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div class='kpi-card' style='border-top-color:{TEAL}'><h2 style='color:{TEAL}'>{compliance_rate}%</h2>"
                    f"<span>Overall SLA compliance</span></div>", unsafe_allow_html=True)

    st.write("")
    tab_action, tab_insights = st.tabs(["🎫 Ticket Action Center", "📊 Insights & Analytics"])

    with tab_action:
        col_list, col_detail = st.columns([1, 1.4])

        with col_list:
            st.markdown("#### Tickets at risk")
            st.caption(f"Sorted worst-first · {breached_now} breached · {critical_now} critical")

            if warning_df.empty:
                st.success("No tickets currently at risk. 🎉")
            else:
                for _, row in warning_df.head(30).iterrows():
                    color, label, badge_class = severity(row["sla_percent"])
                    is_selected = st.session_state.selected_ticket_id == row["ticket_id"]
                    border = f"5px solid {INDIGO}" if is_selected else f"5px solid {color}"

                    st.markdown(
                        f"""<div class="ticket-card" style="border-left:{border}">
                            <b style="color:#1E293B">{row['ticket_id']}</b>
                            <span class="badge {badge_class}">{label}</span><br>
                            <span style="color:#64748B;font-size:13px">{row['category']} · {row['priority']} priority</span>
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

                    if st.session_state.show_first_response_preview.get(row["ticket_id"], False):
                        st.divider()
                        st.write("**Email preview:**")
                        st.text_area("First response template:", value=FIRST_RESPONSE_TEMPLATE, height=180,
                                     disabled=True, key=f"prev_{row['ticket_id']}")
                        col_a, col_b = st.columns(2)
                        if col_a.button("✅ Confirm & send", key=f"confirm_{row['ticket_id']}", width="stretch"):
                            if not sender_email or not sender_app_password or not demo_recipient:
                                st.warning("Open **📧 Email (SMTP) Settings** in the sidebar and fill in the sender, App Password, and recipient first.")
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
                                    st.toast(f"📧 Email sent to {demo_recipient}", icon="✅")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Email send failed — check the App Password and sender address. ({e})")
                        if col_b.button("❌ Cancel", key=f"cancel_{row['ticket_id']}", width="stretch"):
                            st.session_state.show_first_response_preview[row["ticket_id"]] = False
                            st.rerun()
                        st.divider()

                    st.write("")

        with col_detail:
            st.markdown("#### Ticket detail & AI-drafted resolution update")

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

                if st.button("✨ Generate resolution update", type="primary"):
                    if use_claude and not claude_key:
                        st.warning("Open **⚙️ Advanced Settings** in the sidebar and add your Claude API key first.")
                    elif not use_claude and not api_key:
                        st.warning("Open **⚙️ Advanced Settings** in the sidebar and add your Gemini API key first.")
                    else:
                        with st.spinner("The model is drafting a response..."):
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
                            try:
                                if use_claude:
                                    import anthropic
                                    client = anthropic.Anthropic(api_key=claude_key)
                                    message = client.messages.create(
                                        model=claude_model,
                                        max_tokens=max_tokens,
                                        temperature=temperature,
                                        messages=[{"role": "user", "content": prompt}],
                                    )
                                    st.session_state.generated_draft = message.content[0].text
                                else:
                                    client = genai.Client(api_key=api_key)
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
                                st.toast("Draft ready for review", icon="📝")
                            except Exception as e:
                                st.error(f"The model call didn't go through — try a different model in Advanced Settings. ({e})")

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
                        st.toast(f"Resolution update approved for {ticket['ticket_id']}", icon="✅")
                        st.session_state.generated_draft = None
                    if b2.button("❌ Reject / discard draft"):
                        st.session_state.generated_draft = None
                        st.warning("Draft discarded.")

                if st.session_state.approval_history:
                    st.divider()
                    st.markdown("#### 📋 Approved this session")
                    for rec in reversed(st.session_state.approval_history[-5:]):
                        type_label = "First response" if rec["type"] == "first_response" else "Resolution update"
                        with st.expander(f"{rec['ticket_id']} ({type_label}) — {rec['time']}"):
                            st.text_area("", value=rec["draft"], height=140, disabled=True,
                                         key=f"hist_{rec['ticket_id']}_{rec['time']}")

    with tab_insights:
        st.markdown("#### Where SLA breaches actually come from")
        st.caption("Same underlying ticket data, aggregated to show the pattern instead of ticket-by-ticket detail.")

        resolved_df = df[df["status"] == "Resolved"].copy()

        if resolved_df.empty:
            st.info("No resolved tickets yet in this dataset to analyze.")
            return

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
            f"""<div class="content-card">
            <b style="color:#1E293B">Biggest bottleneck:</b>
            <span style="color:#475569"><code>{bottleneck['category']}</code> tickets breach
            {bottleneck['breach_rate_pct']:.0f}% of the time — average handling time is
            {bottleneck['avg_handling_time']:.1f}h against a {bottleneck['sla_target']:.0f}h target.</span>
            </div>""",
            unsafe_allow_html=True,
        )

        chart1, chart2 = st.columns(2)

        with chart1:
            pareto = cat_df.sort_values("breach_count", ascending=False).copy()
            pareto["cumulative_pct"] = (pareto["breach_count"].cumsum() / pareto["breach_count"].sum() * 100).round(1)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=pareto["category"], y=pareto["breach_count"],
                name="SLA breaches", marker_color=INDIGO, opacity=0.9,
            ))
            fig.add_trace(go.Scatter(
                x=pareto["category"], y=pareto["cumulative_pct"],
                name="Cumulative %", yaxis="y2",
                mode="lines+markers", line=dict(color=ORANGE, width=2),
                marker=dict(symbol="diamond", size=8),
            ))
            fig.update_layout(
                **PLOTLY_LAYOUT,
                title="SLA breaches by category (Pareto)",
                yaxis=dict(title="Breaches"),
                yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 110]),
                legend=dict(orientation="h", y=-0.25),
                height=380,
            )
            st.plotly_chart(fig, width="stretch")

        with chart2:
            csat = resolved_df.groupby(["category", "sla_breach"])["csat_score"].mean().reset_index()
            csat["outcome"] = csat["sla_breach"].map({0: "SLA Met", 1: "SLA Breached"})
            fig = px.bar(
                csat, x="category", y="csat_score", color="outcome", barmode="group",
                color_discrete_map={"SLA Met": INDIGO, "SLA Breached": ORANGE},
            )
            fig.update_layout(
                **PLOTLY_LAYOUT,
                title="Customer satisfaction: met vs breached",
                yaxis=dict(title="Avg CSAT (1–5)", range=[0, 5.5]),
                xaxis=dict(title=""),
                legend=dict(orientation="h", y=-0.25, title=""),
                height=380,
            )
            st.plotly_chart(fig, width="stretch")

        st.write("")
        df_trend = df.copy()
        df_trend["created_dt"] = pd.to_datetime(df_trend["created_at"])
        df_trend["week"] = df_trend["created_dt"].dt.to_period("W").astype(str)

        def outcome(row):
            if row["status"] != "Resolved":
                return "Open / In Progress"
            return "Resolved (Breached)" if row["sla_breach"] == 1 else "Resolved (Met)"

        df_trend["outcome"] = df_trend.apply(outcome, axis=1)
        weekly = df_trend.groupby(["week", "outcome"]).size().reset_index(name="tickets")

        fig = px.bar(
            weekly, x="week", y="tickets", color="outcome",
            color_discrete_map={
                "Resolved (Met)": INDIGO,
                "Resolved (Breached)": ORANGE,
                "Open / In Progress": SLATE,
            },
        )
        fig.update_layout(
            **PLOTLY_LAYOUT,
            title="Ticket volume by week and outcome",
            xaxis=dict(title="Week", tickangle=-30),
            yaxis=dict(title="Tickets"),
            legend=dict(orientation="h", y=-0.35, title=""),
            height=400,
            barmode="stack",
        )
        st.plotly_chart(fig, width="stretch")

        st.write("")
        st.markdown("#### Category breakdown")
        display_df = cat_df[["category", "volume", "avg_handling_time", "sla_target", "breach_rate_pct", "avg_csat"]].copy()
        display_df.columns = ["Category", "Volume", "Avg handling (h)", "SLA target (h)", "Breach rate (%)", "Avg CSAT"]
        display_df = display_df.round(1)
        st.dataframe(display_df, width="stretch", hide_index=True)
