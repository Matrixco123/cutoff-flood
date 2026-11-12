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

Status: PASS (2026-10-27). 446 hand-labelled chips downloaded (252 train, 89 valid; test untouched).

| Method | Val IoU | Val Dice | Precision | Recall |
|---|---|---|---|---|
| Threshold baseline (Otsu on VV) | 0.309 | 0.472 | 0.347 | 0.738 |
| U-Net ResNet-34, 10 epochs (last) | 0.585 | 0.738 | 0.882 | 0.635 |

Notes:
- Training loss fell steadily (0.70 to 0.16). Validation IoU peaked at 0.624 (epoch 7) and jumps between epochs (0.52 to 0.62): the validation set is small and the learning rate is constant.
- U-Net nearly doubles the threshold baseline's IoU. The threshold finds most water but with many false alarms (precision 0.35); the U-Net is the reverse: precise (0.88) but misses about a third of water (recall 0.63).
- For the real training: more epochs (about 50), learning-rate schedule, keep the best checkpoint by validation IoU, add Dice loss to the BCE (helps recall), and tune the 0.5 decision threshold on validation data.

### Go / no-go

| Result | Decision |
|---|---|
| All three pass | Lock Upper Assam, start model training (Weeks 2 to 3) |
| Roads fail | Shrink to the district with the best roads, or test Barpeta |
| Imagery fails | Test Barpeta |
| Training fails | Debug the code; not a reason to change area |

Decision (2026-10-27): Checks 2 and 3 pass; Check 1 passes on numbers, rural visual check still to do. Upper Assam (Sivasagar, Charaideo, Jorhat) is provisionally locked. Start model training.

## Weeks 2 to 3: ensemble training (`04_train_ensemble.ipynb`, run on Kaggle)

Status: DONE (Kaggle run, 2026-10-29). Files in `results/kaggle_run1/`; the five models are kept outside GitHub (about 100 MB each).

Setup: 5 U-Nets (seeds 0 to 4), 50 epochs, AdamW + cosine schedule, BCE + Dice loss, best epoch kept by validation IoU, mixed precision. Decision threshold tuned on validation: 0.35.

| Split | Baseline IoU | Single U-Net IoU (mean +/- std) | Ensemble IoU (0.35) | Single ECE | Ensemble ECE |
|---|---|---|---|---|---|
| Valid (89 chips) | 0.309 | 0.674 +/- 0.010 | 0.685 | 0.022 | 0.017 |
| Test (90 chips) | 0.334 | 0.689 +/- 0.005 | 0.697 | 0.027 | 0.022 |
| Bolivia (15 chips, unseen country) | 0.560 | 0.639 +/- 0.056 | 0.668 | 0.041 | 0.023 |

Findings:
- U-Net roughly doubles the threshold baseline on test (0.69 vs 0.33).
- Recall fixed: ensemble at 0.35 gives test recall 0.82 with precision 0.83 (first run: recall 0.63).
- The ensemble matters most on the unseen country: single models range 0.585 to 0.700 IoU on Bolivia, and calibration error falls from 0.041 to 0.023 (about 45% lower). This is the closest proxy we have for transfer to Assam.
- Uncertainty maps light up where the model is wrong (e.g. Pakistan test chip with flooded fields the model misses).

Caveats:
- Bolivia is only 15 chips; its numbers are noisy. Two single seeds (0 and 4) beat the ensemble there; the ensemble's value is that you cannot know in advance which seed transfers well.
- Validation IoU is noisy between epochs (single drops to about 0.36); best-epoch selection on validation makes validation scores optimistic, so quote test.
- ECE is small for every model because most pixels are confidently dry. The reliability diagram shows both models are overconfident at both ends (curve flatter than the diagonal); the ensemble is closer in the 0.4 to 0.8 range.
- Baseline is Otsu on VV only, which is weak. A stronger baseline (VH or VV+VH threshold) would make the comparison harder to dismiss.
- Validation IoU plateaus around epoch 25 to 30; 30 epochs would likely be enough next time.

Next: temperature scaling; test whether uncertainty predicts errors (AUROC); stronger threshold baseline; then apply the ensemble to the Assam July 2026 images.

## Open questions

- Does Prof. Sobti want more weight on the method (uncertainty) or the application (cut-off villages)?
- Which revenue circles exactly form the study area?

## Environment notes

- OpenStreetMap, Overpass and the Sen1Floods11 bucket are blocked from the Claude workspace and from the shared shell on the laptop. Run all download steps in Google Colab.

## Week 4: Assam inputs (`05_export_assam.ipynb`, run in Colab)

Status: DONE (Colab, 2026-11-09). All three exports completed; image IDs match Check 2. Grid 14039 x 10147 pixels (140 x 101 km). Record: `results/assam_export_info.json`. Files are in Google Drive `cutoff_assam` (not on GitHub).

Exports three GeoTIFFs to Google Drive (`cutoff_assam`), all on one 10 m grid in UTM 46N (EPSG:32646) over STUDY_BBOX:
- `s1_pre_20260717.tif` and `s1_post_20260729.tif`: VV, VH in dB x 100, int16, no smoothing.
- `aux_jrc_hand.tif`: JRC occurrence (%), MERIT HAND (m x 10, bilinear from ~90 m).
No-data = -32768. The exact grid and image IDs are saved in `results/assam_export_info.json` when the notebook runs.

## Week 4: Assam flood maps (`06_predict_assam.ipynb`, run on Kaggle)

Status: DONE (Kaggle, 2026-11-13). Results in `results/assam_run1/` (maps kept outside GitHub, about 190 MB). NOT yet validated on Assam labels.

Runs all five models over both dates in 512 tiles with 64 px overlap (centre-weighted averaging), threshold 0.35, then the flood rule per model (water 29 Jul, dry 17 Jul, JRC <= 80%, HAND <= 15 m, both images have data). Missing HAND does not exclude a pixel. Saves per-model flood maps as bits in one uint8 file (`flood_bits.tif`) plus a version without the "dry on 17 July" rule (`water29_bits.tif`) for the open decision on roads already under water.

## Week 4: Road network, facilities, villages (`07_build_network.ipynb`, run in Colab by Tanush)

Status: RUN by Tanush (Colab, 2026-11-12). Outputs in Drive `cutoff_network`; summary in `results/network_run1/`. Network and facilities usable; villages NOT usable (see findings).

Decisions (in `src/config.py`):
- One network for the whole STUDY_BBOX, not per district, so villages near a border can use facilities across it. Villages are only made for the three districts.
- Walking-only ways (footway, steps, pedestrian, cycleway, bridleway) excluded; `path` and `track` kept because many rural villages are reached only by them.
- Open Buildings v3, confidence >= 0.70; settlements = DBSCAN 100 m, min 1 building (`n_buildings` kept so small groups can be filtered later).
- WorldPop 2020 constrained, 100 m; each cell's people split equally among the buildings in it.
- Health facilities merged within 50 m; `kind` kept (hospital / clinic / doctors / healthcare tag) so analysis can be restricted to hospitals later.
- Road strip = 20 m wide in total (10 m each side), flat ends.
- Dry-run routing gives each village's normal route length; villages unreachable even with no flood are map gaps and must never be counted as flood-cut-off.

### Assam run 1 findings (2026-11-13), whole study box, NOT just the three districts

- Grid: radar files are 14040 x 10148, JRC/HAND file 14039 x 10147 (Earth Engine added one row and column to the radar). Same origin and pixel size, so the one-pixel alignment is harmless.
- Radar values look normal (VV median -9 dB, VH median -15 dB on both dates).
- Flood (new water) per model: 580 to 713 km2. Agreement: any model 1,153; at least 3 of 5: 579; all 5: 295 km2. Uncertainty inside flooded areas is about 4 times that outside (mean std 0.107 vs 0.024).
- 2.4 times the rough threshold estimate (271 km2, VV < -16 dB, smoothed). Not explained yet; the Assam labels decide which is closer.
- Change between dates (5-model average): water on both dates 2,415 km2; new on 29 July 653 km2; water on 17 July only 580 km2. The 17-July-only water is almost all NORTH of the Brahmaputra, and the new water is mostly on the SOUTH bank (Sivasagar, Jorhat, Charaideo, south-west of the box). A clear spatial pattern, so it looks like real drainage vs new flooding, not random noise.
- Sivasagar close-up looks right: new dark water in fields is flagged, the town, the tanks (dark on both dates) and the river are not.
- JRC permanent-water filter (occurrence > 80%) removed almost nothing: the monsoon Brahmaputra spreads over sand bars that are dry most of the year, so their occurrence is below 80%. Rule 2 (dry on 17 July) is what removes the river. Consequence: `water29_bits` (without rule 2) still contains the whole river and is NOT usable for roads as is. Bridges are flagged separately, so most roads do not cross the river anyway, but this must be fixed before testing the "without rule 2" option (e.g. use JRC seasonality or the 17 July river channel).
- All areas above are for the whole 140 x 101 km box, which includes north-bank districts. Clip to the three districts (Tanush's `districts.gpkg`) before quoting numbers.

### Network run 1 findings (2026-11-13)

- Network: 538,703 road stretches, 16,367 km, 975 bridge stretches. 176 separate pieces; the largest holds 78% of junctions. The next two (about 53k and 49k junctions) are expected to be the north bank and Majuli, which have no road bridge inside the study box. Villages are only made for the three south-bank districts, so this is fine.
- Facilities: 228 after merging. Kinds include dentist (8), pharmacy (1) and rehabilitation (1), which are not places to go in an emergency: exclude them. Keep hospital, clinic, health centre (`centre`), doctors.
- PROBLEM 1, people: only 31% of WorldPop people landed on a detected building, so the village populations total about 750k against roughly 2 million living in the three districts. Not a code bug: checked on file 373 directly, only 27% of WorldPop people sit in a 100 m cell with an Open Buildings building (54% within one cell, 69% within two). The two datasets place people and houses differently (houses under tree canopy are often missed).
- PROBLEM 2, mega-settlements: DBSCAN with 100 m chains continuous rural housing into huge groups (largest: 114,158 buildings, 131k people, Jorhat town plus surrounding villages). One route for 131k people is meaningless.
- PROBLEM 3, tiny groups: 59% of settlements have fewer than 5 buildings (median 2 among "no road access"). Mostly isolated sheds or false detections in fields.
- Decision: replace building clusters with fixed 500 m population squares built straight from WorldPop (people counted 100% by construction, no chaining, equal-size units). Done inside notebook 08, so the network does not need rebuilding. Open Buildings kept only as a cross-check.
- Visual check of 10 villages: NOT done yet.

## Week 4: Cut-off analysis (`08_cutoff_villages.ipynb`)

Status: RUN 1 DONE (2026-11-13, run by Claude on the Step 6 and Step 7 outputs). Results in `results/cutoff_run1/`. PROVISIONAL: the flood map is not yet validated on Assam labels, and the OSM visual check is not done.

Method changes from the plan (all in `src/config.py`):
- Population units = 500 m squares from WorldPop 2020 constrained (replaces building clusters). 17,899 squares, 2,213,930 people in the three districts (Charaideo 488k, Jorhat 916k, Sivasagar 810k), close to expected district totals.
- Each square joins the nearest junction that reaches a facility on a normal day (skips disconnected map fragments), up to 500 m; 1,000 m tested as sensitivity.
- Facilities counted: 205 (hospital, clinic, health centre, doctors; dentists, pharmacies, diagnostics etc. dropped by type or name).
- Flooded share per road stretch: points every 5 m along and at 4 positions across the 20 m strip, per model. Checked against true strip polygons on 290 stretches: mean absolute difference 0.045.
- A square counts as "dry" if under 25% of it is flooded on the majority map; only dry squares are counted as "dry but cut off".
- Long detour = route at least 2 times the normal length.

Run 1 results (road blocked if > 20% of strip flooded, join within 500 m):
- Blocked road length per model: 502 to 933 km (of 16,367 km).
- People in dry squares cut off from every facility by road: 167,805 (all 5 models), 314,899 (majority map), 507,722 (any model). 339,917 people are uncertain (1 to 4 of 5 models): more than the number all five agree on. This is the answer to sub-question 4.
- Threshold sensitivity (majority map): 10% -> 436,700; 20% -> 314,899; 40% -> 178,844 people.
- Join distance 1,000 m: majority-map cut off 439,744 (more people on the network).
- NOT COUNTED: 735,217 people (33%) live in squares with no road reaching a facility within 500 m on a normal day; only 348 of those squares look like map gaps (a disconnected road nearby). Most are simply far from any mapped road: OpenStreetMap is missing many village lanes or tracks. Biggest limitation of the results so far; the visual check must quantify it.
- 111,380 people on the network live in squares at least 25% flooded (need rescue, not a road; reported separately).
