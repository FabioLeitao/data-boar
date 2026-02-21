class ReportGenerator:
    def __init__(self, resultados):
        self.resultados = resultados

    def gerar_relatorio(self):
        relatorio = "Relatório de Dados Sensíveis:\n\n"
        for resultado in self.resultados:
            relatorio += f"Tipo: {resultado['tipo']}\n"
            relatorio += f"Valor: {resultado['valor']}\n"
            relatorio += f"Regex Match: {resultado['regex_match']}\n"
            relatorio += f"Classificação ML: {resultado['ml_classification']}\n\n"
        return relatorio

