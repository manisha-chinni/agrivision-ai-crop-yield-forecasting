import numpy as np

def _safe_ratio(numerator, denominator):
    a, b = np.asarray(numerator, dtype=float), np.asarray(denominator, dtype=float)
    return np.divide(a, b, out=np.zeros(np.broadcast_shapes(a.shape, b.shape)), where=np.abs(b) > 1e-8)

def vegetation_indices(red, nir, blue=None, green=None, soil_factor=0.5):
    result = {"ndvi": _safe_ratio(np.asarray(nir) - red, np.asarray(nir) + red)}
    if blue is not None:
        result["evi"] = 2.5 * _safe_ratio(np.asarray(nir) - red, np.asarray(nir) + 6 * np.asarray(red) - 7.5 * np.asarray(blue) + 1)
    result["savi"] = (1 + soil_factor) * _safe_ratio(np.asarray(nir) - red, np.asarray(nir) + red + soil_factor)
    if green is not None:
        result["ndwi"] = _safe_ratio(np.asarray(green) - nir, np.asarray(green) + nir)
    return {k: np.asarray(v).tolist() for k, v in result.items()}

def summarize_series(values):
    a = np.asarray(values, dtype=float)
    if a.size == 0 or not np.isfinite(a).all():
        raise ValueError("Index series must contain finite values")
    return {"mean": float(a.mean()), "min": float(a.min()), "max": float(a.max()), "trend": float(a[-1] - a[0])}
