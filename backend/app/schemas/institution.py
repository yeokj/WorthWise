"""
Institution Pydantic Schemas
Models for institution/school selection
"""

from pydantic import BaseModel, Field
from typing import Optional


class InstitutionOption(BaseModel):
    """Institution option for dropdown selection"""
    id: int = Field(..., description="Institution UNITID")
    name: str = Field(..., description="Institution name")
    city: Optional[str] = Field(None, description="City")
    state_code: Optional[str] = Field(None, description="State code")
    ownership_label: Optional[str] = Field(None, description="Public/Private/For-profit")
    tuition_in_state: Optional[int] = Field(None, description="In-state tuition and fees (USD/year)")
    tuition_out_state: Optional[int] = Field(None, description="Out-of-state tuition and fees (USD/year)")
    avg_net_price_public: Optional[int] = Field(None, description="Average net price for public institutions (USD/year)")
    avg_net_price_private: Optional[int] = Field(None, description="Average net price for private institutions (USD/year)")
    has_data: bool = Field(True, description="Has sufficient data for ROI calculation")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 110635,
                "name": "University of California-Berkeley",
                "city": "Berkeley",
                "state_code": "CA",
                "ownership_label": "Public",
                "tuition_in_state": 14254,
                "tuition_out_state": 44008,
                "avg_net_price_public": 16200,
                "avg_net_price_private": None,
                "has_data": True
            }
        }


class CampusOption(BaseModel):
    """Campus option for branch selection"""
    id: int = Field(..., description="Campus ID")
    institution_id: int = Field(..., description="Parent institution UNITID")
    campus_name: str = Field(..., description="Campus name")
    city: Optional[str] = Field(None, description="City")
    state_code: Optional[str] = Field(None, description="State code")
    is_main: bool = Field(..., description="Is main campus")
    is_active: bool = Field(..., description="Currently active")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "institution_id": 110635,
                "campus_name": "Main Campus",
                "city": "Berkeley",
                "state_code": "CA",
                "is_main": True,
                "is_active": True
            }
        }

