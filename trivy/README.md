# Container Image Security with Aqua Security Trivy

## Member 2 — Automated Local DevSecOps: Secret Scanner & Image Guard

[![Trivy](https://img.shields.io/badge/Security%20Scanner-Aqua%20Trivy%20v0.75.0-blue.svg)](https://github.com/aquasecurity/trivy)
[![Docker](https://img.shields.io/badge/Container-Docker%20Engine%20v29.7.2-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/Policy-Fail%20on%20HIGH%2CCRITICAL-red.svg)]()

---

## 1. Module Overview

This module represents **Part 2 (Member 2: Container Security Gate)** in the automated DevSecOps pipeline. 

Once source code successfully passes Member 1's Gitleaks Secret Detection Gate, it enters the containerization phase. The application container image is built and subjected to automated vulnerability scanning using **Aqua Security's Trivy** before any deployment or Kubernetes admission (Member 3) is permitted.

### The Problem Trivy Solves
Building a Docker image combines application code with an operating system distribution, third-party system packages (e.g., `openssl`, `glibc`, `busybox`, `libcrypto`), and runtime libraries (e.g., Python `pip`, Node.js `npm`). 

Even if the application source code has zero bugs, the container image can inherit hundreds of publicly known security vulnerabilities (Common Vulnerabilities and Exposures — **CVEs**) present in outdated or unpatched base images and OS packages.

Trivy inspects the built container image layer by layer, catalogs all installed packages, cross-references them against upstream vulnerability databases, and enforces an automated security gate.

---

## 2. Team Pipeline Architecture

```text
Developer Git Push / PR
          │
          ▼
┌────────────────────────────────────────┐
│ Member 1: Secret Security Gate         │
│ Gitleaks Scans Git Commits & History   │
└──────────────────┬─────────────────────┘
                   │
         [Secrets Detected?]
         ├────── YES ──────► [FAIL: Pipeline Blocked (Exit Code 1)]
         │
         NO (Exit Code 0)
         ▼
┌────────────────────────────────────────┐
│ Member 2: Container Security Gate      │ ◄── THIS MODULE
│ 1. Build Image: devsecops-demo:local   │
│ 2. Trivy Vulnerability Scan            │
└──────────────────┬─────────────────────┘
                   │
    [HIGH / CRITICAL Vulnerabilities?]
         ├────── YES ──────► [FAIL: Image Rejected (Exit Code 1)]
         │
         NO (Exit Code 0)
         ▼
┌────────────────────────────────────────┐
│ Member 3: Kubernetes Security Gate     │
│ Cluster Admission & Kyverno Policies   │
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│ Member 4: CI/CD Orchestration & Alerts │
│ GitHub Actions Matrix + Notifications  │
└────────────────────────────────────────┘
```

---

## 3. How Trivy Works

Trivy identifies known vulnerabilities using a multi-step analysis process:

1. **Layer Extraction & Package Discovery**: Trivy unpacks each layer of the target container image (`devsecops-demo:local`) and locates installed package databases:
   - **OS Package Managers**: Alpine (`/lib/apk/db/installed`), Debian/Ubuntu (`/var/lib/dpkg/status`), Red Hat/CentOS (`RPM DB`).
   - **Language Dependencies**: Python (`pip`, `wheel`, `requirements.txt`, `Pipfile.lock`), Node.js (`package-lock.json`), Go (`go.mod`), Java (`pom.xml`), Rust (`Cargo.lock`).
2. **Vulnerability Database Matching**: Trivy downloads a compact, hourly-updated vulnerability database compiled from:
   - National Vulnerability Database (NVD / NIST)
   - Alpine SecDB
   - Debian Security Bug Tracker
   - Red Hat Security Data (OVAL)
   - GitHub Advisory Database
3. **Severity Calculation**: Each CVE is rated according to CVSS v3/v4 scores:
   - **LOW**: Minor issues with low exploitability or minimal impact.
   - **MEDIUM**: Moderate issues requiring specific conditions to exploit.
   - **HIGH**: Significant vulnerabilities with reliable exploits or high impact.
   - **CRITICAL**: Remote Code Execution (RCE), privilege escalation, or unauthenticated exploits.
4. **Policy Enforcement**: If any detected vulnerability meets or exceeds the configured severity threshold (`HIGH,CRITICAL`), Trivy returns **Exit Code 1**, failing the security gate.

---

## 4. Dockerfile Security Best Practices

The sample application in `docker/` adheres to key container hardening principles:

| Hardening Control | Implementation in `docker/Dockerfile` | Security Benefit |
| :--- | :--- | :--- |
| **Pinned Minimal Base** | `python:3.12.9-alpine3.21` | Reduces attack surface to ~17 MB; eliminates unnecessary binaries (e.g. compilers, shells, curl) that attackers exploit. |
| **Non-Root User** | `adduser -u 10001 -S appuser` & `USER 10001:10001` | Prevents container breakout and privilege escalation if the application is compromised. |
| **Explicit Workdir** | `WORKDIR /app` | Avoids writing files to container root filesystem. |
| **Scoped Copying** | `COPY --chown=appuser:appgroup docker/app.py /app/app.py` | Copies only runtime code; prevents test fixtures or sensitive artifacts from entering the image. |
| **Strict .dockerignore** | Excludes `.git`, `test-secrets/`, `*.env`, reports | Guarantees that neither Member 1 test secrets nor local developer credentials can leak into the container. |
| **Active Healthcheck** | `HEALTHCHECK --interval=30s CMD python -c ...` | Enables orchestrators (Docker, Kubernetes) to monitor container state without external agents. |

---

## 5. Local Execution on Windows PowerShell

### 5.1 Prerequisites Check

Verify that Docker Desktop is running on Windows:

```powershell
# 1. Check Docker client and server version
docker --version

# 2. Verify Docker daemon is responsive
docker info
```

### 5.2 Build the Application Container Image

From the repository root:

```powershell
docker build -t devsecops-demo:local -f docker/Dockerfile .
```

*Expected Result:*
Image `devsecops-demo:local` is built successfully with content size under 20 MB.

### 5.3 Run Trivy Image Scan (Enforced Security Gate)

You can run Trivy locally either using the official Docker container or via the native Windows executable.

#### Method A: Using Trivy Docker Container (Recommended, Zero Local Dependencies)
```powershell
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --severity HIGH,CRITICAL --exit-code 1 devsecops-demo:local
echo "Security Gate Exit Code: $LASTEXITCODE"
```

#### Method B: Using Native Windows Trivy (Installed via Winget)
To install native Trivy:
```powershell
winget install AquaSecurity.Trivy
```
Then run:
```powershell
trivy image --config trivy/trivy.yaml devsecops-demo:local
echo "Security Gate Exit Code: $LASTEXITCODE"
```

*Expected Result for Hardened Demo Image:*
```text
devsecops-demo:local (alpine 3.21.3)
===================================
Total: 0 (HIGH: 0, CRITICAL: 0)

Security Gate Exit Code: 0
```
Status: **PASS &check;** (Exit Code 0).

---

## 6. Machine-Readable JSON Export

For compliance evidence, audit logging, and automated consumption by Member 4:

```powershell
# Run scan and export structured JSON evidence
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock `
  aquasec/trivy:latest image `
  --severity HIGH,CRITICAL `
  --format json `
  --output /dev/stdout devsecops-demo:local | Out-File -Encoding utf8 trivy-report.json

# Check file existence
Get-Item trivy-report.json
```
*(Note: `trivy-report.json` is listed in `.gitignore` and `.dockerignore` so audit artifacts are never committed).*

---

## 7. Pass vs. Fail Behavior

### Passing Scenario (&check; Exit Code 0)
When scanning `devsecops-demo:local`:
- Base OS is patched Alpine Linux 3.21.
- No third-party packages with known HIGH or CRITICAL CVEs are detected.
- Result: **0 High, 0 Critical**. Exit Code: **0**.
- Pipeline outcome: Security gate succeeds; image is approved for Kubernetes deployment (Member 3).

### Failing Scenario (&cross; Exit Code 1)
To demonstrate gate failure when an unpatched or vulnerable container is introduced, run Trivy against an outdated image (e.g. `python:3.8-slim-buster` or unpatched legacy base):
```powershell
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --severity HIGH,CRITICAL --exit-code 1 python:3.8-slim-buster
echo "Security Gate Exit Code: $LASTEXITCODE"
```
*Expected Result:*
Trivy outputs detected CVEs (e.g. `CVE-2023-xxxx`, `CVE-2024-xxxx`) in a red terminal table, blocks deployment, and outputs:
```text
Security Gate Exit Code: 1
```

---

## 8. Exit Code Contract

| Exit Code | Meaning | Pipeline Action |
| :---: | :--- | :--- |
| **`0`** | **PASS**: No HIGH or CRITICAL vulnerabilities detected. | Pipeline advances to Member 3 (Kubernetes / Kyverno). |
| **`1`** | **FAIL**: One or more HIGH or CRITICAL CVEs found. | Pipeline halted immediately; pull request blocked. |
| **`2`** | **ERROR**: Scan failed (network failure, invalid image name, engine error). | Pipeline aborted with error; fails safe (does not pass). |

---

## 9. Cleanup Commands

To remove local demo images after testing:

```powershell
docker rmi devsecops-demo:local
```

---

## 10. Security Limitations

While Trivy is a state-of-the-art static vulnerability scanner, it has known boundaries:
1. **Known vs. Unknown Vulnerabilities**: Trivy detects known CVEs published in security advisories. It cannot identify zero-day vulnerabilities or custom logical flaws in your proprietary code.
2. **Static vs. Runtime Behavior**: Trivy analyzes the static contents of container layers. It does not inspect runtime network traffic, memory corruption, or kernel exploit attempts. Those require runtime security tools (e.g., Falco, Kyverno, seccomp).
3. **Database Timeliness**: Findings depend on the freshness of Trivy's vulnerability database. Regular DB updates in CI/CD are mandatory.
