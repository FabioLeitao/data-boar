#!/bin/bash

# Script de automação para instalação de drivers de sistema
# Foco: Auditoria de Dados (Ubuntu/Debian)

# Cores para saída
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # Sem cor

echo -e "${GREEN}### Iniciando configuração do ambiente de Auditoria ###${NC}"

# Verificar se é root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Por favor, execute como root ou usando sudo.${NC}"
  exit
fi

echo -e "${GREEN}1. Atualizando repositórios...${NC}"
apt-get update && apt-get upgrade -y

echo -e "${GREEN}2. Instalando ferramentas de compilação básicas...${NC}"
apt-get install -y build-essential python3-dev libffi-dev pkg-config libssl-dev libmagic1

echo -e "${GREEN}3. Instalando drivers para Bancos de Dados Comuns...${NC}"
# Postgres
apt-get install -y libpq-dev
# MariaDB / MySQL
apt-get install -y libmariadb-dev-compat libmariadb-dev default-libmysqlclient-dev
# SQLite
apt-get install -y sqlite3 libsqlite3-dev

echo -e "${GREEN}4. Configurando drivers para Microsoft SQL Server (MSSQL)...${NC}"
if ! command -v sqlcmd &>/dev/null; then
  curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor >/usr/share/keyrings/microsoft-archive-keyring.gpg
  curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
  # Detectar versão para o repositório correto
  DISTRO=$(lsb_release -is | tr '[:upper:]' '[:lower:]')
  CODENAME=$(lsb_release -cs)
  echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/ubuntu/$(lsb_release -rs)/prod $CODENAME main" >/etc/apt/sources.list.d/mssql-release.list
  apt-get update
  ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev
else
  echo "Drivers MSSQL já detectados."
fi
n
echo -e "${GREEN}5. Instalando dependências para Oracle e IBM DB2 (Bibliotecas de suporte)...${NC}"
# Oracle Instant Client requer libaio1
apt-get install -y libaio1

echo -e "${GREEN}6. Instalando dependências para extração de arquivos (PDF/Docx/Imagens)...${NC}"
# Dependências para processamento de documentos e imagens se necessário
apt-get install -y libxml2-dev libxslt1-dev zlib1g-dev

echo -e "${GREEN}7. Verificando instalação do gerenciador 'uv'...${NC}"
if ! command -v uv &>/dev/null; then
  echo "Instalando o gerenciador uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  source $HOME/.cargo/env
else
  echo "Gerenciador uv já está instalado."
fi

echo -e "${GREEN}### Instalação Concluída com Sucesso! ###${NC}"
echo -e "Agora você pode executar: ${GREEN}uv pip install -r requirements.txt${NC}"
