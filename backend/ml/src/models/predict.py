from pathlib import Path

import joblib
import pandas as pd


def load_crop_model(path: str | Path):
    artifact = joblib.load(path)

    if not isinstance(artifact, dict):
        raise ValueError("Invalid crop model artifact")

    required = {"model", "model_name", "feature_columns", "classes"}
    if not required.issubset(artifact):
        raise ValueError("Model artifact is missing required metadata")

    return artifact


def predict_crop(
    artifact: dict,
    features: dict[str, float],
) -> dict:
    columns = artifact["feature_columns"]
    missing = [column for column in columns if column not in features]

    if missing:
        raise ValueError(f"Missing input features: {missing}")

    row = pd.DataFrame(
        [[features[column] for column in columns]],
        columns=columns,
    )

    model = artifact["model"]
    predicted_crop = str(model.predict(row)[0])

    result = {
        "crop": predicted_crop,
        "model_name": artifact["model_name"],
    }

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(row)[0]
        classes = model.classes_
        result["confidence"] = float(max(probabilities))
        result["top_predictions"] = sorted(
            [
                {"crop": str(crop), "probability": float(probability)}
                for crop, probability in zip(classes, probabilities)
            ],
            key=lambda item: item["probability"],
            reverse=True,
        )[:3]

    return result