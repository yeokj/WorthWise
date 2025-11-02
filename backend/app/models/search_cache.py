"""
Search Cache Models
Pre-computed search data for autocomplete and selection
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class InstitutionSearchCache(Base):
    """Pre-computed search data for institution autocomplete"""
    __tablename__ = "institution_search_cache"
    
    institution_id = Column(
        Integer,
        ForeignKey("institutions.id", ondelete="CASCADE"),
        primary_key=True
    )
    search_text = Column(String(500), nullable=False, comment="Concatenated searchable text")
    display_text = Column(String(255), nullable=False, comment="Formatted display name")
    state_code = Column(String(2))
    ownership_label = Column(String(50))
    programs_count = Column(Integer, default=0, comment="Number of programs offered")
    has_data = Column(Boolean, default=True, comment="Has sufficient data for calculations")
    sort_priority = Column(Integer, default=999, index=True, comment="Search result ranking")
    
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    # Relationships
    institution = relationship("Institution", back_populates="search_cache")
    
    def __repr__(self):
        return f"<InstitutionSearchCache(institution_id={self.institution_id})>"


class MajorSearchCache(Base):
    """Pre-computed search data for major selection"""
    __tablename__ = "major_search_cache"
    
    cip_code = Column(
        String(7),
        ForeignKey("cip_codes.cip_code", ondelete="CASCADE"),
        primary_key=True
    )
    search_text = Column(String(500), nullable=False, comment="Searchable text")
    display_text = Column(String(255), nullable=False, comment="Formatted display name")
    category = Column(String(100), comment="2-digit CIP category name")
    institutions_count = Column(Integer, default=0, comment="Number of institutions offering this major")
    programs_count = Column(Integer, default=0, comment="Total program count")
    avg_median_earnings = Column(Integer, comment="Average median earnings across programs")
    sort_priority = Column(Integer, default=999, index=True)
    
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    # Relationships
    cip = relationship("CIPCode", back_populates="search_cache")
    
    def __repr__(self):
        return f"<MajorSearchCache(cip_code={self.cip_code})>"

