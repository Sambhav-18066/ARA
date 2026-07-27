from fastapi import FastAPI

from app.ara import ARA
from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str

ara = ARA()
ara.boot()

app = FastAPI(
    title="ARA",
    version=ARA.VERSION,
    description="ARA AI Operating System",
)


@app.get("/")
def home():

    return {
        "message": "ARA AI Operating System"
    }


@app.get("/status")
def status():

    return ara.status()


@app.post("/process")
def process(data: PromptRequest):

    return ara.process(data.prompt)