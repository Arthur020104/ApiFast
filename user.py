from pydantic import BaseModel
from typing import Optional
class Usuario(BaseModel):
    name: str
    number_tel:str
class UsuarioUpdate(BaseModel):
    name: Optional[str] = None
    number_tel: Optional[str] = None
