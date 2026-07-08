from pathlib import Path
from typing import Any

import json
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

ML_MODEL_DIR = PROJECT_ROOT / "ml" / "models"
EVALUATION_DIR = PROJECT_ROOT / "ml" / "evaluation"


TRIAGE_METADATA_PATH = ML_MODEL_DIR / "model_metadata.json"
DNA_METADATA_PATH = ML_MODEL_DIR / "dna_model_metadata.json"

TRIAGE_RESULTS_PATH = EVALUATION_DIR / "triage_model_results.csv"
DNA_RESULTS_PATH = EVALUATION_DIR / "dna_model_results.csv"


def read_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "available": False,
            "message": f"File not found: {path}",
        }

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    data["available"] = True

    return data


def read_results_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    dataframe = pd.read_csv(path)

    return dataframe.to_dict(orient="records")


def get_model_monitoring_summary() -> dict[str, Any]:
    triage_metadata = read_json_file(
        TRIAGE_METADATA_PATH
    )

    dna_metadata = read_json_file(
        DNA_METADATA_PATH
    )

    triage_results = read_results_csv(
        TRIAGE_RESULTS_PATH
    )

    dna_results = read_results_csv(
        DNA_RESULTS_PATH
    )

    return {
        "triage_model": {
            "metadata": triage_metadata,
            "results": triage_results,
            "classification_report_path": str(
                EVALUATION_DIR
                / "logistic_regression_classification_report.txt"
            ),
            "confusion_matrix_path": str(
                EVALUATION_DIR
                / "triage_confusion_matrix.png"
            ),
        },
        "dna_model": {
            "metadata": dna_metadata,
            "results": dna_results,
            "classification_report_path": str(
                EVALUATION_DIR
                / "logistic_regression_dna_classification_report.txt"
            ),
            "confusion_matrix_path": str(
                EVALUATION_DIR
                / "dna_confusion_matrix.png"
            ),
        },
    }