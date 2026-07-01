from fastapi import FastAPI
from pydantic import BaseModel

from app.ara import ARA

app = FastAPI()

ara = ARA()


class Prompt(BaseModel):

    message: str


@app.on_event("startup")
async def startup():

    ara.start()


@app.get("/")
async def root():

    return {
        "assistant": "ARA",
        "status": "online"
    }


@app.post("/chat")
async def chat(prompt: Prompt):

    return ara.process(prompt.message)