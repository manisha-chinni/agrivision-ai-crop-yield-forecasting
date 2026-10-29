from fastapi import APIRouter, HTTPException
from functools import lru_cache
from ..schemas.requests import AnalysisRequest, CROPS
from ..config.settings import get_settings
from ..gee.demo import DemoSatelliteDataProvider
from ..gee.earth_engine import EarthEngineProvider
from ..ml.model import model, FEATURES
from ..preprocessing.indices import summarize_series

router = APIRouter(prefix="/api")
settings = get_settings()
provider_fallback_reason = None
if settings["provider"] == "gee":
    gee_provider = EarthEngineProvider(settings["gee_project"])
    if gee_provider.ee is None:
        provider = DemoSatelliteDataProvider()
        provider_fallback_reason = gee_provider.reason
    else:
        provider = gee_provider
else:
    provider = DemoSatelliteDataProvider()

REGIONS = [
 {"name":"Telangana, India","latitude":17.385,"longitude":78.4867,"kind":"Demo centroid"},
 {"name":"Punjab, India","latitude":30.7333,"longitude":76.7794,"kind":"Demo centroid"},
 {"name":"Maharashtra, India","latitude":19.7515,"longitude":75.7139,"kind":"Demo centroid"},
 {"name":"Karnataka, India","latitude":15.3173,"longitude":75.7139,"kind":"Demo centroid"},
]

@lru_cache(maxsize=64)
def cached_satellite_data(latitude, longitude, start_date, end_date, cloud_threshold):
    return provider.analyze(latitude, longitude, start_date, end_date, cloud_threshold)

@router.get("/health")
async def health(): return {"status":"ok", "provider":provider.name, "demo":provider.name == "demo", "fallback_reason":provider_fallback_reason}

@router.get("/crops")
async def crops(): return {"crops":CROPS}

def do_analysis(req):
    try:
        result = dict(cached_satellite_data(req.latitude, req.longitude, req.start_date, req.end_date, req.cloud_threshold))
        result.update({"region":req.region,"latitude":req.latitude,"longitude":req.longitude,"crop":req.crop,"start_date":str(req.start_date),"end_date":str(req.end_date)})
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

@router.post("/satellite/search")
async def satellite_search(req: AnalysisRequest):
    result=do_analysis(req)
    return {"provider":provider.name,"demo":result["demo"],"regions":REGIONS,"imagery_status":result["imagery_status"],"acquisitions":result["acquisitions"],"collection":result["collection"],"start_date":result["start_date"],"end_date":result["end_date"]}

@router.post("/satellite/analyze")
async def satellite_analyze(req: AnalysisRequest): return do_analysis(req)

@router.post("/features/extract")
async def features_extract(req: AnalysisRequest):
    result=do_analysis(req)
    result["feature_names"]=FEATURES
    return result

@router.post("/predict-yield")
async def predict_yield(req: AnalysisRequest):
    result=do_analysis(req)
    forecast=model.predict(result["features"], req.crop)
    return {**forecast,"demo":True,"satellite_demo":result["demo"],"data_notice":f"DEMO PREDICTION — model trained on synthetic yield labels. Satellite features: {result['data_notice']}","crop":req.crop,"region":req.region,"vegetation":result["features"],"model_evaluation":model.metrics}

@router.get("/model/info")
async def model_info(): return {"name":"Random Forest Regressor","version":"demo-synthetic-v1","features":FEATURES,"training_data":"500 generated synthetic rows","demo":True}

@router.get("/model/metrics")
async def model_metrics(): return {**model.metrics,"demo":True,"unit":"tons/ha","evaluation_points":model.evaluation_points}

@router.get("/model/features")
async def model_features(): return {"features":FEATURES,"importances":[{"name":n,"importance":float(v)} for n,v in sorted(zip(FEATURES,model.model.feature_importances_),key=lambda p:p[1],reverse=True)],"demo":True}

@router.get("/demo/sample")
async def demo_sample():
    req=AnalysisRequest(latitude=17.385,longitude=78.4867,region="Telangana, India",crop="Rice",start_date="2025-06-01",end_date="2025-11-01",cloud_threshold=30)
    analysis=do_analysis(req)
    forecast={**model.predict(analysis["features"],req.crop),"demo":True,"satellite_demo":analysis["demo"],"data_notice":f"DEMO PREDICTION — model trained on synthetic yield labels. Satellite features: {analysis['data_notice']}","crop":req.crop,"region":req.region,"vegetation":analysis["features"],"model_evaluation":model.metrics}
    return {"analysis":analysis,"prediction":forecast,"regions":REGIONS}
