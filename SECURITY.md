# Security Policy

## Supported Versions

Security fixes and integrity updates are actively provided for the latest release line (`v0.4.x`). Older versions are unsupported.

| Version | Supported |
| ------- | --------- |
| `v0.4.x` (`master` / latest release) | Supported |
| `< v0.4.0` | Unsupported |

## Reporting a Vulnerability

Please **do not** open a public GitHub Issue for security vulnerabilities in the installers (`install.bat`, `install.sh`), C# runtime mod (`RTL_Persian_Support`), Python tooling, or CI/CD workflows.

Instead, report vulnerabilities privately through:
- **GitHub Security Advisories:** <https://github.com/Ludeon/RimWorld-Farsi/security/advisories/new>

### What to Expect
- **Acknowledgment:** Within 72 hours of submission.
- **Triage & Assessment:** Within 7 days, including affected components and severity.
- **Remediation & Disclosure:** Confirmed issues are patched on `beta` and released in the next `v0.4.x` security update with coordinated disclosure credit if desired.

## Release Integrity Verification

All official release artifacts include `SHA256SUMS.txt` / `MD5SUMS.txt` (or `.sha256` / `.md5` sidecars on older releases) alongside Sigstore Cosign `.sig` signatures generated in GitHub Actions with SLSA build provenance.
