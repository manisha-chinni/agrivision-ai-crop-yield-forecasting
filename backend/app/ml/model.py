import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

FEATURES = ["ndvi_mean", "ndvi_max", "ndvi_trend", "evi_mean", "ndwi_mean", "red_mean", "nir_mean", "season_length_days", "crop_code"]
CROP_CODES = {"Rice": 0, "Wheat": 1, "Maize": 2, "Cotton": 3, "Soybean": 4}

def _synthetic_training_data():
    rng = np.random.default_rng(2025)
    n = 500
    x = np.column_stack([rng.uniform(.2,.85,n), rng.uniform(.35,.95,n), rng.uniform(-.2,.35,n), rng.uniform(.1,.6,n), rng.uniform(-.3,.4,n), rng.uniform(.05,.25,n), rng.uniform(.2,.7,n), rng.integers(90,330,n), rng.integers(0,5,n)])
    y = 1.5 + 5.2*x[:,0] + 1.4*x[:,2] + .003*x[:,7] + np.take([.3,.1,.6,-.2,.25], x[:,8].astype(int)) + rng.normal(0,.48,n)
    return x, y

class YieldModel:
    def __init__(self):
        x, y = _synthetic_training_data()
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.2, random_state=42)
        self.model = RandomForestRegressor(n_estimators=120, min_samples_leaf=2, random_state=42, n_jobs=1)
        self.model.fit(x_train, y_train)
        pred = self.model.predict(x_test)
        self.metrics = {"mae": float(mean_absolute_error(y_test,pred)), "rmse": float(np.sqrt(mean_squared_error(y_test,pred))), "r2": float(r2_score(y_test,pred)), "observations": 500, "evaluation": "Seeded synthetic demo holdout (100 rows); not real-world validation", "split": "80/20 random split", "training_date": "Recomputed at application startup"}
        self.evaluation_points = [{"actual": round(float(a), 2), "predicted": round(float(p), 2)} for a, p in zip(y_test[:16], pred[:16])]

    def predict(self, features, crop):
        row = np.array([[features[k] for k in FEATURES[:-1]] + [CROP_CODES[crop]]], dtype=float)
        value = float(self.model.predict(row)[0])
        tree_predictions = np.array([tree.predict(row)[0] for tree in self.model.estimators_])
        spread = float(np.std(tree_predictions))
        importances = dict(zip(FEATURES, self.model.feature_importances_))
        top = sorted(importances.items(), key=lambda pair: pair[1], reverse=True)[:5]
        return {"predicted_yield": round(max(0, value), 2), "unit": "tons/ha", "model": "Random Forest Regressor", "status": "Demo Prediction", "range": [round(max(0,value-1.96*spread),2),round(max(0,value+1.96*spread),2)], "range_note": "Tree-to-tree spread; not calibrated uncertainty", "features": [{"name": k, "importance": round(float(v), 4)} for k,v in top]}

model = YieldModel()
