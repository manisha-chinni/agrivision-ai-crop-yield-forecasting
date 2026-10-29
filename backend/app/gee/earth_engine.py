from datetime import date
from .provider import SatelliteDataProvider

class EarthEngineProvider(SatelliteDataProvider):
    """Sentinel-2 SR adapter; summarizes a 5 km buffer around the selected point."""
    name = "gee"
    def __init__(self, project: str):
        self.project = project
        try:
            import ee
            ee.Initialize(project=project)
            self.ee = ee
        except Exception as exc:
            self.ee = None
            self.reason = "Earth Engine initialization failed. Check authentication and project configuration."
    def analyze(self, latitude: float, longitude: float, start: date, end: date, cloud_threshold: int) -> dict:
        if self.ee is None:
            raise RuntimeError(getattr(self, "reason", "Earth Engine is not configured. Set GOOGLE_EARTH_ENGINE_PROJECT and authenticate."))
        ee = self.ee
        try:
            region = ee.Geometry.Point([longitude, latitude]).buffer(5000)
            images = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(region).filterDate(start.isoformat(), end.isoformat())
                .filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", cloud_threshold))
                .sort("system:time_start").limit(60))
            count = int(images.size().getInfo())
            if count == 0:
                raise RuntimeError("No Sentinel-2 acquisitions match this point, date range, and cloud threshold. Try a wider date range or higher cloud limit.")

            def add_indices(image):
                scl = image.select("SCL")
                # Exclude saturated, shadow, cloud, cirrus and snow classes.
                mask = scl.neq(1).And(scl.neq(3)).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10)).And(scl.neq(11))
                reflectance = image.select(["B2", "B3", "B4", "B8"]).multiply(0.0001).updateMask(mask)
                blue, green, red, nir = [reflectance.select(b) for b in ["B2", "B3", "B4", "B8"]]
                ndvi = nir.subtract(red).divide(nir.add(red)).rename("NDVI")
                evi = image.expression("2.5 * ((n-r) / (n + 6*r - 7.5*b + 1))", {"n": nir, "r": red, "b": blue}).rename("EVI")
                ndwi = green.subtract(nir).divide(green.add(nir)).rename("NDWI")
                return reflectance.addBands([ndvi, evi, ndwi]).select(["B2", "B3", "B4", "B8", "NDVI", "EVI", "NDWI"]).copyProperties(image, ["system:time_start", "CLOUDY_PIXEL_PERCENTAGE"])

            processed = images.map(add_indices)
            ndvi_composite = processed.select("NDVI").median().clip(region)
            ndvi_map = ndvi_composite.getMapId({"min": 0, "max": 0.8, "palette": ["b98e64", "d4cd7d", "82ad68", "2f7450"]})
            ndvi_tile_url = ndvi_map["tile_fetcher"].url_format
            stats = processed.map(lambda image: image.set("region_stats", image.reduceRegion(reducer=ee.Reducer.mean(), geometry=region, scale=20, maxPixels=1e8)))
            rows = stats.aggregate_array("region_stats").getInfo()
            timestamps = processed.aggregate_array("system:time_start").getInfo()
            clouds = images.aggregate_array("CLOUDY_PIXEL_PERCENTAGE").getInfo()
            series = []
            for timestamp, row in zip(timestamps, rows):
                if row and all(row.get(k) is not None for k in ["NDVI", "EVI", "NDWI", "B4", "B8"]):
                    from datetime import datetime, timezone
                    series.append({"date": datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).date().isoformat(), "ndvi": round(row["NDVI"], 4), "evi": round(row["EVI"], 4), "ndwi": round(row["NDWI"], 4), "red": row["B4"], "nir": row["B8"]})
            if not series:
                raise RuntimeError("Sentinel-2 scenes were found, but cloud masking left no usable pixels in the selected buffer.")
            ndvi_values = [p["ndvi"] for p in series]
            evi_values = [p["evi"] for p in series]
            ndwi_values = [p["ndwi"] for p in series]
            red_values = [p["red"] for p in series]
            nir_values = [p["nir"] for p in series]
            return {"provider": "gee", "demo": False, "data_notice": "Live Sentinel-2 surface-reflectance statistics from Google Earth Engine; 5 km buffer around the selected point.", "collection": "COPERNICUS/S2_SR_HARMONIZED", "cloud_threshold": cloud_threshold, "imagery_status": "Sentinel-2 imagery retrieved", "ndvi_tile_url": ndvi_tile_url, "acquisitions": len(series), "mean_cloud_percent": round(sum(clouds) / max(1, len(clouds)), 1), "series": [{k: v for k, v in p.items() if k in ("date", "ndvi", "evi", "ndwi")} for p in series], "features": {"ndvi_mean": sum(ndvi_values) / len(ndvi_values), "ndvi_max": max(ndvi_values), "ndvi_min": min(ndvi_values), "ndvi_trend": ndvi_values[-1] - ndvi_values[0], "evi_mean": sum(evi_values) / len(evi_values), "ndwi_mean": sum(ndwi_values) / len(ndwi_values), "red_mean": sum(red_values) / len(red_values), "nir_mean": sum(nir_values) / len(nir_values), "season_length_days": (end-start).days}}
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError("Earth Engine could not retrieve regional Sentinel-2 statistics. Check project access, authentication, and request limits.") from exc
