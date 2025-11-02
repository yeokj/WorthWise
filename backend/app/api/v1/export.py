"""
Export Endpoints
CSV export for scenarios and comparisons
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from app.database import get_db
from app.duckdb_client import get_duckdb, DuckDBClient
from app.services.analytics_service import AnalyticsService
from app.services.export_service import ExportService
from app.schemas.compute import ComputeRequest, ComputeResponse
from app.schemas.compare import CompareRequest, CompareResponse
from app.api.v1.compute import compute_roi, compare_scenarios

router = APIRouter()


@router.get("/scenario.csv")
async def export_scenario(
    # All parameters from ComputeRequest as query parameters
    institution_id: int,
    cip_code: str,
    credential_level: int = 3,
    housing_type: str = "1BR",
    roommate_count: int = 0,
    postgrad_region_id: int = None,
    rent_monthly: int = None,
    utilities_monthly: int = None,
    food_monthly: int = None,
    transport_monthly: int = None,
    books_annual: int = None,
    misc_monthly: int = None,
    aid_annual: int = 0,
    cash_annual: int = 0,
    loan_apr: float = 0.0529,
    effective_tax_rate: float = 0.15,
    db: Session = Depends(get_db),
    duckdb: DuckDBClient = Depends(get_duckdb)
) -> StreamingResponse:
    """
    Export single scenario to CSV
    
    Takes same parameters as /compute endpoint via query string
    Returns CSV file download
    """
    # Create request object
    request = ComputeRequest(
        institution_id=institution_id,
        cip_code=cip_code,
        credential_level=credential_level,
        housing_type=housing_type,
        roommate_count=roommate_count,
        postgrad_region_id=postgrad_region_id,
        rent_monthly=rent_monthly,
        utilities_monthly=utilities_monthly,
        food_monthly=food_monthly,
        transport_monthly=transport_monthly,
        books_annual=books_annual,
        misc_monthly=misc_monthly,
        aid_annual=aid_annual,
        cash_annual=cash_annual,
        loan_apr=loan_apr,
        effective_tax_rate=effective_tax_rate
    )
    
    # Compute KPIs
    response = await compute_roi(request, db, duckdb)
    
    # Generate CSV
    return ExportService.generate_scenario_csv(response)


@router.post("/compare.csv")
async def export_comparison(
    request: CompareRequest,
    db: Session = Depends(get_db),
    duckdb: DuckDBClient = Depends(get_duckdb)
) -> StreamingResponse:
    """
    Export scenario comparison to CSV
    
    Takes same body as /compare endpoint
    Returns CSV file download
    """
    # Compute comparisons
    response = await compare_scenarios(request, db, duckdb)
    
    # Generate CSV
    return ExportService.generate_comparison_csv(response)

