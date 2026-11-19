# Panel identification from the supplied management Excel diagram

## Files supplied and how the naming works

- Source workbook: `docs/Solar Panel Management Diagram 9-9-2025.xlsx`.
- Source worksheet: `SOLAR FARM`.
- Extracted machine-readable list: `data/panel_catalog.csv` (exactly 2,538 module positions).
- Updated interactive plots: `outputs/coverage_map.html` and `outputs/panel_heatmap.html`.
- RF measurements with illustrative matches: `outputs/measurements_with_panel_ids.csv`.

The Excel worksheet has *row letters* A through P, *numbered positions* (1, 2, 3, ...), and `T` and `B` markers placed above and below each numbered strip. The dashboard creates a readable, **derived** ID for each position:

- `A-001-T` = row A, position 1, top slot.
- `A-001-B` = row A, position 1, bottom slot.
- `P-081-B` = row P, position 81, bottom slot.

These full IDs do **not** appear as ready-made strings in the workbook. They are assembled from its labels, and `T`/`B` are interpreted as top/bottom. Verify this convention with the site manager before treating them as official asset identifiers.

### Numbered positions per Excel row

| Excel row | Position numbers present | Module positions (T+B) |
| --- | --- | ---: |
| A–D | 1–108 each | 216 each |
| E | 1–108, except 82 | 214 |
| F | 1–82 | 164 |
| G–L | 1–54 each | 108 each |
| M–P | 1–81 each | 162 each |
| **Total** | **1,269 numbered positions** | **2,538 module positions** |

**Important:** The source Excel worksheet is missing **E-082** (both T and B). The catalog intentionally does not invent this position. Each module ID retains the source Excel number cell (e.g. `A-001-T` → `C9`).

## Alignment on the engineering drawing

The background for both plots is `assets/site_panels_crop.png`, derived from the original supplied site engineering drawing. The image has ten visible horizontal strips. For the top six strips, the left block represents A–F while the right block represents G–L. The lower four strips of the right block represent M–P. Within each strip, numbers increase from left to right, in the same order as the Excel sheet.

A numbered position is placed at an **estimated** evenly spaced horizontal center within its drawing strip. Its `T` and `B` slots are shown slightly above/below the strip center. These are **pixel/diagram coordinates**, not known surveyed GPS coordinates. The top/bottom offset, module-spacing assumptions and drawing placement should be calibrated against real survey data before field usage.

`panel_catalog.csv` exposes `panel_px_x`, `panel_px_y`, `row_id`, `panel_number`, `tier`, and the source `excel_number_cell`. The `position_type` is `SCHEMATIC_PIXEL_ONLY` on every row.

## Synthetic RF measurements and pairing

The existing sample CSV contains simulated RSSI values, temperatures, latitudes and longitudes and schematic normalized route positions (`layout_x`, `layout_y`). Their numeric values and original graphs have **not** been replaced with measurements from Excel.

For each synthetic point, the program first places `layout_x`/`layout_y` onto one of the ten drawing strips and then selects the nearest **actual numbered Excel position** on that strip. The original sample does **not** identify the top (`T`) versus bottom (`B`) module. Accordingly, it records **both** potential IDs: `panel_id_top`, `panel_id_bottom`, and a pair label such as `A-008 (T/B)`. **Neither is proven to be the physical location of that measurement.**

A GPS-only CSV without `layout_x`/`layout_y` will not be automatically aligned to the drawing. For real field sampling, collect a verified site plan transform or explicitly record validated panel IDs and their surveyed coordinates.

## How to view and use the dashboard

1. Run `python run_kit.py` from the extracted project folder (install `requirements.txt` first).
2. Open the **Panel coverage + heatmap** tab.
3. The RF dots display short row/number labels such as `A-008`; hover to see both T/B names plus simulated latitude/longitude, RSSI and survey details.
4. Hover over a drawn solar module to inspect its individual Excel-derived ID, or search/select an ID in the **Find and highlight a named panel** list. Zoom into the drawing when modules are densely packed.
5. Uncheck **Display names beside RF points** if the dot labels become crowded. Hover information stays available.
6. Download the interactive HTML files, the complete panel ID catalog CSV, or the RF readings with their nearest schematic panel pair labels.
7. The **Signals & trends** graph shows the nearby pair ID when hovering on a measurement; the original synthetic graph values remain unchanged.

For a quick offline demonstration, open `outputs/coverage_map.html` in a browser without Python or Streamlit.

## Accuracy / scope warning

**This build does not georeference the Excel diagram or produce verified panel-level coverage measurements.** Both the original latitudes/longitudes and the RF readings are synthetic demo data; the letter/number/top-bottom IDs are derived from the uploaded Excel management worksheet; the connections between them are nearest-diagram-position *illustrations*. Do not present a specific module as field-tested or report its RF health without approved on-site measurement, calibration and validation.
