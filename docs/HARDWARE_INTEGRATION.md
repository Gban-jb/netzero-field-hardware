# Connecting real equipment when it arrives

## 1. Physical kit

Assemble the approved laptop or Raspberry Pi, GPS/GNSS receiver, suitable 5 GHz Wi-Fi survey adapter **or** receive-only HackRF SDR, power and cables. Confirm compatibility and site permission with Dr. Yaqub. The ground-based RF kit is **separate from the DJI Matrice 4TD**; no installation on the drone without approval.

## 2. Confirm measurements and units

- Wi-Fi adapter: obtain a driver-reported received signal strength indication (RSSI) in **dBm**, if available for approved observations. Select permitted 5 GHz Wi-Fi **channel 36, center frequency 5.180 GHz** where device capabilities permit, and record actual tuned channel/frequency.
- HackRF: use its supported receive-only driver/toolchain. FFT-bin values and arbitrary SDR magnitudes are **not** direct Wi-Fi RSSI or calibrated dBm. Save separate measurement type/units (e.g. `Spectrum relative power` / `dBFS` where applicable), receiver settings (sample rate, center frequency, gain, antenna), and appropriate calibration evidence. Do not mix these with Wi-Fi RSSI on one threshold chart.
- GPS receiver: verify a real GNSS fix, timestamp/UTC, latitude/longitude and optional quality. Do not use the demo latitude/longitude as truth.

## 3. Live-data adapter to implement

Open `hardware_adapter.py` and replace the deliberate `HardwareNotConfigured` exception with *tested, device-specific, receive-only* acquisition. Once each record is available, construct a dict matching `rf_core.FIELDS` and append through `write_rows([record], output_path, append=True)`. Use `source='REAL'` only for genuine instrument readings. A measurement must include timestamp, location, units, receiver identity, actual frequency and a real GPS-lock indication. For a new CSV, write the header once. Validate with `python rf_survey.py --mode validate --output path/to/real.csv`.

## 4. Field validation

1. Run one powered bench sample with real GPS and the permitted receiver.
2. Record at least 30 samples on an **approved** walking route.
3. Disconnect/reconnect receiver under supervision; confirm recorded error, safe stop and resume when integrated.
4. Check raw CSV fields and distinguish bad/no-lock GPS readings.
5. Replay with dashboard; export HTML map, CSV, report on professor's computer.
6. Collect baseline repeat route in same measurement units/settings before calling coverage weak; use thresholds agreed with professor.

## 5. Geographic alignment

The final supplied PDF is a **drawing**, not a georeferenced GeoJSON. To plot true PV boundaries and per-inverter locations, request surveyed coordinates or properly georeferenced CAD/GIS. Do not assign one WGS84 coordinate to every module from a page image. Example data may demonstrate dashboard functionality but cannot validate field coverage.
