# Student 4 — completion status against Dr. Yaqub's updated scope

| Requirement | Status in this ZIP |
| --- | --- |
| Fall 1: assemble GPS + adapter/HackRF + power; prove live readings | **Pending equipment**; integration outline supplied |
| Fall 2: Python GPS/RF logger, timestamped CSV, 30 samples | **Software demonstration ready**; 120 synthetic readings/session; **real 30-sample walk pending** |
| Fall 3: live status, GPS lock, start/stop, disconnect and recovery | **CSV replay ready**, simulated session controls; true device start/stop and unplug/reconnect **pending** |
| Fall 4: coverage map, weak values, unsampled areas, exports, setup | **Software demonstration ready** with labelled artificial positions |
| Fall acceptance: running source, test dataset, instructions, demo recording | Software + dataset + instructions included; **in-person demo/recording and any repository commit pending** |
| Spring 5: repeat route alignment, compare nearby samples | **Demo zone-average comparison**; GPS-nearest-neighbor matched field comparisons not yet verified |
| Spring 6: weak-zone thresholds, minimum sample counts | **Software demo ready**; require empirical field calibration |
| Spring 7: asset overlay and PDF/CSV reporting | Site plan **image overlay separately**; zone CSV and summary JSON included; geocoded asset overlay and PDF report **not supplied** |
| Spring 8: secure field kit, battery and end-to-end handover | **Pending equipment/physical testing** |

**Why not label a demo as completed hardware?** The PDF contains system-layout facts (2,538 modules, 94 strings, eight inverters), but no tested receiver, GPS track, verified per-asset WGS84 positions or authorized measurement data. Those cannot be synthesized into real hardware acceptance.

### Image-based coverage and heat map (2026-11-16)
- Streamlit panel coverage dots and RSSI heatmap now overlay the original engineering drawing, rather than a GPS tile map.
- Both charts and offline HTML exports use image layout positions (`layout_x`/`layout_y`) with no inference from fabricated GPS.
- Heatmap colors represent interpolated simulated RSSI, and the estimated coverage is masked to illustrated panel rows near samples.
- **Not field-validated**: no measured positions or signal values were collected. Actual transmitter/receiver placement is still proposed only.
- Existing thresholds, simulation controls, CSV history/downloads, and future hardware adaptation remain unchanged.

### Panel name integration from Excel (2026-11-17)
- Source: user-provided `Solar Panel Management Diagram 9-9-2025.xlsx`, `SOLAR FARM` worksheet.
- `data/panel_catalog.csv` lists 2,538 letter-number-T/B IDs and approximate pixel positions, with source Excel cell traceability. Excel E-082 is absent and intentionally not imputed.
- Map adds hover identification for all modules, search highlight, nearest T/B pair labels for simulated readings, and module pair metadata in CSV and graph hover.
- No individual panel GPS was provided; pixel positions and synthetic RF-to-panel associations remain illustrative.
