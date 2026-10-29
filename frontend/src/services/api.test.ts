import {afterEach,describe,expect,it,vi} from 'vitest';
import {api} from './api';

afterEach(()=>vi.unstubAllGlobals());

describe('API client',()=>{
 it('submits a selected region and crop for deterministic demo prediction',async()=>{
  const payload={latitude:17.385,longitude:78.4867,region:'Telangana, India',crop:'Rice' as const,start_date:'2025-06-01',end_date:'2025-11-01',cloud_threshold:30};
  const prediction={predicted_yield:4.2,unit:'tons/ha',model:'Random Forest Regressor',status:'Demo Prediction',range:[3.8,4.6],range_note:'demo',features:[],demo:true,data_notice:'DEMO DATA',crop:'Rice',region:'Telangana, India',vegetation:{},model_evaluation:{mae:.4,rmse:.5,r2:.6,observations:500,evaluation:'synthetic'}};
  const fetchMock=vi.fn().mockResolvedValue({ok:true,json:async()=>prediction});vi.stubGlobal('fetch',fetchMock);
  const result=await api.predict(payload);
  expect(fetchMock).toHaveBeenCalledWith('/api/predict-yield',expect.objectContaining({method:'POST',body:JSON.stringify(payload)}));
  expect(result.status).toBe('Demo Prediction');expect(result.demo).toBe(true);
 });
 it('surfaces a human-readable API validation error',async()=>{
  vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,status:422,json:async()=>({detail:[{type:'value_error',loc:['body'],msg:'Value error, End date must be after start date'}]})}));
  await expect(api.analyze({latitude:0,longitude:0,region:'Test',crop:'Rice',start_date:'2025-06-01',end_date:'2025-05-01',cloud_threshold:30})).rejects.toThrow('End date must be after start date');
 });
 it('reports when the backend cannot be reached',async()=>{
  vi.stubGlobal('fetch',vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));
  await expect(api.health()).rejects.toThrow('Check that the FastAPI backend is running');
 });
});
