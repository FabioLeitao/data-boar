# Skill: GPG Key Lifecycle Management

Apply when: managing GPG keys (create, revoke, publish, configure git signing, GitHub upload).

## Standard GPG path on this machine

```powershell
$gpg = "C:\Program Files\GnuPG\bin\gpg.exe"
```

## Key inventory (primary Windows dev PC keystore)

| Key ID | Algorithm | Emails | Status | Notes |
|---|---|---|---|---|
| `871542E6F789F64F` | ED25519 | gmail + outlook | ACTIVE | Primary signing key |
| `AD93917A9ED8C7EA` | DSA1024 | gmail | REVOKED | Superseded 2026-04-04 |
| `5D51F19DB731BEFE` | DSA1024 | onsite+gmail | REVOKED | Superseded 2026-04-04 |
| Others | DSA1024 | various employers | EXPIRED/unknown | Retain for historical record |

## Fingerprint (ED25519 primary)

`D6F81740 AA5FAB8A CE5716AF 871542E6 F789F64F`

## Publish to keyservers

```powershell
$gpg = "C:\Program Files\GnuPG\bin\gpg.exe"
$keyId = "D6F81740AA5FAB8ACE5716AF871542E6F789F64F"
& $gpg --keyserver hkps://keyserver.ubuntu.com --send-keys $keyId
& $gpg --keyserver hkps://keys.openpgp.org --send-keys $keyId
& $gpg --keyserver hkps://keys.mailvelope.com --send-keys $keyId
```

## Add to GitHub (requires write:gpg_key scope)

```powershell
# Step 1: refresh scope
gh auth refresh -h github.com -s write:gpg_key
# Step 2: export and add (after browser device flow)
& $gpg --armor --export $keyId | Out-File -Encoding ascii "$env:TEMP\gpg_pub.asc"
gh gpg-key add "$env:TEMP\gpg_pub.asc"
```

**Alternative (manual):** copy the armor block to <https://github.com/settings/gpg/new>

## Why some keys show "Verified" on GitHub

GitHub marks a GPG key as "Verified" if **at least one UID email** in the key matches a **verified email** in the GitHub account settings.
- UIDs that match verified account emails show **Verified**.
- Legacy/corporate UIDs that are no longer verified show **Unverified**.

## Revoking a key (interactive via Process)

```powershell
$gpg = "C:\Program Files\GnuPG\bin\gpg.exe"
$keyToRevoke = "<KEY_ID>"
$outFile = "$env:TEMP\revoke_$keyToRevoke.asc"
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $gpg
$psi.Arguments = "--command-fd 0 --output `"$outFile`" --gen-revoke $keyToRevoke"
$psi.RedirectStandardInput = $true; $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true
$proc = [System.Diagnostics.Process]::Start($psi)
$proc.StandardInput.WriteLine("y")   # confirm
$proc.StandardInput.WriteLine("3")   # reason: no longer used
$proc.StandardInput.WriteLine("Superseded by ED25519 D6F81740AA5FAB8ACE5716AF871542E6F789F64F")
$proc.StandardInput.WriteLine("")    # end description
$proc.StandardInput.WriteLine("y")   # confirm again
$proc.StandardInput.Close(); $proc.WaitForExit(15000)
& $gpg --import $outFile  # apply revocation locally
# Then publish to keyservers (see above)
```

## Git signing (current config)

```
gpg.format = ssh
user.signingkey = C:\Users\<username>\.ssh\id_ed25519
commit.gpgsign = true
```

SSH signing is active. To switch to GPG for a specific repo:

```bash
git config gpg.format openpgp
git config user.signingkey D6F81740AA5FAB8ACE5716AF871542E6F789F64F
```

Dual signing (SSH + GPG simultaneously) is NOT supported by git natively.

## Whisper audio transcription (approved tool)

```powershell
# Install (one-time)
uv tool install openai-whisper
winget install --id Gyan.FFmpeg -e
# Run (use safe filenames without special chars)
$env:PYTHONUTF8 = "1"
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
whisper "path\to\audio.m4a" --language Portuguese --model small --output_dir "path\to\output" --output_format txt
```

Model sizes: tiny=39MB fast, small=244MB good quality, medium=769MB best for pt-BR.