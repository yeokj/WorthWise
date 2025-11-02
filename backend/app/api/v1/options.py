"""
Options Endpoints
Provide dropdown options for UI selectors
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Institution, CIPCode, Region, Campus, DataVersion
from app.schemas.institution import InstitutionOption, CampusOption
from app.schemas.major import MajorOption
from app.schemas.region import RegionOption
from app.schemas.common import DataVersionResponse

router = APIRouter()


@router.get("/schools", response_model=List[InstitutionOption])
async def get_schools(
    state: Optional[str] = Query(None, description="Filter by state code"),
    search: Optional[str] = Query(None, description="Search term for institution name"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Get list of schools/institutions for dropdown
    
    Optionally filter by state or search term
    """
    query = db.query(Institution).filter(
        Institution.operating == True,
        Institution.main_campus == True
    )
    
    # Apply filters
    if state:
        query = query.filter(Institution.state_code == state.upper())
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(Institution.name.ilike(search_term))
    
    # Order by name and limit
    query = query.order_by(Institution.name).limit(limit)
    
    institutions = query.all()
    
    # Convert to response model
    result = []
    for inst in institutions:
        ownership_map = {
            1: "Public",
            2: "Private Nonprofit",
            3: "Private For-Profit"
        }
        
        result.append(InstitutionOption(
            id=inst.id,
            name=inst.name,
            city=inst.city,
            state_code=inst.state_code,
            ownership_label=ownership_map.get(inst.ownership, "Unknown"),
            tuition_in_state=inst.tuition_in_state,
            tuition_out_state=inst.tuition_out_state,
            avg_net_price_public=inst.avg_net_price_public,
            avg_net_price_private=inst.avg_net_price_private,
            has_data=True  # Will be determined by search cache in full implementation
        ))
    
    return result


@router.get("/campuses", response_model=List[CampusOption])
async def get_campuses(
    institution_id: int = Query(..., description="Institution UNITID"),
    db: Session = Depends(get_db)
):
    """
    Get list of campuses for a given institution
    """
    campuses = db.query(Campus).filter(
        Campus.institution_id == institution_id,
        Campus.is_active == True
    ).order_by(
        Campus.is_main.desc(),  # Main campus first
        Campus.campus_name
    ).all()
    
    return [
        CampusOption(
            id=campus.id,
            institution_id=campus.institution_id,
            campus_name=campus.campus_name,
            city=campus.city,
            state_code=campus.state_code,
            is_main=campus.is_main,
            is_active=campus.is_active
        )
        for campus in campuses
    ]


@router.get("/majors", response_model=List[MajorOption])
async def get_majors(
    institution_id: Optional[int] = Query(None, description="Filter majors by institution"),
    category: Optional[str] = Query(None, description="Filter by 2-digit CIP category"),
    search: Optional[str] = Query(None, description="Search term for major name"),
    limit: int = Query(500, ge=1, le=1000, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Get list of majors/CIP codes for dropdown
    
    When institution_id is provided, only returns majors offered by that institution.
    Otherwise returns all majors, optionally filtered by category or search term.
    """
    from app.duckdb_client import get_duckdb
    
    # If institution_id is provided, query DuckDB for majors at that institution
    if institution_id:
        duckdb = get_duckdb()
        
        try:
            # Get distinct CIP codes offered by this institution from programs table
            sql = """
                SELECT DISTINCT 
                    cip_code,
                    cip_description,
                    COUNT(*) as program_count,
                    AVG(earnings_1yr) as avg_earnings_1yr
                FROM programs
                WHERE institution_id = ?
                GROUP BY cip_code, cip_description
                ORDER BY cip_description
            """
            
            programs_data = duckdb.query(sql, (institution_id,))
            
            if not programs_data:
                # Institution has no programs in database
                return []
            
            # Extract CIP codes from DuckDB results
            available_cip_codes = [row[0] for row in programs_data]
            
            # Query MySQL for CIP code details
            query = db.query(CIPCode).filter(CIPCode.cip_code.in_(available_cip_codes))
            
            # Apply additional filters
            if category:
                query = query.filter(CIPCode.cip_2digit == category)
            
            if search:
                search_term = f"%{search}%"
                query = query.filter(CIPCode.cip_title.ilike(search_term))
            
            # Order and limit
            query = query.order_by(CIPCode.cip_title).limit(limit)
            cip_codes = query.all()
            
            # Build results with program count and earnings from DuckDB
            programs_dict = {row[0]: (row[2], row[3]) for row in programs_data}
            
            return [
                MajorOption(
                    cip_code=cip.cip_code,
                    cip_title=cip.cip_title,
                    category=cip.cip_2digit_title,
                    institutions_count=programs_dict.get(cip.cip_code, (0, None))[0],
                    avg_median_earnings=int(programs_dict.get(cip.cip_code, (0, None))[1]) 
                        if programs_dict.get(cip.cip_code, (0, None))[1] else None
                )
                for cip in cip_codes
            ]
            
        except Exception as e:
            print(f"Error fetching majors for institution {institution_id}: {e}")
            # Fallback to all majors if DuckDB query fails
            pass
    
    # Default behavior: return all majors (filtered by category/search if provided)
    query = db.query(CIPCode)
    
    # Apply filters
    if category:
        query = query.filter(CIPCode.cip_2digit == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(CIPCode.cip_title.ilike(search_term))
    
    # Order by title and limit
    query = query.order_by(CIPCode.cip_title).limit(limit)
    
    cip_codes = query.all()
    
    return [
        MajorOption(
            cip_code=cip.cip_code,
            cip_title=cip.cip_title,
            category=cip.cip_2digit_title,
            institutions_count=0,  # Will be populated by search cache
            avg_median_earnings=None  # Will be populated by search cache
        )
        for cip in cip_codes
    ]


@router.get("/regions", response_model=List[RegionOption])
async def get_regions(
    region_type: Optional[str] = Query(None, description="Filter by type: national, state, metro, county"),
    state: Optional[str] = Query(None, description="Filter by state code"),
    db: Session = Depends(get_db)
):
    """
    Get list of regions for post-graduation location selection
    """
    query = db.query(Region).filter(Region.is_active == True)
    
    # Apply filters
    if region_type:
        query = query.filter(Region.region_type == region_type)
    
    if state:
        query = query.filter(Region.state_code == state.upper())
    
    # Order by display order and name
    query = query.order_by(Region.display_order, Region.region_name)
    
    regions = query.all()
    
    return [
        RegionOption(
            id=region.id,
            region_name=region.region_name,
            region_type=region.region_type.value,
            state_code=region.state_code,
            geo_fips=region.geo_fips
        )
        for region in regions
    ]


@router.get("/versions", response_model=List[DataVersionResponse])
async def get_data_versions(db: Session = Depends(get_db)):
    """
    Get dataset versions currently in use
    
    Used to display data provenance in UI
    """
    versions = db.query(DataVersion).filter(
        DataVersion.status == "active"
    ).order_by(DataVersion.dataset_name).all()
    
    return [
        DataVersionResponse(
            dataset_name=v.dataset_name,
            version_identifier=v.version_identifier,
            version_date=v.version_date,
            row_count=v.row_count,
            loaded_at=v.loaded_at
        )
        for v in versions
    ]

