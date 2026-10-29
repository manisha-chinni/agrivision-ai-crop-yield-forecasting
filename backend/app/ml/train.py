from pathlib import Path
import joblib
from .model import _synthetic_training_data
from sklearn.ensemble import RandomForestRegressor

if __name__ == "__main__":
    x, y = _synthetic_training_data()
    estimator = RandomForestRegressor(n_estimators=120, min_samples_leaf=2, random_state=42, n_jobs=1).fit(x,y)
    target = Path(__file__).resolve().parents[3] / "models" / "random_forest.joblib"
    target.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(estimator, target)
    print(f"Saved synthetic-demo model: {target}")
