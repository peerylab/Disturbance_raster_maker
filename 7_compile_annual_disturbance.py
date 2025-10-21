# Anu Kramer - hakramer@wisc.edu
# Updated 6-9-2025

# PURPOSE: combine annual rasters. Multiple disturbances should not occur in the same year, but if they do, assign only one, with precedence to fire, then treatment, then drought
#               assigning values:
#                   hi sev fire = 5000
#                   mod sev fire = 4500
#                   low sev fire = 4000

#                   post-HiSev fire salvage = 3500-3600 (note this is in USFS only, associated with codes 3132, 4231, and 4232)
#                   post-HiSev fire treat = 3300-3400 (note this is in USFS only)
#                   recently burned at high severity (1-3 years post-fire) = 3000

#                   post-ModSev fire salvage = 2500-2600 (note this is in USFS only, associated with codes 3132, 4231, and 4232)
#                   post-ModSev fire treat = 2300-2400 (note this is in USFS only)
#                   recently burned at mod severity (1-3 years post-fire) = 2000

#                   post-LowSev fire salvage = 1500-1600 (note this is in USFS only, associated with codes 3132, 4231, and 4232)
#                   post-LowSev fire treat = 1300-1400 (note this is in USFS only)
#                   recently burned at low severity (1-3 years post-fire) = 1000

#                   non-USFS = 999

#                   salvage without fire = 500-600, shouldn't be much in this category, but need to investigate!...likely some before fire and some after fire, but should be fire sometime nearby!
#                   fuel management = 300-400, where 300 corresponds to an MMI value of 0 within a treatment polygon and 400 corresponds to an MMI value of 100
#                   drought = 100-200, where 100 corresponds to an MMI value of 0 where there is no fire or fuel management and 200 corresponds to an MMI value of 100
#                   nothing = 0
#
# SPEED: 41 min (~8 min each x 38 years = 5 hours!?)...if split into 10-year chuncks and run in paralell, can do in 1.3 hours...
# 
#
# TYPE THE FOLLOWING INTO CMD:
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 7_compile_annual_disturbance.py
#           ...was paralell (~ 5 min), but with so many years and having to split them up to not use up all licenses, it was easier to just run one after the other without parallel... :(

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
fire_longevity = master_variables.fire_longevity_master
step2_folder = master_variables.step2_master
step3_folder = master_variables.step3_master
step4_folder = master_variables.step4_master
step5_folder = master_variables.step5_master
step6_folder = master_variables.step6_master
FINAL_1_folder = master_variables.FINAL_1_master
FINAL_3_folder = master_variables.FINAL_3_master
MMI_min_year = master_variables.MMI_min_year_master

snap_tile = master_variables.snap_path_master
step1_folder = master_variables.step1_master
step2_folder = master_variables.step2_master

study_area_path = base_folder+"ANALYSIS/"+step1_folder+"/"+"study_area_dissolve.shp"
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
        in_features=study_area_path,
        value_field="ones",
        out_rasterdataset=final_disturbance+"study_area_rast_nobuff.tif",
        #out_rasterdataset=saveTo+"study_area_rast_intermediate.tif",
        cell_assignment="CELL_CENTER",
        priority_field="NONE",
        cellsize=MMI_raster_path,
        build_rat="BUILD") 

#for year in range(2002,2004): 
for year in range(1985+fire_longevity,2023):
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
    
    # MOD SEV FIRE - 4500
    modSev_path = base_folder+"ANALYSIS/"+step3_folder+"/"+str_year+"/"+"fire_modsev_"+str_year+"_final.tif"
    modSev_x_4500 = Times(modSev_path,4500)
    modSev_x_4500.save(saveto_path+"COVA_modSev4500_"+str_year+".tif")
    modSev_path = saveto_path+"COVA_modSev4500_"+str_year+".tif"
    
    # LOW SEV FIRE - 4000
    lowSev_path = base_folder+"ANALYSIS/"+step3_folder+"/"+str_year+"/"+"fire_lowsev_"+str_year+"_final.tif"
    lowSev_x_4000 = Times(lowSev_path,4000)
    lowSev_x_4000.save(saveto_path+"COVA_lowSev4000_"+str_year+".tif")
    lowSev_path = saveto_path+"COVA_lowSev4000_"+str_year+".tif"
    
    MMI_rast = base_folder+"ANALYSIS/"+step5_folder+"/"+str_year+"/MMI_"+str(year)+"_0s_nofireUSFS_gt10.tif"
        
    # POST-HISEV FIRE SALVAGE - 3500-3600
    recent_burn_path = base_folder+"ANALYSIS/"+step3_folder+"/multi_year_fire/fire_hisev_"+str(year-fire_longevity)+"to"+str(year)+"_final.tif"
    treat12s_path = base_folder+"ANALYSIS/"+step6_folder+"/multi_year/multi_year_YrFINAL_"+str(year)+"_usfs.tif"
    out_raster = arcpy.sa.Reclassify(
        in_raster=treat12s_path,
        reclass_field="Value", remap="1 1 0;2 2 1",
        missing_values="DATA")
    out_raster.save(saveto_path+"salvage1s_"+str_year+".tif")
    salvage_path = saveto_path+"salvage1s_"+str_year+".tif"
    post_HiSev_fire_salvage = Times(Raster(recent_burn_path)*Raster(salvage_path),3500)
    post_HiSev_fire_salvage.save(saveto_path+"postHiSev_fire_salvage3500s_"+str_year+".tif")
    post_HiSev_fire_salvage_path = saveto_path+"postHiSev_fire_salvage3500s_"+str_year+".tif"
    
    # POST-HISEV FIRE TREATMENT - 3300-3400
    out_raster = arcpy.sa.Reclassify(
        in_raster=treat12s_path,
        reclass_field="Value", remap="0 0 0;1 2 1;3 300 0",
        missing_values="DATA")
    out_raster.save(saveto_path+"treat1s_"+str_year+".tif")
    treat1s_path = saveto_path+"treat1s_"+str_year+".tif"
    post_HiSev_fire_treat = Times(Raster(recent_burn_path)*Raster(treat1s_path),3300)
    post_HiSev_fire_treat.save(saveto_path+"postHiSev_fire_treat3300s_"+str_year+".tif")
    post_HiSev_fire_treat_path = saveto_path+"postHiSev_fire_treat3300s_"+str_year+".tif"
    
    # RECENTLY BURNED HI SEV - 3000 
    recent_burn_HiSev_path = base_folder+"ANALYSIS/"+step3_folder+"/multi_year_fire/fire_hisev_"+str(year-fire_longevity)+"to"+str(year)+"_final.tif"
    recent_burn_HiSev = Times(recent_burn_HiSev_path,3000)
    recent_burn_HiSev.save(saveto_path+"recent_HiSev_fire3000_"+str_year+".tif")
    recent_burn_HiSev_path = saveto_path+"recent_HiSev_fire3000_"+str_year+".tif"



    # POST-MODSEV FIRE SALVAGE - 2500-2600
    recent_burn_path = base_folder+"ANALYSIS/"+step3_folder+"/multi_year_fire/fire_modsev_"+str(year-fire_longevity)+"to"+str(year)+"_final.tif"
    post_ModSev_fire_salvage = Times(Raster(recent_burn_path)*Raster(salvage_path),2500)
    post_ModSev_fire_salvage.save(saveto_path+"postModSev_fire_salvage2500s_"+str_year+".tif")
    post_ModSev_fire_salvage_path = saveto_path+"postModSev_fire_salvage2500s_"+str_year+".tif"
    
    # POST-MODSEV FIRE TREATMENT - 2300-2400
    post_ModSev_fire_treat = Times(Raster(recent_burn_path)*Raster(treat1s_path),2300)
    post_ModSev_fire_treat.save(saveto_path+"postModSev_fire_treat2300s_"+str_year+".tif")
    post_ModSev_fire_treat_path = saveto_path+"postModSev_fire_treat2300s_"+str_year+".tif"
    
    # RECENTLY BURNED MOD SEV - 2000 
    recent_burn_ModSev_path = base_folder+"ANALYSIS/"+step3_folder+"/multi_year_fire/fire_modsev_"+str(year-fire_longevity)+"to"+str(year)+"_final.tif"
    recent_burn_ModSev = Times(recent_burn_ModSev_path,2000)
    recent_burn_ModSev.save(saveto_path+"recent_ModSev_fire2000_"+str_year+".tif")
    recent_burn_ModSev_path = saveto_path+"recent_ModSev_fire2000_"+str_year+".tif"
    
    
    
    # POST-LOWSEV FIRE SALVAGE - 1500-1600
    recent_burn_path = base_folder+"ANALYSIS/"+step3_folder+"/multi_year_fire/fire_lowsev_"+str(year-fire_longevity)+"to"+str(year)+"_final.tif"
    post_LowSev_fire_salvage = Times(Raster(recent_burn_path)*Raster(salvage_path),1500)
    post_LowSev_fire_salvage.save(saveto_path+"postLowSev_fire_salvage1500s_"+str_year+".tif")
    post_LowSev_fire_salvage_path = saveto_path+"postLowSev_fire_salvage1500s_"+str_year+".tif"
    
    # POST-LOWSEV FIRE TREATMENT - 1300-1400
    post_LowSev_fire_treat = Times(Raster(recent_burn_path)*Raster(treat1s_path),1300)
    post_LowSev_fire_treat.save(saveto_path+"postLowSev_fire_treat1300s_"+str_year+".tif")
    post_LowSev_fire_treat_path = saveto_path+"postLowSev_fire_treat1300s_"+str_year+".tif"
    
    # RECENTLY BURNED LOW SEV - 1000 
    recent_burn_LowSev_path = base_folder+"ANALYSIS/"+step3_folder+"/multi_year_fire/fire_lowsev_"+str(year-fire_longevity)+"to"+str(year)+"_final.tif"
    recent_burn_LowSev = Times(recent_burn_LowSev_path,1000)
    recent_burn_LowSev.save(saveto_path+"recent_LowSev_fire1000_"+str_year+".tif")
    recent_burn_LowSev_path = saveto_path+"recent_LowSev_fire1000_"+str_year+".tif"


    # NON-USFS - 999
    non_usfs_path = base_folder+"ANALYSIS/"+step4_folder+"/non_usfs_final.tif"
    non_usfs = Times(non_usfs_path,999)
    non_usfs.save(saveto_path+"non_usfs999_"+str_year+".tif")
    non_usfs_path = saveto_path+"non_usfs999_"+str_year+".tif"
    
    # NO FIRE SALVAGE - 500-600
    if year >= MMI_min_year:
        nofire_salvage = Times(Raster(salvage_path),500)+MMI_rast
    else:
        nofire_salvage = Times(Raster(salvage_path),500)
    nofire_salvage.save(saveto_path+"nofire_salvage500s_"+str_year+".tif")
    nofire_salvage_path = saveto_path+"nofire_salvage500s_"+str_year+".tif"
    
    # TREATMENTS - 300-400
    if year >= MMI_min_year:
        treatmentsx300 = Times(treat1s_path,300)+MMI_rast
    else:
        treatmentsx300 = Times(treat1s_path,300)
    treatmentsx300.save(saveto_path+"treats300s_"+str_year+".tif")
    treatments_path = saveto_path+"treats300s_"+str_year+".tif"
    
    # DROUGHT - 100-200
    drought_path = base_folder+"ANALYSIS/"+step5_folder+"/"+str_year+"/MMI_"+str(year)+"_0s_nofireUSFS_drought10.tif"
    
    print("mosaicing rasters...")
    if year >= MMI_min_year:
        input_rasters_str = hiSev_path+";"+modSev_path+";"+lowSev_path+";"+post_HiSev_fire_salvage_path+";"+post_HiSev_fire_treat_path+";"+recent_burn_HiSev_path+";"+post_ModSev_fire_salvage_path+";"+post_ModSev_fire_treat_path+";"+recent_burn_ModSev_path+";"+post_LowSev_fire_salvage_path+";"+post_LowSev_fire_treat_path+";"+recent_burn_LowSev_path+";"+non_usfs_path+";"+nofire_salvage_path+";"+treatments_path+";"+drought_path # NEW2
    else:
        input_rasters_str = hiSev_path+";"+modSev_path+";"+lowSev_path+";"+post_HiSev_fire_salvage_path+";"+post_HiSev_fire_treat_path+";"+recent_burn_HiSev_path+";"+post_ModSev_fire_salvage_path+";"+post_ModSev_fire_treat_path+";"+recent_burn_ModSev_path+";"+post_LowSev_fire_salvage_path+";"+post_LowSev_fire_treat_path+";"+recent_burn_LowSev_path+";"+non_usfs_path+";"+nofire_salvage_path+";"+treatments_path # NEW2
        # mosaic rasters - make another copy in the "disturbance" folder so it's easy to find later
        arcpy.management.MosaicToNewRaster(
            input_rasters=input_rasters_str,
            output_location=saveto_path,
            raster_dataset_name_with_extension="disturbance_"+str_year+".tif",
            coordinate_system_for_the_raster=coordinate_system, pixel_type="16_BIT_UNSIGNED", cellsize=None, number_of_bands=1, mosaic_method="MAXIMUM", mosaic_colormap_mode="FIRST")
        # clip to USFS only 
        print("clipping to USFS only")
        usfs_path = base_folder+"ANALYSIS/"+step4_folder+"/usfs_final_OsNull.tif"
        disturbance_usfs = Times(usfs_path,saveto_path+"disturbance_"+str_year+".tif")
        disturbance_usfs.save(saveto_path+"disturbance_USFSonly_"+str_year+"_buff.tif")
        # clip to unbuffered study area
        print("clipping to unbuffered study area")
        disturbance_final = Times(saveto_path+"disturbance_USFSonly_"+str_year+"_buff.tif",final_disturbance+"study_area_rast_nobuff.tif")
        disturbance_final.save(final_disturbance+"disturbance_USFSonly_"+str_year+"_nobuff.tif") 

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
