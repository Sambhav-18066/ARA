from fastapi import FastAPI

from app.ara import ARA

ara = ARA()

app = FastAPI(
    title="ARA",
    version=ara.version
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
def process(data: dict):

    prompt = data.get("prompt", "")

    return ara.process(prompt)