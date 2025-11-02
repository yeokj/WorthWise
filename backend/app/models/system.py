"""
System Configuration Model
Application configuration and feature flags
"""

from sqlalchemy import Column, String, Text, Boolean, TIMESTAMP, Enum, func
from app.database import Base
import enum


class ValueType(str, enum.Enum):
    """Configuration value type enumeration"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"


class SystemConfig(Base):
    """System configuration key-value store"""
    __tablename__ = "system_config"
    
    config_key = Column(String(100), primary_key=True)
    config_value = Column(Text, nullable=False)
    value_type = Column(Enum(ValueType, values_callable=lambda x: [e.value for e in x]), default=ValueType.STRING)
    category = Column(String(50), index=True, comment="Config category")
    description = Column(Text, comment="Configuration description")
    is_secret = Column(Boolean, default=False, comment="Sensitive data flag")
    is_editable = Column(Boolean, default=True, comment="Can be modified via UI/API")
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    def __repr__(self):
        return f"<SystemConfig(key={self.config_key}, category={self.category})>"

