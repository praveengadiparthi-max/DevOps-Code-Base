import io
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    ListFlowable,
    ListItem,
    KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


NAVY = colors.HexColor("#1a3a5c")
DARK = colors.HexColor("#1a1a1a")
GRAY = colors.HexColor("#555555")


def _styles():
    base = getSampleStyleSheet()
    return {
        "name": ParagraphStyle(
            "name",
            fontName="Times-Bold",
            fontSize=20,
            textColor=DARK,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "contact": ParagraphStyle(
            "contact",
            fontName="Times-Roman",
            fontSize=9,
            textColor=GRAY,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "section": ParagraphStyle(
            "section",
            fontName="Times-Bold",
            fontSize=10.5,
            textColor=NAVY,
            spaceBefore=10,
            spaceAfter=2,
            leading=14,
        ),
        "job_title": ParagraphStyle(
            "job_title",
            fontName="Times-Bold",
            fontSize=10.5,
            textColor=DARK,
            spaceAfter=1,
        ),
        "job_meta": ParagraphStyle(
            "job_meta",
            fontName="Times-Italic",
            fontSize=9.5,
            textColor=GRAY,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Times-Roman",
            fontSize=10,
            textColor=DARK,
            leading=14,
            spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Times-Roman",
            fontSize=10,
            textColor=DARK,
            leading=13,
            leftIndent=12,
            spaceAfter=1,
        ),
        "skills_label": ParagraphStyle(
            "skills_label",
            fontName="Times-Bold",
            fontSize=10,
            textColor=DARK,
            leading=14,
        ),
    }


def _section_block(story, title, s):
    story.append(Paragraph(title.upper(), s["section"]))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=4))


def _contact_line(contact: dict) -> str:
    parts = []
    if contact.get("location"):
        parts.append(contact["location"])
    if contact.get("email"):
        parts.append(contact["email"])
    if contact.get("phone"):
        parts.append(contact["phone"])
    if contact.get("linkedin"):
        parts.append(contact["linkedin"])
    if contact.get("github"):
        parts.append(contact["github"])
    return "  ·  ".join(parts)


def generate_pdf(data: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=LETTER,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    s = _styles()
    story = []

    # --- Header ---
    contact = data.get("contact", {})
    story.append(Paragraph(contact.get("name", ""), s["name"]))
    contact_line = _contact_line(contact)
    if contact_line:
        story.append(Paragraph(contact_line, s["contact"]))

    # --- Summary ---
    if data.get("summary"):
        _section_block(story, "Professional Summary", s)
        story.append(Paragraph(data["summary"], s["body"]))

    # --- Experience ---
    if data.get("experience"):
        _section_block(story, "Experience", s)
        for job in data["experience"]:
            title = job.get("title", "")
            company = job.get("company", "")
            location = job.get("location", "")
            start = job.get("start_date", "")
            end = job.get("end_date", "")
            date_range = f"{start} – {end}" if start else end

            company_loc = f"{company}, {location}" if location else company
            header = f'<b>{title}</b><font color="#555555" size="9">    {date_range}</font>'
            meta = f'<i>{company_loc}</i>'

            block = [
                Paragraph(header, s["job_title"]),
                Paragraph(meta, s["job_meta"]),
            ]
            for bullet in job.get("bullets", []):
                block.append(Paragraph(f"• {bullet}", s["bullet"]))
            block.append(Spacer(1, 4))
            story.append(KeepTogether(block))

    # --- Education ---
    if data.get("education"):
        _section_block(story, "Education", s)
        for edu in data["education"]:
            degree = edu.get("degree", "")
            institution = edu.get("institution", "")
            year = edu.get("graduation_year", "")
            gpa = edu.get("gpa", "")
            honors = edu.get("honors", "")

            header = f'<b>{degree}</b><font color="#555555" size="9">    {year}</font>'
            meta_parts = [institution]
            if gpa:
                meta_parts.append(f"GPA: {gpa}")
            if honors:
                meta_parts.append(honors)

            block = [
                Paragraph(header, s["job_title"]),
                Paragraph("  ·  ".join(meta_parts), s["job_meta"]),
                Spacer(1, 4),
            ]
            story.append(KeepTogether(block))

    # --- Skills ---
    if data.get("skills"):
        skills = data["skills"]
        tech = skills.get("technical", [])
        soft = skills.get("soft", [])
        if tech or soft:
            _section_block(story, "Skills", s)
            if tech:
                story.append(
                    Paragraph(f'<b>Technical:</b>  {", ".join(tech)}', s["body"])
                )
            if soft:
                story.append(
                    Paragraph(f'<b>Core Competencies:</b>  {", ".join(soft)}', s["body"])
                )

    # --- Projects ---
    if data.get("projects"):
        _section_block(story, "Projects", s)
        for proj in data["projects"]:
            name = proj.get("name", "")
            desc = proj.get("description", "")
            techs = proj.get("technologies", [])
            block = [Paragraph(f"<b>{name}</b>", s["job_title"])]
            if desc:
                block.append(Paragraph(desc, s["body"]))
            if techs:
                block.append(
                    Paragraph(
                        f'<font color="#555555" size="9">Technologies: {", ".join(techs)}</font>',
                        s["body"],
                    )
                )
            block.append(Spacer(1, 4))
            story.append(KeepTogether(block))

    # --- Certifications ---
    if data.get("certifications"):
        _section_block(story, "Certifications", s)
        for cert in data["certifications"]:
            story.append(Paragraph(f"• {cert}", s["bullet"]))

    doc.build(story)
    return buf.getvalue()
