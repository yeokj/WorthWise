"""
Institution Model
College and university reference data
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, DECIMAL, SmallInteger, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Institution(Base):
    __tablename__ = "institutions"
    
    # Primary identification
    id = Column(Integer, primary_key=True, comment="UNITID from IPEDS")
    ope8_id = Column(String(10), comment="8-digit OPE ID")
    ope6_id = Column(String(10), comment="6-digit OPE ID")
    name = Column(String(255), nullable=False, index=True, comment="Institution name")
    
    # Location
    city = Column(String(100), comment="City location")
    state_code = Column(String(2), ForeignKey("states.state_code"), index=True, comment="State postal code")
    zip = Column(String(10), index=True, comment="ZIP code")
    latitude = Column(DECIMAL(10, 7), comment="Latitude coordinate")
    longitude = Column(DECIMAL(11, 7), comment="Longitude coordinate")
    
    # Characteristics
    ownership = Column(SmallInteger, index=True, comment="1=Public, 2=Private nonprofit, 3=Private for-profit")
    tuition_in_state = Column(Integer, index=True, comment="In-state tuition and fees (USD/year)")
    tuition_out_state = Column(Integer, index=True, comment="Out-of-state tuition and fees (USD/year)")
    avg_net_price_public = Column(Integer, comment="Average net price for public institutions (USD/year)")
    avg_net_price_private = Column(Integer, comment="Average net price for private institutions (USD/year)")
    main_campus = Column(Boolean, default=True, index=True, comment="TRUE if main campus")
    branch_count = Column(SmallInteger, default=0, comment="Number of branch campuses")
    operating = Column(Boolean, default=True, index=True, comment="TRUE if currently operating")
    predominant_degree = Column(SmallInteger, index=True, comment="Predominant degree type")
    highest_degree = Column(SmallInteger, comment="Highest degree awarded")
    
    # URLs
    school_url = Column(String(255), comment="Institution homepage URL")
    price_calculator_url = Column(String(255), comment="Net price calculator URL")
    
    # Additional metadata
    locale = Column(SmallInteger, comment="Locale code")
    region_id = Column(SmallInteger, comment="IPEDS region code")
    carnegie_basic = Column(SmallInteger, comment="Carnegie Classification")
    
    # Flags
    under_investigation = Column(Boolean, default=False, comment="Heightened Cash Monitoring flag")
    hbcu = Column(Boolean, default=False, comment="Historically Black College/University")
    tribal = Column(Boolean, default=False, comment="Tribal college")
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    # Relationships
    state = relationship("State", foreign_keys=[state_code])
    campuses = relationship("Campus", back_populates="institution", cascade="all, delete-orphan")
    search_cache = relationship("InstitutionSearchCache", back_populates="institution", uselist=False)
    
    def __repr__(self):
        return f"<Institution(id={self.id}, name={self.name})>"

