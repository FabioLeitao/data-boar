import yaml
import psycopg2
import pymysql
from sqlalchemy import create_engine, MetaData, Table, inspect
from typing import Dict, List, Optional
import logging

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseScanner:
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

    def _get_connection(self, db_config: Dict) -> Optional[Dict]:
        """Cria conexão com o banco de dados."""
        try:
            if db_config["engine"] == "mysql":
                conn = pymysql.connect(
                    host=db_config["host"],
                    port=db_config["port"],
                    user=db_config["user"],
                    password=db_config["password"],
                    database=db_config["dbname"]
                )
            elif db_config["engine"] == "postgresql":
                conn = psycopg2.connect(
                    host=db_config["host"],
                    port=db_config["port"],
                    user=db_config["user"],
                    password=db_config["password"],
                    database=db_config["dbname"]
                )
            else:
                raise ValueError(f"Engine {db_config['engine']} não suportado.")
            return {"conn": conn, "engine": db_config["engine"]}
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco {db_config['name']}: {str(e)}")
            return None

    def _scan_table(self, conn: Dict, table_name: str) -> List[Dict]:
        """Escaneia uma tabela e retorna metadados."""
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=conn["conn"])
        inspector = inspect(table)

        results = []
        for column in inspector.columns:
            column_name = column["name"]
            data_type = column["type"]

            # Reconhecimento de padrões de sensibilidade
            sensitivity = self._check_sensitivity(column_name, data_type)

            results.append({
                "schema": table.schema,
                "table": table.name,
                "column": column_name,
                "data_type": data_type,
                "sensitivity": sensitivity,
                "description": self._get_description(sensitivity)
            })
        return results

    def _check_sensitivity(self, column_name: str, data_type: str) -> Dict[str, bool]:
        """Verifica se a coluna contém dados sensíveis (LGPD/GDPR/CCPA)."""
        sensitivity = {"lgpd": False, "gdpr": False, "ccpa": False}

        # Padrões para LGPD (Lei Geral de Proteção de Dados)
        if any(padrão in column_name.lower() for padrão in ["cpf", "rg", "email", "telefone", "endereço", "data_nascimento"]):
            sensitivity["lgpd"] = True

        # Padrões para GDPR (Regulamento Geral de Proteção de Dados)
        if any(padrão in column_name.lower() for padrão in ["name", "email", "phone", "address", "ip", "biometric"]):
            sensitivity["gdpr"] = True

        # Padrões para CCPA (California Consumer Privacy Act)
        if any(padrão in column_name.lower() for padrão in ["email", "phone", "ssn", "date_of_birth"]):
            sensitivity["ccpa"] = True

        return sensitivity

    def _get_description(self, sensitivity: Dict) -> str:
        """Gera descrição de sensibilidade."""
        desc = []
        if sensitivity["lgpd"]:
            desc.append("LGPD (Lei Geral de Proteção de Dados)")
        if sensitivity["gdpr"]:
            desc.append("GDPR (Regulamento Geral de Proteção de Dados)")
        if sensitivity["ccpa"]:
            desc.append("CCPA (California Consumer Privacy Act)")
        return ", ".join(desc)

    def scan_all(self) -> List[Dict]:
        """Escaneia todos os bancos de dados."""
        results = []
        for db_config in self.config["databases"]:
            conn = self._get_connection(db_config)
            if not conn:
                continue

            try:
                tables = conn["conn"].tables
                for table in tables:
                    table_name = f"{db_config['dbname']}.{table}"
                    table_results = self._scan_table(conn, table_name)
                    results.extend(table_results)
            except Exception as e:
                logger.error(f"Erro ao escanear tabela {table_name}: {str(e)}")
            finally:
                conn["conn"].close()

        return results

# Exemplo de uso
if __name__ == "__main__":
    scanner = DatabaseScanner()
    report = scanner.scan_all()
    import json
    with open("report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("Relatório gerado: report.json")

