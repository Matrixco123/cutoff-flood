# Cut Off: road-map check and ASDMA flood reports (25 July to 3 August 2026)

Done by Claude on 13 Nov 2026 for Tanush, following "Cut Off: Checking the Road Map in QGIS".

## 1. check_sheet_filled.csv
The 12-point visual check. Done by comparing Esri World Imagery against OpenStreetMap (Mapnik) at zoom 16 in a browser,
not in QGIS and not against network.gpkg (not provided). network.gpkg is built from OSM, so the comparison is the same,
except that the project network drops construction/proposed roads, which affects none of these points.
Distances are estimated from the map scale (~2.1 m/pixel), not measured, so treat them as +/-20%.
Verdicts: 2 x A, 2 x B, 5 x C, 3 x D. Four of the five C's are tea gardens whose internal road grid is not in OSM.

## 2. ASDMA reports
Source: the ASDMA daily flood report generator at https://sdrf.assam.gov.in/dfr/download?type=flood (the old
asdma.assam.gov.in report page now redirects here). One PDF per date; the text was extracted with pdf.js.

- raw_text/asdma_flood_report_<date>.txt: full text of each day's report (all districts), one line per PDF text row,
  cells separated by " | ". Page breaks are marked "=== PAGE n END ===". Keep these as the primary record.
  The PDFs themselves were not downloaded; regenerate any day from the URL above in a few seconds if needed.
- asdma_circle_table.csv: one row per date x district x revenue circle for Sivasagar, Charaideo and Jorhat:
  villages affected, population affected, crop area submerged (ha), relief-camp inmates.
- asdma_district_table.csv: one row per date x district: villages, population, crop area, relief camps,
  camp inmates, flood deaths (cumulative), houses fully / partially damaged.
- asdma_damage_appendix_our_districts.txt: the infrastructure-damage rows (roads, bridges, embankments, schools,
  health centres, anganwadis, water supply schemes) for the three districts, each date. Many entries carry
  longitude/latitude. These are the closest thing in the reports to "which roads were under water where".

## Things to know before using the numbers
1. No report lists villages as "cut off" or "marooned", and none has a per-village table. Validation stays at
   revenue-circle level, as planned.
2. The site returned a report headed 27-07-2026 when asked for 28-07-2026. There appears to be no separate 28 July
   report; the 28 July rows repeat 27 July (with a few later corrections). Treat 27 and 28 as one observation.
3. All reports carry "Report Generated On: 27/28-08-2026", i.e. they were regenerated from the DRIMS database a month
   later. Figures are the district submissions as they stood then, which can differ from what newspapers printed on
   the day.
4. Population figures are cumulative "affected" counts as reported by circles, and jump around (e.g. Sivsagar circle
   195,846 on 25 July, 72,846 on 26 July). Use ranks and trends, not exact values.
5. A few cells fell across PDF page breaks and were patched by hand from the text (noted in scratch/parse.py).
   Blank cells mean the circle was not listed that day.
6. Circle names as ASDMA spells them: "Sivsagar" (circle) vs "Sivasagar" (district); "Sonari RC part" is the part of
   Sonari circle that falls in Sivasagar district; "Sapekhati" appears only on 25-28 July.

## Peak and recession, for matching to the 17 and 29 July images
Villages affected (three districts): 588 on 25 Jul, 575 on 26 Jul, 489 on 27 Jul, 441 on 29 Jul, 348 on 30 Jul,
309 on 31 Jul, 278 on 1 Aug, 246 on 2 Aug, 249 on 3 Aug. The 29 July image is after the peak but still within
the main flood; by 1 August about half the villages had been dropped from the list.
