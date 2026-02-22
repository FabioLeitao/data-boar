import os
import pathlib
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
import sqlite3
from datetime import datetime

class FileScanner:
    def __init__(self, scanner_engine, db_session):
        self.scanner = scanner_engine
        self.db = db_session
        self.supported_extensions = {
            '.txt', '.csv', '.pdf', '.docx', '.xlsx', '.xls', '.odt', '.json'
        }

    def scan_directory(self, root_path, recursive=True):
        path = pathlib.Path(root_path)
        search_pattern = "**/*" if recursive else "*"
        
        for file_path in path.glob(search_pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                self._process_file(file_path)

    def _process_file(self, file_path):
        """Extrai texto baseado na extensão e envia para o scanner de sensibilidade."""
        content = ""
        ext = file_path.suffix.lower()
        
        try:
            if ext == '.txt' or ext == '.csv':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000) # Amostra para performance
            
            elif ext == '.pdf':
                reader = PdfReader(file_path)
                content = " ".join([page.extract_text() for page in reader.pages[:3]]) # Primeiras 3 páginas
            
            elif ext == '.docx':
                doc = Document(file_path)
                content = " ".join([p.text for p in doc.paragraphs[:20]])

            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, nrows=10) # Apenas cabeçalho e primeiras linhas
                content = " ".join(df.columns.astype(str)) + " " + df.to_string()

            # Investigar sensibilidade
            findings = self.scanner.scan_text(content)
            
            if findings:
                self._log_to_local_db(file_path, findings)
                self._notify_operator(file_path, findings)

        except Exception as e:
            print(f"Erro ao processar {file_path}: {e}")

    def _log_to_local_db(self, file_path, findings, target_info):
        # target_info vem do arquivo de configuração yaml
        for pattern in findings:
            self.db_manager.save_finding(
                target_name=target_info['name'],
                source_type='filesystem',
                server_ip=target_info.get('host', 'localhost'),
                engine_version=file_path.suffix,
                schema_name=str(file_path.parent),
                table_name=file_path.name,
                column_name="Content",
                data_type=file_path.suffix.replace('.', '').upper(),
                sensitivity_level="HIGH", # Baseado nos padrões detectados
                pattern_detected=pattern,
                sample_format="Regex Match"
            )

    def _notify_operator(self, path, findings):
        print(f"[ALERTA] Dado Sensível ({', '.join(findings)}) encontrado em: {path}")
