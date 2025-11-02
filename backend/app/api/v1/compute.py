"""
Compute Endpoints
ROI and KPI computation for scenarios
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from app.database import get_db
from app.duckdb_client import get_duckdb, DuckDBClient
from app.services.analytics_service import AnalyticsService
from app.schemas.compute import ComputeRequest, ComputeResponse
from app.schemas.compare import CompareRequest, CompareResponse, ScenarioComparison
from app.models import Institution, CIPCode, DataVersion
from app.utils.exceptions import DataNotFoundException

router = APIRouter()


def get_data_versions_dict(db: Session) -> Dict[str, str]:
    """Helper to get active data versions as dictionary"""
    versions = db.query(DataVersion).filter(
        DataVersion.status == "active"
    ).all()
    
    return {
        v.dataset_name: v.version_identifier
        for v in versions
    }


@router.post("/compute", response_model=ComputeResponse)
async def compute_roi(
    request: ComputeRequest,
    db: Session = Depends(get_db),
    duckdb: DuckDBClient = Depends(get_duckdb)
):
    """
    Compute ROI and KPIs for a single scenario
    
    Takes institution, major, and user assumptions as input.
    Returns comprehensive financial metrics.
    """
    # Initialize analytics service
    analytics = AnalyticsService(duckdb)
    
    try:
        # Compute KPIs
        kpis, assumptions, warnings = analytics.compute_kpis(db, request)
        
        # Get data versions
        data_versions = get_data_versions_dict(db)
        
        return ComputeResponse(
            scenario=request,
            kpis=kpis,
            assumptions=assumptions,
            data_versions=data_versions,
            warnings=warnings
        )
        
    except DataNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Computation failed: {str(e)}"
        )


@router.post("/compare", response_model=CompareResponse)
async def compare_scenarios(
    request: CompareRequest,
    db: Session = Depends(get_db),
    duckdb: DuckDBClient = Depends(get_duckdb)
):
    """
    Compare multiple scenarios (up to 4)
    
    Computes KPIs for each scenario and returns side-by-side comparison
    """
    analytics = AnalyticsService(duckdb)
    comparisons = []
    
    for idx, scenario in enumerate(request.scenarios):
        try:
            # Get institution and major names
            institution = db.query(Institution).filter(
                Institution.id == scenario.institution_id
            ).first()
            
            cip = db.query(CIPCode).filter(
                CIPCode.cip_code == scenario.cip_code
            ).first()
            
            institution_name = institution.name if institution else f"Institution {scenario.institution_id}"
            major_name = cip.cip_title if cip else f"Major {scenario.cip_code}"
            
            # Compute KPIs for this scenario
            kpis, _, warnings = analytics.compute_kpis(db, scenario)
            
            comparisons.append(ScenarioComparison(
                scenario_index=idx,
                institution_name=institution_name,
                major_name=major_name,
                scenario=scenario,
                kpis=kpis,
                warnings=warnings
            ))
            
        except DataNotFoundException as e:
            # Add placeholder for failed scenario
            comparisons.append(ScenarioComparison(
                scenario_index=idx,
                institution_name="Unknown",
                major_name="Unknown",
                scenario=scenario,
                kpis=None,  # Will need to handle this in schema
                warnings=[f"Failed to compute: {str(e)}"]
            ))
        except Exception as e:
            comparisons.append(ScenarioComparison(
                scenario_index=idx,
                institution_name="Unknown",
                major_name="Unknown",
                scenario=scenario,
                kpis=None,
                warnings=[f"Computation error: {str(e)}"]
            ))
    
    # Get data versions
    data_versions = get_data_versions_dict(db)
    
    return CompareResponse(
        comparisons=comparisons,
        data_versions=data_versions
    )

