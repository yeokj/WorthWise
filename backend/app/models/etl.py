"""
ETL Metadata Models
Track dataset versions, ETL runs, and data quality checks
"""

from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, BigInteger, Text, Enum, JSON, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class DataVersionStatus(str, enum.Enum):
    """Data version status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    LOADED = "loaded"
    ACTIVE = "active"
    ARCHIVED = "archived"
    FAILED = "failed"


class ETLRunStatus(str, enum.Enum):
    """ETL run status enumeration"""
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ETLRunType(str, enum.Enum):
    """ETL run type enumeration"""
    FULL_REFRESH = "full_refresh"
    INCREMENTAL = "incremental"
    BACKFILL = "backfill"
    VALIDATION = "validation"
    MANUAL = "manual"


class CheckType(str, enum.Enum):
    """Data quality check type enumeration"""
    COUNT = "count"
    NULL = "null"
    RANGE = "range"
    UNIQUENESS = "uniqueness"
    REFERENTIAL_INTEGRITY = "referential_integrity"
    CUSTOM = "custom"


class CheckStatus(str, enum.Enum):
    """Data quality check status enumeration"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIPPED = "skipped"


class CheckSeverity(str, enum.Enum):
    """Data quality check severity enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class DataVersion(Base):
    """Track versions of ingested datasets"""
    __tablename__ = "data_versions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_name = Column(String(100), nullable=False, index=True, comment="Dataset identifier")
    version_identifier = Column(String(100), nullable=False, comment="Version string")
    version_date = Column(Date, index=True, comment="Official version date")
    file_name = Column(String(255), comment="Source file name")
    file_path = Column(String(500), comment="Path to source file")
    file_size_bytes = Column(BigInteger, comment="File size in bytes")
    row_count = Column(Integer, comment="Number of rows processed")
    
    # Status and timestamps
    status = Column(
        Enum(DataVersionStatus, values_callable=lambda x: [e.value for e in x]),
        default=DataVersionStatus.PENDING,
        index=True
    )
    loaded_at = Column(TIMESTAMP, index=True, comment="When data was loaded")
    activated_at = Column(TIMESTAMP, comment="When version became active")
    archived_at = Column(TIMESTAMP, comment="When version was archived")
    
    # Metadata
    checksum = Column(String(64), comment="SHA256 checksum of source file")
    notes = Column(Text, comment="Version notes, changes, or issues")
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    def __repr__(self):
        return f"<DataVersion(id={self.id}, dataset={self.dataset_name}, version={self.version_identifier})>"


class ETLRun(Base):
    """ETL execution history and audit log"""
    __tablename__ = "etl_runs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), unique=True, nullable=False, index=True, comment="Unique run identifier (UUID)")
    run_type = Column(Enum(ETLRunType, values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    
    # Timing
    started_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), index=True)
    completed_at = Column(TIMESTAMP)
    duration_seconds = Column(Integer, comment="Total run duration")
    
    # Status
    status = Column(
        Enum(ETLRunStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ETLRunStatus.RUNNING,
        index=True
    )
    
    # Datasets processed
    datasets_processed = Column(JSON, comment="List of datasets processed with row counts")
    datasets_failed = Column(JSON, comment="List of failed datasets with error messages")
    
    # Metrics
    total_rows_processed = Column(Integer, default=0)
    total_rows_inserted = Column(Integer, default=0)
    total_rows_updated = Column(Integer, default=0)
    total_rows_failed = Column(Integer, default=0)
    
    # Error tracking
    error_count = Column(Integer, default=0)
    error_summary = Column(Text, comment="Summary of errors encountered")
    error_log = Column(Text, comment="Detailed error log")
    
    # Environment
    executed_by = Column(String(100), comment="User or system that executed ETL")
    execution_environment = Column(String(50), comment="e.g., local, ci, production")
    git_commit_hash = Column(String(40), comment="Git commit hash of ETL code")
    
    # Metadata
    config_used = Column(JSON, comment="ETL configuration parameters")
    notes = Column(Text, comment="Run notes or special conditions")
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    # Relationships
    quality_checks = relationship("DataQualityCheck", back_populates="etl_run", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ETLRun(id={self.id}, run_id={self.run_id}, status={self.status})>"


class DataQualityCheck(Base):
    """Data quality validation results"""
    __tablename__ = "data_quality_checks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    etl_run_id = Column(
        Integer,
        ForeignKey("etl_runs.id", ondelete="CASCADE"),
        index=True,
        comment="Associated ETL run"
    )
    dataset_name = Column(String(100), nullable=False, index=True)
    check_name = Column(String(100), nullable=False, comment="Name of quality check")
    check_type = Column(Enum(CheckType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    
    # Check details
    expected_value = Column(String(255), comment="Expected value or range")
    actual_value = Column(String(255), comment="Actual value found")
    status = Column(Enum(CheckStatus, values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    
    # Results
    records_checked = Column(Integer)
    records_failed = Column(Integer)
    failure_rate = Column(DECIMAL(5, 2), comment="Percentage of failures")
    
    # Metadata
    check_sql = Column(Text, comment="SQL query used for check")
    error_message = Column(Text, comment="Error or warning message")
    severity = Column(Enum(CheckSeverity, values_callable=lambda x: [e.value for e in x]), default=CheckSeverity.MEDIUM, index=True)
    
    checked_at = Column(TIMESTAMP, server_default=func.current_timestamp(), index=True)
    
    # Relationships
    etl_run = relationship("ETLRun", back_populates="quality_checks")
    
    def __repr__(self):
        return f"<DataQualityCheck(id={self.id}, dataset={self.dataset_name}, status={self.status})>"

