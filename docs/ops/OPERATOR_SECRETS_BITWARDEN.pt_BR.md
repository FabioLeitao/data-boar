# Segredos do operador: Bitwarden (cofre pessoal)

**Objetivo:** O **Bitwarden** pode ser o **repositório de segredos** onde **você** guarda senhas e chaves; o Data Boar continua usando **`pass_from_env`** / variáveis de ambiente em **runtime**. Não substitui o **vault dentro da app** planejado na [PLAN_SECRETS_VAULT.md](../plans/PLAN_SECRETS_VAULT.md) (fase B).

**Grátis:** em geral **suficiente** para uso solo (senhas ilimitadas, sync, 2FA na **conta** Bitwarden — ative).

**Pago:** faz sentido para **TOTP no cofre**, **anexos** criptografados, **Famílias/Equipes** ou **emergency access** — confira [bitwarden.com/pricing](https://bitwarden.com/pricing/).

**Documento completo (EN):** [OPERATOR_SECRETS_BITWARDEN.md](OPERATOR_SECRETS_BITWARDEN.md)

**Bitwarden Authenticator (ex. iPhone):** QR → **TOTP/OTP**, sincronização com a conta Bitwarden — alinhado ao mesmo cofre que extensão/desktop; capacidades exatas conforme plano e documentação atual da Bitwarden.

**Confirmar `bw` em cada máquina:** o repositório **não** consegue ver o seu Latitude ou mini-PC. Em cada Linux: `command -v bw && bw --version`. Ou **execute** `scripts/homelab-host-report.sh` (inclui bloco `bw` se existir no `PATH`). Ver a seção **“Verify bw”** no EN.

---

## Compartilhar segredos (parceiro, lab-op, equipe pequena)

**O compartilhamento no Bitwarden não é “dar acesso ao meu cofre pessoal”.** Usa-se uma **organização** (plano pago: **Teams**, **Enterprise**, ou **Famílias** para contexto familiar). Cada pessoa mantém **sua** conta Bitwarden; a org tem **coleções** compartilhadas.

## Passos habituais:

1. **Quem paga / admin** — uma conta cria ou faz upgrade da org em [bitwarden.com/pricing](https://bitwarden.com/pricing/) (confirmar nomes e limites atuais).
1. **Criar a organização** no cofre web (**console de administração**), ex.: `Homelab` ou `Lab-op`.
1. **Convidar por e-mail** — o outro **aceita** com conta Bitwarden existente (ou cria conta).
1. **Criar coleções** por tema: `UniFi`, `SNMP`, `GitHub`, `API solar`, `SSH`, `LAB-OP — notas` — evitar **dados secretos no nome** da coleção.
1. **Mover ou duplicar** itens para essas coleções e definir **permissões** (só leitura vs editar).
1. **2FA** obrigatório para quem **acessa** credenciais de produção; **códigos de recuperação** guardados fora do disco do projeto (impresso / cofre físico, conforme guia Bitwarden).

**Famílias vs Teams:** **Famílias** costuma chegar para **duas pessoas + compartilhamento no âmbito familiar**; **Teams** para **colaboradores nomeados** e mais **auditoria/admin** — comparar no site antes de escolher.

**CLI `bw`:** Depois de `bw login` / `bw unlock`, itens da org aparecem na CLI conforme **suas** permissões nas coleções. Usar **`BW_SESSION`** com TTL curto em scripts; **nunca** commitar o token de sessão.

**Documento EN (detalhe + “Practices”):** [OPERATOR_SECRETS_BITWARDEN.md](OPERATOR_SECRETS_BITWARDEN.md)
