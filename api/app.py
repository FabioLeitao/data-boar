from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class DatabaseConfig(BaseModel):
    name: str
    host: str
    port: int
    user: str
    password: str
    database: str


@app.post("/scan_database")
async def scan_database(config: DatabaseConfig):
    # Lógica de escaneamento
    return {"status": "success"}
