import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


APP_DIR = Path(__file__).resolve().parents[1]
REPORT_DIR = APP_DIR.parent / "generated_reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def decode_json_list(value: str | None) -> list[str]:
    if not value:
        return []

    try:
        decoded_value = json.loads(value)

        if isinstance(decoded_value, list):
            return [str(item) for item in decoded_value]

    except json.JSONDecodeError:
        return []

    return []


def safe_text(value) -> str:
    if value is None:
        return "Not available"

    return str(value)


def create_section_title(text: str, styles):
    return Paragraph(f"<b>{text}</b>", styles["Heading2"])


def create_key_value_table(rows: list[list[str]]) -> Table:
    table = Table(
        rows,
        colWidths=[160, 330],
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    return table


def generate_referral_report(
    referral,
    latest_triage,
    latest_dna,
    reviews,
) -> Path:
    file_path = REPORT_DIR / f"referral_{referral.id}_report.pdf"

    document = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(
        Paragraph(
            "<b>CareFlow-MCP Referral Decision-Support Report</b>",
            styles["Title"],
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "This report is generated from a synthetic clinical decision-support prototype. "
            "It must not be used for diagnosis or real healthcare decision-making.",
            styles["BodyText"],
        )
    )

    story.append(Spacer(1, 18))

    story.append(create_section_title("Patient Information", styles))

    patient_rows = [
        ["Patient ID", safe_text(referral.patient.patient_id)],
        ["Age", safe_text(referral.patient.age)],
        ["Gender", safe_text(referral.patient.gender)],
        ["Department", safe_text(referral.department)],
        ["Waiting Days", safe_text(referral.waiting_days)],
        ["Referral Status", safe_text(referral.status)],
    ]

    story.append(create_key_value_table(patient_rows))
    story.append(Spacer(1, 18))

    story.append(create_section_title("Referral Note", styles))
    story.append(Paragraph(safe_text(referral.referral_text), styles["BodyText"]))
    story.append(Spacer(1, 18))

    symptoms = decode_json_list(referral.extracted_symptoms)
    conditions = decode_json_list(referral.extracted_conditions)

    story.append(create_section_title("Extracted Information", styles))

    extracted_rows = [
        [
            "Symptoms",
            ", ".join(symptoms) if symptoms else "None detected",
        ],
        [
            "Conditions",
            ", ".join(conditions) if conditions else "None detected",
        ],
        [
            "Duration",
            (
                f"{referral.duration_days} days"
                if referral.duration_days is not None
                else "Not detected"
            ),
        ],
    ]

    story.append(create_key_value_table(extracted_rows))
    story.append(Spacer(1, 18))

    story.append(create_section_title("Red-Flag Assessment", styles))

    red_flag_rows = [
        [
            "Red Flag Detected",
            "Yes" if referral.red_flag_detected else "No",
        ],
        [
            "Red Flag Score",
            f"{round(referral.red_flag_score * 100)}%",
        ],
        [
            "Reason",
            safe_text(referral.red_flag_reason),
        ],
    ]

    story.append(create_key_value_table(red_flag_rows))
    story.append(Spacer(1, 18))

    story.append(create_section_title("ML Triage Prediction", styles))

    if latest_triage is not None:
        triage_rows = [
            ["Predicted Urgency", latest_triage.predicted_urgency],
            ["Final Urgency", latest_triage.final_urgency],
            ["Confidence", f"{round(latest_triage.confidence * 100)}%"],
            ["Risk Score", f"{round(latest_triage.risk_score * 100)}%"],
            ["Model", latest_triage.model_name],
            ["Explanation", latest_triage.explanation],
        ]
    else:
        triage_rows = [
            ["Triage Prediction", "Not generated yet"],
        ]

    story.append(create_key_value_table(triage_rows))
    story.append(Spacer(1, 18))

    story.append(create_section_title("DNA Missed Appointment Prediction", styles))

    if latest_dna is not None:
        dna_rows = [
            ["DNA Risk", latest_dna.dna_risk],
            ["Confidence", f"{round(latest_dna.confidence * 100)}%"],
            ["Risk Score", f"{round(latest_dna.risk_score * 100)}%"],
            ["Appointment Day", latest_dna.appointment_day],
            ["Appointment Time", latest_dna.appointment_time],
            ["Distance Band", latest_dna.distance_band],
            ["Recommended Action", latest_dna.recommended_action],
            ["Model", latest_dna.model_name],
        ]
    else:
        dna_rows = [
            ["DNA Prediction", "Not generated yet"],
        ]

    story.append(create_key_value_table(dna_rows))
    story.append(Spacer(1, 18))

    story.append(create_section_title("Clinician Review History", styles))

    if reviews:
        for review in reviews:
            review_rows = [
                ["Reviewer", review.reviewer_name],
                ["Decision", review.decision],
                ["Final Urgency", review.final_urgency],
                ["Notes", review.notes],
                ["Reviewed At", safe_text(review.created_at)],
            ]

            story.append(create_key_value_table(review_rows))
            story.append(Spacer(1, 10))
    else:
        story.append(
            Paragraph(
                "No clinician review has been recorded yet.",
                styles["BodyText"],
            )
        )

    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            "<b>Safety Note:</b> AI outputs are decision-support only. "
            "Final clinical decisions must be made by qualified healthcare staff.",
            styles["BodyText"],
        )
    )

    document.build(story)

    return file_path