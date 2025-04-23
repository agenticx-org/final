from sqlalchemy import Column, String, DateTime, Boolean, create_engine, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime
import json
from sqlalchemy import inspect
from sqlalchemy.sql import text

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'
    
    project_id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.now, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)
    message_history = relationship("ProjectMessage", back_populates="project", cascade="all, delete-orphan")
    system_prompt = Column(String, nullable=True)
    plan = Column(String, nullable=True)
    findings = Column(String, nullable=True)
    final_answer = Column(String, nullable=True)

class ProjectMessage(Base):
    __tablename__ = 'project_messages'
    
    event_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey('projects.project_id'), nullable=False)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)
    project = relationship("Project", back_populates="message_history")

# Global database session
_db_session = None
_engine = None

def get_db_session(drop_all=False):
    global _db_session, _engine
    
    # If drop_all is True and session exists, close it and reset
    if drop_all and _db_session is not None:
        _db_session.close()
        _db_session = None
        _engine = None
    
    # If session already exists, return it
    if _db_session is not None:
        return _db_session
    
    # Create new session if it doesn't exist
    database_url = os.environ.get("DATABASE_URL")
    print(f"database_url: {database_url}")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    _engine = create_engine(database_url)
    
    if drop_all:
        print("Dropping all tables...")
        # Check if tables exist before dropping
        inspector = inspect(_engine)
        existing_tables = inspector.get_table_names()
        print(f"Tables before dropping: {existing_tables}")
        
        # Drop all tables with CASCADE to handle foreign key dependencies
        for table in existing_tables:
            print(f"Dropping table with CASCADE: {table}")
            with _engine.connect() as conn:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                conn.commit()
        
        # Verify tables were dropped
        inspector = inspect(_engine)
        remaining_tables = inspector.get_table_names()
        print(f"Tables after dropping: {remaining_tables}")
        
        if remaining_tables:
            print("WARNING: Some tables were not dropped!")
            # Force drop each table individually
            for table in remaining_tables:
                print(f"Force dropping table: {table}")
                with _engine.connect() as conn:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    conn.commit()
        
        print("All tables dropped successfully.")
    
    # Create all tables
    Base.metadata.create_all(_engine)
    
    # Verify tables were created
    inspector = inspect(_engine)
    created_tables = inspector.get_table_names()
    print(f"Tables after creation: {created_tables}")
    
    Session = sessionmaker(bind=_engine)
    _db_session = Session()
    return _db_session 