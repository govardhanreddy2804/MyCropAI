import pandas as pd
import pytest

from ml.src.data.loader import load_crop_dataset
from ml.src.data.validation import validate_crop_dataset
from ml.src.features.split import split_features_target
from ml.src.data.split import split_dataset


@pytest.fixture
def sample_dataset():
    rows = []

    # Enough samples per class for stratified train/validation/test splits.
    for index in range(20):
        rows.append({
            "N": 50 + index,
            "P": 30 + index,
            "K": 20 + index,
            "temperature": 20 + index / 10,
            "humidity": 60 + index / 10,
            "ph": 6 + index / 100,
            "rainfall": 100 + index,
            "label": "rice" if index % 2 == 0 else "maize",
        })

    return pd.DataFrame(rows)


def test_loader_normalizes_label_column(tmp_path, sample_dataset):
    path = tmp_path / "crops.csv"
    sample_dataset.to_csv(path, index=False)

    result = load_crop_dataset(path)

    assert "crop" in result.columns
    assert "label" not in result.columns
    assert len(result) == 20


def test_loader_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_crop_dataset(tmp_path / "missing.csv")


def test_validation_rejects_missing_values(sample_dataset):
    sample_dataset.loc[0, "N"] = None

    with pytest.raises(ValueError, match="missing values"):
        validate_crop_dataset(sample_dataset)


def test_feature_target_split(sample_dataset):
    df = sample_dataset.rename(columns={"label": "crop"})
    X, y = split_features_target(df)

    assert X.shape == (20, 7)
    assert y.name == "crop"
    assert set(y.unique()) == {"rice", "maize"}


def test_dataset_split_has_no_overlap(sample_dataset):
    df = sample_dataset.rename(columns={"label": "crop"})
    X, y = split_features_target(df)

    X_train, X_val, X_test, y_train, y_val, y_test = split_dataset(X, y)

    assert len(X_train) + len(X_val) + len(X_test) == len(df)
    assert len(X_train) == len(y_train)
    assert len(X_val) == len(y_val)
    assert len(X_test) == len(y_test)

    assert set(X_train.index).isdisjoint(X_val.index)
    assert set(X_train.index).isdisjoint(X_test.index)
    assert set(X_val.index).isdisjoint(X_test.index)