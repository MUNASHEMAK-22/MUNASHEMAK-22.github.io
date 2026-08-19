# IoT Equipment Performance & Predictive Maintenance

Detects equipment failure precursors from temperature and vibration sensor data using a rolling z-score anomaly detector, sustained over consecutive readings to avoid false alarms.

## Structure

```
iot-maintenance/
├── generate_sensor_data.py   # generates 90 days of hourly sensor data for 6 machines
├── detect_anomalies.py       # the anomaly detection logic + dashboard data export
├── sensor_readings.csv       # raw generated data (12,960 rows)
├── dashboard_data.json       # daily aggregates consumed by the web dashboard
└── alerts_log.csv            # every sustained anomaly flagged, with z-scores
```

## Running it

```bash
python generate_sensor_data.py   # creates sensor_readings.csv
python detect_anomalies.py       # creates dashboard_data.json and alerts_log.csv
```

## How detection works

Each machine gets its own 14-day baseline (mean/stddev per sensor). New readings are scored as a z-score against that baseline. A single noisy reading isn't enough — an alert only fires once 3 consecutive hourly readings exceed a 2.5σ threshold, which filters ordinary sensor noise from a genuine drift pattern.

## Results

- 2 of 6 machines carried a genuine failure precursor pattern in the data; both were flagged
- Average lead time: ~9 days before failure
- 0 false alarms across the 4 healthy machines over 90 days of hourly monitoring

## Next steps

- Adapt the anomaly threshold per equipment class instead of using one fixed value
- Translate lead time into an estimated downtime-avoided / cost-saved figure
- Move from batch CSV processing to near-real-time stream ingestion
