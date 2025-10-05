from pydantic import BaseModel,Field,validator
from typing import Optional
from bson.objectid import ObjectId
class Project(BaseModel):
    _id:Optional[ObjectId]=Field(None,alias='_id')
    project_id:str=Field(...,min_length=1)

    @validator("Project_id")
    def validate_project_id(cls,value):
        if not value.isalnum():
            raise ValueError("Project_id Must be alphanumeric")
        return value
    
    class Config:
        arbitrary_types_allowed=True


    @classmethod
    def get_indexes(cls):
        
        return [
            {
                 "key":[
                     ('project_id',1)
                 ],
                 'name':'project_id_index_1',
                 'unique': True
            }
        ]