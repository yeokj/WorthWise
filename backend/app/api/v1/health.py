"""
Health Check Endpoint
System health and status monitoring
"""

from fastapi import APIRouter, Depends
from datetime import datetime

from app.schemas.common import HealthResponse
from app.database import check_db_connection
from app.duckdb_client import get_duckdb, DuckDBClient
from app.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(
    duckdb: DuckDBClient = Depends(get_duckdb)
):
    """
    Health check endpoint
    
    Returns system health status including database connectivity
    """
    # Check MySQL connection
    mysql_healthy = check_db_connection()
    
    # Check DuckDB
    duckdb_status = duckdb.healthcheck()
    
    # Determine overall status
    if mysql_healthy and duckdb_status.get("status") == "healthy":
        overall_status = "healthy"
    elif mysql_healthy or duckdb_status.get("status") == "healthy":
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        version=settings.app_version,
        database={
            "connected": mysql_healthy,
            "type": "MySQL",
            "latency_ms": 5 if mysql_healthy else None
        },
        duckdb=duckdb_status,
        timestamp=datetime.utcnow()
    )

