from models.enums import DataBaseEnum

from .BaseDataModel import BaseDataModel
from .db_schemes import Project

class ProjectModel(BaseDataModel):

    def __init__(self, db_client:object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]


    async def create_project(self, project:Project):

        result = await self.collection.insert_one(project.dict())
        project.id = result.inserted_id

        return project
    
    async def get_project_or_create_one(self, project_id:str):

        record = await self.collection.find_one({
            "project_id": project_id
        })
        #returned record is dict

        if record is None:
            #create the project
            project = Project(project_id= project_id)
            #create_project method need Project Model as parameter for this i make project variable on the line above
         
            project = await self.create_project(project)

            return project


        #convert recorddict to Project model(we can say that take evrey value on dict and pit it on ProjectModel)
        return Project(**record)     



    async def get_all_projects(self, page:int= 1, page_size= 10):

        #count total number of documents
        total_documents = await self.collection.count_documents({})

        #calculate total number of pages
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1

        cursor = await self.colection.find().skip((page-1)*page_size).limit(page_size)
        projects = []

        async for document in cursor:
            projects.append(
                Project(**document)
            )
        
        return projects, total_pages




    
