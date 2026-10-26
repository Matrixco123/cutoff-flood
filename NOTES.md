# Project notes and decision log

Keep this file updated. Newest entries at the top of each section.

## Decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-26 | Expansion to Golaghat and Nagaon planned for Week 5 (all five districts of the July 2026 flood), if one image pair covers them | Same event and method; core three first so a result is guaranteed |
| 2026-10-26 | Not doing "all districts ever affected or prone" | Most of Assam, many separate events, and "prone" is a different (risk) model |
| 2026-10-25 | Study area: Upper Assam (Sivasagar, Charaideo, Jorhat), July 2026 flood | Floods almost every year; recent documented event; utility outage reports available |
| 2026-10-25 | Backup area: Barpeta (Assam), then Bihar | Lower Assam floods last longer, easier to capture by satellite |
| 2026-10-25 | Train on Sen1Floods11 hand-labelled chips only | Public, expert labels; no manual training labels needed |
| 2026-10-25 | Locked settings in `src/config.py` | Same values for everyone |

## Week 1 checks

### Check 1: Roads and hospitals (`01_road_check.ipynb`)

Status: numbers PASS for all three districts (2026-10-26, Geofabrik file, district boundaries); rural visual check pending

| District | Minor road share | Road density (km/km²) | Health facilities | Villages checked visually | Villages with roads complete |
|---|---|---|---|---|---|
| Sivasagar | 0.59 | 1.21 | 37 | | |
| Charaideo | 0.60 | 1.68 | 27 | | |
| Jorhat | 0.71 | 1.18 | 80 | | |

Notes:
- Sivasagar and Charaideo pass on numbers: most road length is residential and unclassified roads.
- CORRECTION (2026-10-26): the first notebook counted every two-way road twice (once per direction), so the densities above are about double the true value. True density is roughly 1.1 (Sivasagar) and 1.5 (Charaideo) km/km², still above the guide of 1. Road shares were not affected. Rerun with the new notebook for exact figures.
- 2026-10-26: public Overpass servers were overloaded for hours. Notebook rewritten to download one Geofabrik OSM file for northeast India and read it locally, so it no longer depends on those servers.
- Jorhat fell back to the rough bounding box because the public Overpass server was overloaded (502). The box overlaps neighbouring districts, so its numbers (9,078 km, 134 facilities) are not valid. Notebook now retries before falling back.
- First visual check was on Sivasagar town only; towns are always well mapped. Still need 4 rural villages (e.g. Nazira, Gaurisagar, Amguri, Demow).

### Check 2: Satellite images (`02_sentinel1_check.ipynb`)

Status: not run yet

| | Image ID | Date | Orbit | Pass | Area covered |
|---|---|---|---|---|---|
| Before | | | | | |
| During | | | | | |

Flood visible in the quick look? (yes / partly / no):

Notes:

### Check 3: First training run (`03_sen1floods11_first_train.ipynb`)

Status: not run yet

| Method | Val IoU | Val Dice | Precision | Recall |
|---|---|---|---|---|
| Threshold baseline | | | | |
| U-Net, 10 epochs | | | | |

Notes:

### Go / no-go

| Result | Decision |
|---|---|
| All three pass | Lock Upper Assam, start model training (Weeks 2 to 3) |
| Roads fail | Shrink to the district with the best roads, or test Barpeta |
| Imagery fails | Test Barpeta |
| Training fails | Debug the code; not a reason to change area |

Decision:

## Open questions

- Does Prof. Sobti want more weight on the method (uncertainty) or the application (cut-off villages)?
- Which revenue circles exactly form the study area?

## Environment notes

- OpenStreetMap, Overpass and the Sen1Floods11 bucket are blocked from the Claude workspace and from the shared shell on the laptop. Run all download steps in Google Colab.
