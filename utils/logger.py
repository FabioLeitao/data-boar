import logging

class Logger:
    def __init__(self):
        self.logger = logging.getLogger("DataScanner")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler("scanner.log")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log(self, message, level="info"):
        if level == "info":
            self.logger.info(message)
        elif level == "error":
            self.logger.error(message)

