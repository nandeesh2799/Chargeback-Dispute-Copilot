import io
from datetime import datetime, timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)


def generate_dispute_pdf_report(dispute, order, payment, customer, fulfilment, investigation, draft, scoring) -> bytes:
    """
    Generate an executive-grade Dispute Evidence & Representation PDF report.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom styles
    brand_blue = colors.HexColor("#1E3A8A")
    slate_dark = colors.HexColor("#0F172A")
    slate_muted = colors.HexColor("#64748B")
    border_color = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=brand_blue
    )

    h2_style = ParagraphStyle(
        "Heading2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=brand_blue,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=slate_dark
    )

    body_muted = ParagraphStyle(
        "BodyMuted",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=slate_muted
    )

    code_style = ParagraphStyle(
        "CodeText",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=slate_dark
    )

    elements = []

    # 1. Header with Metadata
    elements.append(Paragraph("RJ KITCHEN — DISPUTE EVIDENCE & RESOLUTION REPORT", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')} | Provider Mode: MOCK / DEMO", body_muted))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=brand_blue, spaceBefore=8, spaceAfter=14))

    # 2. Executive Dispute Summary Table
    amt_fmt = f"INR {dispute.amount / 100:.2f}"
    status_fmt = dispute.status.value.upper() if hasattr(dispute.status, "value") else str(dispute.status).upper()
    readiness_fmt = dispute.evidence_readiness.value.replace('_', ' ').title() if hasattr(dispute.evidence_readiness, "value") else str(dispute.evidence_readiness)

    summary_data = [
        [
            Paragraph("<b>Dispute ID:</b>", body_style), Paragraph(dispute.id, code_style),
            Paragraph("<b>Disputed Amount:</b>", body_style), Paragraph(f"<b>{amt_fmt}</b>", body_style)
        ],
        [
            Paragraph("<b>Reason Code:</b>", body_style), Paragraph(dispute.reason_code.replace('_', ' ').title(), body_style),
            Paragraph("<b>Status / Phase:</b>", body_style), Paragraph(f"{status_fmt} ({dispute.phase.value})", body_style)
        ],
        [
            Paragraph("<b>Order Reference:</b>", body_style), Paragraph(order.order_number if order else "N/A", code_style),
            Paragraph("<b>Response Deadline:</b>", body_style), Paragraph(dispute.response_deadline.strftime("%Y-%m-%d %H:%M UTC"), body_style)
        ],
        [
            Paragraph("<b>Customer Name:</b>", body_style), Paragraph(customer.name if customer else "N/A", body_style),
            Paragraph("<b>Evidence Readiness:</b>", body_style), Paragraph(readiness_fmt, body_style)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[100, 160, 110, 160])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    # 3. Explainable Win-Score Card
    elements.append(Paragraph("Explainable Win-Score & Risk Intelligence", h2_style))
    score_val = f"{dispute.win_probability_score:.1f}%" if dispute.win_probability_score else "N/A"
    tier_val = dispute.win_score_tier.value.upper() if dispute.win_score_tier else "MEDIUM"

    score_card_data = [
        [
            Paragraph(f"<font size=14 color='#1E40AF'><b>Model Win-Score: {score_val}</b></font> (Tier: {tier_val})", body_style),
            Paragraph(f"Completeness: <b>{dispute.evidence_completeness_pct:.0f}%</b>", body_style)
        ]
    ]
    score_table = Table(score_card_data, colWidths=[350, 180])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#BFDBFE")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(score_table)

    if scoring and scoring.top_positive_factors:
        elements.append(Spacer(1, 4))
        for factor in scoring.top_positive_factors:
            elements.append(Paragraph(f"• <font color='#059669'><b>+{factor.get('impact_points', 0):.1f} pts:</b></font> {factor.get('description')}", body_style))
    if scoring and scoring.top_negative_factors:
        for factor in scoring.top_negative_factors:
            elements.append(Paragraph(f"• <font color='#DC2626'><b>{factor.get('impact_points', 0):.1f} pts:</b></font> {factor.get('description')}", body_style))

    elements.append(Spacer(1, 10))

    # 4. Fulfilment & Delivery Telematics
    if fulfilment:
        elements.append(Paragraph("Fulfilment & Carrier Telematics", h2_style))
        ful_data = [
            [Paragraph("Carrier", body_muted), Paragraph("Tracking #", body_muted), Paragraph("Proof Type", body_muted), Paragraph("Delivered At", body_muted)],
            [
                Paragraph(fulfilment.carrier, body_style),
                Paragraph(fulfilment.tracking_number or "N/A", code_style),
                Paragraph(fulfilment.delivery_proof_type.value.upper(), body_style),
                Paragraph(fulfilment.delivered_at.strftime('%Y-%m-%d %H:%M') if fulfilment.delivered_at else 'N/A', body_style)
            ]
        ]
        ful_table = Table(ful_data, colWidths=[130, 130, 130, 140])
        ful_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ('BOX', (0, 0), (-1, -1), 0.5, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(ful_table)
        elements.append(Spacer(1, 10))

    # 5. Contradiction Alerts (if any)
    if investigation and investigation.contradictions:
        elements.append(Paragraph("Inconsistency & Contradiction Alerts", h2_style))
        for c in investigation.contradictions:
            alert_data = [[
                Paragraph(f"<font color='#B91C1C'><b>[ALERT: {c.get('severity', 'HIGH').upper()}] {c.get('title')}</b></font><br/>{c.get('description')}", body_style)
            ]]
            t = Table(alert_data, colWidths=[530])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#FECACA")),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 4))
        elements.append(Spacer(1, 6))

    # 6. Response Draft & Contest Summary
    if draft:
        elements.append(Paragraph("Gateway Contest Submission Summary (<= 1,000 Chars)", h2_style))
        summary_box = [[Paragraph(draft.contest_summary, code_style)]]
        sb_table = Table(summary_box, colWidths=[530])
        sb_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(sb_table)
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("Formal Representation Letter", h2_style))
        letter_paras = draft.representation_letter.split("\n\n")
        for p_text in letter_paras:
            elements.append(Paragraph(p_text.replace("\n", "<br/>"), body_style))
            elements.append(Spacer(1, 4))

    # 7. Provenance & Disclaimer Footer
    elements.append(Spacer(1, 14))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceBefore=4, spaceAfter=8))
    elements.append(Paragraph(
        "<b>LEGAL & COMPLIANCE NOTICE:</b> This document contains proprietary dispute evidence assembled by Chargeback & Dispute Copilot. "
        "All customer and order records are synthetic fixtures modeled after RJ Kitchen cloud kitchen operations. "
        "Not an official banking arbitration ruling.",
        body_muted
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
