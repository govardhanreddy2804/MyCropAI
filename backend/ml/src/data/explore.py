from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from ml.src.data.loader import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    load_crop_dataset,
)


def explore_dataset(
    dataset_path: str | Path,
    output_dir: str | Path,
) -> dict:
    df = load_crop_dataset(dataset_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "rows": int(len(df)),
        "features": FEATURE_COLUMNS,
        "crop_classes": int(df[TARGET_COLUMN].nunique()),
        "class_counts": df[TARGET_COLUMN].value_counts().to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "statistics": df[FEATURE_COLUMNS].describe().to_dict(),
    }

    df[TARGET_COLUMN].value_counts().sort_index().plot(kind="bar")
    plt.title("Samples per Crop Class")
    plt.xlabel("Crop")
    plt.ylabel("Number of samples")
    plt.tight_layout()
    plt.savefig(output_dir / "crop_class_distribution.png", dpi=150)
    plt.close()

    df[FEATURE_COLUMNS].hist(figsize=(12, 8))
    plt.tight_layout()
    plt.savefig(output_dir / "feature_distributions.png", dpi=150)
    plt.close()

    return summary