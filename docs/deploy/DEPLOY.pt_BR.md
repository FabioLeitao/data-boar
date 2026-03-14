# Implantar auditoria LGPD (Docker, Compose, Swarm, Kubernetes)

**English:** [DEPLOY.md](DEPLOY.md)

Você pode executar a aplicação com **Docker** (`docker run`), **Docker Compose**, **Docker Swarm** ou **Kubernetes** — escolha a opção que se adequa ao seu ambiente. Todas usam a mesma imagem; o comportamento padrão é API web e frontend na porta 8088.

## Padrão: API web e frontend

Quando você executa a imagem **sem** sobrescrever o comando (ex.: `docker run ... imagem`, Compose, Swarm ou Kubernetes sem `command`/`args`), o container inicia a **API web e o frontend**:

- **Dashboard:** `http://<host>:8088/` (status, botão **Iniciar varredura**, sessões recentes, download de relatórios).
- **Relatórios:** `http://<host>:8088/reports`
- **Configuração:** `http://<host>:8088/config`
- **Documentação da API:** `http://<host>:8088/docs`
- **Health:** `http://<host>:8088/health`

A porta **8088** é exposta. Config e dados persistentes (SQLite, relatórios) ficam em **`/data`** (monte um volume ou bind mount com `config.yaml`).

## CLI one-shot (sobrescrever)

Para rodar **uma única auditoria pela CLI** em vez da API, sobrescreva o comando do container e passe o config (e opcionalmente `--tenant` / `--technician`):

```bash
docker run --rm -v "$(pwd)/data:/data" \
  SUA_IMAGEM \
  python main.py --config /data/config.yaml --tenant "Acme" --technician "Ops"
```

Ou com `--entrypoint`:

```bash
docker run --rm -v "$(pwd)/data:/data" \
  --entrypoint python \
  SUA_IMAGEM \
  main.py --config /data/config.yaml
```

O relatório é escrito em `report.output_dir` do config (ex.: `/data`). **Não** use `--web` nessas sobrescritas.

## Imagem pré-construída no Docker Hub

Você pode executar a aplicação **sem clonar o repositório** usando a imagem publicada no Docker Hub:

- **Branded (Data Boar):** [hub.docker.com/r/fabioleitao/data_boar](https://hub.docker.com/r/fabioleitao/data_boar) — **`fabioleitao/data_boar:latest`** e **`fabioleitao/data_boar:1.5.1`**
- **Legado:** [hub.docker.com/r/fabioleitao/python3-lgpd-crawler](https://hub.docker.com/r/fabioleitao/python3-lgpd-crawler) — `fabioleitao/python3-lgpd-crawler:latest`

Exemplo:

```bash
docker pull fabioleitao/data_boar:latest
docker run -d -p 8088:8088 -v "$(pwd)/data:/data" -e CONFIG_PATH=/data/config.yaml fabioleitao/data_boar:latest
```

Garanta que `/data/config.yaml` exista (ex.: copie de `deploy/config.example.yaml` no repositório). Para atualizar quando novas versões forem publicadas: `docker pull fabioleitao/data_boar:latest` e reinicie o container ou stack.

## Imagem (build a partir do código)

- **Dockerfile** na raiz do repositório. Build: `docker build -t python3-lgpd-crawler:latest .`
- O Dockerfile usa **multi-stage build**: a etapa final contém apenas bibliotecas de runtime e o código da aplicação (sem ferramentas de build), reduzindo tamanho e superfície de ataque.

## 1. Build e push da imagem

### Opção A – GitHub Container Registry (ghcr.io)

```bash
docker build -t ghcr.io/fabioleitao/python3-lgpd-crawler:latest .
docker login ghcr.io
docker push ghcr.io/fabioleitao/python3-lgpd-crawler:latest
```

### Opção B – Docker Hub (imagem branded Data Boar)

```bash
docker build -t fabioleitao/data_boar:latest -t fabioleitao/data_boar:1.5.1 .
docker login
docker push fabioleitao/data_boar:latest
docker push fabioleitao/data_boar:1.5.1
```

Opcional: publicar a mesma imagem com o nome legado: `docker tag fabioleitao/data_boar:latest fabioleitao/python3-lgpd-crawler:latest` e `docker push ...`. Veja também [DOCKER_SETUP.md](../DOCKER_SETUP.md).

## 2. Preparar o config

A aplicação espera **config em `/data/config.yaml`** dentro do container. Use o mesmo esquema do repositório (veja [USAGE.md](../USAGE.md) e [USAGE.pt_BR.md](../USAGE.pt_BR.md)). Mínimo para apenas API: `targets: []`, `report.output_dir: /data`, `sqlite_path: /data/audit_results.db`, `api.port: 8088`.

**Detecção de sensibilidade (ML/DL):** Configure termos de treino via `ml_patterns_file`, `dl_patterns_file` ou `sensitivity_detection.ml_terms` / `dl_terms` no config. Monte seus arquivos de termos em `/data`. Veja [sensitivity-detection.md](../sensitivity-detection.md) e [sensitivity-detection.pt_BR.md](../sensitivity-detection.pt_BR.md).

Copie `deploy/config.example.yaml`, edite e use volume ou bind mount para `/data`.

### Segurança e endurecimento (opcional)

Práticas opcionais para endurecer a implantação. Veja [SECURITY.md](../../SECURITY.md). A imagem já roda como usuário não-root (`appuser`, UID 1000). Para Kubernetes, você pode adicionar securityContext, NetworkPolicy e PDB (exemplos em `deploy/kubernetes/`).

## 3. Executar como container único (docker run)

```bash
mkdir -p data
cp deploy/config.example.yaml data/config.yaml
# Edite data/config.yaml

docker run -d --name lgpd-audit \
  -p 8088:8088 \
  -v "$(pwd)/data:/data" \
  -e CONFIG_PATH=/data/config.yaml \
  python3-lgpd-crawler:latest
```

Acesso: <http://localhost:8088/> (dashboard), <http://localhost:8088/docs> (API). Parar: `docker stop lgpd-audit && docker rm lgpd-audit`.

## 4. Executar com Docker Compose

Use o arquivo Compose em `deploy/` e opcionalmente um override para bind mount do config:

```bash
mkdir -p data
cp deploy/config.example.yaml data/config.yaml
cp deploy/docker-compose.override.example.yml deploy/docker-compose.override.yml

docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml up -d
```

Logs: `docker compose -f deploy/docker-compose.yml logs -f lgpd-audit`. Parar: `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml down`.

## 5. Docker Swarm

Use o mesmo Compose com `docker stack deploy`:

```bash
docker swarm init
# Com override para bind mount ./data
docker stack deploy -c deploy/docker-compose.yml -c deploy/docker-compose.override.yml lgpd-audit
```

Remover: `docker stack rm lgpd-audit`.

## 6. Kubernetes

Manifests em `deploy/kubernetes/`. Defina a imagem em `deploy/kubernetes/deployment.yaml`. Aplique:

```bash
kubectl apply -f deploy/kubernetes/
```

Detalhes (NodePort, LoadBalancer, Ingress, persistência) em `deploy/kubernetes/README.md`.

## 7. Usar a imagem pública (sem build local)

Em `deploy/docker-compose.yml` defina `image: fabioleitao/python3-lgpd-crawler:latest` e remova ou comente o bloco `build:`. Prepare `/data/config.yaml` como na seção 2 e use docker run, Compose, Swarm ou Kubernetes como acima.

## Resumo

| Objetivo              | Comando / passo                                                                                     |
| --------------------- | -------------------------------------------------------------------------------                     |
| Padrão (API + front)  | Executar imagem sem sobrescrever comando                                                            |
| CLI one-shot          | `docker run ... --entrypoint python IMAGE main.py --config /data/config.yaml`                       |
| Build                 | `docker build -t python3-lgpd-crawler:latest .`                                                     |
| Push                  | `docker tag ... fabioleitao/python3-lgpd-crawler:latest` e `docker push ...`                        |
| **Container único**   | `docker run -d -p 8088:8088 -v ./data:/data python3-lgpd-crawler:latest`                            |
| **Compose**           | `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml up -d`           |
| **Swarm**             | `docker stack deploy -c deploy/docker-compose.yml -c deploy/docker-compose.override.yml lgpd-audit` |
| **Kubernetes**        | `kubectl apply -f deploy/kubernetes/`                                                               |

## Atrás de NAT, load balancer ou proxy reverso

A aplicação funciona corretamente atrás de **NAT**, **load balancer** ou **proxy reverso** (nginx, Traefik, Caddy). Se HTTPS for terminado no proxy, defina **X-Forwarded-Proto: https** nas requisições. Veja [SECURITY.md](../../SECURITY.md) para cabeçalhos de segurança HTTP.
