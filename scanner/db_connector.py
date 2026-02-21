from sqlalchemy import create_engine
import yaml
import os

class DBConnector:
    def __init__(self, config_path="config/db_config.yaml"):
        self.config = self._load_config(config_path)
        self.connections = {}

    def _load_config(self, config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def connect(self):
        for db in self.config["databases"]:
            try:
                engine = create_engine(db["driver"], 
                                      connect_args={k:v for k, v in db.items() if k in ["host", "port", "user", "password", "database"]})
                self.connections[db["name"]] = engine
                self._log(f"Conexão estabelecida com {db['name']}")
            except Exception as e:
                self._log(f"Erro ao conectar com {db['name']}: {str(e)}", level="error")

    def get_connection(self, db_name):
        return self.connections.get(db_name)

