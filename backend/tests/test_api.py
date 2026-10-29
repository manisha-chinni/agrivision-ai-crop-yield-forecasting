import asyncio
import httpx
from app.main import app
from app.preprocessing.indices import vegetation_indices

async def call(method, path, **kwargs):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.request(method, path, **kwargs)

def request(method, path, **kwargs):
    return asyncio.run(call(method, path, **kwargs))

def payload(): return {"latitude":17.385,"longitude":78.4867,"region":"Telangana, India","crop":"Rice","start_date":"2025-06-01","end_date":"2025-11-01","cloud_threshold":30}

def test_health_and_demo_prediction():
    assert request('GET','/api/health').json()['status']=='ok'
    result=request('POST','/api/predict-yield',json=payload())
    assert result.status_code==200
    data=result.json()
    assert data['status']=='Demo Prediction' and data['demo'] is True
    assert data['unit']=='tons/ha' and data['predicted_yield'] > 0

def test_validation_errors():
    bad=payload(); bad['latitude']=99
    assert request('POST','/api/satellite/analyze',json=bad).status_code==422
    bad=payload(); bad['crop']='Coffee'
    assert request('POST','/api/satellite/analyze',json=bad).status_code==422
    bad=payload(); bad['end_date']='2025-05-01'
    assert request('POST','/api/satellite/analyze',json=bad).status_code==422

def test_ndvi():
    result=vegetation_indices([.2],[.6],blue=[.05],green=[.3])
    assert abs(result['ndvi'][0]-.5)<1e-9
    assert 'evi' in result and 'ndwi' in result and 'savi' in result

def test_model_metrics_are_computed():
    metrics=request('GET','/api/model/metrics').json()
    assert metrics['observations']==500 and metrics['mae']>=0 and metrics['rmse']>=0
    assert 'synthetic' in metrics['evaluation']
