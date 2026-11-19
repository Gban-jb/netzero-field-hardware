# Student 4 — Fall RF/GPS Demo Guide

## Objective
Show the five Fall-semester software views without misrepresenting mock data as physically collected RF/GPS measurements.

## Run

Install `requirements.txt` and run `python run_kit.py`, then open the local Streamlit page.
The simplified Fall dashboard is the default. The older six-tab app remains in `dashboard_advanced.py`.

## What to show Dr. Yaqub

1. **GPS + RF**: Show a saved UTC timestamp, simulated latitude and longitude, and RSSI in dBm. Say: "The field values are mock data today. The physical GPS and RF receiver have not been integrated."
2. **Live status**: Press **Start demo**. Watch the status and count update. Press **Mock unplug** and show the paused state; then reconnect and stop. Explain this is an application-state mock, not actual hardware disconnection.
3. **CSV logger**: Open the measurement table, show fields (`timestamp_utc`, `latitude`, `longitude`, `measurement_type`, `value`, `units`, `receiver_id` and `survey_id`) and download the CSV. The logger writes a real data file, but the readings themselves are simulated.
4. **Coverage + heatmap**: In **Coverage points**, show red weak-RSSI markers, unsampled layout areas, and panel IDs from the Excel diagram. Switch to **RSSI heatmap** for the red/yellow/green signal-strength estimate. Toggle sample dots and download each interactive HTML map. Both views use simulated samples and drawing-only coordinates, not verified panel GPS positions.
5. **Replay + export**: Choose Demo A, move the replay slider from 1 to the last sample, then export CSV and summary files.

## Fall acceptance items to complete in person

- Bring an assembled powered receiver/GPS kit.
- Demonstrate one **actual** GPS reading and one permitted RF reading.
- Record **30 actual readings** on an approved walking route to the CSV.
- Show physical device unplug/disconnect handling and successful resume.
- Replay the measured route, export the weak-coverage map and CSV on the supervisor's computer.
- Provide setup instructions, source code, a recorded demonstration, and limitations.

Keep the sample source field clear (`SIMULATED` versus measured hardware). Do not treat unsampled regions as having strong signal. A GPS route cannot be plotted accurately on a panel drawing unless corresponding survey/georeferencing data is provided.
