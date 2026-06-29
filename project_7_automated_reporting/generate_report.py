import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report():
    print("Generating executive PDF report...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "../assets")
    output_pdf_path = os.path.join(script_dir, "Executive_Performance_Report.pdf")
    
    # Check if charts exist. If not, copy them or notify
    monthly_rev_chart = os.path.join(assets_dir, "monthly_revenue.png")
    pareto_chart = os.path.join(assets_dir, "pareto_sla_breaches.png")
    ab_chart = os.path.join(assets_dir, "conversion_rate_comparison.png")
    dq_chart = os.path.join(assets_dir, "data_quality_heatmap.png")
    
    # Initialize report PDF document
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_blue = colors.HexColor("#2563EB")
    c_slate = colors.HexColor("#1E293B")
    c_muted = colors.HexColor("#64748B")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=c_blue,
        spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        textColor=c_muted,
        spaceAfter=20
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=c_slate,
        spaceBefore=14,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=c_slate,
        leading=14,
        spaceAfter=8
    )
    
    metric_label_style = ParagraphStyle(
        'MetricLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white
    )
    
    metric_val_style = ParagraphStyle(
        'MetricVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.white
    )
    
    story = []
    
    # Title Block
    story.append(Paragraph("Executive Performance & Operations Report", title_style))
    story.append(Paragraph("Q2 2026 • Prepared for Operations & Product Stakeholders", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Section 1: Executive Summary
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(
        "This performance audit report compiles data-driven findings across retail sales cohorts, "
        "operations support SLA bottlenecks, product checkout funnel A/B tests, and database profiling. "
        "The goal is to translate raw transactional data and system logs into structured KPIs and operational recommendations.",
        body_style
    ))
    
    # Section 2: Sales Cohort & RFM
    story.append(Paragraph("2. Customer Cohort & RFM Profiles", h1_style))
    story.append(Paragraph(
        "Analysis of our customer base (N=500) shows overall positive sales growth, with completed order revenue "
        "reaching INR 53.72 Lakhs. However, cohort retention profiles reveal a sharp drop in Month 1 customer returns "
        "(dropping to ~35-45% active), signifying onboarding friction.",
        body_style
    ))
    
    # Embed Project 1 KPI Table
    kpi_data = [
        [Paragraph("Metric Label", metric_label_style), Paragraph("Value", metric_label_style), Paragraph("Business Impact", metric_label_style)],
        [Paragraph("Completed Sales", body_style), Paragraph("INR 53.72 Lakhs", body_style), Paragraph("Total completed transaction volume", body_style)],
        [Paragraph("Active Repeat Rate", body_style), Paragraph("63.0%", body_style), Paragraph("249 active customers are repeat buyers", body_style)],
        [Paragraph("Order Return Rate", body_style), Paragraph("4.5%", body_style), Paragraph("Minimal revenue leak, but needs monitoring", body_style)]
    ]
    t_kpi = Table(kpi_data, colWidths=[150, 120, 250])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_blue),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 10))
    
    # Embed Monthly Revenue Chart if exists
    if os.path.exists(monthly_rev_chart):
        story.append(Image(monthly_rev_chart, width=360, height=200))
    story.append(PageBreak())
    
    # Section 3: SLA Bottleneck Analysis
    story.append(Paragraph("3. Operations Queue SLA & CSAT Audit", h1_style))
    story.append(Paragraph(
        "Auditing support ticket queues (N=1,000) revealed an overall SLA compliance of 80.67% (below the target of 90%). "
        "Pareto analysis isolated 'Delivery Issue' requests as the primary bottleneck, representing 40.7% of all breaches. "
        "SLA misses directly hurt customer satisfaction (CSAT), driving scores from a healthy 3.98/5.0 down to a critical 1.44/5.0.",
        body_style
    ))
    
    # Embed Pareto Chart
    if os.path.exists(pareto_chart):
        story.append(Image(pareto_chart, width=360, height=200))
    story.append(Spacer(1, 15))
    
    # Section 4: Product A/B Test Findings
    story.append(Paragraph("4. Checkout Funnel A/B Experiment", h1_style))
    story.append(Paragraph(
        "To optimize checkout conversions, we evaluated a simplified 1-page checkout variant (N=2,505) against the control flow (N=2,495). "
        "The variant achieved a conversion rate of 14.13% (vs. 11.74% control), indicating a +2.39% absolute lift. "
        "Hypothesis testing proved statistical significance (Z = 2.52, p = 0.01188 < 0.05), warranting a 100% rollout.",
        body_style
    ))
    
    if os.path.exists(ab_chart):
        story.append(Image(ab_chart, width=360, height=200))
        
    story.append(PageBreak())
    
    # Section 5: Process Action Plan
    story.append(Paragraph("5. Stakeholder Recommendations", h1_style))
    recommendations_html = """
    * **Redesign 'Delivery Issue' Workflows:** Restructure standard operating procedures for delivery queues to lower handling times (AHT) below the 72-hour target.
    * **Implement Escalation Warnings:** Program real-time alerts in Zendesk/Salesforce when high-priority tickets reach 50% and 75% of their SLA windows.
    * **Roll out New Checkout Flow:** Approve the variant checkout release across 100% of e-commerce traffic, keeping mobile performance as a guardrail.
    * **Apply Staging Gate Schema Rules:** Enforce NOT NULL constraints on critical customer fields and unique primary keys on transactions to eliminate duplicate logs.
    """
    for bullet in recommendations_html.strip().split('\n'):
        if bullet.strip():
            story.append(Paragraph(bullet.strip(), body_style))
            
    # Build Document
    doc.build(story)
    print(f"Report generated successfully: {output_pdf_path}")

if __name__ == "__main__":
    generate_pdf_report()
