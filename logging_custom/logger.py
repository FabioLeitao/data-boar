# logging_custom/logger.py
import logging
import json
import smtplib
from email.mime.text import MIMEText

# Configuração básica de logging
def setup_logging(log_config):
    logging.basicConfig(
        level=log_config["log_level"],
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("lgpd_violation.log"),
            logging.StreamHandler()
        ]
    )
    logging.info("Configuração de logging aplicada")

# Função para notificar violações (exemplo com email)
def notify_violation(data):
    try:
        # Configuração de email (ajuste conforme sua configuração)
        config = {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "email_from": "your_email@example.com",
            "email_to": "admin@example.com",
            "email_subject": "Violação de LGPD detectada",
            "email_body": f"Violação de LGPD detectada em dados: {json.dumps(data)}"
        }

        msg = MIMEText(config["email_body"])
        msg["Subject"] = config["email_subject"]
        msg["From"] = config["email_from"]
        msg["To"] = config["email_to"]

        with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
            server.starttls()
            server.login(config["email_from"], "senha_email")  # Substitua pela senha real
            server.send_message(msg)

        print("Notificação enviada com sucesso.")
    except Exception as e:
        print(f"Erro ao enviar notificação: {e}")

