# data in O:\Sierra-wide GPS Tagging Project\Anu\Helping\Elizabeth\Elizabeth_final_data_prep
# Anu Kramer
# 7-30-2024

# PURPOSE: combine annual rasters
#               see FINAL1 comments for breakdown of codes

# SPEED: 15 min
# 
#
# TYPE THE FOLLOWING INTO CMD:
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat FINAL_4_compile_20yr_for_each_disturb.py

import arcpy  
from arcpy import env  
from arcpy.sa import *
import sys
import os
import functions

#################################################
############ ADJUST THE VALUES BELOW ############
#################################################
base_folder = functions.base_folder_master
coordinate_system = functions.coordinate_system_master
step4_folder = functions.step4_master # NEW
FINAL_1_folder = functions.FINAL_1_master
FINAL_2_folder = functions.FINAL_2_master
FINAL_3_folder = functions.FINAL_3_master
MMI_min_year = functions.MMI_min_year_master

###############################################################
############ EVERYTHING BELOW SHOULD BE GOOD TO GO ############
###############################################################
# if the folder doesn't exist, make it
single_rasters = base_folder+"ANALYSIS/"+FINAL_3_folder+"/single_year/"
os.makedirs(single_rasters, exist_ok=True)
folder_20yr= base_folder+"ANALYSIS/"+FINAL_3_folder+"/20_year/" # NEW
older_20yr_intermediate= base_folder+"ANALYSIS/"+FINAL_3_folder+"/20_year/intermediate/" # NEW
os.makedirs(older_20yr_intermediate, exist_ok=True) # NEW

# compile into single 20-year raster for each disturb type
def mosaic_20yr(file_type):
    print(file_type)
    compile_rasters = single_rasters+file_type+"2002.tif"
    for year in range(2003,2023):
        compile_rasters = compile_rasters+";"+single_rasters+file_type+str(year)+".tif"
    
    # mosaic max of all drought rasters and disturb_raster 
    arcpy.management.MosaicToNewRaster(
        input_rasters=compile_rasters,
        output_location=older_20yr_intermediate,  # NEW
        raster_dataset_name_with_extension="disturbance_"+file_type+"20yr.tif",
        coordinate_system_for_the_raster=coordinate_system, pixel_type="16_BIT_UNSIGNED", cellsize=None, number_of_bands=1, mosaic_method="MAXIMUM", mosaic_colormap_mode="FIRST")
    # clip to USFS ownership only # NEW
    usfs_path = base_folder+"ANALYSIS/"+step4_folder+"/usfs_final_OsNull.tif"
    final_disturbance = Times(usfs_path,older_20yr_intermediate+"/disturbance_"+file_type+"20yr.tif")
    final_disturbance.save(folder_20yr+"/disturbance_"+file_type+"20yr.tif")

mosaic_20yr("HiSev_any_") # NEW
mosaic_20yr("LowModSev_any_") # NEW2
mosaic_20yr("TreatAll_")
mosaic_20yr("Drought_")
mosaic_20yr("Any_disturb_")
mosaic_20yr("All_fire_")


print("DONE!")
