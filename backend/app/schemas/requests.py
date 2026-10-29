from datetime import date
from pydantic import BaseModel, Field, model_validator

CROPS = ["Rice", "Wheat", "Maize", "Cotton", "Soybean"]

class AnalysisRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    region: str = Field(min_length=2, max_length=100)
    crop: str
    start_date: date
    end_date: date
    cloud_threshold: int = Field(default=30, ge=0, le=100)

    @model_validator(mode="after")
    def validate_selection(self):
        if self.crop not in CROPS:
            raise ValueError(f"Unsupported crop. Choose from: {', '.join(CROPS)}")
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")
        if (self.end_date - self.start_date).days > 1100:
            raise ValueError("Analysis period cannot exceed 3 years")
        return self
