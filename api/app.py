from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scanner.data_scanner import DataScanner
from scanner.db_connector import DBConnector
from utils.logger import Logger

app = FastAPI()
logger = Logger()

@app.post("/scan")
async def start_scan():
    try:
        db_connector = DBConnector()
        db_connector.connect()
        scanner = DataScanner(db_connector)
        scanner.scan()
        return {"status": "Scan concluído", "log": logger.get_logs()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

