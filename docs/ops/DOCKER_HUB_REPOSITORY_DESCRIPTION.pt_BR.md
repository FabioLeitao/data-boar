# Docker Hub — descrição do repositório (fonte para copiar/colar)

**English (canônico):** [DOCKER_HUB_REPOSITORY_DESCRIPTION.md](DOCKER_HUB_REPOSITORY_DESCRIPTION.md)

**Objetivo:** O texto curto e a descrição longa no [Docker Hub](https://hub.docker.com/r/fabioleitao/data_boar) **não** ficam versionados no Git. O documento em inglês [DOCKER_HUB_REPOSITORY_DESCRIPTION.md](DOCKER_HUB_REPOSITORY_DESCRIPTION.md) é a **fonte** para colar após cada release, alinhada a **`pyproject.toml`** e às notas em **`docs/releases/`**.

**Quando atualizar:** Logo após **`docker push`** de **`fabioleitao/data_boar:<semver>`** e **`latest`**. Atualize a linha da versão no bloco **Short description** e no corpo **Full description** no arquivo em inglês.

**Checklist:** Veja a seção **Maintainer checklist** no documento em inglês (inclui **copyright/mantenedor** no bloco **Full** — com link opcional ao **LinkedIn** do mantenedor para contexto profissional); mantenha **[PUBLISHED_SYNC.md](today-mode/PUBLISHED_SYNC.md)** coerente com o que os clientes podem puxar do Hub.

**Versão em todos os artefatos:** [VERSIONING.md](../VERSIONING.md) (seção **6. Distribuição…**, EN) — Docker Hub, `PUBLISHED_SYNC`, TECH_GUIDE, rascunhos sociais.
