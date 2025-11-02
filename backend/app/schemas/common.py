"""
Common Pydantic Schemas
Shared models across different endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date, datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status: healthy, degraded, unhealthy")
    version: str = Field(..., description="Application version")
    database: Dict[str, Any] = Field(..., description="Database health status")
    duckdb: Dict[str, Any] = Field(..., description="DuckDB health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "database": {"connected": True, "latency_ms": 5},
                "duckdb": {"status": "healthy", "tables_ready": True},
                "timestamp": "2025-10-27T10:00:00Z"
            }
        }


class DataVersionResponse(BaseModel):
    """Data version information"""
    dataset_name: str = Field(..., description="Dataset identifier")
    version_identifier: str = Field(..., description="Version string (e.g., 2024-09-15, FY2026)")
    version_date: Optional[date] = Field(None, description="Official version date")
    row_count: Optional[int] = Field(None, description="Number of rows in dataset")
    loaded_at: Optional[datetime] = Field(None, description="When data was loaded")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "dataset_name": "college_scorecard_institution",
                "version_identifier": "2024-09-15",
                "version_date": "2024-09-15",
                "row_count": 7000,
                "loaded_at": "2025-10-27T08:00:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for programmatic handling")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Institution not found",
                "error_code": "INSTITUTION_NOT_FOUND",
                "timestamp": "2025-10-27T10:00:00Z"
            }
        }

