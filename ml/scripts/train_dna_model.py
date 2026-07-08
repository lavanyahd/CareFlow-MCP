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

DATA_PATH = PROJECT_ROOT / "ml" / "data" / "synthetic_appointments.csv"

ML_MODEL_DIR = PROJECT_ROOT / "ml" / "models"
EVALUATION_DIR = PROJECT_ROOT / "ml" / "evaluation"
BACKEND_MODEL_DIR = PROJECT_ROOT / "backend" / "app" / "ml_models"

ML_MODEL_DIR.mkdir(parents=True, exist_ok=True)
EVALUATION_DIR.mkdir(parents=True, exist_ok=True)
BACKEND_MODEL_DIR.mkdir(parents=True, exist_ok=True)


NUMERIC_FEATURES = [
    "age",
    "waiting_days",
    "previous_missed_appointments",
    "previous_cancellations",
    "reminder_sent",
]


CATEGORICAL_FEATURES = [
    "department",
    "appointment_day",
    "appointment_time",
    "distance_band",
]


TARGET_COLUMN = "dna_label"


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


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                StandardScaler(),
                NUMERIC_FEATURES,
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

    high_recall = recall_score(
        y_test,
        predictions,
        labels=["High"],
        average="macro",
        zero_division=0,
    )

    medium_recall = recall_score(
        y_test,
        predictions,
        labels=["Medium"],
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
        / f"{model_name.lower().replace(' ', '_')}_dna_classification_report.txt"
    )

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report)

    priority_score = (
        macro_f1 * 0.50
        + high_recall * 0.35
        + medium_recall * 0.15
    )

    return {
        "model_name": model_name,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "high_recall": high_recall,
        "medium_recall": medium_recall,
        "priority_score": priority_score,
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

    figure = plt.figure(figsize=(7, 5))
    axis = figure.add_subplot(111)

    image = axis.imshow(matrix)
    figure.colorbar(image)

    axis.set_xticks(range(len(labels)))
    axis.set_yticks(range(len(labels)))

    axis.set_xticklabels(labels)
    axis.set_yticklabels(labels)

    axis.set_xlabel("Predicted Label")
    axis.set_ylabel("True Label")
    axis.set_title("DNA Risk Model Confusion Matrix")

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

    output_path = EVALUATION_DIR / "dna_confusion_matrix.png"
    figure.savefig(output_path, dpi=150)

    plt.close(figure)


def main() -> None:
    print("Starting DNA model training...")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Dataset path: {DATA_PATH}")

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}. "
            "Run generate_synthetic_data.py first."
        )

    dataframe = pd.read_csv(DATA_PATH)

    print(f"Dataset loaded successfully. Rows: {len(dataframe)}")

    required_columns = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
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

    print()
    print("DNA label distribution:")
    print(dataframe[TARGET_COLUMN].value_counts())

    x = dataframe[
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
    ]

    y = dataframe[TARGET_COLUMN]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    preprocessor = build_preprocessor()

    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            class_weight="balanced",
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
        print(f"High DNA Recall: {result['high_recall']:.4f}")
        print(f"Medium DNA Recall: {result['medium_recall']:.4f}")
        print(f"Priority Score: {result['priority_score']:.4f}")

    best_result = max(
        results,
        key=lambda item: item["priority_score"],
    )

    best_model_name = best_result["model_name"]
    best_pipeline = trained_pipelines[best_model_name]

    model_path = ML_MODEL_DIR / "dna_model.pkl"
    backend_model_path = BACKEND_MODEL_DIR / "dna_model.pkl"

    joblib.dump(
        best_pipeline,
        model_path,
    )

    shutil.copy2(
        model_path,
        backend_model_path,
    )

    label_order = [
        "High",
        "Medium",
        "Low",
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
        "accuracy": round(best_result["accuracy"], 4),
        "macro_f1": round(best_result["macro_f1"], 4),
        "high_recall": round(best_result["high_recall"], 4),
        "medium_recall": round(best_result["medium_recall"], 4),
        "priority_score": round(best_result["priority_score"], 4),
        "training_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "dataset_path": str(DATA_PATH),
    }

    metadata_path = ML_MODEL_DIR / "dna_model_metadata.json"
    backend_metadata_path = (
        BACKEND_MODEL_DIR / "dna_model_metadata.json"
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
                "high_recall": item["high_recall"],
                "medium_recall": item["medium_recall"],
                "priority_score": item["priority_score"],
            }
            for item in results
        ]
    )

    results_path = (
        EVALUATION_DIR / "dna_model_results.csv"
    )

    results_dataframe.to_csv(
        results_path,
        index=False,
    )

    print()
    print("Best DNA model saved successfully.")
    print(f"Best model: {best_model_name}")
    print(f"Model saved to: {model_path}")
    print(f"Backend model copied to: {backend_model_path}")
    print(f"Metadata saved to: {metadata_path}")
    print(f"Backend metadata copied to: {backend_metadata_path}")
    print(f"Evaluation saved to: {EVALUATION_DIR}")


if __name__ == "__main__":
    main()