URGENCY_WEIGHT = {
    "Emergency": 1.0,
    "Urgent": 0.8,
    "Soon": 0.6,
    "Routine": 0.35,
    "Self-care": 0.15,
    "Not predicted": 0.0,
}


def normalise_waiting_days(waiting_days: int) -> float:
    return min(waiting_days / 90, 1.0)


def calculate_priority_score(
    triage_risk_score: float,
    waiting_days: int,
    red_flag_score: float,
    final_urgency: str,
) -> float:
    waiting_score = normalise_waiting_days(waiting_days)

    urgency_score = URGENCY_WEIGHT.get(
        final_urgency,
        0.0,
    )

    priority_score = (
        triage_risk_score * 45
        + waiting_score * 25
        + red_flag_score * 20
        + urgency_score * 10
    )

    return round(priority_score, 2)


def get_suggested_action(
    final_urgency: str,
    priority_score: float,
    red_flag_detected: bool,
) -> str:
    if final_urgency == "Emergency" or priority_score >= 85:
        return "Immediate clinical review required"

    if final_urgency == "Urgent" or priority_score >= 70:
        return "Prioritise for urgent appointment"

    if final_urgency == "Soon" or priority_score >= 50:
        return "Book sooner appointment and monitor"

    if final_urgency == "Routine":
        return "Routine appointment pathway"

    if red_flag_detected:
        return "Clinical review recommended due to red flag"

    return "GP, pharmacy, self-care, or routine follow-up"