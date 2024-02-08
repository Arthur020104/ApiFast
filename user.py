from pydantic import BaseModel
from typing import Optional
class Usuario(BaseModel):
    id:int
    name: str
    number_tel:str
class UsuarioUpdate(BaseModel):
    name: Optional[str]
    number_tel:Optional[str]