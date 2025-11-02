"""
Compare Pydantic Schemas
Models for comparing multiple scenarios
"""

from pydantic import BaseModel, Field, field_validator
from typing import List
from app.schemas.compute import ComputeRequest, KPIResult


class CompareRequest(BaseModel):
    """Request model for comparing up to 4 scenarios"""
    scenarios: List[ComputeRequest] = Field(..., description="List of scenarios to compare (1-4)")
    
    @field_validator("scenarios")
    @classmethod
    def validate_scenarios_count(cls, v):
        if len(v) < 1:
            raise ValueError("At least 1 scenario is required")
        if len(v) > 4:
            raise ValueError("Maximum 4 scenarios allowed")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenarios": [
                    {"institution_id": 110635, "cip_code": "11.0701"},
                    {"institution_id": 243744, "cip_code": "11.0701"}
                ]
            }
        }


class ScenarioComparison(BaseModel):
    """Comparison result for a single scenario"""
    scenario_index: int = Field(..., description="Scenario index (0-3)")
    institution_name: str = Field(..., description="Institution name")
    major_name: str = Field(..., description="Major name")
    scenario: ComputeRequest = Field(..., description="Input parameters")
    kpis: KPIResult = Field(..., description="Computed KPIs")
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario_index": 0,
                "institution_name": "University of California-Berkeley",
                "major_name": "Computer Science",
                "scenario": {"institution_id": 110635, "cip_code": "11.0701"},
                "kpis": {"true_yearly_cost": 35000, "expected_debt_at_grad": 28000},
                "warnings": []
            }
        }


class CompareResponse(BaseModel):
    """Response model for compare endpoint"""
    comparisons: List[ScenarioComparison] = Field(..., description="Comparison results for each scenario")
    data_versions: dict = Field(..., description="Dataset versions used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "comparisons": [
                    {
                        "scenario_index": 0,
                        "institution_name": "UC Berkeley",
                        "major_name": "Computer Science",
                        "kpis": {"true_yearly_cost": 35000}
                    }
                ],
                "data_versions": {"college_scorecard": "2024-09-15"}
            }
        }

