"""
Region Model
Geographic regions for post-graduation location selection
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class RegionType(str, enum.Enum):
    """Region type enumeration"""
    NATIONAL = "national"
    STATE = "state"
    METRO = "metro"
    COUNTY = "county"
    CENSUS_REGION = "census_region"


class Region(Base):
    __tablename__ = "regions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    geo_fips = Column(String(10), index=True, comment="FIPS code for geography")
    region_name = Column(String(150), nullable=False, comment="Region display name")
    region_type = Column(
        Enum(RegionType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
        comment="Geographic level"
    )
    state_code = Column(
        String(2),
        ForeignKey("states.state_code"),
        index=True,
        comment="Associated state code"
    )
    parent_region_id = Column(
        Integer,
        ForeignKey("regions.id"),
        comment="Parent region for hierarchy"
    )
    
    # Display and filtering
    display_order = Column(Integer, default=999, index=True, comment="Sort order for UI dropdowns")
    is_active = Column(Boolean, default=True, index=True, comment="Show in UI selectors")
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    # Relationships
    state = relationship("State", foreign_keys=[state_code])
    parent_region = relationship("Region", remote_side=[id], foreign_keys=[parent_region_id])
    
    def __repr__(self):
        return f"<Region(id={self.id}, name={self.region_name}, type={self.region_type})>"

