from datetime import date
import hashlib
import numpy as np
from .provider import SatelliteDataProvider
from ..preprocessing.indices import vegetation_indices

class DemoSatelliteDataProvider(SatelliteDataProvider):
    name = "demo"
    def analyze(self, latitude, longitude, start: date, end: date, cloud_threshold):
        seed = int(hashlib.sha256(f"{latitude:.3f}|{longitude:.3f}|{start}|{end}".encode()).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        count = max(4, min(12, (end - start).days // 30))
        dates = np.linspace(0, (end - start).days, count, dtype=int)
        red = np.clip(0.16 - np.linspace(0, .055, count) + rng.normal(0, .008, count), .06, .30)
        nir = np.clip(0.28 + np.linspace(0, .23, count) + rng.normal(0, .018, count), .10, .75)
        blue, green = np.full(count, .07), np.clip(red * 1.25, .08, .4)
        indices = vegetation_indices(red, nir, blue, green)
        series = [{"date": str(start.fromordinal(start.toordinal() + int(day))), "ndvi": round(indices["ndvi"][i], 3), "evi": round(indices["evi"][i], 3), "ndwi": round(indices["ndwi"][i], 3)} for i, day in enumerate(dates)]
        return {"provider": "demo", "demo": True, "data_notice": "DEMO DATA — generated reflectance and indices; no Sentinel-2 observations retrieved.", "collection": "COPERNICUS/S2_SR_HARMONIZED (target collection)", "cloud_threshold": cloud_threshold, "imagery_status": "Simulated sample sequence", "acquisitions": count, "mean_cloud_percent": round(float(rng.uniform(0, max(.01, cloud_threshold))), 1), "series": series, "features": {"ndvi_mean": float(np.mean(indices["ndvi"])), "ndvi_max": float(np.max(indices["ndvi"])), "ndvi_min": float(np.min(indices["ndvi"])), "ndvi_trend": float(indices["ndvi"][-1]-indices["ndvi"][0]), "evi_mean": float(np.mean(indices["evi"])), "ndwi_mean": float(np.mean(indices["ndwi"])), "red_mean": float(red.mean()), "nir_mean": float(nir.mean()), "season_length_days": (end-start).days}}
