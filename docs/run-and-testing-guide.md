# Execution, Verification & Screenshot Proof Guide

## Automated Local DevSecOps — Secret Scanner & Image Guard

This guide provides the complete flowwise execution commands, expected outputs, and exact instructions on where to capture screenshots proving that both security gates operate correctly under both scenarios (**PASS &check;** and **FAIL &cross;**).

---

## 1. Overview of Scenarios & Security Gates

| Security Gate | Tool | Scenario 1: PASS (&check;) | Scenario 2: FAIL (&cross;) |
| :--- | :--- | :--- | :--- |
| **Gate 1: Secret Detection** | **Gitleaks** | Clean configuration (`clean.env`) produces **0 leaks** and returns **Exit Code `0`**. | Mock credentials (`bad.env`) trigger custom rules, produce **3 detections**, and return **Exit Code `1`**. |
| **Gate 2: Container Security** | **Docker + Aqua Trivy** | Hardened container (`devsecops-demo:local`) has **0 HIGH/CRITICAL CVEs** and returns **Exit Code `0`**. | Legacy unpatched image (`python:3.8-slim-buster`) triggers **HIGH/CRITICAL CVEs** and halts with **Exit Code `1`**. |
| **Gate 3: CI/CD Pipeline** | **GitHub Actions** | Push with clean code yields green checkmarks across all jobs. | Commits with secrets or vulnerable base images block the workflow with red failure status. |

---

## 2. Environment Preparation

Open **Windows PowerShell** in the project root directory:

```powershell
cd c:\Users\sailee\OneDrive\Pictures\Documents\automated-local-devsecops
```

### Pre-Flight Verification
```powershell
# 1. Verify Gitleaks is installed and reachable
gitleaks version

# 2. Verify Docker Desktop daemon is running
docker --version
docker info
```
> [!NOTE]
> If `docker info` fails with a pipe error, open **Docker Desktop** from your Windows Start Menu and wait until the daemon status shows running.

---

## 3. Flowwise Execution: Gate 1 — Secret Security Gate (Gitleaks)

### Scenario 1: Clean Code Scan (PASS &check;)
Scan the safe configuration fixture [`test-secrets/clean.env`](../test-secrets/clean.env):

```powershell
gitleaks dir --config gitleaks/.gitleaks.toml --verbose test-secrets/clean.env; echo "Exit Code: $LASTEXITCODE"
```

#### Expected Terminal Output:
```text
    ○
    │╲
    │ ○
    ○ ░
    ░    gitleaks

8:15PM INF scanned ~763 bytes (763 bytes) in 32.4ms
8:15PM INF no leaks found
Exit Code: 0
```

#### 📸 Where to Take Screenshot:
- **Location:** PowerShell terminal window.
- **Key Evidence to Highlight:**
  1. Input command pointing to `test-secrets/clean.env`.
  2. `INF no leaks found`.
  3. `Exit Code: 0`.

---

### Scenario 2: Detected Leaks / Vulnerable Code (FAIL &cross;)
Scan the fixture containing simulated leaked credentials [`test-secrets/bad.env`](../test-secrets/bad.env):

```powershell
gitleaks dir --config gitleaks/.gitleaks.toml --verbose test-secrets/bad.env; echo "Exit Code: $LASTEXITCODE"
```

#### Expected Terminal Output:
```text
Finding:     API_KEY="FAKE_API_KEY_123456"
Secret:      FAKE_API_KEY_123456
RuleID:      generic-api-key-assignment
Entropy:     3.681881
File:        test-secrets/bad.env
Line:        14

Finding:     ACCESS_TOKEN="superSecretToken_Demo_NotReal_9999"
Secret:      superSecretToken_Demo_NotReal_9999
RuleID:      generic-api-key-assignment
Entropy:     3.998652
File:        test-secrets/bad.env
Line:        23

Finding:     DATABASE_PASSWORD="mysecret123"
Secret:      mysecret123
RuleID:      generic-password-assignment
Entropy:     3.277613
File:        test-secrets/bad.env
Line:        11

8:17PM WRN leaks found: 3
Exit Code: 1
```

#### 📸 Where to Take Screenshot:
- **Location:** PowerShell terminal window.
- **Key Evidence to Highlight:**
  1. The 3 detected secrets with their RuleIDs (`generic-password-assignment`, `generic-api-key-assignment`).
  2. `WRN leaks found: 3`.
  3. `Exit Code: 1` demonstrating the pipeline guard blocked execution.

---

## 4. Flowwise Execution: Gate 2 — Container Security Gate (Docker + Trivy)

### Step 4.1: Build the Hardened Application Image
Build the container microservice using [`docker/Dockerfile`](../docker/Dockerfile):

```powershell
docker build -t devsecops-demo:local -f docker/Dockerfile .
```

### Step 4.2: Verify Container Healthcheck (Functional Test)
Run the container locally and query the `/status` endpoint:

```powershell
# Start container in background
docker run -d --rm -p 8080:8080 --name test-demo devsecops-demo:local

# Query microservice health endpoint
Invoke-RestMethod -Uri http://localhost:8080/status | ConvertTo-Json

# Stop container
docker stop test-demo
```

#### Expected Output:
```json
{
  "service": "automated-local-devsecops",
  "module": "Member 2 — Container Security",
  "version": "1.0.0",
  "status": "healthy",
  "non_root": true
}
```

---

### Scenario 1: Hardened Image Vulnerability Scan (PASS &check;)
Scan the hardened production candidate image (`devsecops-demo:local`):

```powershell
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --severity HIGH,CRITICAL --exit-code 1 devsecops-demo:local; echo "Security Gate Exit Code: $LASTEXITCODE"
```

#### Expected Terminal Output:
```text
devsecops-demo:local (alpine 3.21.3)
===================================
Total: 0 (HIGH: 0, CRITICAL: 0)

Security Gate Exit Code: 0
```

#### 📸 Where to Take Screenshot:
- **Location:** PowerShell terminal window.
- **Key Evidence to Highlight:**
  1. Scanned target name: `devsecops-demo:local`.
  2. Vulnerability tally: `Total: 0 (HIGH: 0, CRITICAL: 0)`.
  3. Exit code: `Security Gate Exit Code: 0`.

---

### Scenario 2: Vulnerable Container Image Scan (FAIL &cross;)
Scan an unpatched legacy image (`python:3.8-slim-buster`) to prove Trivy flags vulnerabilities and blocks the gate:

```powershell
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --severity HIGH,CRITICAL --exit-code 1 python:3.8-slim-buster; echo "Security Gate Exit Code: $LASTEXITCODE"
```

#### Expected Terminal Output:
```text
Total: 4 (HIGH: 4, CRITICAL: 0)

┌───────────────────────┬────────────────┬──────────┬────────┬───────────────────┬───────────────┬────────────────────────────────
│        Package        │ Vulnerability  │ Severity │ Status │ Installed Version │ Fixed Version │             Title              │
├───────────────────────┼────────────────┼──────────┼────────┼───────────────────┼───────────────┼────────────────────────────────
│ libsqlite3-0          │ CVE-2023-xxxx  │ HIGH     │ fixed  │ 3.27.2-3+deb10u1  │ 3.27.2-3+deb1 │ ...                            │
└───────────────────────┴────────────────┴──────────┴────────┴───────────────────┴───────────────┴────────────────────────────────

Security Gate Exit Code: 1
```

#### 📸 Where to Take Screenshot:
- **Location:** PowerShell terminal window.
- **Key Evidence to Highlight:**
  1. The vulnerability table listing the detected CVE identifiers and severity ratings.
  2. `Total: 4 (HIGH: 4, CRITICAL: 0)`.
  3. `Security Gate Exit Code: 1` demonstrating the gate prevented downstream deployment.

---

## 5. Flowwise Execution: Gate 3 — Automated CI/CD (GitHub Actions)

### Step 5.1: Push Changes to Trigger Pipeline
```powershell
git status
git add .
git commit -m "docs: add comprehensive execution and verification testing guide"
git push origin main
```

### 📸 Where to Take Screenshots on GitHub:

1. **GitHub "Actions" Tab (`https://github.com/<your-username>/<repo>/actions`):**
   - Click on the latest workflow run for **Container Security Gate** or **Secret Security Gate**.
   - **PASS Screenshot Proof:**
     - Expand the job steps.
     - Capture the green checkmark &check; on `Aqua Security Trivy` showing `0 HIGH, CRITICAL vulnerabilities`.
     - Capture the overall green workflow banner: `All jobs have succeeded`.
   - **FAIL Screenshot Proof (Simulated via branch or PR):**
     - Push a branch with `test-secrets/bad.env` staged or an unpinned base image.
     - Capture the red cross &cross; showing `Process completed with exit code 1.` and workflow marked as `Failed`.

2. **Pull Request "Checks" Widget:**
   - Under the PR conversation tab, capture the checks box at the bottom showing:
     - `Run Gitleaks Security Gate — Successful in ...` (&check;)
     - `Container Security Gate / scan — Successful in ...` (&check;)

---

## 6. Quick Reference Command Summary

```powershell
# ==========================================
# GATE 1: GITLEAKS SECRET SCANNER
# ==========================================
# Scenario 1 (PASS):
gitleaks dir --config gitleaks/.gitleaks.toml --verbose test-secrets/clean.env; echo "Exit Code: $LASTEXITCODE"

# Scenario 2 (FAIL):
gitleaks dir --config gitleaks/.gitleaks.toml --verbose test-secrets/bad.env; echo "Exit Code: $LASTEXITCODE"

# ==========================================
# GATE 2: DOCKER & AQUA TRIVY CONTAINER SCAN
# ==========================================
# Build Hardened Image:
docker build -t devsecops-demo:local -f docker/Dockerfile .

# Scenario 1 (PASS):
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --severity HIGH,CRITICAL --exit-code 1 devsecops-demo:local; echo "Security Gate Exit Code: $LASTEXITCODE"

# Scenario 2 (FAIL):
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --severity HIGH,CRITICAL --exit-code 1 python:3.8-slim-buster; echo "Security Gate Exit Code: $LASTEXITCODE"
```
