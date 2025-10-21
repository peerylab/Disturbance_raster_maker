# Anu Kramer - hakramer@wisc.edu
# Updated 6-9-2025

# PURPOSE: use projected FACTS polygons to convert to rasters per year, using YrFINAL, and summarize
#               note that FACTS treatments should be temporally buffered for 2 years before to 1 year after (e.g. if YrFINAL=2015, then buffer it out to 2013-2016)
#               so if making an annual raster for FACTS in 2013, include YrFINAL from year-1 to +2 (e.g. 2012-2015)
#               essentially prep FACTS rasters to combine with MMI to reclass into whether a given pixel was FACTS&MMI, FACTS only, MMI only, or neither
# SPEED: 5 min
#
# TYPE THE FOLLOWING INTO CMD:
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 6c_FACTS_to_multi_year_raster.py 1985
#       ...
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 6c_FACTS_to_multi_year_raster.py 2022

import arcpy  
from arcpy import env  
from arcpy.sa import *
import sys
import os
import master_variables

year=sys.argv[1]
str_year=str(year)
year=int(str_year)
print(year)
#################################################
############ ADJUST THE VALUES BELOW ############
#################################################
base_folder = master_variables.base_folder_master
MMI_folder = master_variables.MMI_folder_master
coordinate_system = master_variables.coordinate_system_master
step1_folder = master_variables.step1_master
step2_folder = master_variables.step2_master
step4_folder = master_variables.step4_master
step6_folder = master_variables.step6_master

###############################################################
############ EVERYTHING BELOW SHOULD BE GOOD TO GO ############
###############################################################
FACTS_path = base_folder+"ANALYSIS/"+step6_folder+"/FACTS_FINAL.shp"
FACTS_new_field="YrFINAL"
saveTo=base_folder+"ANALYSIS/"+step6_folder+"/"+str_year+"/"

# convert FACTS polygons to raster in single- and multi-year groups, clipped to tile boundaries
# loop through each year, select all facts polygons for that year, turn into raster that matches each MMI raster, and save
# make folders if they don't exist

print("making multi-year rasters")
# merge to multi-year rasters
def make_in_raster_string (pre_year_path, mid_year_path, years):
    in_rasters_string = ""
    for year_span in years:
        if(year_span == max(years)):
            in_rasters_string += pre_year_path+str(year_span)+mid_year_path+str(year_span)+".tif"
        else:
            in_rasters_string += pre_year_path+str(year_span)+mid_year_path+str(year_span)+".tif;"
    return(in_rasters_string)

pre_year_path = base_folder+"ANALYSIS/"+step6_folder+"/"
mid_year_path = "/FACTS_"+FACTS_new_field+"_"
arcpy.management.MosaicToNewRaster(
    input_rasters=make_in_raster_string(pre_year_path, mid_year_path, range(year-1,year+3)), # corresponding to FACTS yrFINAL 1 year before to 2 years after
    output_location=saveTo,
    raster_dataset_name_with_extension="multi_year_"+FACTS_new_field+"_"+str(year)+".tif",
    coordinate_system_for_the_raster=coordinate_system, pixel_type="8_BIT_UNSIGNED", cellsize=None, number_of_bands=1, mosaic_method="MAXIMUM", mosaic_colormap_mode="FIRST")

# remove any non-usfs areas
save_final=base_folder+"ANALYSIS/"+step6_folder+"/multi_year/"
os.makedirs(save_final, exist_ok=True)
usfs_multi = Times(saveTo+"multi_year_"+FACTS_new_field+"_"+str(year)+".tif",base_folder+"ANALYSIS/"+step4_folder+"/usfs_final.tif")
usfs_multi.save(save_final+"multi_year_"+FACTS_new_field+"_"+str(year)+"_usfs.tif")

print("DONE!")
