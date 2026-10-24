# Cut Off: Finding Villages Stranded by Floods

AI3001 Deep Learning project, Plaksha University.

## The idea

During floods, some villages stay dry but every road out of them goes underwater, so the people living there cannot reach a hospital. Normal flood maps show where the water is, not who is stranded.

We use Sentinel-1 satellite radar images and deep learning to find flood water, check which roads are underwater, and identify villages with no dry route to a hospital. Because any model can be wrong, we also report how confident we are about each village.

**Case study:** July 2026 floods in Upper Assam (Charaideo, Sivasagar and Jorhat districts).

**Research question:** Can a deep learning flood model, trained on public data and aware of its own uncertainty, reliably identify villages that have lost road access to medical care during a flood?

## How it works

1. Train five U-Net models on Sen1Floods11 (radar images with water marked by experts).
2. Download Sentinel-1 images of Upper Assam from before (June 2026) and during (July 2026) the flood.
3. Each model marks every 10 m pixel as water or not water.
4. Keep only new flood water: remove water already present in June, permanent water (JRC), and high ground where water cannot collect (MERIT Hydro HAND).
5. Lay the OpenStreetMap road network over the flood map and mark underwater road stretches as blocked.
6. For each village, check whether any route to a hospital uses only dry roads.
7. Show the results on a map: flooded, dry but cut off, dry and connected, with confidence.

## Repository layout

```
cutoff-flood/
  README.md            this file
  NOTES.md             decision log and check results (keep it updated)
  requirements.txt     Python packages
  src/
    config.py          ALL shared settings (dates, areas, thresholds)
    preprocess.py      the ONE radar preprocessing function
    metrics.py         IoU, Dice, precision, recall
  notebooks/
    01_road_check.ipynb              Check 1: are village roads and hospitals mapped?
    02_sentinel1_check.ipynb         Check 2: is there satellite imagery of the flood?
    03_sen1floods11_first_train.ipynb Check 3: first U-Net training run
  data/
    raw/               downloaded data, saved with dates (not pushed to GitHub)
    processed/         cleaned data ready for the model (not pushed)
    assam_test_labels/ hand-labelled Assam tiles, for testing only
  results/             tables and figures
  docs/                reports and presentations
```

## Getting started

1. **Register for Google Earth Engine** at earthengine.google.com: create a Cloud project and register it for non-commercial use. Approval can take up to a day.
2. **Push this folder to GitHub** (from inside the `cutoff-flood` folder):
   ```
   git init
   git add .
   git commit -m "Project setup"
   git branch -M main
   git remote add origin https://github.com/Matrixco123/cutoff-flood.git
   git push -u origin main
   ```
   Create the empty repository `cutoff-flood` on GitHub first. If you use a different account or name, also change `REPO_URL` in the first cell of each notebook.
3. **Run the checks in Google Colab**, in this order:
   1. `01_road_check.ipynb` (no account needed; biggest risk, so first)
   2. `02_sentinel1_check.ipynb` (needs Earth Engine approval)
   3. `03_sen1floods11_first_train.ipynb` (choose a T4 GPU runtime)

   To open a notebook in Colab: go to colab.research.google.com, choose *GitHub*, and paste the repository link.
4. **Record each result in `NOTES.md`**, then make the go / no-go decision.

## Rules for the team

- **One preprocessing function.** Every radar image goes through `src/preprocess.py`. Never write a second version.
- **One set of settings.** Numbers live in `src/config.py`. If you change one, write it in `NOTES.md`.
- **Save raw data with dates** (e.g. `roads_Sivasagar_2026-10-25.graphml`) so results can be reproduced.
- **Never train on the test set** or on the hand-labelled Assam tiles. They are for evaluation only.

## Data sources

| Purpose | Dataset | Access |
|---|---|---|
| Training labels | Sen1Floods11 | `gs://sen1floods11` ([GitHub](https://github.com/cloudtostreet/Sen1Floods11)) |
| Flood images | Sentinel-1 GRD | Earth Engine `COPERNICUS/S1_GRD` |
| Permanent water | JRC Global Surface Water | Earth Engine `JRC/GSW1_4/GlobalSurfaceWater` |
| Terrain (HAND) | MERIT Hydro | Earth Engine `MERIT/Hydro/v1_0_1` |
| Roads | OpenStreetMap | OSMnx |
| Villages | Google Open Buildings | Earth Engine |
| Population | WorldPop | Earth Engine |
| Hospitals | OpenStreetMap, Healthsites.io | OSMnx, healthsites.io |
| Validation | ASDMA flood reports, news | asdma.assam.gov.in |
