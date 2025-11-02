"""
Region Pydantic Schemas
Models for region/geographic selection
"""

from pydantic import BaseModel, Field
from typing import Optional


class RegionOption(BaseModel):
    """Region option for post-graduation location selection"""
    id: int = Field(..., description="Region ID")
    region_name: str = Field(..., description="Region display name")
    region_type: str = Field(..., description="Geographic level: national, state, metro, county")
    state_code: Optional[str] = Field(None, description="State code (if applicable)")
    geo_fips: Optional[str] = Field(None, description="FIPS code")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "region_name": "San Francisco Bay Area",
                "region_type": "metro",
                "state_code": "CA",
                "geo_fips": "06075"
            }
        }

