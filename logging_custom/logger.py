import logging
from typing import Dict

def setup_logging(config: Dict) -> None:
    logging.basicConfig(
        filename="auditoria.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    logger.info("Iniciando auditoria...")

    def notify_violation(data: Dict) -> None:
        logger.error(f"Violação detectada: {data}")
        # Notificação via email/SMS (opcional)

