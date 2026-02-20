import json
import yaml
from sqlalchemy import create_engine
from sqlalchemy.inspector import Inspector
from concurrent.futures import ThreadPoolExecutor
import re
from typing import Dict, List, Optional

class DatabaseScanner:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.sensitive_patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, List[str]]:
        """Compila padrões de sensibilidade para LGPD/GDPR/CCPA."""
        patterns = {
            "lgpd": [
                r'\bCPF\b', r'\bRG\b', r'\bNome\b', r'\bEndereço\b',
                r'\bDataNascimento\b', r'\bEmail\b', r'\bTelefone\b'
            ],
            "gdpr": [
                r'\bPersonal Data\b', r'\bLocation Data\b',
                r'\bBiometric Data\b', r'\bIP Address\b'
            ],
            "ccpa": [
                r'\bDo Not Sell My Personal Information\b',
                r'\bPersonal Information\b'
            ]
        }
        return patterns

    def _check_sensitivity(self, column_name: str, data_type: str) -> Dict[str, bool]:
        """Verifica se a coluna contém dados sensíveis."""
        sensitivity = {"lgpd": False, "gdpr": False, "ccpa": False}

        for reg, patterns in self.sensitive_patterns.items():
            for pattern in patterns:
                if re.search(pattern, column_name, re.IGNORECASE):
                    sensitivity[reg] = True
                    break

        # Adiciona sensibilidade baseada em tipos de dados (ex: email, telefone)
        if data_type.lower() in ["varchar", "text"]:
            if "email" in column_name.lower() or "telefone" in column_name.lower():
                sensitivity["lgpd"] = True
                sensitivity["gdpr"] = True

        return sensitivity

    def scan_database(self, db_config: Dict) -> List[Dict]:
        """Escaneia um banco de dados e retorna metadados sensíveis."""
        results = []
        try:
            engine = create_engine(f"{db_config['dialect']}+{db_config['dialect']}://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

            with engine.connect() as conn:
                inspector = Inspector.from_engine(conn)
                for schema in inspector.get_schema_names():
                    for table in inspector.get_table_names(schema):
                        columns = inspector.get_columns(table)
                        for col in columns:
                            sensitivity = self._check_sensitivity(col['name'], col['type'])
                            if any(sensitivity.values()):
                                results.append({
                                    "ip": db_config["host"],
                                    "db_engine": db_config["dialect"],
                                    "version": db_config["version"],
                                    "schema": schema,
                                    "table": table,
                                    "column": col['name'],
                                    "data_type": col['type'],
                                    "sensitivity": sensitivity,
                                    "description": self._get_description(sensitivity)
                                })
        except Exception as e:
            print(f"Erro ao acessar {db_config['name']}: {str(e)}")
        return results

    def _get_description(self, sensitivity: Dict) -> str:
        """Gera descrição de sensibilidade baseada na regulação."""
        desc = []
        if sensitivity["lgpd"]:
            desc.append("LGPD (Lei Geral de Proteção de Dados)")
        if sensitivity["gdpr"]:
            desc.append("GDPR (Regulamento Geral de Proteção de Dados)")
        if sensitivity["ccpa"]:
            desc.append("CCPA (California Consumer Privacy Act)")
        return ", ".join(desc)

    def scan_all_databases(self) -> List[Dict]:
        """Escaneia todos os bancos de dados em paralelo."""
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(self.scan_database, self.config["databases"]))
        return [item for sublist in results for item in sublist]

# Exemplo de uso
if __name__ == "__main__":
    scanner = DatabaseScanner("config.json")
    report = scanner.scan_all_databases()

    with open("report.json", "w") as f:
        import json
        json.dump(report, f, indent=2)
    print("Relatório gerado: report.json")

