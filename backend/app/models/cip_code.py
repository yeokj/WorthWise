"""
CIP Code Model
Classification of Instructional Programs
"""

from sqlalchemy import Column, String, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database import Base


class CIPCode(Base):
    __tablename__ = "cip_codes"
    
    cip_code = Column(String(7), primary_key=True, comment="6-digit CIP code (e.g., 11.0701)")
    cip_title = Column(String(255), nullable=False, index=True, comment="CIP program title")
    cip_2digit = Column(String(2), nullable=False, index=True, comment="2-digit broad field code")
    cip_2digit_title = Column(String(255), comment="2-digit field title")
    cip_4digit = Column(String(5), nullable=False, index=True, comment="4-digit intermediate code")
    cip_4digit_title = Column(String(255), comment="4-digit field title")
    cip_definition = Column(Text, comment="Full CIP definition")
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    # Relationships
    search_cache = relationship("MajorSearchCache", back_populates="cip", uselist=False)
    
    def __repr__(self):
        return f"<CIPCode(code={self.cip_code}, title={self.cip_title})>"

