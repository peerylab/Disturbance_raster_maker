# data in O:\Sierra-wide GPS Tagging Project\Anu\Helping\Elizabeth\Elizabeth_final_data_prep
# Anu Kramer
# 7-30-2024

# PURPOSE: once make single disturbance raster, split back out into single 1/0 rasters for each disturbance type
#               see FINAL1 comments for breakdown of codes

# SPEED: 3 min
# 
#
# TYPE THE FOLLOWING INTO CMD:
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat FINAL_2_compile_annual_single_rasters.py 1988
#       ...
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat FINAL_2_compile_annual_single_rasters.py 2022

import arcpy  
from arcpy import env  
from arcpy.sa import *
import sys
import os
import functions

year=sys.argv[1]
str_year=str(year)
year=int(str_year)
#################################################
############ ADJUST THE VALUES BELOW ############
#################################################
base_folder = functions.base_folder_master
coordinate_system = functions.coordinate_system_master
FINAL_1_folder = functions.FINAL_1_master
FINAL_2_folder = functions.FINAL_2_master
MMI_min_year = functions.MMI_min_year_master
disturb_path = base_folder+"ANALYSIS/"+FINAL_1_folder+"/"+str_year+"/disturbance_"+str_year+".tif"
###############################################################
############ EVERYTHING BELOW SHOULD BE GOOD TO GO ############
###############################################################
# if the folder doesn't exist, make it
single_rasters = base_folder+"ANALYSIS/"+FINAL_2_folder+"/"
os.makedirs(single_rasters, exist_ok=True)
drought_single_rasters = base_folder+"ANALYSIS/"+FINAL_2_folder+"/drought_single_year/"
os.makedirs(drought_single_rasters, exist_ok=True)
print(str_year)

# split drought into rasters of 1/0s and save to single_rasters folder

# # HIGH SEV FIRE - 5000 # NEW2
# out_raster = arcpy.sa.Reclassify(
#     in_raster=disturb_path,
#     reclass_field="Value", remap="0 4999 0; 5000 5000 1; 5001 10000 0",
#     missing_values="DATA")
# out_raster.save(single_rasters+"HiSev_"+str_year+".tif")
# 
# # ALL FIRE - 3000-5000
# out_raster = arcpy.sa.Reclassify(
#     in_raster=disturb_path,
#     reclass_field="Value", remap="0 2999 0; 3000 5000 1; 5001 10000 0",
#     missing_values="DATA")
# out_raster.save(single_rasters+"All_fire_"+str_year+".tif")
# 
# # NON-USFS - 2000
# out_raster = arcpy.sa.Reclassify(
#     in_raster=disturb_path,
#     reclass_field="Value", remap="0 1999 0; 2000 2000 1; 2001 10000 0",
#     missing_values="DATA")
# out_raster.save(single_rasters+"NonUSFS_"+str_year+".tif")
# 
# # TREATMENTS (any) - 300-400
# out_raster = arcpy.sa.Reclassify(
#     in_raster=disturb_path,
#     reclass_field="Value", remap="0 299 0; 300 400 1; 401 10000 0",
#     missing_values="DATA")
# out_raster.save(single_rasters+"TreatAll_"+str_year+".tif")

# if the year is on or after MMI, then put single drought years in a separate folder so can implement drought lag in next step
if year >= MMI_min_year:
    # DROUGHT - 1
    out_raster = arcpy.sa.Reclassify(
        in_raster=disturb_path,
        reclass_field="Value", remap="0 0 0; 1 1 1; 2 10000 0",
        missing_values="DATA")
    out_raster.save(drought_single_rasters+"Drought_"+str_year+".tif")

else: # if before MMI start, there's no drought, so everything below 10 is no disturbance
    # NO DISTURBANCE - 0
    out_raster = arcpy.sa.Reclassify(
        in_raster=disturb_path,
        reclass_field="Value", remap="0 9 1; 10 10000 0",
        missing_values="DATA")
    out_raster.save(single_rasters+"NoDisturbance_"+str_year+".tif")

print("DONE!")
