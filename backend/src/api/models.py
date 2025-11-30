from pydantic import BaseModel

class CodeInput(BaseModel):
    filename: str
    code: str

class KleeRunRequest(BaseModel):
    bc_path: str

class ResultResponse(BaseModel):
    test_id: str
    values: dict
