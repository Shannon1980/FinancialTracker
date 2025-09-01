"""
Database Configuration Module
Supports SQLite, PostgreSQL, and MySQL databases
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self):
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self.database_url: Optional[str] = None
        self.database_type: str = "sqlite"
        
    def get_database_url(self) -> str:
        """Get database URL from environment or use default SQLite"""
        
        # Check for environment variables first
        if os.getenv("DATABASE_URL"):
            self.database_url = os.getenv("DATABASE_URL")
            self.database_type = self._detect_database_type(self.database_url)
            return self.database_url
        
        # Check for specific database environment variables
        if os.getenv("POSTGRES_DB"):
            return self._build_postgres_url()
        elif os.getenv("MYSQL_DB"):
            return self._build_mysql_url()
        else:
            # Default to SQLite
            return self._build_sqlite_url()
    
    def _detect_database_type(self, url: str) -> str:
        """Detect database type from URL"""
        if url.startswith("postgresql://"):
            return "postgresql"
        elif url.startswith("mysql://"):
            return "mysql"
        elif url.startswith("sqlite://"):
            return "sqlite"
        else:
            return "unknown"
    
    def _build_sqlite_url(self) -> str:
        """Build SQLite database URL"""
        db_path = Path("data/seas_financial_tracker.db")
        db_path.parent.mkdir(exist_ok=True)
        self.database_type = "sqlite"
        return f"sqlite:///{db_path}"
    
    def _build_postgres_url(self) -> str:
        """Build PostgreSQL database URL"""
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DB", "seas_financial_tracker")
        username = os.getenv("POSTGRES_USER", "seas")
        password = os.getenv("POSTGRES_PASSWORD", "")
        
        self.database_type = "postgresql"
        return f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    def _build_mysql_url(self) -> str:
        """Build MySQL database URL"""
        host = os.getenv("MYSQL_HOST", "localhost")
        port = os.getenv("MYSQL_PORT", "3306")
        database = os.getenv("MYSQL_DB", "seas_financial_tracker")
        username = os.getenv("MYSQL_USER", "seas")
        password = os.getenv("MYSQL_PASSWORD", "")
        
        self.database_type = "mysql"
        return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    
    def create_engine(self) -> Engine:
        """Create database engine with appropriate configuration"""
        
        database_url = self.get_database_url()
        logger.info(f"Connecting to {self.database_type} database")
        
        # Engine configuration based on database type
        if self.database_type == "sqlite":
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False  # Set to True for SQL debugging
            )
        elif self.database_type == "postgresql":
            self.engine = create_engine(
                database_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False
            )
        elif self.database_type == "mysql":
            self.engine = create_engine(
                database_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False
            )
        else:
            raise ValueError(f"Unsupported database type: {self.database_type}")
        
        return self.engine
    
    def get_session(self) -> Session:
        """Get database session"""
        if not self.engine:
            self.create_engine()
        
        if not self.SessionLocal:
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            if not self.engine:
                self.create_engine()
            
            with self.engine.connect() as connection:
                if self.database_type == "sqlite":
                    connection.execute(text("SELECT 1"))
                elif self.database_type == "postgresql":
                    connection.execute(text("SELECT 1"))
                elif self.database_type == "mysql":
                    connection.execute(text("SELECT 1"))
                
            logger.info(f"✅ Successfully connected to {self.database_type} database")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return False
    
    def close_connection(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")

# Global database configuration instance
db_config = DatabaseConfig()

def get_db() -> Session:
    """Dependency function to get database session"""
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database connection and test"""
    return db_config.test_connection()
