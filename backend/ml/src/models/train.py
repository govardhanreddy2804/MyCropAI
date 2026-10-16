from sklearn.base import ClassifierMixin


def train_model(
    model: ClassifierMixin,
    X_train,
    y_train,
):
    model.fit(
        X_train,
        y_train,
    )

    return model