import pandas as pd

from ml.src.data.loader import FEATURE_COLUMNS, TARGET_COLUMN


def split_features_target(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()

    if "label" in df.columns and TARGET_COLUMN not in df.columns:
        df = df.rename(columns={"label": TARGET_COLUMN})

    required = FEATURE_COLUMNS + [TARGET_COLUMN]
    missing = [column for column in required if column not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()

    return X, y