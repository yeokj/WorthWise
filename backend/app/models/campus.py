"""
Campus Model
Branch campus information
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, DECIMAL, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Campus(Base):
    __tablename__ = "campuses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    institution_id = Column(
        Integer,
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Parent institution UNITID"
    )
    campus_name = Column(String(255), nullable=False, index=True, comment="Campus or branch name")
    
    # Location
    city = Column(String(100))
    state_code = Column(String(2), ForeignKey("states.state_code"), index=True)
    zip = Column(String(10))
    latitude = Column(DECIMAL(10, 7))
    longitude = Column(DECIMAL(11, 7))
    
    # Status
    is_main = Column(Boolean, default=False, comment="Is this the main campus")
    is_active = Column(Boolean, default=True, comment="Campus currently operating")
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    # Relationships
    institution = relationship("Institution", back_populates="campuses")
    state = relationship("State", foreign_keys=[state_code])
    
    def __repr__(self):
        return f"<Campus(id={self.id}, name={self.campus_name})>"

