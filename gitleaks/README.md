# Gitleaks Secret Detection Gate

## Member 1 — DevSecOps Mini-Project: Automated Local DevSecOps — Secret Scanner & Image Guard

---

## What is Gitleaks?

**Gitleaks** is an open-source SAST (Static Application Security Testing) tool that scans Git repositories — including their full commit history — to detect sensitive information that has been accidentally exposed.

It can detect:
- API keys and tokens
- Database passwords
- AWS / cloud credentials
- Private keys (RSA, SSH, PGP)
- GitHub / GitLab personal access tokens
- JWT tokens
- And hundreds of other secret patterns via built-in rules

> **Official site:** https://github.com/gitleaks/gitleaks

---

## Why Do We Need It?

Accidentally committing a secret to a Git repository is one of the **most common and most costly** security mistakes in software development.

| Risk | Example consequence |
|------|---------------------|
| API key leakage | Attacker uses your key to make API calls, runs up your bill |
| Database password leakage | Full database compromise |
| AWS credential leakage | Cloud infrastructure takeover, data breach |
| GitHub token leakage | Source code theft, supply chain attack |
| Private key leakage | HTTPS/SSH impersonation |

Even if you delete the secret in a later commit, **it still exists in Git history** and can be extracted by anyone with repository access.

Gitleaks solves this by scanning **before or immediately after a commit**, giving you an automated gate.

---

## Architecture

```
Developer writes code
        ↓
git add / git commit
        ↓
┌──────────────────────┐
│      Gitleaks        │
│  Scans repository /  │
│  staged files        │
└──────────────────────┘
        ↓
  Secret detected?
  ┌─────┴──────┐
 YES           NO
  ↓             ↓
BLOCK          PASS
  ↓             ↓
Commit/      Next pipeline
Pipeline     stage runs
stopped
```

**Two integration points:**
1. **Pre-commit hook** (local, optional) — blocks commit before it reaches the remote
2. **CI/CD pipeline** (GitHub Actions, Member 4) — blocks deployment if a secret is found in the repo

---

## Project File Structure

```
gitleaks/                        ← This module's home directory
│
├── .gitleaks.toml               ← Gitleaks scan configuration
└── README.md                    ← This file

test-secrets/                    ← Demo test files
├── bad.env                      ← ❌ Contains fake secrets (demo FAIL)
└── clean.env                    ← ✅ Contains only safe config (demo PASS)

docs/
└── secret-scanning.md           ← Extended documentation

.gitignore                       ← Prevents accidental real secret commits
```

---

## Installation (Windows)

### Option 1 — Winget (recommended, built into Windows 10/11)

```powershell
winget install gitleaks
```

### Option 2 — Chocolatey

```powershell
choco install gitleaks
```

### Option 3 — Scoop

```powershell
scoop install gitleaks
```

### Option 4 — Manual download

1. Go to https://github.com/gitleaks/gitleaks/releases/latest
2. Download `gitleaks_<version>_windows_x64.zip`
3. Extract `gitleaks.exe`
4. Move `gitleaks.exe` to a folder on your `PATH` (e.g., `C:\tools\`)

### Verify installation

```powershell
gitleaks version
```

---

## Usage — Scanning the Repository

All commands are run from the **repository root** (`gitleaks/` workspace root).

### Scan the entire Git repository (including full history)

```powershell
gitleaks git --config gitleaks/.gitleaks.toml --verbose
```

- `git` — scan the git repository history
- `--config` — path to our custom configuration file
- `--verbose` — show detailed findings

### Scan only the working directory (no git history)

```powershell
gitleaks dir --config gitleaks/.gitleaks.toml --verbose
```

### Save report to JSON file

```powershell
gitleaks git --config gitleaks/.gitleaks.toml --report-format json --report-path gitleaks-report.json
```

---

## Testing

### Test 1 — ❌ FAIL: bad.env contains fake secrets

```powershell
# Scan the entire repo (bad.env is committed)
gitleaks git --config gitleaks/.gitleaks.toml --verbose
```

**Expected result:**
```
○ (findings) ○ ... rule: generic-password-assignment, file: test-secrets/bad.env
○ (findings) ○ ... rule: generic-api-key-assignment,  file: test-secrets/bad.env
...
WRN leaks found: 4
```

**Exit code:** `1` (non-zero = secrets detected)

### Test 2 — ✅ PASS: clean.env only

To demonstrate a clean scan, scan only the clean file (path is a positional argument in v8):

```powershell
gitleaks dir --config gitleaks/.gitleaks.toml --verbose test-secrets/clean.env
```

Or, if you want to scan the full repo after removing bad.env from git tracking temporarily:

```powershell
git stash        # temporarily stash bad.env changes
gitleaks git --config gitleaks/.gitleaks.toml --verbose
git stash pop    # restore
```

**Expected result:**
```
INF no leaks found
```

**Exit code:** `0` (zero = clean)

---

## Exit Codes

Gitleaks uses standard Unix exit codes that CI/CD pipelines interpret automatically:

| Exit Code | Meaning | CI/CD Action |
|-----------|---------|--------------|
| `0` | No secrets found — clean | ✅ Pipeline continues |
| `1` | Secrets detected | ❌ Pipeline stops, deployment blocked |
| `126` | Unknown flag / config error | ❌ Pipeline stops (fix config) |

### How to check exit code in PowerShell

```powershell
gitleaks git --config gitleaks/.gitleaks.toml
echo "Exit code: $LASTEXITCODE"
```

---

## Optional: Git Pre-Commit Hook

A pre-commit hook runs Gitleaks automatically before every commit.

### Setup (Windows PowerShell)

```powershell
# Create the hook file
New-Item -Path .git\hooks\pre-commit -ItemType File -Force

# Write the hook script
Set-Content -Path .git\hooks\pre-commit -Value @'
#!/bin/sh
echo "[Gitleaks] Scanning staged files for secrets..."
gitleaks git --config gitleaks/.gitleaks.toml --pre-commit --staged --verbose
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
  echo ""
  echo "❌  COMMIT BLOCKED: Gitleaks detected secrets in staged files."
  echo "    Remove the secrets and try again."
  exit 1
fi
echo "✅  Gitleaks scan passed. Proceeding with commit."
exit 0
'@
```

### How it works

1. You run `git commit`
2. Git automatically runs `.git/hooks/pre-commit`
3. Gitleaks scans only the **staged files** (`--staged`)
4. If secrets are found → exit code 1 → **commit is blocked**
5. If clean → exit code 0 → commit proceeds

> **Note:** The `.git/hooks/` directory is not committed to the repository. Each developer must set this up locally. For a team-wide solution, Member 4 can enforce it through GitHub Actions.

---

## CI/CD Integration (Member 1 Reusable Workflow)

Member 1 provides two centralized GitHub Actions workflows:
- **Reusable Workflow:** [reusable-gitleaks.yml](file:///C:/Users/nikit/OneDrive/Pictures/Documents/gitleaks/.github/workflows/reusable-gitleaks.yml)
- **Caller Workflow:** [secret-scan.yml](file:///C:/Users/nikit/OneDrive/Pictures/Documents/gitleaks/.github/workflows/secret-scan.yml)

### Calling the Reusable Workflow
Other repositories and team members (including Member 4's pipeline) can integrate Gitleaks with a simple job invocation:

```yaml
jobs:
  secret-scan:
    uses: Akansha1425/automated-local-devsecops/.github/workflows/reusable-gitleaks.yml@main
    permissions:
      contents: read
    with:
      fetch-depth: 0
```

**Pipeline behaviour:**

```
Gitleaks exit code 0 (PASS)
        ↓
Next stage: Docker build (Member 2)

Gitleaks exit code 1 (FAIL)
        ↓
Pipeline stops
        ↓
Deployment blocked
        ↓
(Optional: Member 4 sends Discord/Slack alert)
```

The key point is: **Gitleaks' exit code does all the work.** GitHub Actions automatically stops the pipeline when any step returns a non-zero exit code.


---

## Security Notes

- `test-secrets/bad.env` contains **only fake, hardcoded, obviously fictional values**
- No real credentials have ever been stored in this repository
- Real `.env` files (with actual credentials) are blocked by `.gitignore`
- The Gitleaks configuration does **not** disable any detection rules
- Always rotate any credential you accidentally commit — even after deleting it, it exists in history

---

## Module Owner

**Member 1** — Secret Detection Gate  
Tools: Gitleaks, Git  
This module is designed to be integrated into the full pipeline by **Member 4** (GitHub Actions + Discord/Slack alerts).
