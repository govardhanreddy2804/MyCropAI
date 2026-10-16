from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def evaluate_classifier(model, X, y) -> dict:
    predictions = model.predict(X)

    return {
        "accuracy": float(accuracy_score(y, predictions)),
        "precision_macro": float(
            precision_score(y, predictions, average="macro", zero_division=0)
        ),
        "recall_macro": float(
            recall_score(y, predictions, average="macro", zero_division=0)
        ),
        "f1_macro": float(
            f1_score(y, predictions, average="macro", zero_division=0)
        ),
        "classification_report": classification_report(
            y,
            predictions,
            output_dict=True,
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(y, predictions).tolist(),
    }