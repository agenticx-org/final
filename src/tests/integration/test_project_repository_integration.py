import pytest
import os
import uuid
from datetime import datetime
from researchinc.domain.models import Project
from researchinc.repositories.project_repository import ProjectRepository

def generate_unique_id():
    """Generate a unique ID for testing to avoid conflicts"""
    return str(uuid.uuid4())

def test_put_project_integration():
    project_repository = ProjectRepository()
    project_id = generate_unique_id()
    
    # Clean up any existing project with this ID (just in case)
    project_repository.delete(project_id)
    
    project = Project(project_id=project_id)
    project_repository.put(project)
    retrieved_project = project_repository.get(project.project_id)
    assert retrieved_project is not None
    assert retrieved_project.project_id == project.project_id
    project_repository.delete(project.project_id)

def test_put_project_updates_existing_integration():
    project_repository = ProjectRepository()
    project_id = generate_unique_id()
    
    # Clean up any existing project with this ID (just in case)
    project_repository.delete(project_id)
    project = Project(project_id=project_id)
    project_repository.put(project)
    project.plan = "new plan"
    project_repository.put(project)
    
    retrieved_project = project_repository.get(project.project_id)
    assert retrieved_project is not None
    assert retrieved_project.plan == "new plan"
    
    project_repository.delete(project.project_id)

def test_delete_project_delete_integration():
    project_repository = ProjectRepository()
    project_id = generate_unique_id()
    
    # Clean up any existing project with this ID (just in case)
    project_repository.delete(project_id)
    
    project = Project(project_id=project_id)
    project_repository.put(project)
    
    # Delete the project
    project_repository.delete(project.project_id)
    
    # Verify project is deleted
    retrieved_project = project_repository.get(project.project_id)
    assert retrieved_project is None 