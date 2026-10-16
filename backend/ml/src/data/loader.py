from pathlib import Path

import pandas as pd

FEATURE_COLUMNS = [
    "n",
    "p",
    "k",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
]
TARGET_COLUMN = "crop"


def load_crop_dataset(path: str | Path) -> pd.DataFrame:
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()

    # Common versions of this dataset call the target "label".
    if "label" in df.columns and "crop" not in df.columns:
        df = df.rename(columns={"label": "crop"})

    required = FEATURE_COLUMNS + [TARGET_COLUMN]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Dataset is missing columns: {missing}")

    return df[required].copy()