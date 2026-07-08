import random
from pathlib import Path

import numpy as np
import pandas as pd


RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


GENDERS = [
    "Female",
    "Male",
    "Other",
]


DEPARTMENTS = [
    "Cardiology",
    "Respiratory",
    "Gastroenterology",
    "Dermatology",
    "Neurology",
    "General Medicine",
]


SYMPTOM_GROUPS = {
    "Cardiology": [
        "chest pain",
        "shortness of breath",
        "palpitations",
        "dizziness",
        "fatigue",
    ],
    "Respiratory": [
        "shortness of breath",
        "cough",
        "fever",
        "chest tightness",
        "fatigue",
    ],
    "Gastroenterology": [
        "abdominal pain",
        "blood in stool",
        "weight loss",
        "vomiting",
        "fatigue",
    ],
    "Dermatology": [
        "skin rash",
        "itching",
        "swelling",
        "redness",
        "painful skin lesion",
    ],
    "Neurology": [
        "severe headache",
        "weakness",
        "speech difficulty",
        "dizziness",
        "confusion",
    ],
    "General Medicine": [
        "fever",
        "fatigue",
        "cough",
        "weight loss",
        "vomiting",
    ],
}


DISTANCE_BANDS = [
    "0-5 km",
    "5-10 km",
    "10-20 km",
    "20+ km",
]


APPOINTMENT_DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
]


APPOINTMENT_TIMES = [
    "Morning",
    "Afternoon",
    "Evening",
]


def choose_department() -> str:
    return random.choices(
        DEPARTMENTS,
        weights=[20, 18, 16, 14, 14, 18],
        k=1,
    )[0]


def choose_symptoms(department: str) -> list[str]:
    possible_symptoms = SYMPTOM_GROUPS[department]

    number_of_symptoms = random.choices(
        [1, 2, 3],
        weights=[35, 45, 20],
        k=1,
    )[0]

    return random.sample(
        possible_symptoms,
        k=number_of_symptoms,
    )


def create_conditions(age: int) -> dict[str, int]:
    diabetes = int(
        random.random() < (0.10 if age < 45 else 0.28)
    )

    heart_disease = int(
        random.random() < (0.05 if age < 50 else 0.22)
    )

    asthma = int(random.random() < 0.12)

    bp_high = int(
        random.random() < (0.12 if age < 45 else 0.35)
    )

    pregnancy = int(
        random.random() < 0.04
        and 18 <= age <= 45
    )

    return {
        "diabetes": diabetes,
        "heart_disease": heart_disease,
        "asthma": asthma,
        "bp_high": bp_high,
        "pregnancy": pregnancy,
    }


def detect_red_flag(
    age: int,
    symptoms: list[str],
    conditions: dict[str, int],
) -> int:
    symptom_set = set(symptoms)

    if {
        "chest pain",
        "shortness of breath",
    }.issubset(symptom_set):
        return 1

    if (
        "chest pain" in symptom_set
        and conditions["heart_disease"] == 1
    ):
        return 1

    if (
        "chest pain" in symptom_set
        and conditions["diabetes"] == 1
    ):
        return 1

    if (
        age >= 50
        and {
            "blood in stool",
            "weight loss",
        }.issubset(symptom_set)
    ):
        return 1

    if (
        "severe headache" in symptom_set
        and (
            "weakness" in symptom_set
            or "speech difficulty" in symptom_set
        )
    ):
        return 1

    if (
        conditions["pregnancy"] == 1
        and "abdominal pain" in symptom_set
    ):
        return 1

    return 0


def assign_urgency_label(
    age: int,
    symptoms: list[str],
    pain_score: int,
    duration_days: int,
    waiting_days: int,
    previous_admissions: int,
    red_flag: int,
    conditions: dict[str, int],
) -> str:
    risk_score = 0

    risk_score += red_flag * 5

    if age >= 70:
        risk_score += 2
    elif age >= 50:
        risk_score += 1

    if pain_score >= 8:
        risk_score += 3
    elif pain_score >= 6:
        risk_score += 2
    elif pain_score >= 4:
        risk_score += 1

    if duration_days >= 30:
        risk_score += 1

    if waiting_days >= 45:
        risk_score += 2
    elif waiting_days >= 21:
        risk_score += 1

    if previous_admissions >= 2:
        risk_score += 1

    if conditions["heart_disease"] == 1:
        risk_score += 1

    if conditions["diabetes"] == 1:
        risk_score += 1

    symptom_set = set(symptoms)

    if "speech difficulty" in symptom_set:
        risk_score += 2

    if "shortness of breath" in symptom_set:
        risk_score += 1

    if risk_score >= 9:
        return "Emergency"

    if risk_score >= 6:
        return "Urgent"

    if risk_score >= 4:
        return "Soon"

    if risk_score >= 2:
        return "Routine"

    return "Self-care"


def assign_dna_label(
    age: int,
    waiting_days: int,
    previous_missed_appointments: int,
    distance_band: str,
    appointment_time: str,
    reminder_sent: int,
    previous_cancellations: int,
) -> str:
    dna_score = 0

    dna_score += previous_missed_appointments * 3

    if waiting_days >= 45:
        dna_score += 2
    elif waiting_days >= 21:
        dna_score += 1

    if distance_band == "20+ km":
        dna_score += 2
    elif distance_band == "10-20 km":
        dna_score += 1

    if appointment_time == "Morning":
        dna_score += 1

    if reminder_sent == 0:
        dna_score += 2

    dna_score += previous_cancellations * 2

    if age < 25:
        dna_score += 1

    if dna_score >= 7:
        return "High"

    if dna_score >= 4:
        return "Medium"

    return "Low"


def generate_dataset(number_of_records: int = 1200) -> pd.DataFrame:
    records = []

    for index in range(1, number_of_records + 1):
        patient_id = f"P{index:04d}"

        age = int(
            np.clip(
                np.random.normal(loc=52, scale=18),
                1,
                95,
            )
        )

        gender = random.choice(GENDERS)
        department = choose_department()
        symptoms = choose_symptoms(department)
        conditions = create_conditions(age)

        duration_days = random.choice(
            [2, 3, 5, 7, 10, 14, 21, 30, 45, 60]
        )

        pain_score = random.randint(1, 10)

        previous_admissions = random.choices(
            [0, 1, 2, 3],
            weights=[55, 25, 15, 5],
            k=1,
        )[0]

        waiting_days = random.randint(1, 90)

        previous_missed_appointments = random.choices(
            [0, 1, 2, 3],
            weights=[65, 22, 10, 3],
            k=1,
        )[0]

        distance_band = random.choice(DISTANCE_BANDS)
        appointment_day = random.choice(APPOINTMENT_DAYS)
        appointment_time = random.choice(APPOINTMENT_TIMES)

        previous_cancellations = random.choices(
            [0, 1, 2],
            weights=[75, 20, 5],
            k=1,
        )[0]

        reminder_sent = random.choices(
            [0, 1],
            weights=[25, 75],
            k=1,
        )[0]

        red_flag = detect_red_flag(
            age=age,
            symptoms=symptoms,
            conditions=conditions,
        )

        urgency_label = assign_urgency_label(
            age=age,
            symptoms=symptoms,
            pain_score=pain_score,
            duration_days=duration_days,
            waiting_days=waiting_days,
            previous_admissions=previous_admissions,
            red_flag=red_flag,
            conditions=conditions,
        )

        dna_label = assign_dna_label(
            age=age,
            waiting_days=waiting_days,
            previous_missed_appointments=previous_missed_appointments,
            distance_band=distance_band,
            appointment_time=appointment_time,
            reminder_sent=reminder_sent,
            previous_cancellations=previous_cancellations,
        )

        records.append(
            {
                "patient_id": patient_id,
                "age": age,
                "gender": gender,
                "symptoms": ", ".join(symptoms),
                "duration_days": duration_days,
                "pain_score": pain_score,
                "diabetes": conditions["diabetes"],
                "heart_disease": conditions["heart_disease"],
                "asthma": conditions["asthma"],
                "bp_high": conditions["bp_high"],
                "pregnancy": conditions["pregnancy"],
                "previous_admissions": previous_admissions,
                "waiting_days": waiting_days,
                "previous_missed_appointments": previous_missed_appointments,
                "department": department,
                "red_flag": red_flag,
                "urgency_label": urgency_label,
                "dna_label": dna_label,
                "appointment_day": appointment_day,
                "appointment_time": appointment_time,
                "distance_band": distance_band,
                "previous_cancellations": previous_cancellations,
                "reminder_sent": reminder_sent,
            }
        )

    return pd.DataFrame(records)


def main() -> None:
    referrals_df = generate_dataset(
        number_of_records=1200
    )

    referrals_path = DATA_DIR / "synthetic_referrals.csv"
    appointments_path = DATA_DIR / "synthetic_appointments.csv"

    referrals_df.to_csv(
        referrals_path,
        index=False,
    )

    appointment_columns = [
        "patient_id",
        "age",
        "department",
        "waiting_days",
        "previous_missed_appointments",
        "appointment_day",
        "appointment_time",
        "distance_band",
        "previous_cancellations",
        "reminder_sent",
        "dna_label",
    ]

    referrals_df[appointment_columns].to_csv(
        appointments_path,
        index=False,
    )

    print("Synthetic dataset generated successfully.")
    print(f"Referral data saved to: {referrals_path}")
    print(f"Appointment data saved to: {appointments_path}")
    print()
    print("Urgency label distribution:")
    print(referrals_df["urgency_label"].value_counts())
    print()
    print("DNA label distribution:")
    print(referrals_df["dna_label"].value_counts())


if __name__ == "__main__":
    main()