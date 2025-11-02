"""
Compute Pydantic Schemas
Models for single scenario ROI computation
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List, Any


class ComputeRequest(BaseModel):
    """Request model for computing ROI for a single scenario"""
    
    # Institution and program
    institution_id: int = Field(..., description="Institution UNITID", gt=0)
    cip_code: str = Field(..., description="6-digit CIP code", pattern=r"^\d{2}\.\d{4}$")
    credential_level: int = Field(default=3, description="Credential level: 1=Certificate, 2=Associate, 3=Bachelor's", ge=1, le=6)
    
    # Tuition residency
    is_instate: bool = Field(default=True, description="In-state resident (for public institutions)")
    
    # Housing
    housing_type: str = Field(default="1BR", description="Housing type: none, studio, 1BR, 2BR, 3BR, 4BR")
    roommate_count: int = Field(default=0, description="Number of roommates (ignored if housing_type is 'none')", ge=0, le=10)
    
    # Post-graduation
    postgrad_region_id: Optional[int] = Field(None, description="Post-graduation region ID for cost-of-living adjustment")
    
    # User-provided budgets (monthly USD)
    rent_monthly: Optional[int] = Field(None, description="Override monthly rent (if not using FMR)", ge=0)
    utilities_monthly: Optional[int] = Field(None, description="Override monthly utilities", ge=0)
    food_monthly: Optional[int] = Field(None, description="Override monthly food budget", ge=0)
    transport_monthly: Optional[int] = Field(None, description="Override monthly transportation", ge=0)
    books_annual: Optional[int] = Field(None, description="Override annual books cost", ge=0)
    misc_monthly: Optional[int] = Field(None, description="Override monthly miscellaneous", ge=0)
    
    # Financial aid and savings
    aid_annual: int = Field(default=0, description="Annual grants/scholarships (non-loan aid)", ge=0)
    cash_annual: int = Field(default=0, description="Annual cash contribution (savings/family)", ge=0)
    
    # Loan terms
    loan_apr: float = Field(default=0.0, description="Annual loan interest rate (decimal)", ge=0, le=1)
    
    # Tax rate
    effective_tax_rate: float = Field(default=0.0, description="Effective tax rate (decimal)", ge=0, le=1)
    
    @field_validator("housing_type")
    @classmethod
    def validate_housing_type(cls, v):
        valid_types = ["none", "studio", "0BR", "1BR", "2BR", "3BR", "4BR"]
        if v not in valid_types:
            raise ValueError(f"housing_type must be one of {valid_types}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "institution_id": 110635,
                "cip_code": "11.0701",
                "credential_level": 3,
                "housing_type": "1BR",
                "roommate_count": 1,
                "postgrad_region_id": 5,
                "rent_monthly": None,
                "utilities_monthly": 150,
                "food_monthly": 400,
                "transport_monthly": 100,
                "books_annual": 1200,
                "misc_monthly": 200,
                "aid_annual": 5000,
                "cash_annual": 10000,
                "loan_apr": 0.0529,
                "effective_tax_rate": 0.15
            }
        }


class KPIResult(BaseModel):
    """Key Performance Indicators for a scenario"""
    
    # Cost metrics
    true_yearly_cost: int = Field(..., description="Total annual cost including all living expenses (USD)")
    tuition_fees: int = Field(..., description="Annual tuition and fees (USD)")
    housing_annual: int = Field(..., description="Annual housing cost (USD)")
    other_expenses: int = Field(..., description="Other annual expenses (USD)")
    
    # Debt metrics
    expected_debt_at_grad: int = Field(..., description="Expected total debt at graduation (USD)")
    
    # Earnings projections
    earnings_year_1: Optional[int] = Field(None, description="Projected earnings year 1 post-grad (USD)")
    earnings_year_3: Optional[int] = Field(None, description="Projected earnings year 3 post-grad (USD)")
    earnings_year_5: Optional[int] = Field(None, description="Projected earnings year 5 post-grad (USD)")
    
    # ROI metrics
    roi: Optional[float] = Field(None, description="Return on investment (ratio)")
    payback_years: Optional[float] = Field(None, description="Years to pay back debt")
    dti_year_1: Optional[float] = Field(None, description="Debt-to-income ratio year 1 (ratio)")
    
    # Completion metrics
    graduation_rate: Optional[float] = Field(None, description="Graduation rate (0-1)")
    
    # Comfort index
    comfort_index: Optional[float] = Field(None, description="Financial comfort index (0-100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "true_yearly_cost": 35000,
                "tuition_fees": 14000,
                "housing_annual": 15000,
                "other_expenses": 6000,
                "expected_debt_at_grad": 28000,
                "earnings_year_1": 75000,
                "earnings_year_3": 95000,
                "earnings_year_5": 115000,
                "roi": 3.12,
                "payback_years": 4.5,
                "dti_year_1": 0.37,
                "graduation_rate": 0.92,
                "comfort_index": 78.5
            }
        }


class ComputeResponse(BaseModel):
    """Response model for compute endpoint"""
    scenario: ComputeRequest = Field(..., description="Input scenario parameters")
    kpis: KPIResult = Field(..., description="Computed KPIs")
    assumptions: Dict[str, Any] = Field(..., description="Assumptions used in calculations")
    data_versions: Dict[str, str] = Field(..., description="Dataset versions used")
    warnings: List[str] = Field(default_factory=list, description="Warnings about data quality or fallbacks")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario": {"institution_id": 110635, "cip_code": "11.0701"},
                "kpis": {"true_yearly_cost": 35000, "expected_debt_at_grad": 28000},
                "assumptions": {"program_years": 4, "default_food_monthly": 400},
                "data_versions": {"college_scorecard": "2024-09-15", "hud_fmr": "FY2026"},
                "warnings": []
            }
        }

