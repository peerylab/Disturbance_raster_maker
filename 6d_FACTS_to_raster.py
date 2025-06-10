# Anu Kramer
# 11-16-2024


# PURPOSE: use projected FACTS polygons to convert to rasters per year, using YrFINAL, and summarize
#               note that FACTS treatments should be temporally buffered for 2 years before to 1 year after (e.g. if YrFINAL=2015, then buffer it out to 2013-2016)
#               so if making an annual raster for FACTS in 2013, include YrFINAL from year-1 to +2 (e.g. 2012-2015)
#               essentially prep FACTS rasters to combine with MMI to reclass into whether a given pixel was FACTS&MMI, FACTS only, MMI only, or neither
# SPEED: 5 min
#
# TYPE THE FOLLOWING INTO CMD:
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 6d_FACTS_to_raster.py 2001
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 6d_FACTS_to_raster.py 1984 ...CAN GO BACK AS FAR AS YOU WANT! ...DO UNTIL 1 YEARS BEFORE WHAT YOU ULTIMATELY WANT
#       ...
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 6d_FACTS_to_raster.py 2024 ...DO UNTIL 2 YEARS PAST WHAT YOU ULTIMATELY WANT

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
MMI_folder = functions.MMI_folder_master
snap_tile = functions.snap_path_master
step1_folder = functions.step1_master
step2_folder = functions.step2_master
step4_folder = functions.step4_master
step6_folder = functions.step6_master

###############################################################
############ EVERYTHING BELOW SHOULD BE GOOD TO GO ############
###############################################################
FACTS_path = base_folder+"ANALYSIS/"+step6_folder+"/FACTS_FINAL.shp"
MMI_raster_path = base_folder+"ANALYSIS/"+step2_folder+"/2010/"+snap_tile+"_2010_WGS.tif"

# make folders if they don't exist
saveTo=base_folder+"ANALYSIS/"+step6_folder+"/"+str_year+"/"
os.makedirs(saveTo, exist_ok=True)
print("prepping FACTS...")
#################
##### FACTS #####
#################
# use projected FACTS polygons to convert to rasters per year, using either year_compl or year_composite, and summarize at different time envelopes
# essentially prep FACTS rasters to combine with MMI to reclass into whether a given pixel was FACTS&MMI, FACTS only, MMI only, or neither

#FACTS_path has been projected, with ownership adjusted, year variants calculated, and columns reduced

# copy over FACTS layer
copyTo_filepath = saveTo+"FACTS_FINAL.shp"
arcpy.management.CopyFeatures(FACTS_path, copyTo_filepath)
FACTS_path = copyTo_filepath

FACTS_new_field="YrFINAL"

# convert FACTS polygons to raster in single- and multi-year groups, clipped to tile boundaries
# loop through each year, select all facts polygons for that year, turn into raster that matches each MMI raster, and save
# make folders if they don't exist

select_FACTS = arcpy.management.SelectLayerByAttribute(
in_layer_or_view=FACTS_path,
selection_type="NEW_SELECTION",
where_clause=FACTS_new_field+" = "+str(year),
invert_where_clause=None)

print("making single-year rasters")
# convert to single-year raster
with arcpy.EnvManager(snapRaster=MMI_raster_path):
    arcpy.conversion.PolygonToRaster(
        in_features=select_FACTS,
        value_field="ones",
        out_rasterdataset=saveTo+"FACTS_"+FACTS_new_field+"_"+str(year)+".tif",
        cell_assignment="CELL_CENTER",
        priority_field="NONE",
        cellsize=MMI_raster_path,
        build_rat="BUILD")

print("DONE!")