from typing import List
from pydantic import BaseModel

class UpdateUserRoles(BaseModel):
    roles: List[str]