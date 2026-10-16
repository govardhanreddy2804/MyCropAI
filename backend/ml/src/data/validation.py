
import pandas as pd

from ml.src.data.loader import FEATURE_COLUMNS, TARGET_COLUMN


def validate_crop_dataset(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError("Dataset is empty")

    # Normalize raw Kaggle column names.
    df.columns = df.columns.str.strip().str.lower()

    # Convert the original target name to the expected name.
    if "label" in df.columns and TARGET_COLUMN not in df.columns:
        df.rename(columns={"label": TARGET_COLUMN}, inplace=True)

    required = FEATURE_COLUMNS + [TARGET_COLUMN]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if df[required].isnull().any().any():
        raise ValueError("Dataset contains missing values")

    for column in FEATURE_COLUMNS:
        converted = pd.to_numeric(df[column], errors="coerce")

        if converted.isnull().any():
            raise ValueError(f"{column} must contain numeric values")

        if not converted.map(
            lambda value: float("-inf") < value < float("inf")
        ).all():
            raise ValueError(f"{column} must contain finite values")

        df[column] = converted

    df[TARGET_COLUMN] = df[TARGET_COLUMN].astype(str).str.strip()

    if (df[TARGET_COLUMN] == "").any():
        raise ValueError("Crop labels cannot be empty")

    if df[TARGET_COLUMN].nunique() < 2:
        raise ValueError("At least two crop classes are required")
