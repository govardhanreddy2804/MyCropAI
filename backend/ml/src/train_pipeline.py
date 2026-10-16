import json
from pathlib import Path

import joblib

from ml.src.data.loader import FEATURE_COLUMNS, load_crop_dataset
from ml.src.data.validation import validate_crop_dataset
from ml.src.features.split import split_features_target
from ml.src.data.split import split_dataset
from ml.src.models.candidates import get_candidate_models
from ml.src.evaluation.metrics import evaluate_classifier


def run_training(
    dataset_path: str | Path,
    artifact_dir: str | Path = "ml/artifacts/crop_recommendation",
) -> dict:
    df = load_crop_dataset(dataset_path)
    validate_crop_dataset(df)

    X, y = split_features_target(df)

    X_train, X_val, X_test, y_train, y_val, y_test = split_dataset(X, y)

    # Model selection uses validation data, not the test set.
    candidates = get_candidate_models()
    validation_results = {}
    fitted_candidates = {}

    for name, model in candidates.items():
        model.fit(X_train, y_train)
        fitted_candidates[name] = model

        validation_results[name] = evaluate_classifier(
            model,
            X_val,
            y_val,
        )

    best_name = max(
        validation_results,
        key=lambda name: validation_results[name]["f1_macro"],
    )

    # Refit the selected model on training + validation data.
    import pandas as pd

    X_train_val = pd.concat([X_train, X_val])
    y_train_val = pd.concat([y_train, y_val])

    best_model = get_candidate_models()[best_name]
    best_model.fit(X_train_val, y_train_val)

    # Evaluate the selected model on the test set only after selection.
    test_metrics = evaluate_classifier(best_model, X_test, y_test)

    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {
            "model": best_model,
            "model_name": best_name,
            "feature_columns": FEATURE_COLUMNS,
            "classes": sorted(y.unique().tolist()),
        },
        artifact_dir / "model.joblib",
    )

    report = {
        "dataset_rows": int(len(df)),
        "class_count": int(y.nunique()),
        "selected_model": best_name,
        "validation_results": {
            name: {
                "accuracy": metrics["accuracy"],
                "precision_macro": metrics["precision_macro"],
                "recall_macro": metrics["recall_macro"],
                "f1_macro": metrics["f1_macro"],
            }
            for name, metrics in validation_results.items()
        },
        "test_metrics": test_metrics,
    }

    (artifact_dir / "metrics.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    return report