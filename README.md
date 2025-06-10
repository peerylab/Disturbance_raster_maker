# Disturbance_raster_maker
Generate annual 30 m disturbance rasters for fire, fuels management, and drought for CA

Updated June 2, 2025  
Contact: Anu Kramer (hakramer@wisc.edu)

## Purpose
Generate annual 30 m disturbance rasters from input data (see the output section below for a complete breakdown of disturbance types and corresponding codes). We used this code to generate the data used in our manuscript “Mapping disturbance across California’s rapidly changing forests.”


## Overall format
The code is written as 13 python scripts. The “master.py” script should be the only one where the user changes the values. The other 12 scripts are are designed to be run in sequence and use the filepaths specified in “master.py” to run the code. Note that the code is designed to be run in parallel in the command line terminal, but depending on your system’s capabilities (and the number of concurrent ArcGIS licenses you have), you may have to run the parallel scripts in smaller batches of years. Find an accompanying excel spreadsheet showing an example of the code to paste into the terminal.

## Output
The code generates a raster for each year, with the following values. Users can decide how they want to consolidate the data, depending on their needs and research questions

- 5000 = high severity fire
- 4000 = low/mod severity fire
- 3175 = post-high severity fire salvage
  - 1-3 years post-fire
  - note this is in USFS only, associated with FACTS activity codes 3132, 4231, and 4232
  - ALSO NOTE that fire takes precedence over this code for the year of the fire, but because of the 4-year temporal span of FACTS polygons, these will show up the year after the fire whether they were completed the year of the fire or the year after
- 3150 = post-high severity fire fuel management 
  - 1-3 years post-fire
  - note this is in USFS only
  - note that these pixels might have been salvaged
- 3100 = recently burned at high severity
  - 1-3 years post-fire
- 3075 = post-low/moderate sev fire salvage 
  - 1-3 years post-fire
  - note this is in USFS only, associated with FACTS activity codes 3132, 4231, and 4232
- 3050 = post-low/moderate sev fire fuel management 
  - 1-3 years post-fire
  - note this is in USFS only
  - note that these pixels might have been salvaged
- 3000 = recently burned at low/moderate severity 
  - 1-3 years post-fire
- 2000 = non-USFS
- 475 = salvage without fire 
  - associated with FACTS activity codes 3132, 4231, and 4232
  - shouldn't be much in this category, but this would happen anytime the completion date is on or one year after the date of the fire, due to the 4-year temporal span on fuel management polygons (2 years before to one year after the completion year)
  - likely some before / after fire, but should be fire sometime nearby!
- 300-400 = fuel management 
  - 300 corresponds to an MMI value of 0 within a fuel management polygon 
  - 400 corresponds to an MMI value of 100
  - Note that these pixels definitely were NOT salvaged
- 100-200 = drought 
  - 100 corresponds to an MMI value of 0 where there is no fire or fuel management 
  - 200 corresponds to an MMI value of 100
  - Only generated for years where MMI exists
- 0 = nothing


## Prep to run
- Ensure that ArcGIS Pro is installed (the python code runs functions in ArcGIS without opening any project, but requires the program and license(s)
- Create a new folder that will house all code, data, and output for this run
  - Copy in the “CODE” folder
  - Create a “DATA” folder and copy in:
    - MMI files
    - CBI rasters 
      - projected in NAD 1983 California (Teale) Albers (Meters); with filenames that follow "cbi_cat_yyyy.tif" where yyyy is the year
    - fire perimeter shapefiles
      - projected in NAD 1983 California (Teale) Albers (Meters)
      - Download from FRAP https://frap.fire.ca.gov/mapping/gis-data/
    - study area shapefile
      - projected in WGS 1984
    - ownership shapefile
      - projected in WGS 1984 Web Mercator (auxiliary sphere)
      - downloadable from ESRI’s living atlas (https://www.arcgis.com/home/item.html?id=5e92f2e0930848faa40480bcb4fdc44e)
    - FACTS shapefile
      - projected in NAD 1983
      - download common attributes data for region 5 (FACTS Common Attributes - Region 05) from https://data.fs.usda.gov/geodata/edw/datasets.php
      - note number of rows in attribute table to ensure complete processing
      - delete all but a few columns (use delete field tool with method = keep field): "FACTS_ID", "ACTIVITY_C", "ACTIVITY", "DATE_AWARD", "DATE_COMPL", "AWARD_DATE", "OWNERSHIP", "STATE_ABBR"
      - confirm number of rows remains same as above!
      - select polygons that intersect study area within 10km buffer
      - export as shapefile: "Actv_CommonAttribute_PL_Region05_ReducedCols_study_area_10km.shp"
      - delete AGAIN: all but a few columns (use delete field tool with method = keep field): "FACTS_ID", "ACTIVITY_C", "ACTIVITY", "DATE_AWARD", "DATE_COMPL", "AWARD_DATE", "OWNERSHIP", "STATE_ABBR"
- Open “master.py” and update the filepaths to the base data:
  - fire_longevity_master
    - the number of years after a fire that “fire” should be considered a disturbance (e.g. to include secondary or lagged fire effects)
    - we used a value of 3 in the manuscript (where disturbances for 2020 would include fires from 2017-2020)
  - MMI_min_year_master
    - The earliest year with MMI data
  - base_folder_master 
    - path to the folder for this run (that contains “CODE” and “DATA” folders)
  - MMI_folder_master
    - path to the folder with MMI data 
  - tiles_master
    - list of tile names that are in your study area
    - go to the MMI tiles shapefile and compare tile coverage with your study area
    - e.g. for the Sierra Nevada study area, we used the following list:
      - ("sc303ns","sc304ns","sc305ns","sc307ns","sc308ns","sc309ns","sc401ss","sc402ss","sc403ss","sc404ss","sc405ss","sc406ss","sc408ss","sc409ss","sc410ss","sc411ss")
  - snap_path_master
    - the name of the tile that all the rasters should be snapped to (we chose one in the middle of our study area) 
    - e.g. for the Sierra Nevada study area, we used "sc309ns"
    - Note that while it’s possible to snap the cells to a non-MMI raster, that capability is not built into this code
  - coordinate_system_master 
    - The base coordinate system that gets entered into the reprojection functions
    - Should be in WGS 84 and match your study area (confirm the info in the layer properties source pane under spatial reference or set up a reprojection and look at the arcpy code)
    - E.g. 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
  - geographic_transform_master
    - specify the transformation in the appropriate format
    - If following the recommended projections, this will be: "WGS_1984_(ITRF00)_To_NAD_1983"
  - fires_path_master 
    - folder containing the CBI rasters
    - see “Input data” section for more details
  - fire_perimeters_path_master 
    - shapefile containing fire perimeters
    - see “Input data” section for more details
  - study_area_path_master
    - shapefile containing the study area
    - see “Input data” section for more details
  - ownership_path_master
    - shapefile containing data on ownership
    - see “Input data” section for more details
  - FACTS_CommonAttribute_reduceCols_master
    - shapefile containing the FACTS data
    - see “Input data” section for more details
- Don’t change the folder names on lines 31-39

## Set up your command prompt in windows
- Type “cmd” into your windows search bar and open “command prompt”
- set your working directory as the path to your code folder e.g. "cd …\test_run\CODE"
- use “Command_line_guide.xlsx” to guide you through the commands to enter for each code step
- Some steps include a single code run, and others are most efficient when run in parallel (one run for each year)
  - The prompts in “Command_line_guide.xlsx” are designed for parallel runs, but you can remove the “start” command if you don’t want to use parallel processing
  - Importantly, some of the steps may overwhelm your computer’s capabilities (or the number of concurrent ArcGIS licenses you have access to) – please ensure that all runs complete without errors before moving to the next code step
  - Note that some steps will take longer than others, and the runtime depends on the geographical area you are processing and your computer’s capabilities
  - If you are getting unexplainable errors, try running fewer parallel processes or find a computer with faster processing speed and more RAM
  - It can also help to open your task manager and monitor the CPU and memory use when running this code

## Code breakdown
Note that time estimates are given for a sample run in parallel (for a ~20,000 km2 study area and high-powered desktop computer). Use these as a relative indication of the length of the steps in relation to one another
Also note that much of this documentation is repeated as comments in the code itself

- 1_prep_study_area
  - TIME: 1 min
  - Confirm study area projected in WGS 84 (study_area_WGS.shp)
  - Dissolve into a single polygon (study_area_dissolve.shp)
  - Create a 10 km buffered study area to calculate the disturbance layers within (study_area_dissolve_10km.shp)
- 2_prep_MMI 
  - TIME: 5 min; Be sure to run the MMI years first, then run any pre-MMI years
  - project each MMI tile to target coord system (tile_yyyy_WGS_reclass.tif)
  - reclass MMI 101-200-> 150; NODATA -> 150 (tile_yyyy_WGS_reclass.tif)
  - mosaic all MMI into annual MMI layers (MMI_mosaic_yyyy_WGS.tif)
  - study area -> raster, maintaining alignment with MMI (1s and NODATA; study_area_rast.tif)
  - MMI_ yyyy0s.tif * study_area_rast.tif (MMI_ 150s_yyyy_study_area.tif)
- 3_prep_fires
  - TIME: 45 min 
  - Project fire CBI rasters, maintaining alignment with MMI
  - Reclass NODATA -> 150
  - Multiply by study_area_rast.tif (fire_CBI_yyyy.tif)
  - Reclass 0-2 -> 0; 3 -> 1; 150 -> 0 (fire_hisev_yyyy_final.tif)
  - Reclass 0-3 -> 1; 150 -> 0 (fire_allsev_yyyy_final.tif)
  - Build multi-year all severity fire history, using fire_longevity (fire_allsev_yyyytoyyyy_final.tif)
- 4_prep_ownership
  - TIME: 3 min 
  - Project federal ownership
  - Convert to raster (of 0s and 1s), maintaining alignment with MMI
  - Multiply by study_area_rast.tif (usfs_final.tif, non_usfs_final.tif, usfs_final_OsNull, federal_final.tif, non_federal_final.tif)
- 5_MMI_nofire
  - TIME: 2 min 
  - Mosaic MMI tiles together, snapping to the chosen snap tile and eliminating the MMI value for any pixel that burned that year or within the fire longevity number of years previously (e.g. any areas where canopy loss is likely due to direct or indirect fire effects)
  - Mosaic (MAXIMUM; max_MMI_FIRE_OWNER_yyyy.tif)
    - MMI_999s_yyyy_study_area.tif.tif 
    - fire_allsev_yyyy-longevitytoyyyy_final.tif * 1000
    - usfs_final.tif * 1000
  - reclass a dataset where burned/NA MMI values are NODATA
    - reclass MMI_yyyy_0s_nofire.tif fire/non-USFS -> NODATA 
    - save as MMI_yyyy_NODATA_nofireUSFS.tif
    - use this to calculate mean MMI per FACTS and recombine with fuel management and drought at the end
  - reclass a dataset where burned/NA MMI values are 0, but full spectrum of MMI values remains
    - reclass MMI_yyyy_0s_nofire.tif 0-10 -> 0; fire/non-USFS-> 0
    - save as MMI_yyyy_0s_nofireUSFS_drought.tif
    - use this to populate drought and fuel management pixels at the end
  - reclass a dataset where burned/NA MMI values are 0, MMI 10-100 = 1, all else 0
    - reclass MMI_yyyy0s_nofire.tif 0-10 -> 0; 10-100 -> 1; fire/non-USFS-> 0
    - save as MMI _0s_nofireUSFS_drought10.tif
    - use this to classify drought/not drought in a given year in prep for calculating drought lag
- 6_FACTS_annual_rasters
  - TIME: 66 min 
  - Clean and prep FACTS into fuel management polygons with a YR_FINAL col that can be used to date FACTS polygons from here onward
  - Project all FACTS
  - Select FACTS: (Actv_CommonAttribute_PL_CA_reducedCols_minCols_Teale.shp)
    - intersect with study_area.shp
    - appropriate activity codes 
  - intersect FACTS with study_area.shp (need this for calculating mean MMI values later)
  - Calc yr_compl, yr_award, award_yr
  - Make YR_FINAL and assign where can
- 6b_FACTS_to_raster
  - TIME: 5 min
  - use projected FACTS polygons to convert to rasters per year, using YrFINAL, and maintaining alignment with MMI (FACTS_ YrFINAL_yyyy.tif)
- 6c_FACTS_to_multi_year_raster
  - TIME: 2 min
  - Use single-year rasters from 6b to compile multi-year rasters that account for temporal uncertainty of FACTS data – any pixel with canopy cover change in these cells was most likely due to fuel management
  - assign 2 years before to 1 year after YR_FINAL (multi-year_ YrFINAL_yyyy.tif)
    - so if making an annual raster for FACTS in 2013, include YrFINAL from year-1 to +2 (e.g. 2012-2015)
  - Remove non_usfs (usfs_final.tif * multi-year_ YrFINAL_yyyy.tif = multi-year_ YrFINAL_yyyy_usfs.tif)
- FINAL1_compile_annual_disturbance
  - TIME: 3 min
  - Mosaic (MAXIMUM) = disturbance_yyyy.tif
    - hiSev fire = 5000
    - low/mod fire = 4000 
    - post hisev salvage = 3175
    - post hisev fuel management = 3150
    - recent burn (1-3 years post-fire) hisev = 3100
    - recent burn (1-3 years post-fire) salvage = 3075
    - recent burn (1-3 years post-fire) fuel management = 3050
    - recent burn (1-3 years post-fire) anysev = 3000
    - non-USFS = 2000
    - salvage (without fire in current or preceding 3 years) = 475
    - fuel management (without fire in current or preceding 3 years) = 300-400, where 300 corresponds to an MMI value of 0 within a treatment polygon and 400 corresponds to an MMI value of 100
    - drought = 100-200, where 100 corresponds to an MMI value of 0 where there is no fire or fuel management and 200 corresponds to an MMI value of 100
    - nothing = 0
- FINAL2_compile_annual_single_rasters
  - TIME: 3 min
  - once make single disturbance raster (FINAL_1_folder/Disturbance/disturbance_yyyy.tif), split back out into single 1/0 rasters for each disturbance type – this facilitates each pixel only being classified as one disturbance type, but still having individual disturbance rasters
- FINAL2b_ compile_annual_disturbance_droughtLAG
  - TIME: 18 min
  - incorporate drought lag and create new disturbance raster (FINAL_3_folder/disturbance_yyyy.tif) 
    - note that this version includes area within the 10 km buffer around the study area, and fires are included on non-usfs land
    - while some users may prefer this version, see the following bullet for the nobuff version
  - note that there are disturbance_yyyy_nobuff files as well that include only cells in the original study area
    - we suspect that most users will use this version, and this was the version that we used for the manuscript
    - note that this layer also excludes any non-usfs land
- FINAL3_ compile_annual_single_rasters_full_value_range
  - TIME: 45 min
  - once make single disturbance raster, split back out into single 1/0 rasters for each disturbance type
  - save to FINAL_3_folder/single_year/
