import pytest

from ml.src.models.predict import predict_crop


class FakeModel:
    classes_ = ["maize", "rice"]

    def predict(self, X):
        return ["rice"]

    def predict_proba(self, X):
        return [[0.1, 0.9]]


def test_predict_crop_returns_prediction():
    artifact = {
        "model": FakeModel(),
        "model_name": "test_model",
        "feature_columns": [
            "N", "P", "K", "temperature",
            "humidity", "ph", "rainfall",
        ],
        "classes": ["maize", "rice"],
    }

    features = {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 25,
        "humidity": 80,
        "ph": 6.5,
        "rainfall": 200,
    }

    result = predict_crop(artifact, features)

    assert result["crop"] == "rice"
    assert result["model_name"] == "test_model"
    assert result["confidence"] == pytest.approx(0.9)
    assert len(result["top_predictions"]) == 2


def test_predict_crop_rejects_missing_features():
    artifact = {
        "model": FakeModel(),
        "model_name": "test_model",
        "feature_columns": ["N", "P"],
        "classes": ["maize", "rice"],
    }

    with pytest.raises(ValueError, match="Missing input features"):
        predict_crop(artifact, {"N": 90})