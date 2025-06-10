# Anu Kramer - hakramer@wisc.edu
# Updated 6-9-2025

# PURPOSE: set the relevant global variables, paths, and thresholds to be used throughout each step in the code
# reference accompanying doc "Code descriptions" for more details on each layer

import arcpy  
from arcpy import env  
from arcpy.sa import *
import sys
import os

# variables - confirm that these are correct
fire_longevity_master = 3
MMI_min_year_master = 2002

# data paths - change these to match the paths for your computer / the specs for your data
base_folder_master = r"R:/Anu/MMI_x_FACTS_analysis/20241101_PARENT_CODE_DISTURBANCE/20250319_salvage/"
MMI_folder_master = "R:/Anu/GIS_Data/Drought/eDaRT-talk_with_Anu_before_using/20240423_fromAlex_eDaRT2.32/Mortality_Index_Sierra/"
tiles_master = ("sc303ns","sc304ns","sc305ns","sc307ns","sc308ns","sc309ns","sc401ss","sc402ss","sc403ss","sc404ss","sc405ss","sc406ss","sc408ss","sc409ss","sc410ss","sc411ss")
snap_path_master = "sc309ns"
coordinate_system_master = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
geographic_transform_master = "WGS_1984_(ITRF00)_To_NAD_1983"
fires_path_master = base_folder_master+"DATA/cbi_sierra_cat_rasters"
fire_perimeters_path_master = base_folder+"DATA/1950to2023_fire_perimeters.shp"
study_area_path_master = base_folder_master+"DATA/StudyArea_dissolve.shp"
ownership_path_master = base_folder_master+"DATA/USA Federal Lands_2024.shp"
FACTS_CommonAttribute_reduceCols_master = base_folder_master+"DATA/Actv_CommonAttribute_PL_Region05_ReducedCols_study_area_10km.shp"

# folder names - DON'T CHANGE THESE
step1_master = "1_prep_study_area"
step2_master = "2_prep_MMI"
step3_master = "3_prep_fires"
step4_master = "4_prep_ownership"
step5_master = "5_MMI_nofire"
step6_master = "6_FACTS_annual_rasters"
FINAL_1_master = "FINAL_1_compile_annual_disturbance"
FINAL_2_master = "FINAL_2_compile_annual_single_rasters"
FINAL_3_master = "FINAL_3_final_disturbance_rasters"
