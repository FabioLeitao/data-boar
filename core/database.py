import uuid
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class AuditFinding(Base):
    __tablename__ = 'audit_findings'
    
    id = Column(Integer, primary_key=True)
    # Identificador único da execução para análise de evolução
    scan_session_id = Column(String(50), index=True) 
    timestamp = Column(DateTime, default=datetime.now)

    target_name = Column(String(100))      # Nome do banco ou pasta (conforme config.yaml)
    source_type = Column(String(50))        # 'database' ou 'filesystem'
    server_ip = Column(String(50))          # IP do host ou caminho de rede
    engine_version = Column(String(100))    # Versão do DB ou Sistema de Arquivos
    
    # Localização exata
    schema_name = Column(String(100))       # Schema (se DB)
    table_name = Column(String(100))        # Tabela ou Nome do Arquivo
    column_name = Column(String(100))       # Coluna ou 'N/A' (se arquivo)
    
    # Classificação
    data_type = Column(String(50))          # Tipo de dado (VARCHAR, PDF, etc)
    sensitivity_level = Column(String(20))  # HIGH, MEDIUM, LOW
    pattern_detected = Column(String(100))  # LGPD_CPF, GDPR_EMAIL, etc
    sample_format = Column(Text)            # Exemplo de formato (sem o dado real)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Status para evolução (Novo, Persistente, Removido)
    status = Column(String(20), default="DETECTED") 


class LocalDBManager:
    def __init__(self, db_path="audit_results.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        # Geramos um ID único para esta sessão de auditoria
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def save_finding(self, **kwargs):
        session = self.Session()
        try:
            finding = AuditFinding(**kwargs)
            session.add(finding)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Erro ao salvar no SQLite local: {e}")
        finally:
            session.close()
