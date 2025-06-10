# Anu Kramer
# 11-14-2024

# PURPOSE: 
#               o	Mosaic (MAXIMUM)
#                  	MMI_yyyy_0s_study_area.tif 
#                  	fire_allsev_yyyy-longevitytoyyyy_final.tif * 200
#               o	reclass 200 -> 0 (MMI_yyyy_0s_nofire.tif)
#               o	reclass MMI_yyyy0s_nofire.tif 0 -> NODATA (MMI_yyyy_NODATA_nofire.tif)
#               o	reclass MMI_yyyy0s_nofire.tif 0-drought_threshold -> 0; drought_threshold-100 -> 1 (MMI_yyyy_0s_nofire_drought.tif)
#               o	reclass MMI_yyyy0s_nofire.tif 0-treat_threshold -> 1; treat_threshold-100 -> 2 (MMI_yyyy_0s_nofire_treat_under1_over2.tif)

# SPEED: 2 min
#
# TYPE THE FOLLOWING INTO CMD:
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 5_MMI_nofire.py 2002
#       ...RUN IN 2 BATCHES!
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 5_MMI_nofire.py 2022

import arcpy  
from arcpy import env  
from arcpy.sa import *
import sys
import os
import functions

year=sys.argv[1]
str_year=str(year)
year=int(str_year)
print(year)

#################################################
############ ADJUST THE VALUES BELOW ############
#################################################
base_folder = functions.base_folder_master
fire_longevity = functions.fire_longevity_master
# treat_threshold = functions.treat_threshold_master
# drought_threshold = functions.drought_threshold_master
snap_tile = functions.snap_path_master
coordinate_system = functions.coordinate_system_master
step2_folder = functions.step2_master
step3_folder = functions.step3_master
step4_folder = functions.step4_master
step5_folder = functions.step5_master

###############################################################
############ EVERYTHING BELOW SHOULD BE GOOD TO GO ############
###############################################################
# make folders if they don't exist
# if the folder doesn't exist, make it
saveTo=base_folder+"ANALYSIS/"+step5_folder+"/"+str_year+"/"
os.makedirs(saveTo, exist_ok=True)
MMI_raster_path = base_folder+"ANALYSIS/"+step2_folder+"/"+str_year+"/"+snap_tile+"_"+str_year+"_WGS.tif"

# prep fires by making them 0s or 1000s
fire_times200 = Times(base_folder+"ANALYSIS/"+step3_folder+"/multi_year_fire/fire_allsev_"+str(year-fire_longevity)+"to"+str(year)+"_final.tif",200)
fire_times200.save(saveTo+"fire_allsev_"+str(year-fire_longevity)+"to"+str(year)+"_times200.tif")
# prep non-usfs by making them 0s or 1000s
owner_times200 = Times(base_folder+"ANALYSIS/"+step4_folder+"/non_usfs_final.tif",200)
owner_times200.save(saveTo+"non_usfs_final_times200.tif")

# mosaic
print("mosaicing...")
with arcpy.EnvManager(snapRaster=MMI_raster_path):
    arcpy.management.MosaicToNewRaster(
        input_rasters=base_folder+"ANALYSIS/"+step2_folder+"/"+str_year+"/MMI_150s_"+str(year)+"_study_area.tif;"+saveTo+"fire_allsev_"+str(year-fire_longevity)+"to"+str(year)+"_times200.tif;"+saveTo+"non_usfs_final_times200.tif",
        output_location=saveTo,
        raster_dataset_name_with_extension="max_MMI_FIRE_OWNER_"+str(year)+".tif",
        coordinate_system_for_the_raster=coordinate_system,
        pixel_type="8_BIT_UNSIGNED",
        cellsize=None,
        number_of_bands=1,
        mosaic_method="MAXIMUM",
        mosaic_colormap_mode="FIRST")


print("reclassifying...")
# reclass a dataset where burned/NA MMI values are NODATA - use this to calculate mean MMI per FACTS and recombine with fuel management and drought at the end
out_raster = arcpy.sa.Reclassify(
        in_raster=saveTo+"max_MMI_FIRE_OWNER_"+str(year)+".tif",
        reclass_field="Value", remap="150 200 NODATA",
        missing_values="DATA")
out_raster.save(saveTo+"MMI_"+str(year)+"_NODATA_nofireUSFS.tif")

# reclass a dataset where burned/NA MMI values are 0
out_raster = arcpy.sa.Reclassify(
        in_raster=saveTo+"max_MMI_FIRE_OWNER_"+str(year)+".tif",
        reclass_field="Value", remap="0 10 0; 150 200 0",
        missing_values="DATA")
out_raster.save(saveTo+"MMI_"+str(year)+"_0s_nofireUSFS_gt10.tif")

# reclass a dataset where burned/NA MMI values are 0, MMI >= drought threshold = 1, all else 0
out_raster = arcpy.sa.Reclassify(
        in_raster=saveTo+"max_MMI_FIRE_OWNER_"+str(year)+".tif",
        reclass_field="Value", remap="0 10 0; 10 100 1; 150 200 0",
        missing_values="DATA")
out_raster.save(saveTo+"MMI_"+str(year)+"_0s_nofireUSFS_drought10.tif")

# # reclass a dataset where burned is 0, 0-treat_threshold -> 1; treat_threshold-100 -> 2; MMI that was NA -> 1
# out_raster = arcpy.sa.Reclassify(
#         in_raster=saveTo+"max_MMI_FIRE_OWNER_"+str(year)+".tif",
#         reclass_field="Value", remap="0 "+str(treat_threshold)+" 1; "+str(treat_threshold)+" 100 2; 150 150 1; 200 200 0",
#         missing_values="DATA")
# out_raster.save(saveTo+"MMI_"+str(year)+"_0s_nofireUSFS_treat_under1_over2.tif")

print("DONE!")