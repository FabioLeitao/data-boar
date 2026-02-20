import yaml
from sqlalchemy.inspector import Inspector
from concurrent.futures import ThreadPoolExecutor
import re

class DatabaseScanner:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.sensitive_keywords = self.get_sensitive_keywords()

    def load_config(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def get_sensitive_keywords(self):
        return [
            r'\bCPF\b', r'\bRG\b', r'\bNome\b', r'\bEmail\b',
            r'\bTelefone\b', r'\bCelular\b', r'\bCNPJ\b',
            r'\bSenha\b', r'\bDataNascimento\b'
        ]

    def scan_databases(self):
        results = []
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.scan_db, db): db for db in self.config['databases']}
            for future in futures:
                db_result = future.result()
                if db_result:
                    results.extend(db_result)
        return results

    def scan_db(self, db_config):
        try:
            engine = create_engine(f"{db_config['dialect']}+{db_config['driver']}://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
            inspector = Inspector.from_engine(engine)
            
            sensitive_data = []
            for schema in inspector.get_schemata():
                for table_name in inspector.get_table_names(schema):
                    columns = inspector.get_columns(table_name, schema)
                    for column in columns:
                        column_name = column['name']
                        data_type = column['type']
                        
                        # Verificar padrões nos nomes das colunas
                        for pattern in self.sensitive_keywords:
                            if re.search(pattern, column_name, re.IGNORECASE):
                                sensitive_data.append({
                                    'ip': db_config['host'],
                                    'db_engine': db_config['dialect'],
                                    'version': db_config['version'],
                                    'schema': schema,
                                    'table': table_name,
                                    'column': column_name,
                                    'data_type': str(data_type),
                                    'is_sensitive': True
                                })
            return sensitive_data
        except Exception as e:
            print(f"Erro no banco {db_config['database']}: {str(e)}")
            return []

# Exemplo de uso
if __name__ == "__main__":
    scanner = DatabaseScanner('config.yaml')
    results = scanner.scan_databases()
    
    with open('report.json', 'w') as f:
        json.dump(results, f, indent=2)

