"""
Major Pydantic Schemas
Models for major/CIP code selection
"""

from pydantic import BaseModel, Field
from typing import Optional


class MajorOption(BaseModel):
    """Major option for dropdown selection"""
    cip_code: str = Field(..., description="6-digit CIP code (e.g., 11.0701)")
    cip_title: str = Field(..., description="Major name")
    category: Optional[str] = Field(None, description="2-digit CIP category name")
    institutions_count: int = Field(0, description="Number of institutions offering this major")
    avg_median_earnings: Optional[int] = Field(None, description="Average median earnings (USD)")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "cip_code": "11.0701",
                "cip_title": "Computer Science",
                "category": "Computer and Information Sciences",
                "institutions_count": 450,
                "avg_median_earnings": 85000
            }
        }

