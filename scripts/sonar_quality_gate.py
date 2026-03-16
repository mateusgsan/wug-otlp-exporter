#!/usr/bin/env python3
"""
SonarCloud Quality Gate enforcer for the Free plan.

On the Free plan, sonar.qualitygate.wait=true fails when no baseline exists
(status=NONE). This script checks overall code metrics directly via the API
and exits with code 1 if any threshold is violated.

Thresholds:
  - Bugs:                  0
  - Vulnerabilities:       0
  - Coverage:              >= 80%
  - Security Hotspots:     all reviewed (100%)
"""
import json
import os
import sys
import urllib.request

SONAR_TOKEN = os.environ.get("SONAR_TOKEN", "")
PROJECT_KEY = "mateusgsan_wug-otlp-exporter"
METRICS = (
    "bugs,vulnerabilities,coverage,"
    "security_hotspots,security_hotspots_reviewed,"
    "code_smells,duplicated_lines_density,ncloc"
)

url = (
    "https://sonarcloud.io/api/measures/component"
    f"?component={PROJECT_KEY}&metricKeys={METRICS}"
)

req = urllib.request.Request(url, headers={"Authorization": f"Bearer {SONAR_TOKEN}"})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
except Exception as exc:
    print(f"ERROR: Failed to reach SonarCloud API: {exc}", file=sys.stderr)
    sys.exit(1)

measures = {
    m["metric"]: float(m.get("value", 0))
    for m in data.get("component", {}).get("measures", [])
}

bugs         = int(measures.get("bugs", 0))
vulns        = int(measures.get("vulnerabilities", 0))
coverage     = measures.get("coverage", 0.0)
hotspots     = int(measures.get("security_hotspots", 0))
reviewed_pct = measures.get("security_hotspots_reviewed", 100.0) if hotspots > 0 else 100.0
code_smells  = int(measures.get("code_smells", 0))
ncloc        = int(measures.get("ncloc", 0))

print("--- SonarCloud Quality Gate (Overall Code) ---")
print(f"  Lines of Code:         {ncloc}")
print(f"  Bugs:                  {bugs}       (threshold: 0)")
print(f"  Vulnerabilities:       {vulns}       (threshold: 0)")
print(f"  Coverage:              {coverage:.1f}%  (threshold: >= 80%)")
print(f"  Code Smells:           {code_smells}")
print(f"  Security Hotspots:     {hotspots}")
print(f"  Hotspots Reviewed:     {reviewed_pct:.0f}%  (threshold: 100%)")
print(f"  Dashboard: https://sonarcloud.io/project/overview?id={PROJECT_KEY}")
print()

failed = []
if bugs > 0:
    failed.append(f"BUGS: {bugs} (expected 0)")
if vulns > 0:
    failed.append(f"VULNERABILITIES: {vulns} (expected 0)")
if coverage < 80.0:
    failed.append(f"COVERAGE: {coverage:.1f}% (expected >= 80%)")
if reviewed_pct < 100:
    failed.append(f"HOTSPOTS_REVIEWED: {reviewed_pct:.0f}% (expected 100%)")

if failed:
    print("Quality Gate: FAILED")
    for f in failed:
        print(f"  - {f}")
    sys.exit(1)

print("Quality Gate: PASSED")
sys.exit(0)
