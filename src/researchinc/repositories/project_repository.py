from researchinc.domain.models import Project, get_db_session
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import uuid
class ProjectRepository:
    def __init__(self):
        self.session = get_db_session(drop_all=False)

    def put(self, project):
        try:            
            # Add the project to the session
            self.session.merge(project)
            
            # Commit the transaction
            self.session.commit()
        except SQLAlchemyError as e:
            # Roll back the session in case of error
            self.session.rollback()
            raise e

    def get(self, project_id):
        return self.session.query(Project).filter_by(project_id=project_id).first()
    
    def get_or_create(self, project_id=None):
        if not project_id:
            project_id = str(uuid.uuid4())
        project = self.get(project_id)
        if not project:
            project = Project(project_id=project_id)
            self.put(project)
        return project

    def delete(self, project_id):
        try:
            self.session.query(Project).filter_by(project_id=project_id).delete()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def list(self):
        return self.session.query(Project).all()

class FakeProjectRepository(ProjectRepository):
    def __init__(self):
        self.projects = {}
        self._initialized = True  # No need to connect to a database for fake repository
        
    def put(self, project):
        self.projects[project.project_id] = project
        
    def get(self, project_id):
        return self.projects.get(project_id)
        
    def delete(self, project_id):
        if project_id in self.projects:
            del self.projects[project_id]
            
    def list(self):
        return list(self.projects.values()) 