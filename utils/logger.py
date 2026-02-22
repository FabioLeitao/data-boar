import logging

def setup_live_logger():
    logger = logging.getLogger("AuditLive")
    logger.setLevel(logging.INFO)
    
    # Log para arquivo
    fh = logging.FileHandler("audit_execution.log")
    # Log para console (ao vivo)
    ch = logging.StreamHandler()
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

# Uso durante a varredura:
# logger.info(f"Conectado com sucesso ao banco {db_name}")
# if sensitive_found:
#    logger.warning(f"VIOLAÇÃO DETECTADA: {pattern} em {table}.{column}")
