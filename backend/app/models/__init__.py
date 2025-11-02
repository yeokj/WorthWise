"""
SQLAlchemy ORM Models
Maps Python classes to database tables
"""

from app.models.state import State
from app.models.institution import Institution
from app.models.cip_code import CIPCode
from app.models.region import Region
from app.models.campus import Campus
from app.models.etl import DataVersion, ETLRun, DataQualityCheck
from app.models.search_cache import InstitutionSearchCache, MajorSearchCache
from app.models.system import SystemConfig

__all__ = [
    "State",
    "Institution",
    "CIPCode",
    "Region",
    "Campus",
    "DataVersion",
    "ETLRun",
    "DataQualityCheck",
    "InstitutionSearchCache",
    "MajorSearchCache",
    "SystemConfig",
]

