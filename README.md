# Automated Local DevSecOps — Secret Scanner & Image Guard

## Part 1: Member 1 — Secret Security Gate (Gitleaks)
## Part 2: Member 2 — Container Security Gate (Docker + Trivy)

[![Gitleaks](https://img.shields.io/badge/Security%20Gate-Gitleaks%20v8.21.2-blue.svg)](https://github.com/gitleaks/gitleaks)
[![Trivy](https://img.shields.io/badge/Container%20Security-Aqua%20Trivy%20v0.75.0-blue.svg)](https://github.com/aquasecurity/trivy)
[![Docker](https://img.shields.io/badge/Container-Docker%20Engine%20v29.7.2-2496ED.svg)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions%20Reusable%20Workflow-green.svg)](https://github.com/Akansha1425/automated-local-devsecops)
[![Platform](https://img.shields.io/badge/Platform-Windows%20PowerShell%20%7C%20Ubuntu%20Runner-lightgrey.svg)]()

---

## 1. Project Overview & Part 1 Scope

### 1.1 What is this Project?
**Automated Local DevSecOps — Secret Scanner & Image Guard** is an automated security pipeline designed to enforce security controls at every stage of the software delivery lifecycle.

This repository contains **Part 1 (Member 1: Secret Detection Gate)**. It provides automated detection of hardcoded secrets, API keys, database credentials, and access tokens before code can be deployed or containerized.

### 1.2 The First Security Gate
Accidentally committing credentials to a Git repository is dangerous because **Git retains deleted items in commit history forever**. 

The Gitleaks Secret Detection Gate serves as the **very first defense boundary** in our DevSecOps workflow:
- Scans files before commit (local CLI & pre-commit hook)
- Scans every push and pull request (automated GitHub Actions workflow)
- Scans complete Git commit history to ensure past commits are clean
- Blocks the pipeline with **Exit Code 1** if secrets are detected
- Passes with **Exit Code 0** when code is safe

---

## 2. Team Architecture & Responsibilities

The DevSecOps project is divided across four specialized member modules:

| Member | Module Focus | Core Tools | Status in this Repo |
| :--- | :--- | :--- | :--- |
| **Member 1** | **Secret Security Gate** | **Gitleaks CLI (v8.21.2), Git, GitHub Actions** | **Implemented & Active** |
| **Member 2** | **Container Image Security** | **Docker Engine (v29.7.2), Aqua Trivy (v0.75.0)** | **Implemented & Active** |
| **Member 3** | Kubernetes Security | Minikube, Kyverno | Downstream module (cluster admission policies) |
| **Member 4** | CI/CD Pipeline & Alerts | GitHub Actions, Slack / Discord Webhooks | Downstream module (orchestration & alert dispatch) |

> [!NOTE]
> Members 1 and 2 deliver the secret detection gate and container vulnerability security gate. Kubernetes/Kyverno (Member 3) and pipeline orchestration/alerts (Member 4) are downstream stages.

---

## 3. Security Flow Architecture

```mermaid
flowchart TD
    A[Developer Git Push / PR] --> B[GitHub Actions Runner]
    B --> C[Checkout Repository: fetch-depth: 0]
    C --> D[Member 1: Resolve Gitleaks Configuration]
    D --> E[Execute Gitleaks Scanner]
    E --> F{Secrets Detected?}
    F -- Yes: Leaks Found --> G[Exit Code 1: Pipeline BLOCKED]
    F -- No: Clean Scan --> H[Exit Code 0: Member 1 PASSED]
    G --> I[Developer Notified: Rotate & Purge Credentials]
    H --> J[Member 2: Build Docker Image]
    J --> K[Member 2: Trivy Container Vulnerability Scan]
    K --> L{HIGH or CRITICAL CVEs?}
    L -- Yes: Findings Detected --> M[Exit Code 1: Image BLOCKED]
    L -- No: Clean Scan --> N[Exit Code 0: Member 2 PASSED]
    M --> O[Developer Notified: Patch Base Image / Libs]
    N --> P[Downstream: Member 3 Kubernetes Admission Gate]
```

---

## 4. Repository Structure

```text
automated-local-devsecops/
├── .github/
│   └── workflows/
│       ├── reusable-gitleaks.yml   # Reusable GitHub Actions workflow for secret scan
│       ├── secret-scan.yml         # Member 1 caller workflow
│       └── container-security.yml  # Member 2 Container Security Gate workflow
├── .dockerignore                   # Excludes secrets, git history, and dev artifacts from image
├── .gitignore                      # Excludes binaries, scan reports, and cache directories
├── docker/                         # Member 2 Container Assets
│   ├── Dockerfile                  # Hardened, pinned non-root container specification
│   ├── .dockerignore               # Local build exclusions
│   └── app.py                      # Minimal Python microservice with healthcheck
├── trivy/                          # Member 2 Vulnerability Scanning
│   ├── trivy.yaml                  # Trivy scan configuration (severity: HIGH,CRITICAL, exit-code: 1)
│   └── README.md                   # In-depth Trivy scanning guide and CLI reference
├── docs/
│   ├── secret-scanning.md          # Member 1 technical and rules documentation
│   ├── container-security.md       # Member 2 container threat model and hardening guide
│   └── run-and-testing-guide.md    # Step-by-step commands, scenarios, and screenshot guide
├── gitleaks/
│   ├── .gitleaks.toml              # Central detection rules (default + 3 custom rules)
│   └── README.md                   # Member 1 module documentation
├── gitleaks_install/               # Local Windows binary extraction (git-ignored)
├── test-secrets/                   # Member 1 Safe test fixtures
│   ├── bad.env                     # Intentionally fake credentials (FAIL test fixture)
│   └── clean.env                   # Harmless configuration (PASS test fixture)
└── README.md                       # Root documentation (this file)
```

---

## 5. Detection Rules & Test Fixtures

### 5.1 Rules Configuration (`gitleaks/.gitleaks.toml`)
- **Built-in Rules:** `[extend] useDefault = true` loads 200+ signatures (AWS access keys, GitHub tokens, JWTs, GCP credentials, private keys, Slack tokens).
- **Custom Rule 1 (`generic-password-assignment`):** Catches variables matching `password = "..."`, `passwd = "..."`, or `pwd = "..."` with entropy checks.
- **Custom Rule 2 (`generic-api-key-assignment`):** Catches variables matching `api_key = "..."`, `api_token = "..."`, or `access_token = "..."`.
- **Custom Rule 3 (`aws-secret-key-assignment`):** Catches `aws_secret_access_key = "..."` patterns.

### 5.2 Test Fixtures
1. **`test-secrets/clean.env` (Safe Demo File):**
   Contains non-sensitive keys (`DATABASE_HOST`, `DATABASE_PORT`, `LOG_LEVEL`, `ENABLE_DEBUG`). Produces **0 leaks** and returns **Exit Code 0 (PASS)**.
2. **`test-secrets/bad.env` (Fake Leaks Demo File):**
   Contains intentionally fake mock credentials (`DATABASE_PASSWORD`, `API_KEY`, `ACCESS_TOKEN`). Triggers custom rules, produces **3 detections**, and returns **Exit Code 1 (FAIL)**.

---

## 6. Exact Commands to Run (Windows PowerShell)

All commands below should be executed from the repository root:
`C:\Users\nikit\OneDrive\Pictures\Documents\gitleaks`

### 6.1 Check Gitleaks Version
Verify that the local binary is present and working:

```powershell
.\gitleaks_install\gitleaks.exe version
```
*Expected Output:*
```text
8.21.2
```

---

### 6.2 Run Clean Test Scan (PASS &check;)
Scan the safe configuration file to confirm zero false positives:

```powershell
.\gitleaks_install\gitleaks.exe dir --config gitleaks/.gitleaks.toml --verbose test-secrets/clean.env
echo "Exit Code: $LASTEXITCODE"
```
*Expected Output:*
```text
INF scan completed in 3.13ms
INF no leaks found
Exit Code: 0
```

---

### 6.3 Run Fake Secret Test Scan (FAIL &cross;)
Scan the fixture with fake credentials to verify that detections trigger:

```powershell
.\gitleaks_install\gitleaks.exe dir --config gitleaks/.gitleaks.toml --verbose test-secrets/bad.env
echo "Exit Code: $LASTEXITCODE"
```
*Expected Output:*
```text
Finding:     DATABASE_PASSWORD="mysecret123"
RuleID:      generic-password-assignment
File:        test-secrets/bad.env:11

Finding:     API_KEY="FAKE_API_KEY_123456"
RuleID:      generic-api-key-assignment
File:        test-secrets/bad.env:14

Finding:     ACCESS_TOKEN="superSecretToken_Demo_NotReal_9999"
RuleID:      generic-api-key-assignment
File:        test-secrets/bad.env:23

WRN leaks found: 3
Exit Code: 1
```

---

### 6.4 Scan Entire Git Repository History
Scan all commits in git history using our custom rules:

```powershell
.\gitleaks_install\gitleaks.exe git --config gitleaks/.gitleaks.toml --verbose
echo "Exit Code: $LASTEXITCODE"
```

> [!WARNING]
> **Why this full-history scan returns Exit Code 1:**
> `test-secrets/bad.env` was committed in git history (commit `1c5e958`) for demonstration purposes. Gitleaks inspects every commit in the repository and correctly detects the 3 historical demo secrets. This proves that Gitleaks successfully catches secrets even after they have been committed.

---

### 6.5 Export Scan Results to JSON / SARIF Report
Generate structured reports for auditing:

```powershell
# JSON format report
.\gitleaks_install\gitleaks.exe dir --config gitleaks/.gitleaks.toml --report-format json --report-path gitleaks-report.json test-secrets/bad.env

# SARIF format report (compatible with GitHub Security tab)
.\gitleaks_install\gitleaks.exe dir --config gitleaks/.gitleaks.toml --report-format sarif --report-path gitleaks-report.sarif test-secrets/bad.env
```
*(Note: Generated report files `gitleaks-report.json` and `gitleaks-report.sarif` are ignored by `.gitignore` so they are never accidentally committed).*

---

### 6.6 Optional: Setup Local Git Pre-Commit Hook
Run this one-time PowerShell snippet to block accidental secret commits locally before code ever leaves your machine:

```powershell
# Create pre-commit hook file
New-Item -Path .git\hooks\pre-commit -ItemType File -Force

# Write the hook script
Set-Content -Path .git\hooks\pre-commit -Value @'
#!/bin/sh
echo "[Gitleaks] Scanning staged files for secrets..."
gitleaks git --config gitleaks/.gitleaks.toml --pre-commit --staged --verbose
if [ $? -ne 0 ]; then
  echo ""
  echo "❌ COMMIT BLOCKED: Gitleaks detected secrets in staged files."
  echo "   Remove credentials and try again."
  exit 1
fi
echo "✅ Gitleaks scan passed. Proceeding with commit."
exit 0
'@
```

---

## 7. GitHub Actions Integration

### 7.1 The Workflows
1. **Reusable Workflow ([`.github/workflows/reusable-gitleaks.yml`](file:///.github/workflows/reusable-gitleaks.yml)):**
   A centralized workflow that any repository can call. It checks out the caller's repository, auto-resolves or downloads the shared `.gitleaks.toml` configuration, runs `gitleaks/gitleaks-action@v2`, and enforces exit code status.
2. **Local Caller Workflow ([`.github/workflows/secret-scan.yml`](file:///.github/workflows/secret-scan.yml)):**
   Automatically triggers on every push and pull request to `main` in this repository, invoking the reusable workflow.

### 7.2 How Other Repositories Integrate this Workflow
Any developer can add this security gate to their project by creating `.github/workflows/secret-scan.yml` in their repository:

```yaml
name: Secret Security Gate

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  secret-scan:
    name: Run Gitleaks Security Gate
    uses: Akansha1425/automated-local-devsecops/.github/workflows/reusable-gitleaks.yml@main
    permissions:
      contents: read
    with:
      fetch-depth: 0
    secrets: inherit
```

---

## 8. Git Push Commands

To commit and push the project changes to GitHub:

```powershell
# 1. Check current status
git status

# 2. Stage changes (README, workflows, documentation)
git add README.md .github/ docs/ gitleaks/ docker/ trivy/ .dockerignore .gitignore

# 3. Commit with descriptive message
git commit -m "feat(member1,member2): Secret and Container Security Gates active"

# 4. Push to remote repository
git push origin main
```

---

---

## 9. Exit Code Contract for CI/CD

| Stage | Exit Code | Result | Pipeline Meaning | Action Taken |
| :--- | :---: | :---: | :--- | :--- |
| **Member 1 (Gitleaks)** | **`0`** | **PASS** | No secrets detected in codebase or Git history | &check; Proceeds to Member 2 (Docker/Trivy) |
| **Member 1 (Gitleaks)** | **`1`** | **FAIL** | One or more credentials detected | &cross; Pipeline halted; PR blocked |
| **Member 2 (Trivy)** | **`0`** | **PASS** | 0 HIGH or CRITICAL CVEs in image | &check; Proceeds to Member 3 (Kubernetes) |
| **Member 2 (Trivy)** | **`1`** | **FAIL** | One or more HIGH or CRITICAL CVEs detected | &cross; Pipeline halted; deployment blocked |
| **Any Stage** | **`2`** | **ERROR** | Scanner runtime or configuration error | &cross; Pipeline fails safe |

---

## 10. Member 2: Container Security Gate (Docker + Trivy)

### 10.1 Module Purpose
Once code passes Member 1's Secret Security Gate, Member 2 builds the application container image and scans it for known Common Vulnerabilities and Exposures (CVEs) in both operating system packages (e.g., `musl`, `libcrypto`, `zlib`) and application dependencies.

### 10.2 Exact Commands to Run (Windows PowerShell)

All commands below should be executed from the repository root:

#### Step 1: Verify Docker Desktop is Running
```powershell
docker --version
docker info
```

#### Step 2: Build the Hardened Sample Image
```powershell
docker build -t devsecops-demo:local -f docker/Dockerfile .
```
*Expected Result:*
Image `devsecops-demo:local` is built with non-root user `appuser` (UID 10001), pinned base `python:3.12.9-alpine3.21`, and content size ~17 MB.

#### Step 3: Verify Container Execution & Healthcheck
```powershell
docker run -d --rm -p 8080:8080 --name test-demo devsecops-demo:local
Invoke-RestMethod -Uri http://localhost:8080/status | ConvertTo-Json
docker stop test-demo
```
*Expected Output:*
```json
{
  "service": "automated-local-devsecops",
  "module": "Member 2 — Container Security",
  "version": "1.0.0",
  "status": "healthy",
  "non_root": true
}
```

#### Step 4: Run Trivy Vulnerability Scan (PASS &check;)
```powershell
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock `
  aquasec/trivy:latest image `
  --severity HIGH,CRITICAL `
  --exit-code 1 `
  devsecops-demo:local

echo "Security Gate Exit Code: $LASTEXITCODE"
```
*Expected Output:*
```text
devsecops-demo:local (alpine 3.21.3)
===================================
Total: 0 (HIGH: 0, CRITICAL: 0)

Security Gate Exit Code: 0
```

#### Step 5: Run Failing Test Scan Demonstration (FAIL &cross;)
To test that Trivy properly detects vulnerabilities and returns Exit Code 1 on unpatched images:
```powershell
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock `
  aquasec/trivy:latest image `
  --severity HIGH,CRITICAL `
  --exit-code 1 `
  python:3.8-slim-buster

echo "Security Gate Exit Code: $LASTEXITCODE"
```
*Expected Result:*
Trivy outputs detected CVEs in a terminal table and halts with:
```text
Security Gate Exit Code: 1
```

#### Step 6: Export Machine-Readable JSON Report
```powershell
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock `
  aquasec/trivy:latest image `
  --severity HIGH,CRITICAL `
  --format json `
  devsecops-demo:local | Out-File -Encoding utf8 trivy-report.json
```

---

## 11. Git Push Commands

To commit and push Member 1 and Member 2 changes to GitHub:

```powershell
# 1. Review status
git status

# 2. Stage all implementation files
git add .gitignore .dockerignore docker/ trivy/ docs/container-security.md .github/workflows/container-security.yml README.md

# 3. Commit with standard conventional commit message
git commit -m "feat(member2): implement Docker build and Aqua Trivy container security gate"

# 4. Push to remote repository
git push origin main
```

---

## 12. Member 4: CI/CD Pipeline & Discord Security Alerts

### 12.1 Purpose

The Security Failure Alert workflow integrates GitHub Actions with Discord to notify the team when the `Container Security Gate` workflow fails. This improves visibility of security pipeline failures.

### 12.2 Workflow Behaviour

- **Trigger:** Runs when the `Container Security Gate` workflow completes.
- **Failure notification:** Sends a Discord alert when the monitored workflow concludes with a failure.
- **Successful run:** Skips the Discord notification when the monitored workflow succeeds.
- **Manual test:** Supports `workflow_dispatch` to verify Discord webhook delivery.

### 12.3 Discord Alert Configuration

Configure the following repository secret in GitHub:

- **Secret name:** `DISCORD_WEBHOOK_URL`
- **Purpose:** Stores the Discord webhook URL securely for sending notifications.

To configure it, open the repository's **Settings → Secrets and variables → Actions → New repository secret** and add the secret.

**Security note:** Never commit the webhook URL to source code, README files, screenshots, or logs.

### 12.4 Alert Contents

The Discord notification includes:

- Repository name
- Failed workflow name
- Failure status
- GitHub Actions run URL
- A `Deployment: BLOCKED` message for alert visibility

The deployment message is informational; actual deployment blocking must be enforced and verified separately.

### 12.5 Verification

1. Open the repository's **Actions** tab.
2. Select **Security Failure Alert**.
3. Use **Run workflow** to test Discord webhook delivery manually.
4. Confirm that the workflow completes successfully and the notification appears in the configured Discord channel.

A controlled failure test was performed to verify that a failed monitored workflow triggers a Discord notification.
