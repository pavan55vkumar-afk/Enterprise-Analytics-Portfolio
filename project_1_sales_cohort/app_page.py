import streamlit as st
import pandas as pd
import os
from google import genai
import anthropic

def generate_cohort_data_if_missing():
    # If the database or outputs are missing, run the generation script
    if os.path.exists("project_1_sales_cohort/outputs/rfm_segmentation.csv"):
        return
    
    import subprocess
    try:
        subprocess.run(["python", "project_1_sales_cohort/generate_data.py"], check=True)
        subprocess.run(["python", "project_1_sales_cohort/run_analysis.py"], check=True)
    except Exception as e:
        st.error(f"Failed to generate cohort dataset: {e}")

def show_page():
    st.subheader("🎫 Cohort Segment Copywriter")
    st.caption("Perform SQL RFM segmentation and write targeted marketing incentives using AI.")

    generate_cohort_data_if_missing()
    
    # Read the RFM dataset
    try:
        df = pd.read_csv("project_1_sales_cohort/outputs/rfm_segmentation.csv")
    except Exception as e:
        st.error(f"Error loading RFM segmentation: {e}")
        return

    # Aggregate cohort metrics
    cohort_stats = df.groupby("rfm_segment").agg(
        size=("customer_id", "count"),
        avg_spend=("monetary", "mean"),
        avg_frequency=("frequency", "mean")
    ).reset_index()

    # KPI Layout
    k1, k2, k3 = st.columns(3)
    with k1:
        champions_size = int(cohort_stats[cohort_stats["rfm_segment"] == "Champions"]["size"].sum())
        st.metric("Champions Cohort Size", champions_size)
    with k2:
        at_risk_size = int(cohort_stats[cohort_stats["rfm_segment"] == "At-Risk High-Value"]["size"].sum())
        st.metric("At-Risk Cohort Size", at_risk_size, delta="-15% month-over-month", delta_color="inverse")
    with k3:
        total_value = float(df["monetary"].sum())
        st.metric("Total Cohort Spend Value", f"₹{total_value/100000:.1f}L")

    st.divider()

    col_selector, col_output = st.columns([1, 1.4])

    with col_selector:
        st.markdown("### Cohort Selection")
        selected_segment = st.selectbox(
            "Select target customer cohort:",
            ["Champions", "At-Risk High-Value", "Loyal Customers", "Lost"]
        )

        # Get stats for the selected cohort
        row = cohort_stats[cohort_stats["rfm_segment"] == selected_segment]
        if not row.empty:
            size = int(row.iloc[0]["size"])
            spend = float(row.iloc[0]["avg_spend"])
            freq = float(row.iloc[0]["avg_frequency"])
            
            st.markdown(f"**Cohort Size:** {size} customers")
            st.markdown(f"**Average Purchases:** {freq:.1f} orders")
            st.markdown(f"**Average Ticket Size:** ₹{spend:,.2f}")
        
        # Get favorite category logic for the cohort
        cohort_df = df[df["rfm_segment"] == selected_segment]
        # Generate dummy category matching if not explicitly in file
        fav_category = "Home Office Setup" if selected_segment == "At-Risk High-Value" else "Consumer Electronics"
        st.markdown(f"**Primary Purchase Category:** `{fav_category}`")

        # Generator button
        st.divider()
        st.markdown("#### Campaign Generation Settings")
        
        # Pull API credentials from the session state (shared from root app.py)
        api_key = st.session_state.get("gemini_key", "")
        model_choice = st.session_state.get("gemini_model", "gemini-2.0-flash")
        temperature = st.session_state.get("temperature", 0.3)
        max_tokens = st.session_state.get("max_tokens", 350)
        use_claude = st.session_state.get("use_claude", False)
        claude_key = st.session_state.get("claude_key", "")

        generate_btn = st.button("✨ Write Campaign Emails", type="primary", use_container_width=True)

    with col_output:
        st.markdown("### 🤖 Generated Email Copy")
        
        if generate_btn:
            if use_claude and not claude_key:
                st.error("Please set your Anthropic Claude API Key in the sidebar.")
            elif not use_claude and not api_key:
                st.error("Please set your Google Gemini API Key in the sidebar.")
            else:
                with st.spinner("AI is drafting your cohort-specific incentive..."):
                    prompt = (
                        f"You are a conversion marketer writing an incentive re-engagement email to a cohort of customers.\n\n"
                        f"Target Cohort: {selected_segment}\n"
                        f"Cohort Average Order Value: ₹{spend:,.2f}\n"
                        f"Most Purchased Category: {fav_category}\n\n"
                        f"Write a personalized promotional email that offers a specific discount or incentive tailored to their buying behavior. "
                        f"Write the subject line and the email body text. Keep it warm, direct, and under 130 words. Output ONLY the email text."
                    )
                    
                    try:
                        if use_claude:
                            # Use Anthropic SDK
                            client = anthropic.Anthropic(api_key=claude_key)
                            message = client.messages.create(
                                model="claude-3-5-sonnet",
                                max_tokens=max_tokens,
                                temperature=temperature,
                                messages=[{"role": "user", "content": prompt}]
                            )
                            draft = message.content[0].text
                        else:
                            # Use Google GenAI SDK
                            client = genai.Client(api_key=api_key)
                            resp = client.models.generate_content(
                                model=model_choice,
                                contents=prompt,
                                config={
                                    "temperature": temperature,
                                    "max_output_tokens": max_tokens,
                                    "thinking_config": {"thinking_budget": 0},
                                }
                            )
                            draft = resp.text
                            
                        st.text_area("Copy / Paste this draft:", value=draft, height=260)
                        st.success("Draft generated successfully!")
                    except Exception as e:
                        st.error(f"Generation failed: {e}")
        else:
            st.info("Set up your selection on the left and click 'Write Campaign Emails' to view AI drafts.")
