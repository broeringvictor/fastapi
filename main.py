from fastapi import FastAPI

from app.schemas.schemas import Message


app = FastAPI()




@app.get("/", status_code=200, response_model=Message)
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

