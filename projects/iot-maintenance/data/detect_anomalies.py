"""
Predictive Maintenance: Anomaly Detection
------------------------------------------
Flags equipment as at-risk when temperature or vibration readings drift
significantly above their normal operating baseline, using a rolling
z-score against each machine's own historical mean/stddev. This is the
same core technique used in real condition-based maintenance systems,
simplified to run without external ML libraries.

Exports:
  - dashboard_data.json: daily aggregates per machine, for the web dashboard
  - alerts_log.csv: every anomaly flag raised, with lead time before failure
"""
import csv
import json
import statistics
from collections import defaultdict
from datetime import datetime

rows = list(csv.DictReader(open("/home/claude/portfolio/projects/iot-maintenance/data/sensor_readings.csv")))
for r in rows:
    r["temperature_c"] = float(r["temperature_c"])
    r["vibration_mm_s"] = float(r["vibration_mm_s"])
    r["voltage_v"] = float(r["voltage_v"])
    r["timestamp"] = datetime.fromisoformat(r["timestamp"])

by_machine = defaultdict(list)
for r in rows:
    by_machine[r["machine_id"]].append(r)

Z_THRESHOLD = 2.5  # flag as anomaly if reading is 2.5 std devs above baseline
BASELINE_WINDOW_HOURS = 24 * 14  # first 14 days establish "normal" baseline

alerts = []
daily_agg = defaultdict(lambda: defaultdict(list))  # machine -> day -> [readings]

for machine, readings in by_machine.items():
    readings.sort(key=lambda r: r["timestamp"])
    baseline = readings[:BASELINE_WINDOW_HOURS]
    temp_mean = statistics.mean(r["temperature_c"] for r in baseline)
    temp_std = statistics.stdev(r["temperature_c"] for r in baseline)
    vibr_mean = statistics.mean(r["vibration_mm_s"] for r in baseline)
    vibr_std = statistics.stdev(r["vibration_mm_s"] for r in baseline)

    first_anomaly_ts = None
    failure_ts = None
    consecutive_anomalies = 0
    SUSTAINED_THRESHOLD = 3  # require 3 consecutive hours above z-threshold to flag

    for r in readings:
        if r["status"] == "failure":
            failure_ts = r["timestamp"]

        temp_z = (r["temperature_c"] - temp_mean) / temp_std if temp_std else 0
        vibr_z = (r["vibration_mm_s"] - vibr_mean) / vibr_std if vibr_std else 0
        is_anomaly_reading = temp_z > Z_THRESHOLD or vibr_z > Z_THRESHOLD

        if is_anomaly_reading:
            consecutive_anomalies += 1
        else:
            consecutive_anomalies = 0

        is_sustained_anomaly = consecutive_anomalies >= SUSTAINED_THRESHOLD

        if is_sustained_anomaly and first_anomaly_ts is None:
            first_anomaly_ts = r["timestamp"]

        if is_sustained_anomaly:
            alerts.append({
                "machine_id": machine,
                "timestamp": r["timestamp"].isoformat(),
                "temp_z": round(temp_z, 2),
                "vibr_z": round(vibr_z, 2),
            })

        day_key = r["timestamp"].date().isoformat()
        daily_agg[machine][day_key].append(r)

    if first_anomaly_ts and failure_ts:
        lead_time_hours = (failure_ts - first_anomaly_ts).total_seconds() / 3600
        print(f"{machine}: first anomaly flagged {lead_time_hours:.0f} hours "
              f"({lead_time_hours/24:.1f} days) before failure.")

# Build daily aggregates for the dashboard (avg temp, avg vibration, worst status of the day)
status_rank = {"normal": 0, "warning": 1, "critical": 2, "failure": 3}
dashboard = {}
for machine, days in daily_agg.items():
    series = []
    for day, readings in sorted(days.items()):
        series.append({
            "date": day,
            "avgTemp": round(statistics.mean(r["temperature_c"] for r in readings), 1),
            "avgVibration": round(statistics.mean(r["vibration_mm_s"] for r in readings), 2),
            "status": max((r["status"] for r in readings), key=lambda s: status_rank[s]),
        })
    dashboard[machine] = series

summary = {
    "totalReadings": len(rows),
    "totalMachines": len(machines := list(by_machine.keys())),
    "totalAnomaliesFlagged": len(alerts),
    "machinesWithFailure": sorted({a["machine_id"] for a in alerts
                                    if any(r["status"] == "failure" and r["machine_id"] == a["machine_id"] for r in rows)}),
}

output = {"summary": summary, "series": dashboard}

with open("/home/claude/portfolio/projects/iot-maintenance/data/dashboard_data.json", "w") as f:
    json.dump(output, f, indent=2)

with open("/home/claude/portfolio/projects/iot-maintenance/data/alerts_log.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["machine_id", "timestamp", "temp_z", "vibr_z"])
    writer.writeheader()
    writer.writerows(alerts)

print("\nSummary:", json.dumps(summary, indent=2))
