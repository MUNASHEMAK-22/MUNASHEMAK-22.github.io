"""
Generates hourly sensor readings (temperature, vibration, voltage) for 6 pieces
of industrial equipment over 90 days. Two machines are given genuine failure
precursor patterns -- a gradual rise in temperature and vibration in the days
leading up to a failure event -- so the "predictive" part of the dashboard is
backed by a real, detectable signal rather than random noise.
"""
import csv
import random
from datetime import datetime, timedelta

random.seed(11)

machines = ["M-101", "M-102", "M-103", "M-104", "M-105", "M-106"]
# Machines that will experience a simulated failure with a real precursor pattern
failing_machines = {"M-103": 62, "M-106": 78}  # machine -> day index of failure

BASE_TEMP = 55.0     # deg C
BASE_VIBR = 2.2       # mm/s RMS
BASE_VOLT = 230.0     # V

start = datetime(2025, 4, 1)
rows = []

for machine in machines:
    fail_day = failing_machines.get(machine)
    for hour_offset in range(90 * 24):
        ts = start + timedelta(hours=hour_offset)
        day_idx = hour_offset // 24

        temp = BASE_TEMP + random.gauss(0, 1.2)
        vibr = BASE_VIBR + random.gauss(0, 0.15)
        volt = BASE_VOLT + random.gauss(0, 1.5)

        status = "normal"

        if fail_day is not None:
            days_to_failure = fail_day - day_idx
            if 0 <= days_to_failure <= 10:
                # Ramp: closer to failure => bigger deviation
                ramp = (10 - days_to_failure) / 10
                temp += ramp * 14        # up to +14C above baseline
                vibr += ramp * 3.1       # up to +3.1 mm/s above baseline
                status = "warning" if ramp < 0.7 else "critical"
            if days_to_failure == 0:
                status = "failure"

        rows.append({
            "timestamp": ts.isoformat(),
            "machine_id": machine,
            "temperature_c": round(temp, 2),
            "vibration_mm_s": round(max(vibr, 0), 2),
            "voltage_v": round(volt, 2),
            "status": status,
        })

with open("/home/claude/portfolio/projects/iot-maintenance/data/sensor_readings.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} readings across {len(machines)} machines.")
print(f"Simulated failures on: {failing_machines}")
