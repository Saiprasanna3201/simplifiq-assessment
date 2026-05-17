import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

TEAL       = colors.HexColor("#0F6E56")
TEAL_LIGHT = colors.HexColor("#E1F5EE")
DARK       = colors.HexColor("#1A1A2E")
GRAY       = colors.HexColor("#555555")
LIGHT_GRAY = colors.HexColor("#F4F4F4")
WHITE      = colors.white
AMBER      = colors.HexColor("#BA7517")
AMBER_LIGHT= colors.HexColor("#FAEEDA")


def build_styles():
    base = getSampleStyleSheet()
    return {
        "cover_company": ParagraphStyle(
            "cover_company", fontSize=28, fontName="Helvetica-Bold",
            textColor=WHITE, alignment=TA_LEFT, spaceAfter=6,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", fontSize=13, fontName="Helvetica",
            textColor=colors.HexColor("#B0E8D8"), alignment=TA_LEFT, spaceAfter=4,
        ),
        "cover_date": ParagraphStyle(
            "cover_date", fontSize=10, fontName="Helvetica",
            textColor=colors.HexColor("#9FE1CB"), alignment=TA_LEFT,
        ),
        "section_heading": ParagraphStyle(
            "section_heading", fontSize=13, fontName="Helvetica-Bold",
            textColor=TEAL, spaceBefore=14, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body", fontSize=10, fontName="Helvetica",
            textColor=DARK, leading=16, spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontSize=10, fontName="Helvetica",
            textColor=GRAY, leading=15, spaceAfter=3,
            leftIndent=12, bulletIndent=0,
        ),
        "label": ParagraphStyle(
            "label", fontSize=9, fontName="Helvetica-Bold",
            textColor=TEAL, spaceAfter=2,
        ),
        "insight_text": ParagraphStyle(
            "insight_text", fontSize=10, fontName="Helvetica-Oblique",
            textColor=colors.HexColor("#412402"), leading=15,
        ),
        "footer": ParagraphStyle(
            "footer", fontSize=8, fontName="Helvetica",
            textColor=colors.HexColor("#999999"), alignment=TA_CENTER,
        ),
        "badge_text": ParagraphStyle(
            "badge_text", fontSize=9, fontName="Helvetica-Bold",
            textColor=TEAL, alignment=TA_CENTER,
        ),
    }


def cover_block(lead, enriched, styles, page_w, page_h):
    elements = []
    now = datetime.now().strftime("%B %d, %Y")
    header_data = [[
        Paragraph(lead["company"], styles["cover_company"]),
    ]]
    sub_data = [[
        Paragraph(f"{lead['industry']}  ·  Prepared for {lead['name']}  ·  {now}", styles["cover_sub"]),
    ]]
    header_table = Table(header_data, colWidths=[page_w - 40*mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TEAL),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
    ]))
    sub_table = Table(sub_data, colWidths=[page_w - 40*mm])
    sub_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#085041")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
    ]))
    elements.append(header_table)
    elements.append(sub_table)
    elements.append(Spacer(1, 8*mm))
    intro = enriched.get("personalized_intro", "")
    if intro:
        elements.append(Paragraph(intro, styles["body"]))
        elements.append(Spacer(1, 4*mm))
    return elements


def info_badges(enriched, styles, page_w):
    badges = [
        ("Industry segment", enriched.get("industry_segment", "—")),
        ("Company size",     enriched.get("company_size_estimate", "—")),
        ("Digital maturity", enriched.get("digital_maturity", "—")),
    ]
    col_w = (page_w - 40*mm) / 3
    badge_data = [[
        Table(
            [[Paragraph(label, styles["label"])], [Paragraph(value, styles["badge_text"])]],
            colWidths=[col_w - 4*mm],
        )
        for label, value in badges
    ]]
    badge_table = Table(badge_data, colWidths=[col_w] * 3)
    badge_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), TEAL_LIGHT),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("LINEAFTER", (0, 0), (1, 0), 0.5, colors.HexColor("#9FE1CB")),
    ]))
    return [badge_table, Spacer(1, 6*mm)]


def bullet_section(title, items, styles):
    elements = [Paragraph(title, styles["section_heading"])]
    for item in items:
        elements.append(Paragraph(f"• &nbsp;{item}", styles["bullet"]))
    elements.append(Spacer(1, 3*mm))
    return elements


def key_insight_box(text, styles, page_w):
    data = [[Paragraph(f'"{text}"', styles["insight_text"])]]
    t = Table(data, colWidths=[page_w - 40*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), AMBER_LIGHT),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ("LINEBEFORE",    (0, 0), (0, -1), 3, AMBER),
    ]))
    return [t, Spacer(1, 5*mm)]


def footer_section(styles, page_w):
    footer_text = (
        "This report was automatically generated by SimplifIQ's AI-powered lead intelligence system. "
        "All insights are derived from publicly available information."
    )
    return [
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD")),
        Spacer(1, 3*mm),
        Paragraph(footer_text, styles["footer"]),
    ]


def generate_pdf(lead, enriched, output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=18*mm, bottomMargin=18*mm,
    )
    page_w, page_h = A4
    styles = build_styles()
    story = []

    story.extend(cover_block(lead, enriched, styles, page_w, page_h))
    story.extend(info_badges(enriched, styles, page_w))

    story.append(Paragraph("Company overview", styles["section_heading"]))
    story.append(Paragraph(enriched.get("company_overview", ""), styles["body"]))
    story.append(Spacer(1, 3*mm))

    left_data = (
        [Paragraph("Key services", styles["label"])]
        + [Paragraph(f"• {s}", styles["bullet"]) for s in enriched.get("key_services", [])]
    )
    right_data = (
        [Paragraph("Target market", styles["label"]),
         Paragraph(enriched.get("target_market", ""), styles["body"]),
         Spacer(1, 4),
         Paragraph("Competitive landscape", styles["label"]),
         Paragraph(enriched.get("competitive_landscape", ""), styles["body"])]
    )
    col = (page_w - 40*mm) / 2
    two_col = Table([[left_data, right_data]], colWidths=[col - 5*mm, col + 5*mm])
    two_col.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEAFTER", (0, 0), (0, -1), 0.5, colors.HexColor("#DDDDDD")),
        ("RIGHTPADDING", (0, 0), (0, -1), 10),
        ("LEFTPADDING",  (1, 0), (1, -1), 10),
    ]))
    story.append(two_col)
    story.append(Spacer(1, 5*mm))

    story.extend(bullet_section(
        "Identified pain points",
        enriched.get("pain_points", []),
        styles,
    ))
    story.extend(bullet_section(
        "Opportunities with SimplifIQ",
        enriched.get("opportunities", []),
        styles,
    ))
    story.extend(bullet_section(
        "Recommended solutions",
        enriched.get("recommended_solutions", []),
        styles,
    ))

    if enriched.get("key_insight"):
        story.append(Paragraph("Key insight", styles["section_heading"]))
        story.extend(key_insight_box(enriched["key_insight"], styles, page_w))

    story.extend(footer_section(styles, page_w))

    doc.build(story)
    print(f"  PDF saved: {output_path}")
    return output_path