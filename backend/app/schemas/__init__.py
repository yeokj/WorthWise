"""
Pydantic Schemas for API Validation
Request and response models
"""

from app.schemas.common import HealthResponse, DataVersionResponse
from app.schemas.institution import InstitutionOption, CampusOption
from app.schemas.major import MajorOption
from app.schemas.region import RegionOption
from app.schemas.compute import ComputeRequest, ComputeResponse, KPIResult
from app.schemas.compare import CompareRequest, CompareResponse, ScenarioComparison

__all__ = [
    "HealthResponse",
    "DataVersionResponse",
    "InstitutionOption",
    "CampusOption",
    "MajorOption",
    "RegionOption",
    "ComputeRequest",
    "ComputeResponse",
    "KPIResult",
    "CompareRequest",
    "CompareResponse",
    "ScenarioComparison",
]

