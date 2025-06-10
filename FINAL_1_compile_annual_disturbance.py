# Anu Kramer
# 11-16-2024

# PURPOSE: combine annual rasters. Multiple disturbances should not occur in the same year, but if they do, assign only one, with precedence to fire, then treatment, then drought
#               assigning values:
#                   hiSev fire = 5000
#                   low/mod fire = 4000
#                   post-HiSev fire salvage = 3175 (note this is in USFS only, associated with codes 3132, 4231, and 4232) # NEW2
#                   post-HiSev fire treat = 3150 (note this is in USFS only) # NEW2
#                   recently burned at high severity (1-3 years post-fire) = 3100 # NEW
#                   post-AnySev fire salvage = 3075 (note this is in USFS only, associated with codes 3132, 4231, and 4232) # NEW2
#                   post-AnySev fire treat = 3050 (note this is in USFS only) # NEW2
#                   recently burned at any severity (1-3 years post-fire) = 3000
#                   non-USFS = 2000
#                   salvage without fire = 475, shouldn't be much in this category, but need to investigate!...likely some before fire and some after fire, but should be fire sometime nearby!
#                   fuel management = 300-400, where 300 corresponds to an MMI value of 0 within a treatment polygon and 400 corresponds to an MMI value of 100
#                   drought = 100-200, where 100 corresponds to an MMI value of 0 where there is no fire or fuel management and 200 corresponds to an MMI value of 100
#                   nothing = 0
#
# SPEED: 41 min (~8 min each x 38 years = 5 hours!?)...if split into 10-year chuncks and run in paralell, can do in 1.3 hours...
# 
#
# TYPE THE FOLLOWING INTO CMD:
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat FINAL_1_compile_annual_disturbance.py
#           ...was paralell (~ 5 min), but with so many years and having to split them up to not use up all licenses, it was easier to just run one after the other without parallel... :(

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
fire_longevity = functions.fire_longevity_master
step2_folder = functions.step2_master
step3_folder = functions.step3_master
step4_folder = functions.step4_master
step5_folder = functions.step5_master
step6_folder = functions.step6_master
FINAL_1_folder = functions.FINAL_1_master
FINAL_3_folder = functions.FINAL_3_master
MMI_min_year = functions.MMI_min_year_master

snap_tile = functions.snap_path_master
step1_folder = functions.step1_master
step2_folder = functions.step2_master

hexes_path = base_folder+"ANALYSIS/"+step1_folder+"/"+"hexes_dissolve.shp"
MMI_raster_path = base_folder+"ANALYSIS/"+step2_folder+"/2010/"+snap_tile+"_2010_WGS.tif"
###############################################################
############ EVERYTHING BELOW SHOULD BE GOOD TO GO ############
###############################################################
disturbance_path=base_folder+"ANALYSIS/"+FINAL_1_folder+"/Disturbance/"
os.makedirs(disturbance_path, exist_ok=True)
final_disturbance = base_folder+"ANALYSIS/"+FINAL_3_folder+"/"
os.makedirs(final_disturbance, exist_ok=True)

# calculate a raster of the unbuffered study area
print("making study area raster")
with arcpy.EnvManager(snapRaster=MMI_raster_path):  
    arcpy.conversion.PolygonToRaster(
        in_features=hexes_path,
        value_field="ones",
        out_rasterdataset=final_disturbance+"study_area_rast_nobuff.tif",
        #out_rasterdataset=saveTo+"study_area_rast_intermediate.tif",
        cell_assignment="CELL_CENTER",
        priority_field="NONE",
        cellsize=MMI_raster_path,
        build_rat="BUILD") 

#for year in range(1995,2023): # NEW
for year in range(1985+fire_longevity,2023): # NEW
    str_year=str(year)
    print(str_year)
        
    # if the folder doesn't exist, make it
    saveto_path=base_folder+"ANALYSIS/"+FINAL_1_folder+"/"+str_year+"/"
    os.makedirs(saveto_path, exist_ok=True)
    
    print("building final rasters to mosaic...")
    # HIGH SEV FIRE - 5000
    hiSev_path = base_folder+"ANALYSIS/"+step3_folder+"/"+str_year+"/"+"fire_hisev_"+str_year+"_final.tif"
    hiSev_x_5000 = Times(hiSev_path,5000)
    hiSev_x_5000.save(saveto_path+"COVA_hiSev5000_"+str_year+".tif")
    hiSev_path = saveto_path+"COVA_hiSev5000_"+str_year+".tif"
    
    # ALL FIRE (BECOMES LOW/MODERATE SEV WHEN PAIRED WITH HIGH ABOVE) - 4000
    fire_path = base_folder+"ANALYSIS/"+step3_folder+"/"+str_year+"/"+"fire_allsev_"+str_year+"_final.tif"
    fire_x_4000 = Times(fire_path,4000)
    fire_x_4000.save(saveto_path+"COVA_all4000_"+str_year+".tif")
    fire_path = saveto_path+"COVA_all4000_"+str_year+".tif"
    
    # # POST-FIRE TREATMENT - 3500 # NEW2
    # recent_burn_path = base_folder+"ANALYSIS/"+step3_folder+"/multi_year_fire/fire_allsev_"+str(year-fire_longevity)+"to"+str(year)+"_final.tif"
    # treat_path = base_folder+"ANALYSIS/"+step6_folder+"/multi_year/multi_year_YrFINAL_"+str(year)+"_usfs.tif"
    # post_fire_treat = Times(Raster(recent_burn_path)*Raster(treat_path),3500)
    # post_fire_treat.save(saveto_path+"postfire_treat3500_"+str_year+".tif")
    # postfire_treat_path = saveto_path+"postfire_treat3500_"+str_year+".tif"
    
    # POST-HISEV FIRE SALVAGE - 3175 # NEW2
    recent_burn_path = base_folder+"ANALYSIS/"+step3_folder+"/multi_year_fire/fire_hisev_"+str(year-fire_longevity)+"to"+str(year)+"_final.tif"
    treat12s_path = base_folder+"ANALYSIS/"+step6_folder+"/multi_year/multi_year_YrFINAL_"+str(year)+"_usfs.tif"
    out_raster = arcpy.sa.Reclassify(
        in_raster=treat12s_path,
        reclass_field="Value", remap="1 1 0;2 2 1",
        missing_values="DATA")
    out_raster.save(saveto_path+"salvage1s_"+str_year+".tif")
    salvage_path = saveto_path+"salvage1s_"+str_year+".tif"
    post_HiSev_fire_salvage = Times(Raster(recent_burn_path)*Raster(salvage_path),3175)
    post_HiSev_fire_salvage.save(saveto_path+"postHiSev_fire_salvage3175_"+str_year+".tif")
    post_HiSev_fire_salvage_path = saveto_path+"postHiSev_fire_salvage3175_"+str_year+".tif"
    
    # POST-HISEV FIRE TREATMENT - 3150 # NEW2
    out_raster = arcpy.sa.Reclassify(
        in_raster=treat12s_path,
        reclass_field="Value", remap="0 0 0;1 2 1;3 300 0",
        missing_values="DATA")
    out_raster.save(saveto_path+"treat1s_"+str_year+".tif")
    treat1s_path = saveto_path+"treat1s_"+str_year+".tif"
    post_HiSev_fire_treat = Times(Raster(recent_burn_path)*Raster(treat1s_path),3150)
    post_HiSev_fire_treat.save(saveto_path+"postHiSev_fire_treat3150_"+str_year+".tif")
    post_HiSev_fire_treat_path = saveto_path+"postHiSev_fire_treat3150_"+str_year+".tif"
    
    # RECENTLY BURNED HI SEV - 3100 # NEW
    recent_burn_HiSev_path = base_folder+"ANALYSIS/"+step3_folder+"/multi_year_fire/fire_hisev_"+str(year-fire_longevity)+"to"+str(year)+"_final.tif"
    recent_burn_HiSev = Times(recent_burn_HiSev_path,3100)
    recent_burn_HiSev.save(saveto_path+"recent_HiSev_fire3100_"+str_year+".tif")
    recent_burn_HiSev_path = saveto_path+"recent_HiSev_fire3100_"+str_year+".tif"
    
    # POST-ANYSEV FIRE SALVAGE - 3075 # NEW2
    recent_burn_path = base_folder+"ANALYSIS/"+step3_folder+"/multi_year_fire/fire_allsev_"+str(year-fire_longevity)+"to"+str(year)+"_final.tif"
    post_AnySev_fire_salvage = Times(Raster(recent_burn_path)*Raster(salvage_path),3075)
    post_AnySev_fire_salvage.save(saveto_path+"postAnySev_fire_salvage3075_"+str_year+".tif")
    post_AnySev_fire_salvage_path = saveto_path+"postAnySev_fire_salvage3075_"+str_year+".tif"
    
    # POST-ANYSEV FIRE TREATMENT - 3050 # NEW2
    post_AnySev_fire_treat = Times(Raster(recent_burn_path)*Raster(treat1s_path),3050)
    post_AnySev_fire_treat.save(saveto_path+"postAnySev_fire_treat3050_"+str_year+".tif")
    post_AnySev_fire_treat_path = saveto_path+"postAnySev_fire_treat3050_"+str_year+".tif"
    
    # RECENTLY BURNED - 3000
    recent_burn_path = base_folder+"ANALYSIS/"+step3_folder+"/multi_year_fire/fire_allsev_"+str(year-fire_longevity)+"to"+str(year)+"_final.tif"
    recent_burn = Times(recent_burn_path,3000)
    recent_burn.save(saveto_path+"recent_fire3000_"+str_year+".tif")
    recent_burn_path = saveto_path+"recent_fire3000_"+str_year+".tif"
    
    # NON-USFS - 2000
    non_usfs_path = base_folder+"ANALYSIS/"+step4_folder+"/non_usfs_final.tif"
    non_usfs = Times(non_usfs_path,2000)
    non_usfs.save(saveto_path+"non_usfs2000_"+str_year+".tif")
    non_usfs_path = saveto_path+"non_usfs2000_"+str_year+".tif"
    
    # POST-ANYSEV FIRE SALVAGE - 475 # NEW2
    nofire_salvage = Times(Raster(salvage_path),475)
    nofire_salvage.save(saveto_path+"nofire_salvage475_"+str_year+".tif")
    nofire_salvage_path = saveto_path+"nofire_salvage475_"+str_year+".tif"
    
    # TREATMENTS - 300
    MMI_rast = base_folder+"ANALYSIS/"+step5_folder+"/"+str_year+"/MMI_"+str(year)+"_0s_nofireUSFS_gt10.tif"

    if year >= MMI_min_year:
        treatmentsx300 = Times(treat1s_path,300)+MMI_rast
    else:
        treatmentsx300 = Times(treat1s_path,300)
    treatmentsx300.save(saveto_path+"treats300_"+str_year+".tif")
    treatments_path = saveto_path+"treats300_"+str_year+".tif"
    
    # DROUGHT - 100
    drought_path = base_folder+"ANALYSIS/"+step5_folder+"/"+str_year+"/MMI_"+str(year)+"_0s_nofireUSFS_drought10.tif"
    
    print("mosaicing rasters...")
    if year >= MMI_min_year:
        input_rasters_str = hiSev_path+";"+fire_path+";"+recent_burn_HiSev_path+";"+post_HiSev_fire_salvage_path+";"+post_HiSev_fire_treat_path+";"+recent_burn_path+";"+post_AnySev_fire_salvage_path+";"+post_AnySev_fire_treat_path+";"+non_usfs_path+";"+nofire_salvage_path+";"+treatments_path+";"+drought_path # NEW2
    else:
        input_rasters_str = hiSev_path+";"+fire_path+";"+recent_burn_HiSev_path+";"+post_HiSev_fire_salvage_path+";"+post_HiSev_fire_treat_path+";"+recent_burn_path+";"+post_AnySev_fire_salvage_path+";"+post_AnySev_fire_treat_path+";"+non_usfs_path+";"+nofire_salvage_path+";"+treatments_path # NEW2
        # mosaic rasters - make another copy in the "disturbance" folder so it's easy to find later
        arcpy.management.MosaicToNewRaster(
            input_rasters=input_rasters_str,
            output_location=final_disturbance,
            raster_dataset_name_with_extension="disturbance_"+str_year+".tif",
            coordinate_system_for_the_raster=coordinate_system, pixel_type="16_BIT_UNSIGNED", cellsize=None, number_of_bands=1, mosaic_method="MAXIMUM", mosaic_colormap_mode="FIRST")
        # clip to unbuffered study area
        print("clipping to unbuffered study area")
        disturbance_final = Times(final_disturbance+"disturbance_"+str_year+".tif",final_disturbance+"study_area_rast_nobuff.tif")
        disturbance_final.save(final_disturbance+"disturbance_"+str_year+"_nobuff.tif")

    # mosaic rasters - make a copy in the year folder to aid in additional processing
    arcpy.management.MosaicToNewRaster(
        input_rasters=input_rasters_str,
        output_location=saveto_path,
        raster_dataset_name_with_extension="disturbance_"+str_year+".tif",
        coordinate_system_for_the_raster=coordinate_system, pixel_type="16_BIT_UNSIGNED", cellsize=None, number_of_bands=1, mosaic_method="MAXIMUM", mosaic_colormap_mode="FIRST")
    # mosaic rasters - make another copy in the "disturbance" folder so it's easy to find later
    arcpy.management.MosaicToNewRaster(
        input_rasters=input_rasters_str,
        output_location=disturbance_path,
        raster_dataset_name_with_extension="disturbance_"+str_year+".tif",
        coordinate_system_for_the_raster=coordinate_system, pixel_type="16_BIT_UNSIGNED", cellsize=None, number_of_bands=1, mosaic_method="MAXIMUM", mosaic_colormap_mode="FIRST")

print("DONE!")