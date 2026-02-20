import json

def generate_report(data: List[Dict]) -> str:
    """Gera um relatório JSON com os dados sensíveis."""
    return json.dumps(data, indent=2)

# Exemplo de uso
if __name__ == "__main__":
    report = generate_report([
        {
            "schema": "public",
            "table": "clientes",
            "column": "cpf",
            "data_type": "varchar(11)",
            "sensitivity": {"lgpd": True, "gdpr": False, "ccpa": False},
            "description": "LGPD (Lei Geral de Proteção de Dados)"
        }
    ])
    with open("report.json", "w") as f:
        f.write(report)

