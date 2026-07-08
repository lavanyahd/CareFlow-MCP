import re
from typing import Any


SYMPTOM_ALIASES = {
    "chest pain": [
        "chest pain",
        "chest discomfort",
        "tightness in chest",
        "chest tightness",
    ],
    "shortness of breath": [
        "shortness of breath",
        "breathing difficulty",
        "difficulty breathing",
        "breathlessness",
        "breathless",
    ],
    "blood in stool": [
        "blood in stool",
        "bloody stool",
        "rectal bleeding",
    ],
    "weight loss": [
        "weight loss",
        "losing weight",
        "unexplained weight loss",
    ],
    "severe headache": [
        "severe headache",
        "sudden headache",
        "worst headache",
    ],
    "headache": [
        "headache",
        "head pain",
    ],
    "weakness": [
        "weakness",
        "weak",
        "loss of strength",
    ],
    "speech difficulty": [
        "speech difficulty",
        "slurred speech",
        "difficulty speaking",
        "unable to speak",
    ],
    "severe abdominal pain": [
        "severe abdominal pain",
        "severe stomach pain",
    ],
    "abdominal pain": [
        "abdominal pain",
        "stomach pain",
        "tummy pain",
    ],
    "fever": [
        "fever",
        "high temperature",
        "febrile",
    ],
    "cough": [
        "cough",
        "coughing",
    ],
    "skin rash": [
        "skin rash",
        "rash",
    ],
    "dizziness": [
        "dizziness",
        "dizzy",
        "light-headed",
        "lightheaded",
    ],
    "fatigue": [
        "fatigue",
        "tiredness",
        "very tired",
    ],
    "vomiting": [
        "vomiting",
        "vomit",
        "being sick",
    ],
    "palpitations": [
        "palpitations",
        "racing heartbeat",
        "irregular heartbeat",
    ],
}


CONDITION_ALIASES = {
    "diabetes": [
        "diabetes",
        "diabetic",
    ],
    "heart disease": [
        "heart disease",
        "cardiac disease",
        "cardiac history",
        "previous heart condition",
    ],
    "asthma": [
        "asthma",
        "asthmatic",
    ],
    "hypertension": [
        "hypertension",
        "high blood pressure",
    ],
    "kidney disease": [
        "kidney disease",
        "renal disease",
        "kidney condition",
    ],
    "cancer history": [
        "history of cancer",
        "previous cancer",
        "cancer history",
    ],
    "pregnancy": [
        "pregnant",
        "pregnancy",
    ],
}


NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}


def normalise_text(text: str) -> str:
    cleaned_text = text.lower().strip()
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)

    return cleaned_text


def find_matching_terms(
    text: str,
    aliases: dict[str, list[str]],
) -> list[str]:
    matches = []

    for standard_name, possible_phrases in aliases.items():
        if any(phrase in text for phrase in possible_phrases):
            matches.append(standard_name)

    return sorted(set(matches))


def parse_number(value: str) -> int | None:
    if value.isdigit():
        return int(value)

    return NUMBER_WORDS.get(value.lower())


def extract_duration_days(text: str) -> int | None:
    duration_pattern = re.compile(
        r"(?:for|since|over the last|past)\s+"
        r"(\d+|one|two|three|four|five|six|seven|eight|"
        r"nine|ten|eleven|twelve)\s+"
        r"(day|days|week|weeks|month|months)",
        re.IGNORECASE,
    )

    match = duration_pattern.search(text)

    if match is None:
        return None

    quantity = parse_number(match.group(1))
    unit = match.group(2).lower()

    if quantity is None:
        return None

    if unit in {"day", "days"}:
        return quantity

    if unit in {"week", "weeks"}:
        return quantity * 7

    if unit in {"month", "months"}:
        return quantity * 30

    return None


def parse_referral_note(referral_text: str) -> dict[str, Any]:
    normalised_text = normalise_text(referral_text)

    symptoms = find_matching_terms(
        normalised_text,
        SYMPTOM_ALIASES,
    )

    conditions = find_matching_terms(
        normalised_text,
        CONDITION_ALIASES,
    )

    duration_days = extract_duration_days(
        normalised_text
    )

    return {
        "symptoms": symptoms,
        "conditions": conditions,
        "duration_days": duration_days,
    }