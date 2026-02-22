from connectors.sql_connector import SQLConnector
from connectors.file_connector import FileScanner
from core.scanner import DataScanner

class AuditEngine:
    def __init__(self, config):
        self.config = config
        self.scanner_logic = DataScanner()
        # Inicializa conexão com SQLite Local para resultados
        
    def start_audit(self):
        for target in self.config['targets']:
            print(f"Iniciando auditoria em: {target['name']}")
            
            if target['type'] == 'database':
                connector = SQLConnector(target, self.scanner_logic)
                connector.run()
                
            elif target['type'] == 'filesystem':
                file_scanner = FileScanner(self.scanner_logic, None)
                file_scanner.scan_directory(target['path'], target.get('recursive', True))

    def generate_final_reports(self):
        # Consolida os dados do SQLite local em Excel/Heatmap
        pass
