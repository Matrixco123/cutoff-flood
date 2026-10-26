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

Status: PASS (2026-10-26). 47 Sentinel-1 images over the core area, 57 same-track pairs.

| | Date | Orbit | Pass | Area covered | Image ID |
|---|---|---|---|---|---|
| Before (chosen) | 2026-07-17 | 4 | Descending | 99% | S1D_IW_GRDH_1SDV_20260717T233756_20260717T233821_003720_006A9E_7B2A |
| During (chosen) | 2026-07-29 | 4 | Descending | 99% | S1D_IW_GRDH_1SDV_20260729T233756_20260729T233821_003895_0070A3_D90B |
| Older baseline | 2026-06-04 | 4 | Descending | 100% | S1A_IW_GRDH_1SDV_20260604T233843_20260604T233908_064826_082B1B_663A |

Flood visible in the quick look? Yes: clustered new water in the plains south of the Brahmaputra around Sivasagar and Jorhat; hills to the southeast stay clean.

Notes:
- Many red patches with the June baseline are field-shaped. In July, paddy fields are deliberately flooded for transplanting, so June to July differences mix crops with flood. Switched the "before" image to 17 July (same track, two days before the rain began on 19 July). New notebook cell compares both baselines.
- Baseline comparison (rough VV < -16 dB threshold, core area): new water vs June = 429.7 km2; vs 17 July = 271.1 km2. About 37% of the June-based "new water" was already present by 17 July, mostly along the Brahmaputra channels (river already high) plus some fields. The field-shaped clusters south of the river remain with the 17 July baseline, so they are flood. Decision: use 17 July as the baseline.
- 29 July is a few days after the peak (situation was improving by 27 July), so some flooding had already receded. Option closer to the peak: orbit 143 ascending, 15 July to 27 July, 88% cover.
- Images after 29 June are Sentinel-1D only (1A ended 29 June); 6-day revisit on orbit 4 (5, 17, 29 July).
- geemap's default OSM background tiles are blocked in Colab; switched to Esri satellite tiles.
- Five-district coverage (ALL_AFFECTED_BBOX) not checked yet.

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
