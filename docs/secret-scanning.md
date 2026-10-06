# Secret Scanning with Gitleaks — Extended Documentation

## DevSecOps Mini-Project — Member 1 Module

---

## Overview

This document provides in-depth technical documentation for the **Secret Detection Gate** built using [Gitleaks](https://github.com/gitleaks/gitleaks). It supplements the `gitleaks/README.md` with deeper explanations of configuration choices, scan types, and CI/CD handoff details.

---

## Why Gitleaks Instead of Alternatives?

| Tool | Strength | Weakness |
|------|----------|----------|
| **Gitleaks** | Scans full git history, fast, config-driven, CI-friendly | Requires git history to exist |
| `detect-secrets` (Yelp) | Baseline file support | Python dependency, slower |
| `truffleHog` | Deep entropy scanning | False positives, slower |
| `git-secrets` (AWS) | Simple, lightweight | AWS-specific focus |

Gitleaks was chosen because:
- Single binary (no dependencies)
- Scans full git history, not just current files
- Returns standard exit codes (CI/CD native)
- Actively maintained with 200+ built-in rules
- Official GitHub Action available for Member 4

---

## Gitleaks Configuration Explained

The configuration file is at `gitleaks/.gitleaks.toml`.

### `[extend]` section

```toml
[extend]
useDefault = true
```

This tells Gitleaks to use its full built-in ruleset (~200+ rules) covering:
- AWS credentials (Access Key ID + Secret)
- GitHub / GitLab / Bitbucket tokens
- Google API keys
- Stripe, Twilio, SendGrid keys
- JWT tokens
- Private keys (RSA, PGP, SSH)
- Slack webhooks
- And many more

We add our own custom rules **on top** of this — not instead of it.

### Custom rules

Three custom rules are added for the demo:

1. `generic-password-assignment` — catches `PASSWORD="..."` patterns in any case
2. `generic-api-key-assignment` — catches `API_KEY="..."` or `API_TOKEN="..."` patterns
3. `aws-secret-key-assignment` — catches `AWS_SECRET_ACCESS_KEY="..."` patterns

Each rule has:
- `id` — unique identifier (shown in scan output)
- `description` — human-readable explanation
- `regex` — the detection pattern
- `secretGroup` — which capture group contains the actual secret value
- `[rules.allowlist]` — per-rule exceptions for obvious placeholders

---

## Scan Modes

Gitleaks v8+ supports three primary scan modes:

| Command | What it scans | Use case |
|---------|--------------|----------|
| `gitleaks git` | Full git history + working tree | CI/CD pipeline, comprehensive scan |
| `gitleaks dir` | Files on disk (no git history) | Quick filesystem scan |
| `gitleaks stdin` | Content piped from stdin | Custom integrations |

### Pre-commit mode

```powershell
gitleaks git --pre-commit --staged --config gitleaks/.gitleaks.toml
```

- `--pre-commit` — tells Gitleaks it's running as a hook
- `--staged` — scans only files staged for the current commit (faster)

---

## Test File Design Decisions

### Why are test-secrets/ files committed?

`test-secrets/bad.env` must be **committed to git** for `gitleaks git` to detect it. If we only created the file without committing, `gitleaks git` would scan history and find nothing (the file wouldn't be in any commit).

The demo flow is:
1. Commit `bad.env` → git history now contains a fake secret
2. Run `gitleaks git` → scans history → finds the fake secret → exits 1
3. Demo complete

### Why not ignore test-secrets/ in .gitignore?

If we ignored `test-secrets/`, git would never track those files, and `gitleaks git` would never see them. The whole demo would fail.

Instead, `.gitignore` ignores patterns like `*.secret`, `.env`, `*.key` — real secret file patterns — while allowing `test-secrets/bad.env` through intentionally.

---

## Exit Code Reference

```
Exit 0  → Clean: no leaks found
Exit 1  → Leaks found: secrets detected
Exit 2  → Error: Gitleaks encountered a non-scanning error
```

CI/CD systems (GitHub Actions, Jenkins, GitLab CI) all treat any non-zero exit as a failure step by default.

---

## Report Formats

Gitleaks can output findings in multiple formats:

```powershell
# JSON report
gitleaks git --config gitleaks/.gitleaks.toml --report-format json --report-path report.json

# SARIF (GitHub Security tab integration)
gitleaks git --config gitleaks/.gitleaks.toml --report-format sarif --report-path report.sarif

# CSV
gitleaks git --config gitleaks/.gitleaks.toml --report-format csv --report-path report.csv
```

> **For Member 4:** Use `--report-format sarif` in GitHub Actions to integrate with GitHub's Security tab and show findings inline in Pull Requests.

---

## Handoff to Member 4 (GitHub Actions Integration)

Member 4 needs to know:

1. **Config file location:** `gitleaks/.gitleaks.toml`
2. **Scan command:** `gitleaks git --config gitleaks/.gitleaks.toml --verbose`
3. **Exit code contract:** 0 = pass, 1 = fail (secrets found)
4. **Report format for GitHub:** `--report-format sarif --report-path gitleaks-report.sarif`
5. **Official GitHub Action:** `gitleaks/gitleaks-action@v2` (handles installation automatically)

### Suggested GitHub Actions step

```yaml
- name: "🔍 Secret Scan — Gitleaks (Member 1)"
  id: gitleaks
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  with:
    config-path: gitleaks/.gitleaks.toml
```

If using the CLI instead of the Action:

```yaml
- name: "🔍 Secret Scan — Gitleaks (Member 1)"
  run: |
    gitleaks git \
      --config gitleaks/.gitleaks.toml \
      --verbose \
      --report-format sarif \
      --report-path gitleaks-report.sarif
  # GitHub Actions automatically stops pipeline on non-zero exit
```

---

## Common Issues and Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| `gitleaks: command not found` | Not installed or not on PATH | Follow installation steps in README |
| `no leaks found` when expecting leaks | File not committed to git | Run `git add` + `git commit` first |
| `config file not found` | Wrong `--config` path | Run from repo root, use `gitleaks/.gitleaks.toml` |
| Pre-commit hook doesn't run | Wrong line endings on Windows | Save hook as LF, not CRLF |
| Too many false positives | Built-in rules too aggressive | Add `[rules.allowlist]` entries to `.gitleaks.toml` |

---

## Security Checklist

- [x] No real credentials in this repository
- [x] `test-secrets/bad.env` contains only obviously fake values
- [x] `.gitignore` blocks real `.env` files
- [x] Gitleaks config does not disable any detection rules
- [x] Custom rules include allowlists for placeholder text
- [x] Exit codes are documented for CI/CD handoff
- [ ] (Member 4) GitHub Actions integration
- [ ] (Member 4) Discord/Slack alert on failure
