# Anu Kramer - hakramer@wisc.edu
# Updated 6-9-2025

# PURPOSE: once make single disturbance raster, split back out into single 1/0 rasters for each disturbance type
#               see FINAL1 comments for breakdown of codes

# SPEED: 45 min
# 
#
# TYPE THE FOLLOWING INTO CMD:
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 9_compile_annual_single_rasters_full_value_range.py

import arcpy  
from arcpy import env  
from arcpy.sa import *
import sys
import os
import master_variables

#################################################
############ ADJUST THE VALUES BELOW ############
#################################################
base_folder = master_variables.base_folder_master
coordinate_system = master_variables.coordinate_system_master
FINAL_1_folder = master_variables.FINAL_1_master
FINAL_2_folder = master_variables.FINAL_2_master
FINAL_3_folder = master_variables.FINAL_3_master
MMI_min_year = master_variables.MMI_min_year_master
fire_longevity = master_variables.fire_longevity_master 
###############################################################
############ EVERYTHING BELOW SHOULD BE GOOD TO GO ############
###############################################################
# if the folder doesn't exist, make it
single_rasters = base_folder+"ANALYSIS/"+FINAL_3_folder+"/single_year/"
os.makedirs(single_rasters, exist_ok=True)

for year in range(1985+fire_longevity,2023): 
    str_year=str(year)
    print(str_year)
    disturb_path = base_folder+"ANALYSIS/"+FINAL_3_folder+"/disturbance_USFSonly_"+str_year+"_nobuff.tif"
    # split into rasters of 1/0s and save to single_rasters folder for USFS ownership ONLY
    
    # HIGH SEV FIRE - 5000 
    out_raster = arcpy.sa.Reclassify(
        in_raster=disturb_path,
        reclass_field="Value", remap="0 1999 0; 2000 2000 NODATA; 2001 4999 0; 5000 5000 1; 5001 10000 0",
        missing_values="DATA")
    OutRas = SetNull(out_raster == 2000, out_raster)
    OutRas.save(single_rasters+"HiSev_"+str_year+".tif")
    
    # RECENTLY BURNED HI SEV - 3100 & 3150 & 3175 
    out_raster = arcpy.sa.Reclassify(
        in_raster=disturb_path,
        reclass_field="Value", remap="0 1999 0; 2000 2000 NODATA; 2001 3099 0; 3100 3175 1; 3176 10000 0",
        missing_values="DATA")
    OutRas = SetNull(out_raster == 2000, out_raster)
    OutRas.save(single_rasters+"HiSev_old_"+str_year+".tif")
    
    # ANY HI SEV - 3100 & 3150 & 3175 & 5000 
    out_raster = arcpy.sa.Reclassify(
        in_raster=disturb_path,
        reclass_field="Value", remap="0 1999 0; 2000 2000 NODATA; 2001 3099 0; 3100 3175 1; 3176 4999 0; 5000 5000 1; 5001 10000 0",
        missing_values="DATA")
    OutRas = SetNull(out_raster == 2000, out_raster)
    OutRas.save(single_rasters+"HiSev_any_"+str_year+".tif")
    
    # ANY LOW-MOD SEV FIRE - 3000 & 3050 & 3075 & 4000 
    out_raster = arcpy.sa.Reclassify(
        in_raster=disturb_path,
        reclass_field="Value", remap="0 1999 0; 2000 2000 NODATA; 2001 2999 0; 3000 3075 1; 3076 3999 0; 4000 4000 1; 4001 10000 0",
        missing_values="DATA")
    out_raster.save(single_rasters+"LowModSev_any_"+str_year+".tif")
    
    # ALL FIRE - 3000-5000 
    out_raster = arcpy.sa.Reclassify(
        in_raster=disturb_path,
        reclass_field="Value", remap="0 1999 0; 2000 2000 NODATA; 2001 2999 0; 3000 5000 1; 5001 10000 0",
        missing_values="DATA")
    out_raster.save(single_rasters+"All_fire_"+str_year+".tif")
    
    # ANY DISTURBANCE - 9-5000
    out_raster = arcpy.sa.Reclassify(
        in_raster=disturb_path,
        reclass_field="Value", remap="0 9 0; 10 1999 1; 2000 2000 NODATA; 2001 5000 1; 5001 10000 0",
        missing_values="DATA")
    out_raster.save(single_rasters+"Any_disturb_"+str_year+".tif")
    
    # NON-USFS - 2000
    out_raster = arcpy.sa.Reclassify(
        in_raster=disturb_path,
        reclass_field="Value", remap="0 1999 0; 2000 2000 1; 2001 10000 0",
        missing_values="DATA")
    out_raster.save(single_rasters+"NonUSFS_"+str_year+".tif")
    
    # SALVAGE (any) - 475 & 3075 & 3175
    out_raster = arcpy.sa.Reclassify(
        in_raster=disturb_path,
        reclass_field="Value", remap="0 474 0; 475 475 1; 476 1999 0; 2000 2000 NODATA; 2001 3074 0; 3075 3075 1; 3076 3174 0; 3175 3175 1; 3176 10000 0",
        missing_values="DATA")
    out_raster.save(single_rasters+"SalvageAll_"+str_year+".tif")
    
    # TREATMENTS (any) - 300-400
    out_raster = arcpy.sa.Reclassify(
        in_raster=disturb_path,
        reclass_field="Value", remap="0 299 0; 401 1999 0; 2000 2000 NODATA; 2001 10000 0",
        missing_values="DATA")
    out_raster.save(single_rasters+"TreatAll_"+str_year+".tif")
    
    # TREATMENTS (any, including fire-treat) - 300-400, 3050, 3150 
    out_raster = arcpy.sa.Reclassify(
        in_raster=disturb_path,
        reclass_field="Value", remap="0 299 0; 300 400 1; 401 1999 0; 2000 2000 NODATA; 2001 3049 0; 3050 3050 1; 3051 3149 0; 3150 3150 1; 3151 10000 0",
        missing_values="DATA")
    out_raster.save(single_rasters+"TreatAll_incl_fire_1s0s_"+str_year+".tif")
    
    # TREATMENTS (any, including fire-treat) - 300-400, 3050, 3150 
    out_raster = arcpy.sa.Reclassify(
        in_raster=disturb_path,
        reclass_field="Value", remap="0 299 0; 401 1999 0; 2000 2000 NODATA; 2001 3049 0; 3050 3050 1; 3051 3149 0; 3150 3150 1; 3151 10000 0",
        missing_values="DATA")
    out_raster.save(single_rasters+"TreatAll_incl_fire_"+str_year+".tif")
    
    # if the year is on or after MMI, then put single drought years in a separate folder so can implement drought lag in next step
    if year >= MMI_min_year:
        # DROUGHT - 100-200
        out_raster = arcpy.sa.Reclassify(
            in_raster=disturb_path,
            reclass_field="Value", remap="0 99 0; 201 1999 0; 2000 2000 NODATA; 2001 10000 0",
            missing_values="DATA")
        out_raster.save(single_rasters+"Drought_"+str_year+".tif")
    
    else: # if before MMI start, there's no drought, so everything below 10 is no disturbance
        # NO DISTURBANCE - 0
        out_raster = arcpy.sa.Reclassify(
            in_raster=disturb_path,
            reclass_field="Value", remap="0 9 1; 10 1999 0; 2000 2000 NODATA; 200110000 0",
            missing_values="DATA")
        out_raster.save(single_rasters+"NoDisturbance_"+str_year+".tif")

print("DONE!")

