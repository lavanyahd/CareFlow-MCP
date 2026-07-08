from pathlib import Path
import json
import shutil

import joblib
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "ml" / "data" / "synthetic_referrals.csv"
ML_MODEL_DIR = PROJECT_ROOT / "ml" / "models"
EVALUATION_DIR = PROJECT_ROOT / "ml" / "evaluation"
BACKEND_MODEL_DIR = PROJECT_ROOT / "backend" / "app" / "ml_models"

ML_MODEL_DIR.mkdir(parents=True, exist_ok=True)
EVALUATION_DIR.mkdir(parents=True, exist_ok=True)
BACKEND_MODEL_DIR.mkdir(parents=True, exist_ok=True)


SYMPTOM_KEYWORDS = [
    "chest pain",
    "shortness of breath",
    "palpitations",
    "dizziness",
    "fatigue",
    "cough",
    "fever",
    "chest tightness",
    "abdominal pain",
    "blood in stool",
    "weight loss",
    "vomiting",
    "skin rash",
    "itching",
    "swelling",
    "redness",
    "painful skin lesion",
    "severe headache",
    "weakness",
    "speech difficulty",
    "confusion",
]


NUMERIC_FEATURES = [
    "age",
    "duration_days",
    "pain_score",
    "diabetes",
    "heart_disease",
    "asthma",
    "bp_high",
    "pregnancy",
    "previous_admissions",
    "waiting_days",
    "previous_missed_appointments",
    "red_flag",
]


CATEGORICAL_FEATURES = [
    "gender",
    "department",
]


TARGET_COLUMN = "urgency_label"


def add_symptom_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe = dataframe.copy()

    dataframe["symptoms"] = (
        dataframe["symptoms"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    for symptom in SYMPTOM_KEYWORDS:
        column_name = (
            "symptom_"
            + symptom.replace(" ", "_")
            .replace("-", "_")
        )

        dataframe[column_name] = dataframe["symptoms"].apply(
            lambda text: int(symptom in text)
        )

    return dataframe


def create_one_hot_encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=False,
        )
    except TypeError:
        return OneHotEncoder(
            handle_unknown="ignore",
            sparse=False,
        )


def build_preprocessor(symptom_features: list[str]) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                StandardScaler(),
                NUMERIC_FEATURES + symptom_features,
            ),
            (
                "categorical",
                create_one_hot_encoder(),
                CATEGORICAL_FEATURES,
            ),
        ],
        remainder="drop",
    )


def evaluate_model(
    model_name: str,
    pipeline: Pipeline,
    x_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    predictions = pipeline.predict(x_test)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0,
    )

    emergency_recall = recall_score(
        y_test,
        predictions,
        labels=["Emergency"],
        average="macro",
        zero_division=0,
    )

    urgent_recall = recall_score(
        y_test,
        predictions,
        labels=["Urgent"],
        average="macro",
        zero_division=0,
    )

    report = classification_report(
        y_test,
        predictions,
        zero_division=0,
    )

    report_path = (
        EVALUATION_DIR
        / f"{model_name.lower().replace(' ', '_')}_classification_report.txt"
    )

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report)

    return {
        "model_name": model_name,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "emergency_recall": emergency_recall,
        "urgent_recall": urgent_recall,
        "priority_score": (
            macro_f1 * 0.50
            + emergency_recall * 0.30
            + urgent_recall * 0.20
        ),
        "predictions": predictions,
        "classification_report_path": str(report_path),
    }


def save_confusion_matrix(
    y_test: pd.Series,
    predictions,
    labels: list[str],
) -> None:
    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=labels,
    )

    figure = plt.figure(figsize=(8, 6))
    axis = figure.add_subplot(111)

    image = axis.imshow(matrix)
    figure.colorbar(image)

    axis.set_xticks(range(len(labels)))
    axis.set_yticks(range(len(labels)))
    axis.set_xticklabels(labels, rotation=45, ha="right")
    axis.set_yticklabels(labels)

    axis.set_xlabel("Predicted Label")
    axis.set_ylabel("True Label")
    axis.set_title("Triage Model Confusion Matrix")

    for row_index in range(matrix.shape[0]):
        for column_index in range(matrix.shape[1]):
            axis.text(
                column_index,
                row_index,
                str(matrix[row_index, column_index]),
                ha="center",
                va="center",
            )

    figure.tight_layout()

    output_path = EVALUATION_DIR / "triage_confusion_matrix.png"
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}. "
            "Run generate_synthetic_data.py first."
        )

    dataframe = pd.read_csv(DATA_PATH)
    dataframe = add_symptom_features(dataframe)

    symptom_features = [
        column
        for column in dataframe.columns
        if column.startswith("symptom_")
    ]

    required_columns = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
        + symptom_features
        + [TARGET_COLUMN]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    x = dataframe[
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
        + symptom_features
    ]

    y = dataframe[TARGET_COLUMN]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    preprocessor = build_preprocessor(symptom_features)

    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            class_weight="balanced",
            max_depth=None,
        ),
    }

    results = []
    trained_pipelines = {}

    for model_name, model in models.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("classifier", model),
            ]
        )

        pipeline.fit(
            x_train,
            y_train,
        )

        result = evaluate_model(
            model_name=model_name,
            pipeline=pipeline,
            x_test=x_test,
            y_test=y_test,
        )

        results.append(result)
        trained_pipelines[model_name] = pipeline

        print()
        print(f"Model: {model_name}")
        print(f"Accuracy: {result['accuracy']:.4f}")
        print(f"Macro F1: {result['macro_f1']:.4f}")
        print(
            f"Emergency Recall: "
            f"{result['emergency_recall']:.4f}"
        )
        print(
            f"Urgent Recall: "
            f"{result['urgent_recall']:.4f}"
        )
        print(
            f"Priority Score: "
            f"{result['priority_score']:.4f}"
        )

    best_result = max(
        results,
        key=lambda item: item["priority_score"],
    )

    best_model_name = best_result["model_name"]
    best_pipeline = trained_pipelines[best_model_name]

    model_path = ML_MODEL_DIR / "triage_model.pkl"
    backend_model_path = BACKEND_MODEL_DIR / "triage_model.pkl"

    joblib.dump(
        best_pipeline,
        model_path,
    )

    shutil.copy2(
        model_path,
        backend_model_path,
    )

    label_order = [
        "Emergency",
        "Urgent",
        "Soon",
        "Routine",
        "Self-care",
    ]

    save_confusion_matrix(
        y_test=y_test,
        predictions=best_result["predictions"],
        labels=label_order,
    )

    metadata = {
        "model_name": best_model_name,
        "target": TARGET_COLUMN,
        "labels": label_order,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "symptom_features": symptom_features,
        "accuracy": round(best_result["accuracy"], 4),
        "macro_f1": round(best_result["macro_f1"], 4),
        "emergency_recall": round(
            best_result["emergency_recall"],
            4,
        ),
        "urgent_recall": round(
            best_result["urgent_recall"],
            4,
        ),
        "priority_score": round(
            best_result["priority_score"],
            4,
        ),
        "training_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "dataset_path": str(DATA_PATH),
    }

    metadata_path = ML_MODEL_DIR / "model_metadata.json"
    backend_metadata_path = (
        BACKEND_MODEL_DIR / "model_metadata.json"
    )

    with open(metadata_path, "w", encoding="utf-8") as file:
        json.dump(
            metadata,
            file,
            indent=4,
        )

    shutil.copy2(
        metadata_path,
        backend_metadata_path,
    )

    results_dataframe = pd.DataFrame(
        [
            {
                "model_name": item["model_name"],
                "accuracy": item["accuracy"],
                "macro_f1": item["macro_f1"],
                "emergency_recall": item["emergency_recall"],
                "urgent_recall": item["urgent_recall"],
                "priority_score": item["priority_score"],
            }
            for item in results
        ]
    )

    results_path = (
        EVALUATION_DIR / "triage_model_results.csv"
    )

    results_dataframe.to_csv(
        results_path,
        index=False,
    )

    print()
    print("Best triage model saved successfully.")
    print(f"Best model: {best_model_name}")
    print(f"Model saved to: {model_path}")
    print(f"Backend model copied to: {backend_model_path}")
    print(f"Metadata saved to: {metadata_path}")
    print(f"Evaluation saved to: {EVALUATION_DIR}")


if __name__ == "__main__":
    main()