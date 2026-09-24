import os
from datetime import datetime
from html import escape

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle
    )
    HAS_REPORTLAB = True
    BRAND = colors.HexColor("#06B6D4")
    BRAND_DARK = colors.HexColor("#0A0F1D")
    INK = colors.HexColor("#17211B")
    MUTED = colors.HexColor("#657269")
    LINE = colors.HexColor("#DFE7E1")
    SOFT = colors.HexColor("#F4F7F4")
    WARNING = colors.HexColor("#FFF7E8")
except ImportError:
    HAS_REPORTLAB = False


def clean_text(value):
    return escape(str(value if value not in (None, "") else "Not Provided"))


def markdown_to_report_text(text):
    lines = []
    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if not line:
            lines.append("<br/>")
        elif line.startswith("## "):
            lines.append(f"<br/><b>{clean_text(line[3:])}</b>")
        elif line.startswith("- "):
            lines.append(f"&bull; {clean_text(line[2:])}")
        else:
            lines.append(clean_text(line))
    return "<br/>".join(lines)


def section_title(title, styles):
    return Paragraph(clean_text(title), styles["section"])


def make_table(rows, widths, header=False):
    if not HAS_REPORTLAB:
        return None
    style = [
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
    ]

    if header:
        style.extend([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ])
    else:
        style.extend([
            ("BACKGROUND", (0, 0), (0, -1), SOFT),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ])

    table = Table(rows, colWidths=widths, hAlign="LEFT")
    table.setStyle(TableStyle(style))
    return table


def generate_report(
    name,
    age,
    gender,
    bmi,
    risk,
    symptoms,
    disease,
    confidence,
    precaution,
    ai_response,
    height=None,
    weight=None,
    temperature=None,
    temperature_status=None,
    spo2=None,
    spo2_status=None,
    health_score=None,
    health_summary=None,
    duration=None,
    severity=None,
    progress=None,
    contact=None,
    history=None,
    emergency=None
):
    if not HAS_REPORTLAB:
        print("[MediAI] Note: reportlab library not found in the current Python environment. PDF generation skipped. (To enable, run: pip install reportlab)")
        return False

    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(base_dir, "static", "report.pdf")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=34,
        bottomMargin=34
    )

    sample = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=sample["Heading1"],
            alignment=TA_CENTER,
            fontSize=22,
            leading=27,
            textColor=BRAND_DARK,
            spaceAfter=6
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=sample["BodyText"],
            alignment=TA_CENTER,
            fontSize=10,
            leading=14,
            textColor=MUTED
        ),
        "section": ParagraphStyle(
            "SectionTitle",
            parent=sample["Heading2"],
            fontSize=13,
            leading=17,
            textColor=BRAND_DARK,
            spaceBefore=14,
            spaceAfter=8
        ),
        "body": ParagraphStyle(
            "Body",
            parent=sample["BodyText"],
            fontSize=9.5,
            leading=14,
            textColor=INK
        ),
        "small": ParagraphStyle(
            "Small",
            parent=sample["BodyText"],
            fontSize=8.5,
            leading=12,
            textColor=MUTED
        )
    }

    generated_at = datetime.now().strftime("%d %b %Y, %I:%M %p")
    emergency_text = ", ".join(emergency) if emergency else "None"

    def draw_page(canvas, doc):
        canvas.saveState()
        width, height = A4
        canvas.setStrokeColor(BRAND)
        canvas.setLineWidth(1.2)
        canvas.line(doc.leftMargin, height - 22, width - doc.rightMargin, height - 22)
        canvas.setFont("Helvetica-Bold", 8.5)
        canvas.setFillColor(BRAND_DARK)
        canvas.drawString(doc.leftMargin, height - 17, "MediAI 2.0")
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(doc.leftMargin, 18, f"Health Assessment Report  •  Page {doc.page}")
        canvas.drawRightString(width - doc.rightMargin, 18, "Educational & informational use")
        canvas.restoreState()

    story = [
        Paragraph("MediAI 2.0", styles["subtitle"]),
        Paragraph("Health Assessment Report", styles["title"]),
        Paragraph(
            "Machine learning health assessment with educational care guidance",
            styles["subtitle"]
        ),
        Spacer(1, 0.18 * inch)
    ]

    summary_rows = [
        [
            Paragraph("<b>Report Generated</b>", styles["body"]),
            Paragraph(clean_text(generated_at), styles["body"]),
            Paragraph("<b>Assessment Type</b>", styles["body"]),
            Paragraph("Educational only", styles["body"])
        ],
        [
            Paragraph("<b>Risk Level</b>", styles["body"]),
            Paragraph(clean_text(risk), styles["body"]),
            Paragraph("<b>Health Score</b>", styles["body"]),
            Paragraph(clean_text(f"{health_score}/100 - {health_summary}" if health_score is not None else "Not Provided"), styles["body"])
        ]
    ]
    story.append(make_table(summary_rows, [115, 145, 115, 145]))

    story.append(section_title("Patient Snapshot", styles))
    patient_rows = [
        [Paragraph("Patient Name", styles["body"]), Paragraph(clean_text(name), styles["body"])],
        [Paragraph("Age", styles["body"]), Paragraph(clean_text(f"{age} years"), styles["body"])],
        [Paragraph("Gender", styles["body"]), Paragraph(clean_text(gender), styles["body"])],
        [Paragraph("Height / Weight", styles["body"]), Paragraph(clean_text(f"{height or 'Not Provided'} cm / {weight or 'Not Provided'} kg"), styles["body"])],
        [Paragraph("BMI", styles["body"]), Paragraph(clean_text(bmi), styles["body"])],
    ]
    story.append(make_table(patient_rows, [150, 370]))

    story.append(section_title("Vitals and Context", styles))
    vitals_rows = [
        [Paragraph("Temperature", styles["body"]), Paragraph(clean_text(f"{temperature or 'Not Provided'} C - {temperature_status or 'Not Provided'}"), styles["body"])],
        [Paragraph("Blood Oxygen", styles["body"]), Paragraph(clean_text(f"{spo2 or 'Not Provided'}% - {spo2_status or 'Not Provided'}"), styles["body"])],
        [Paragraph("Duration / Severity", styles["body"]), Paragraph(clean_text(f"{duration or 'Not Provided'} / {severity or 'Not Provided'}"), styles["body"])],
        [Paragraph("Progress / Contact", styles["body"]), Paragraph(clean_text(f"{progress or 'Not Provided'} / {contact or 'Not Provided'}"), styles["body"])],
        [Paragraph("Medical History", styles["body"]), Paragraph(clean_text(history or "None"), styles["body"])],
        [Paragraph("Emergency Symptoms", styles["body"]), Paragraph(clean_text(emergency_text), styles["body"])],
    ]
    story.append(make_table(vitals_rows, [150, 370]))

    story.append(section_title("Possible Health Assessment", styles))
    assessment_rows = [
        [Paragraph("Model Suggestion", styles["body"]), Paragraph(clean_text(disease), styles["body"])],
        [Paragraph("Confidence", styles["body"]), Paragraph(clean_text(f"{float(confidence):.2f}%"), styles["body"])],
    ]
    story.append(make_table(assessment_rows, [150, 370]))

    story.append(section_title("Symptoms Provided", styles))
    story.append(Paragraph(clean_text(symptoms), styles["body"]))

    story.append(section_title("Recommended Precautions", styles))
    story.append(Paragraph(clean_text(precaution), styles["body"]))

    story.append(section_title("Care Guidance", styles))
    story.append(Paragraph(markdown_to_report_text(ai_response), styles["body"]))

    story.append(section_title("Important Disclaimer", styles))
    disclaimer = (
        "This report is generated for educational and demonstration purposes only. "
        "It is not a medical diagnosis, does not prescribe treatment, and should not "
        "replace consultation with a qualified healthcare professional. Seek urgent "
        "care immediately for emergency symptoms."
    )
    disclaimer_table = make_table(
        [[Paragraph(disclaimer, styles["small"])]],
        [520],
        header=False
    )
    if disclaimer_table:
        disclaimer_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), WARNING)]))
        story.append(disclaimer_table)

    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    return True
