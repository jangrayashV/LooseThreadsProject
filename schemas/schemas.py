from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    pwd: str

class UserResponse(BaseModel):
    uid: int
    username: str
    email: EmailStr

    model_config = {"from_attributes": True}

class ProblemCreate(BaseModel):
    title: str
    description: str
    attempted_approach: str

class ProblemResponse(BaseModel):
    pid: int
    title: str
    model_config = {"from_attributes": True}

class HintResponse(BaseModel):
    hid: int
    pid: int
    hint_count: int
    content: str

    model_config = {"from_attributes": True}

class ProblemWithHints(BaseModel):
    problem: ProblemResponse
    hints: list[HintResponse]