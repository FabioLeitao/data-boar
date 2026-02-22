import os
import re
import yaml
import argparse
import uuid
import logging
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# SQLAlchemy imports
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, inspect
from sqlalchemy.orm import sessionmaker, declarative_base

# Web imports
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse

# ML imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

# File Parsing
from pypdf import PdfReader
from docx import Document

# --- CONFIGURAÇÃO DE LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("audit.log"), logging.StreamHandler()]
)
logger = logging.getLogger("DataAudit")

Base = declarative_base()

# --- MODELO DB LOCAL ---
class AuditFinding(Base):
    __tablename__ = 'audit_findings'
    id = Column(Integer, primary_key=True)
    scan_session_id = Column(String(50))
    timestamp = Column(DateTime, default=datetime.now)
    target_name = Column(String(100))
    source_type = Column(String(50)) # 'database' ou 'filesystem'
    server_ip = Column(String(50))
    engine_details = Column(String(100)) # Versão/Mecanismo
    location = Column(String(255)) # Schema.Tabela ou Caminho/Arquivo
    column_name = Column(String(100))
    data_type = Column(String(50))
    sensitivity = Column(String(20))
    pattern_detected = Column(String(100))
    ml_confidence = Column(Integer)

# --- MOTOR DE MACHINE LEARNING ---
class MLScanner:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.model = RandomForestClassifier(n_estimators=100)
        self._train_base()

    def _train_base(self):
        # Treinamento "Cold Start" com termos de LGPD/GDPR/CCPA
        data = {
            'text': [
                'cpf', 'email', 'credit card', 'cartão de credito', 'password', 
                'health record', 'saude', 'cid', 'data de nascimento', 'salário',
                'birth date', 'salary', 'ethnic origin', 'cor', 'political opinion',
                'afliação política', 'religião', 'gender', 'gênero', 'sexo',
                'senha', 'nome', 'rg', 'cnh', 'documento oficial',
                'ssn', 'card', 'pis',
                'system_log', 'item_count', 'config_file', 'temp_data'
            ],
            'label': [
                1, 1, 1, 1, 1, 
                1, 1, 1, 1, 1, 
                1, 1, 1, 1, 1, 
                1, 1, 1, 1, 1, 
                1, 1, 1, 1, 1, 
                1, 1, 1, 
                0, 0, 0, 0] # 1 = Sensível
        }
        df = pd.DataFrame(data)
        X = self.vectorizer.fit_transform(df['text'])
        self.model.fit(X, df['label'])

    def predict(self, text: str) -> float:
        if not text: return 0.0
        x = self.vectorizer.transform([str(text).lower()])
        return self.model.predict_proba(x)[0][1]

# --- SCANNER HÍBRIDO ---
class HybridScanner:
    def __init__(self):
        self.ml = MLScanner()
        self.patterns = {
            "LGPD_CPF": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
            #"LGPD_RG": r"\b\d{2}\.\d{3}\.\d{3}-\d{1}\b",
            #"LGPD_DATA": r"\b\d{2}\/\d{2}\/\d{4}\b",
            #"LGPD_GENERO": r"m|M|masculino|Masculino|Masc|male|Male|f|F|feminino|Feminino|Fem|female|Female|FEMALE|MALE|Not prefer to say\b",
            "EMAIL": r"[\w\.-]+@[\w\.-]+\.\w+",
            #"CCPA_SSN": r"\b\d{3}-\d{2}-\d{4}\b",
            "CREDIT_CARD": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "PHONE": r"\+?\d{2,3}\s?\(?\d{2,3}\)?\s?\d{4,5}-?\d{4}"
        }

    def scan(self, label: str, content: str):
        found_patterns = []
        for p_name, p_regex in self.patterns.items():
            if re.search(p_regex, str(content)):
                found_patterns.append(p_name)
        
        ml_score = self.ml.predict(f"{label} {content}")
        
        sensitivity = "LOW"
        if found_patterns or ml_score > 0.9:
            sensitivity = "HIGH"
        elif ml_score > 0.4:
            sensitivity = "MEDIUM"
            
        return sensitivity, ", ".join(found_patterns) or "ML_CONTEXT", int(ml_score * 100)

# --- ORQUESTRADOR DE AUDITORIA ---
class AuditEngine:
    def __init__(self, config_dict):
        self.config = config_dict
        self.db_path = "audit_results.db"
        self.engine_local = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine_local)
        self.Session = sessionmaker(bind=self.engine_local)
        self.scanner = HybridScanner()
        self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.is_running = False

    def start_audit(self):
        self.is_running = True
        logger.info(f"Iniciando Sessão de Auditoria: {self.current_session}")
        
        for target in self.config.get('targets', []):
            try:
                if target['type'] == 'database':
                    self._scan_db(target)
                elif target['type'] == 'filesystem':
                    self._scan_files(target)
            except Exception as e:
                logger.error(f"Falha no alvo {target.get('name')}: {e}")
        
        self.is_running = False
        logger.info("Auditoria Concluída.")

    def _scan_db(self, target):
        url = f"{target['driver']}://{target['user']}:{target['pass']}@{target['host']}:{target['port']}/{target['database']}"
        remote_engine = create_engine(url)
        inspector = inspect(remote_engine)
        
        for schema in inspector.get_schema_names():
            if schema in ['information_schema', 'sys', 'performance_schema']: continue
            for table in inspector.get_table_names(schema=schema):
                logger.info(f"Sondando Tabela: {schema}.{table}")
                cols = inspector.get_columns(table, schema=schema)
                for col in cols:
                    sens, pat, conf = self.scanner.scan(col['name'], "")
                    if sens != "LOW":
                        self._save_finding(target, f"{schema}.{table}", col['name'], str(col['type']), sens, pat, conf)

    def _scan_files(self, target):
        path = Path(target['path'])
        recursive = target.get('recursive', True)
        pattern = "**/*" if recursive else "*"
        
        for file in path.glob(pattern):
            if file.is_file():
                ext = file.suffix.lower()
                content = ""
                try:
                    if ext == '.pdf':
                        content = " ".join([p.extract_text() for p in PdfReader(file).pages[:2]])
                    elif ext == '.docx':
                        content = " ".join([p.text for p in Document(file).paragraphs[:10]])
                    elif ext in ['.txt', '.csv']:
                        with open(file, 'r', errors='ignore') as f: content = f.read(2000)
                    
                    sens, pat, conf = self.scanner.scan(file.name, content)
                    if sens != "LOW":
                        self._save_finding(target, str(file.parent), file.name, ext.upper(), sens, pat, conf)
                except Exception as e:
                    logger.warning(f"Erro ao ler arquivo {file.name}: {e}")

    def _save_finding(self, target, loc, col, dtype, sens, pat, conf):
        session = self.Session()
        finding = AuditFinding(
            scan_session_id=self.current_session,
            target_name=target['name'],
            source_type=target['type'],
            server_ip=target.get('host', 'local'),
            engine_details=target.get('driver', 'filesystem'),
            location=loc,
            column_name=col,
            data_type=dtype,
            sensitivity=sens,
            pattern_detected=pat,
            ml_confidence=conf
        )
        session.add(finding)
        session.commit()
        session.close()
        logger.warning(f"VIOLAÇÃO: {sens} detectado em {loc} ({pat})")

    def generate_report(self):
        df = pd.read_sql(f"SELECT * FROM audit_findings WHERE scan_session_id = '{self.current_session}'", self.engine_local)
        if df.empty: return None
        
        report_name = f"Relatorio_Auditoria_{self.current_session}.xlsx"
        
        # Gerar Heatmap
        plt.figure(figsize=(10,6))
        pivot = df.groupby(['target_name', 'sensitivity']).size().unstack(fill_value=0)
        sns.heatmap(pivot, annot=True, cmap="YlOrRd")
        plt.title("Mapa de Calor de Sensibilidade")
        plt.savefig("heatmap.png")
        
        with pd.ExcelWriter(report_name, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Mapeamento Detalhado', index=False)
            
            # Aba de Recomendações
            recs = []
            for _, row in df.drop_duplicates(subset=['pattern_detected']).iterrows():
                recs.append({
                    "Dado": row['pattern_detected'],
                    "Risco": "Vazamento de Dados Pessoais / Violação de Conformidade",
                    "Ações de Mitigação": "1. Criptografia AES-256; 2. Anonimização; 3. Controle de Acesso Estrito (RBAC)",
                    "Base Legal": "LGPD Art. 5 / GDPR Art. 4"
                })
            pd.DataFrame(recs).to_excel(writer, sheet_name='Plano de Mitigação', index=False)
            
        return report_name

# --- INTERFACE API (FASTAPI) ---
app = FastAPI()
audit_engine_global = None

@app.post("/start")
def api_start(background_tasks: BackgroundTasks):
    background_tasks.add_task(audit_engine_global.start_audit)
    return {"status": "Audit started in background"}

@app.get("/report")
def api_report():
    file = audit_engine_global.generate_report()
    if file: return FileResponse(file)
    return {"error": "No findings yet"}

# --- ENTRY POINT ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--web", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        # Exemplo de config caso não exista
        example_config = {
            "targets": [
                {"name": "Local_Files", "type": "filesystem", "path": "./", "recursive": True}
            ]
        }
        with open(args.config, 'w') as f: yaml.dump(example_config, f)

    with open(args.config, 'r') as f:
        config_data = yaml.safe_load(f)

    audit_engine_global = AuditEngine(config_data)

    if args.web:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8080)
    else:
        audit_engine_global.start_audit()
        audit_engine_global.generate_report()
