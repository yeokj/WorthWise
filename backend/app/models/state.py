"""
State Model
U.S. states and territories reference data
"""

from sqlalchemy import Column, String, Boolean, TIMESTAMP, func
from app.database import Base


class State(Base):
    __tablename__ = "states"
    
    state_code = Column(String(2), primary_key=True, comment="Two-letter state postal code")
    state_name = Column(String(100), nullable=False, comment="Full state name")
    state_fips = Column(String(2), nullable=False, comment="FIPS state code")
    region = Column(String(50), comment="Census region")
    division = Column(String(50), comment="Census division")
    is_state = Column(Boolean, default=True, comment="TRUE for states, FALSE for territories")
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    def __repr__(self):
        return f"<State(code={self.state_code}, name={self.state_name})>"

