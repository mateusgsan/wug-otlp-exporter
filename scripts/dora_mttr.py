#!/usr/bin/env python3
"""
DORA Metrics — Mean Time to Restore (MTTR) calculator.

Reads a JSON list of GitHub Issues from stdin and calculates:
  - MTTR in hours (average time from open to close for incidents)
  - Change Failure Rate (incidents / deploys * 100)

Environment variables:
  TOTAL_DEPLOYS  - number of deploys in the last 30 days
  TOTAL_INCIDENTS - total number of incidents in the last 30 days

Outputs to stdout (one KEY=VALUE per line for GitHub Actions):
  mttr_hours
  cfr_percent
  cfr_rating
  mttr_rating
  closed_incidents
"""
import json
import os
import sys
from datetime import datetime, timezone

data = json.load(sys.stdin)

total_deploys   = int(os.environ.get("TOTAL_DEPLOYS", "0"))
total_incidents = len(data)
closed = [x for x in data if x.get("closedAt") and x.get("createdAt")]

# MTTR
if closed:
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    durations = []
    for issue in closed:
        created   = datetime.strptime(issue["createdAt"], fmt).replace(tzinfo=timezone.utc)
        closed_at = datetime.strptime(issue["closedAt"],  fmt).replace(tzinfo=timezone.utc)
        durations.append((closed_at - created).total_seconds() / 3600)
    mttr_hours = sum(durations) / len(durations)
else:
    mttr_hours = 0.0

# Change Failure Rate
cfr = (total_incidents / total_deploys * 100) if total_deploys > 0 else 0.0

# Ratings
if cfr <= 5:
    cfr_rating = "Elite (<=5%)"
elif cfr <= 10:
    cfr_rating = "High (<=10%)"
elif cfr <= 15:
    cfr_rating = "Medium (<=15%)"
else:
    cfr_rating = "Low (>15%)"

if mttr_hours <= 1:
    mttr_rating = "Elite (< 1h)"
elif mttr_hours <= 24:
    mttr_rating = "High (< 1 day)"
elif mttr_hours <= 168:
    mttr_rating = "Medium (< 1 week)"
else:
    mttr_rating = "Low (> 1 week)"

print(f"mttr_hours={mttr_hours:.2f}")
print(f"cfr_percent={cfr:.4f}")
print(f"cfr_rating={cfr_rating}")
print(f"mttr_rating={mttr_rating}")
print(f"closed_incidents={len(closed)}")
print(f"total_incidents={total_incidents}")
