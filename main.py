import argparse
from scanner.data_scanner import DataScanner
from scanner.db_connector import DBConnector
from utils.logger import Logger
from report.report_generator import ReportGenerator

def main():
    parser = argparse.ArgumentParser(description="Scanner de Dados Sensíveis")
    parser.add_argument("--cli", action="store_true", help="Executar no modo CLI")
    parser.add_argument("--api", action="store_true", help="Iniciar servidor API")
    args = parser.parse_args()

    logger = Logger()
    db_connector = DBConnector(logger)
    
    # Exemplo de URL SQLAlchemy (ajuste conforme sua configuração)
    db_url = "mysql+pymysql://user:password@localhost:3306/database_name"
    
    db_connector.connect(db_url)

    if args.cli:
        scanner = DataScanner(db_connector)
        resultados = scanner.scan()
        report = ReportGenerator(resultados)
        print(report.gerar_relatorio())
    elif args.api:
        from app import app
        app.run(host="0.0.0.0", port=8000)
    else:
        print("Use --cli para executar no modo CLI ou --api para iniciar o servidor API.")

