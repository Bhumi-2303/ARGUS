# Frontend Dependency Audit Report

**Audit Date:** 2026-09-19 21:26:28
**Node Version:** 22.23.2
**npm Version:** 10.9.8
**Vulnerability Count:** 12

## Vulnerabilities

### baseline-browser-mapping
- **Severity:** Moderate
- **Affected Package:** baseline-browser-mapping
- **Dependency Chain:** baseline-browser-mapping process termination on invalid input causes denial of service
- **Production/Runtime Impact:** Likely Build/Development only
- **Recommended Remediation:** Manual review needed or `npm audit fix` if available.
- **Safety:** Schedule for manual update.

### brace-expansion
- **Severity:** High
- **Affected Package:** brace-expansion
- **Dependency Chain:** brace-expansion: DoS via exponential-time expansion of consecutive non-expanding {} groups, brace-expansion: DoS via unbounded expansion length causing an out-of-memory process crash, brace-expansion: DoS via unbounded intermediate arrays, bypassing the CVE-2026-14257 mitigation
- **Production/Runtime Impact:** Likely Build/Development only
- **Recommended Remediation:** Manual review needed or `npm audit fix` if available.
- **Safety:** Schedule for manual update.

### browserslist
- **Severity:** High
- **Affected Package:** browserslist
- **Dependency Chain:** Browserslist: Unbounded memory growth (no cache eviction) via distinct query results, leading to eventual OOM, Browserslist: Uncaught crash / prototype write via untrusted browserslist-stats.json custom stats (normalizeStats)
- **Production/Runtime Impact:** Likely Build/Development only
- **Recommended Remediation:** Manual review needed or `npm audit fix` if available.
- **Safety:** Schedule for manual update.

### js-yaml
- **Severity:** High
- **Affected Package:** js-yaml
- **Dependency Chain:** JS-YAML: Quadratic CPU consumption in !!omap resolution (3.x and 4.x) — CVE-2026-59870 fix not backported, js-yaml: maxTotalMergeKeys does not limit CPU use for empty merge sources
- **Production/Runtime Impact:** Likely Build/Development only
- **Recommended Remediation:** Manual review needed or `npm audit fix` if available.
- **Safety:** Schedule for manual update.

### nanoid
- **Severity:** High
- **Affected Package:** nanoid
- **Dependency Chain:** nanoid: non-secure generators can loop indefinitely with negative size, nanoid: custom generators can loop indefinitely when size is zero
- **Production/Runtime Impact:** Likely Build/Development only
- **Recommended Remediation:** Manual review needed or `npm audit fix` if available.
- **Safety:** Schedule for manual update.

### postcss
- **Severity:** High
- **Affected Package:** postcss
- **Dependency Chain:** PostCSS: incomplete fix of GHSA-6g55-p6wh-862q — attacker-controlled sourceMappingURL reads arbitrary .map files when `from` is unset, PostCSS: Path Traversal in Previous Source Map Auto-Loading (sourceMappingURL) leads to Arbitrary .map File Disclosure
- **Production/Runtime Impact:** Likely Build/Development only
- **Recommended Remediation:** Manual review needed or `npm audit fix` if available.
- **Safety:** Schedule for manual update.

