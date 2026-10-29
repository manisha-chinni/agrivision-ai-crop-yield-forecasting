from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from .config.settings import get_settings

app = FastAPI(title="AgriVision AI API", version="1.0.0", description="Satellite crop analytics demonstration; demo data is synthetic.")
app.add_middleware(CORSMiddleware, allow_origins=get_settings()["cors_origins"], allow_credentials=False, allow_methods=["GET","POST"], allow_headers=["Content-Type"])
app.include_router(router)

@app.get("/")
def root(): return {"name":"AgriVision AI","docs":"/docs","api":"/api"}
