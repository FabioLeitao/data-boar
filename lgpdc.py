import yaml
from sqlalchemy import create_engine
from sqlalchemy.inspector import Inspector
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
        for db in self.config['databases']:
            try:
                engine = create_engine(f"{db['dialect']}+{db['driver']}://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}")
                inspector = Inspector.from_engine(engine)
                
                for schema in inspector.get_schemata():
                    for table in inspector.get_table_names(schema):
                        columns = inspector.get_columns(table, schema)
                        for col in columns:
                            if re.search(r'\bCPF\b', col['name'], re.IGNORECASE):
                                results.append({
                                    'ip': db['host'],
                                    'db_engine': db['dialect'],
                                    'version': db['version'],
                                    'schema': schema,
                                    'table': table,
                                    'column': col['name'],
                                    'data_type': str(col['type']),
                                    'is_sensitive': True
                                })
            except Exception as e:
                print(f"Erro no banco {db['database']}: {str(e)}")
        return results

# Exemplo de uso
if __name__ == "__main__":
    scanner = DatabaseScanner('config.yaml')
    results = scanner.scan_databases()
    
    with open('report.json', 'w') as f:
        import json
        json.dump(results, f, indent=2)

