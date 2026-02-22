
from core.ml_engine import MLSensitivityScanner
import re

class DataScanner:
    def __init__(self):
        self.ml_engine = MLSensitivityScanner()
        self.patterns = {
            "LGPD_CPF": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
            #"LGPD_RG": r"\b\d{2}\.\d{3}\.\d{3}-\d{1}\b",
            #"LGPD_DATA": r"\b\d{2}\/\d{2}\/\d{4}\b",
            #"LGPD_GENERO": r"m|M|masculino|Masculino|Masc|male|Male|f|F|feminino|Feminino|Fem|female|Female|FEMALE|MALE|Not prefer to say\b",
            "EMAIL": r"[\w\.-]+@[\w\.-]+\.\w+",
            #"CCPA_SSN": r"\b\d{3}-\d{2}-\d{4}\b",
            "CARD": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
            "EMAIL": r"[\w\.-]+@[\w\.-]+\.\w+",
            "CREDIT_CARD": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "PHONE": r"\+?\d{2,3}\s?\(?\d{2,3}\)?\s?\d{4,5}-?\d{4}"
            # ... outros padrões
        }

    def analyze_data(self, column_name, sample_content):
        """
        Analisa a sensibilidade usando abordagem híbrida.
        """
        score = 0.0
        details = []

        # 1. Verificação por Regex (Peso Alto)
        for label, pattern in self.patterns.items():
            if re.search(pattern, str(sample_content)):
                score += 0.8
                details.append(label)

        # 2. Verificação por ML no nome da coluna e conteúdo (Peso Médio)
        ml_score_name = self.ml_engine.predict_sensitivity(column_name)
        ml_score_content = self.ml_engine.predict_sensitivity(sample_content)
        
        combined_ml = (ml_score_name * 0.4) + (ml_score_content * 0.6)
        score += combined_ml

        # Classificação Final baseada nos requisitos LGPD/GDPR/CCPA
        if score > 0.9:
            return "HIGH", " | ".join(details) if details else "ML_DETECTED_SENSITIVE"
        elif score > 0.3:
            return "MEDIUM", "POTENTIAL_PERSONAL_DATA"
        
        return "LOW", "GENERAL_DATA"
