from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


def get_candidate_models(random_state: int = 42):
    return {
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            random_state=random_state,
            n_jobs=-1,
        ),
        "decision_tree": DecisionTreeClassifier(
            random_state=random_state,
        ),
        "gaussian_nb": GaussianNB(),
        "svm": make_pipeline(
            StandardScaler(),
            SVC(),
        ),
    }