# Operator Today Mode — 2026-04-06 (Segunda-feira)

> Criado automaticamente no EOD de 2026-04-05 (madrugada).
> Referência: `docs/ops/today-mode/OPERATOR_TODAY_MODE_2026-04-05.md` (dia anterior)

---

## STATUS GERAL

Branch: main — sincronizado com origin.
Última sessão: madrugada 2026-04-04 → 2026-04-05.

---

## PENDÊNCIAS DO DIA ANTERIOR (carryover)

### LEGAL (detalhes em docs/private/)
- [ ] Pendencias juridicas: ver docs/private/ para checklist detalhado

### DATA BOAR / PRODUTO
- [ ] **Commit e push das alterações desta sessão** (ansible/, USAGE.md)
      → `git add deploy/ansible docs/USAGE.md && git commit --trailer "Made-with: Cursor" -m "feat(deploy): add Ansible automation paths A and B"`
- [ ] **Testar playbooks Ansible localmente** (se T14 lab-op disponível)
      → `ansible-playbook site-full.yml --check -i inventory/hosts.ini`
- [ ] **Adicionar seção Ansible ao USAGE.pt_BR.md** (sync EN→pt-BR)
- [ ] **PLANS_TODO.md**: marcar Ansible como adicionado (H3/houseclean ou feature)
- [ ] **Branding rename**: execução do ADR 0014 (renomear python3-lgpd-crawler → data-boar)
      → Cheklist completo em `docs/adr/0014-rename-repo-and-package-python3-lgpd-crawler-to-data-boar.md`

### REDES SOCIAIS / FOUNDER
- [ ] **Revisar posts LinkedIn e X revisados** (blobs + lab-op + milestones) e decidir se publica
- [ ] **InComm**: aguardar kit de onboarding físico antes de atualizar LinkedIn

### INFRAESTRUTURA / HOMELAB
- [ ] **Adaptador USB-C do NVMe** — tentar montar disco clonado (verificar parafuso + partição)
- [ ] **VeraCrypt setup** — sequenciar conforme `docs/private/homelab/VERACRYPT_PRIVATE_REPO_SETUP.pt_BR.md`

---

## PRIORIDADES RECOMENDADAS PARA HOJE

1. **COMMIT Ansible + USAGE.md** — tudo pronto, só falta commitar
2. **pt-BR sync do USAGE.md** — adicionar seção Ansible em USAGE.pt_BR.md
3. **Verificar open PRs**: `gh pr list --state open`
4. **check-all**: `.\scripts\check-all.ps1` — confirmar que tudo verde
5. Se tiver energia: atualizar PLANS_TODO.md com status atual

---

## TIMINGS / LEMBRETES

- **Cadência de estudos (combinado):** 2× CWL + 1× IA por semana (ou 1× outro)
  → CWL: BTF → C3SA → seq. em `docs/plans/PORTFOLIO_AND_EVIDENCE_SOURCES.md` §3.2
- **InComm**: não atualizar LinkedIn até receber kit físico
- **Wabbix**: aguardar retorno de Portugal antes de follow-up

---

## REFERÊNCIAS RÁPIDAS

- Dossie privado: `docs/private/legal_dossier/`
- Carta CISO v4 (CVEs): `CARTA_DISCLOSURE_CISO_v4_CVEs.txt`
- Carta CISO v3 (Wazuh): `CARTA_DISCLOSURE_CISO_v3.txt`
- Ansible deploy: `deploy/ansible/README.md`
- ADR rename: `docs/adr/0014-rename-repo-and-package-python3-lgpd-crawler-to-data-boar.md`
- Plans: `docs/plans/PLANS_TODO.md`