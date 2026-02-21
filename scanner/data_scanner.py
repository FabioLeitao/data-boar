import re
from sqlalchemy import text
from utils.logger import Logger

class DataScanner:
    def __init__(self, db_connector):
        self.db_connector = db_connector
        self.logger = Logger()

    def scan(self):
        for db_name, engine in self.db_connector.connections.items():
            self._scan_database(db_name, engine)

    def _scan_database(self, db_name, engine):
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT table_name, column_name, data_type FROM information_schema.columns"))
                for row in result:
                    table_name = row[0]
                    column_name = row[1]
                    data_type = row[2]
                    self._analyze_column(db_name, table_name, column_name, data_type)
        except Exception as e:
            self.logger.log(f"Erro ao escanear {db_name}: {str(e)}", level="error")

    def _analyze_column(self, db_name, table_name, column_name, data_type):
        # Lógica de identificação de dados sensíveis
        if re.search(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$", data_type):
            self.logger.log(f"Potencial dado sensível encontrado em {db_name}.{table_name}.{column_name}")

