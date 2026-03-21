# Segredos do operador: Bitwarden (cofre pessoal)

**Objetivo:** O **Bitwarden** pode ser o **repositório de segredos** onde **você** guarda senhas e chaves; o Data Boar continua a usar **`pass_from_env`** / variáveis de ambiente em **runtime**. Não substitui o **vault dentro da app** planejado na [PLAN_SECRETS_VAULT.md](../plans/PLAN_SECRETS_VAULT.md) (fase B).

**Grátis:** em geral **suficiente** para uso solo (senhas ilimitadas, sync, 2FA na **conta** Bitwarden — ative).

**Pago:** faz sentido para **TOTP no cofre**, **anexos** criptografados, **Famílias/Equipes** ou **emergency access** — confira [bitwarden.com/pricing](https://bitwarden.com/pricing/).

**Documento completo (EN):** [OPERATOR_SECRETS_BITWARDEN.md](OPERATOR_SECRETS_BITWARDEN.md)

**Bitwarden Authenticator (ex. iPhone):** QR → **TOTP/OTP**, sincronização com a conta Bitwarden — alinhado ao mesmo cofre que extensão/desktop; capacidades exatas conforme plano e documentação atual da Bitwarden.

**Confirmar `bw` em cada máquina:** o repositório **não** consegue ver o seu Latitude ou mini-PC. Em cada Linux: `command -v bw && bw --version`. Ou **execute** `scripts/homelab-host-report.sh` (inclui bloco `bw` se existir no `PATH`). Ver a seção **“Verify bw”** no EN.
