# Dentro de connectors/sql_connector.py
from sqlalchemy import inspect

class SQLConnector:
    def __init__(self, target_config, scanner_logic, db_manager):
        self.config = target_config
        self.scanner = scanner_logic
        self.db_manager = db_manager
        self.engine = create_engine(self._build_url())

    def run_scan(self):
        inspector = inspect(self.engine)
        for schema in inspector.get_schema_names():
            if schema in ['information_schema', 'sys']: continue
            
            for table in inspector.get_table_names(schema=schema):
                columns = inspector.get_columns(table, schema=schema)
                
                for col in columns:
                    # Lógica de Regex no nome da coluna
                    sensitivity = self.scanner.identify_sensitivity(col['name'])
                    
                    if sensitivity == "HIGH":
                        self.db_manager.save_finding(
                            target_name=self.config['name'],
                            source_type='database',
                            server_ip=self.config.get('host'),
                            engine_version=str(self.engine.dialect.name),
                            schema_name=schema,
                            table_name=table,
                            column_name=col['name'],
                            data_type=str(col['type']),
                            sensitivity_level=sensitivity,
                            pattern_detected="COL_NAME_MATCH",
                            sample_format=str(col['type'])
                        )
