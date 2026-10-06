# Automated Local DevSecOps — Gitleaks Secret Detection Gate

## 📌 Overview

This module implements the **Secret Security** component of the Automated Local DevSecOps project using **Gitleaks**.

The purpose of this module is to automatically detect accidentally committed secrets such as:

- API keys
- Passwords
- Access tokens
- AWS credentials
- GitHub tokens
- Other hardcoded sensitive values

The Gitleaks scan acts as a **security gate**. If a secret is detected, the scan fails and the pipeline can block further stages such as Docker image building and deployment.

---

## 🏗️ Security Flow

```text
Developer
    │
    ▼
   Git
    │
    ▼
 Gitleaks
    │
    ├───────────────┐
    │               │
    ▼               ▼
Secret Found     No Secret
    │               │
    ▼               ▼
   FAIL            PASS
    │               │
    ▼               ▼
Block Pipeline   Continue Pipeline
```

### Security Gate Logic

```text
Gitleaks Exit Code 0 → PASS
Gitleaks Exit Code 1 → FAIL / Secrets Detected
```

This allows Gitleaks to be integrated easily into a CI/CD pipeline later.

---

## 📁 Project Structure

```text
gitleaks/
│
├── .gitignore
│
├── gitleaks/
│   ├── .gitleaks.toml
│   └── README.md
│
├── test-secrets/
│   ├── bad.env
│   └── clean.env
│
├── docs/
│   └── secret-scanning.md
│
├── gitleaks_install/
│   └── gitleaks.exe          # Local only, ignored by Git
│
└── README.md
```

### File Description

| File/Folder | Purpose |
|---|---|
| `gitleaks/.gitleaks.toml` | Gitleaks configuration and custom rules |
| `test-secrets/bad.env` | Intentionally vulnerable test file containing fake secrets |
| `test-secrets/clean.env` | Safe test file containing no secrets |
| `docs/secret-scanning.md` | Documentation for secret scanning |
| `gitleaks_install/` | Local Gitleaks executable; excluded from Git |
| `.gitignore` | Prevents local executable and unwanted files from being committed |
| `README.md` | Project documentation |

---

## 🛠️ Technologies Used

- **Git** — Version control
- **Gitleaks v8.21.2** — Secret detection
- **PowerShell** — Local testing on Windows
- **GitHub** — Repository and future CI/CD integration

---

## ⚙️ Installation

Gitleaks is currently configured as a local executable for Windows.

Check the installed version:

```powershell
.\gitleaks_install\gitleaks.exe version
```

Expected output:

```text
8.21.2
```

> The `gitleaks_install/` directory is ignored by Git. Team members can install Gitleaks locally or use the CI/CD runner's Gitleaks installation.

---

## 🔍 Testing Secret Detection

### 1. Scan Git History

Run:

```powershell
.\gitleaks_install\gitleaks.exe git --config .\gitleaks\.gitleaks.toml --verbose
```

This scans the Git repository and its commit history for potential secrets.

If secrets are found, Gitleaks reports information such as:

```text
Finding:     API_KEY="FAKE_API_KEY_123456"
RuleID:      generic-api-key-assignment
File:        test-secrets/bad.env
Line:        14
```

---

## 🚨 Negative Test — Secret Detection

The file:

```text
test-secrets/bad.env
```

contains intentionally fake credentials for testing.

Example:

```env
DATABASE_PASSWORD="mysecret123"
API_KEY="FAKE_API_KEY_123456"
ACCESS_TOKEN="superSecretToken_Demo_NotReal_9999"
```

These values are **not real credentials** and exist only to demonstrate Gitleaks detection.

Run:

```powershell
.\gitleaks_install\gitleaks.exe git --config .\gitleaks\.gitleaks.toml --verbose
```

Expected result:

```text
leaks found: 3
```

Gitleaks should return a non-zero exit code.

Check it using:

```powershell
$LASTEXITCODE
```

Expected:

```text
1
```

This represents a **failed security gate**.

---

## ✅ Positive Test — Clean Repository/File

The file:

```text
test-secrets/clean.env
```

contains only harmless configuration values.

Run:

```powershell
.\gitleaks_install\gitleaks.exe dir --config .\gitleaks\.gitleaks.toml --verbose .\test-secrets\clean.env
```

Expected result:

```text
no leaks found
```

Check:

```powershell
$LASTEXITCODE
```

Expected:

```text
0
```

This represents a **passed security gate**.

---

## 🔐 Security Gate Demonstration

The following PowerShell logic simulates how the Gitleaks result can control a DevSecOps pipeline:

```powershell
.\gitleaks_install\gitleaks.exe git --config .\gitleaks\.gitleaks.toml --verbose

if ($LASTEXITCODE -eq 0) {
    Write-Host "SECURITY GATE PASSED"
} else {
    Write-Host "SECURITY GATE FAILED - DEPLOYMENT BLOCKED"
}
```

### Result

If no secrets are detected:

```text
SECURITY GATE PASSED
```

If secrets are detected:

```text
SECURITY GATE FAILED - DEPLOYMENT BLOCKED
```

---

## 🧪 Test Results

The module was tested using both vulnerable and clean files.

### Test 1 — Secret Detection

**Input:**

```text
test-secrets/bad.env
```

**Expected:** Secrets detected

**Result:**

```text
3 leaks found
Exit Code: 1
```

Status:

```text
PASS ✅
```

The test successfully demonstrated that the security gate detects hardcoded secrets.

### Test 2 — Clean File

**Input:**

```text
test-secrets/clean.env
```

**Expected:** No secrets detected

**Result:**

```text
No leaks found
Exit Code: 0
```

Status:

```text
PASS ✅
```

---

## 📋 Gitleaks Rules

The configuration file:

```text
gitleaks/.gitleaks.toml
```

uses Gitleaks built-in detection rules along with custom rules for common secret assignments.

Examples include:

```text
generic-password-assignment
generic-api-key-assignment
aws-secret-key-assignment
```

This improves detection of common hardcoded credentials in configuration files and source code.

---

## 🔄 Future CI/CD Integration

This module is designed to be integrated into the project's CI/CD pipeline.

The planned workflow is:

```text
Git Push
   │
   ▼
GitHub Actions
   │
   ▼
Gitleaks Secret Scan
   │
   ├── Secret Found ──► ❌ Pipeline Failed
   │
   └── No Secret ─────► ✅ Continue
                            │
                            ▼
                       Docker Build
                            │
                            ▼
                       Trivy Scan
                            │
                            ▼
                    Kubernetes Deployment
                            │
                            ▼
                       Kyverno Policy
```

The Gitleaks stage will act as the **first security gate** in the pipeline.

---

## 👥 Project Team Integration

This module is **Member 1's responsibility** in the larger Automated Local DevSecOps project.

| Member | Responsibility | Technology |
|---|---|---|
| Member 1 | Secret Security | **Gitleaks + Git** |
| Member 2 | Container Security | Docker + Trivy |
| Member 3 | Kubernetes Security | Minikube + Kyverno |
| Member 4 | CI/CD + Alerts + Integration | GitHub Actions + Discord/Slack |

Member 1's output will be consumed by the CI/CD integration implemented by Member 4.

---

## ⚠️ Security Note

The credentials inside:

```text
test-secrets/bad.env
```

are **fake credentials created exclusively for security testing**.

Never place real:

- API keys
- passwords
- access tokens
- AWS credentials
- GitHub tokens
- database credentials

inside the repository.

If a real credential is accidentally committed, it should be considered compromised and should be **revoked/rotated immediately**.

---

## 🎯 Objective Achieved

This module successfully demonstrates a local **DevSecOps Secret Detection Gate** capable of:

- Detecting hardcoded secrets
- Scanning Git history
- Applying custom detection rules
- Returning pipeline-friendly exit codes
- Blocking a pipeline when secrets are detected
- Allowing clean code to pass
- Preparing the project for GitHub Actions CI/CD integration

### Final Security Principle

> **Detect secrets early → Fail the security gate → Prevent insecure code from progressing through the pipeline.**

---

## 📌 Status

**Member 1 — Gitleaks Secret Detection Gate: COMPLETED ✅**
