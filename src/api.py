from flask import Flask, jsonify
from src.scanner import DatabaseScanner

app = Flask(__name__)
scanner = DatabaseScanner()

@app.route("/scan", methods=["GET"])
def scan():
    report = scanner.scan_all()
    return jsonify(report)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

