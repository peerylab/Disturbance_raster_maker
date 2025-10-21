# Anu Kramer - hakramer@wisc.edu
# Updated 6-9-2025

# PURPOSE: Confirm study area projected in WGS 84, dissolve into a single polygon, and create a 10 km buffered study area to calculate the disturbance layers within
# SPEED: < 1 min
#
# TYPE THE FOLLOWING INTO CMD:
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 1_prep_study_area.py

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
study_area_path = master_variables.study_area_path_master
coordinate_system = master_variables.coordinate_system_master
geographic_transform = master_variables.geographic_transform_master
step1_folder = master_variables.step1_master
print(base_folder)
###############################################################
############ EVERYTHING BELOW SHOULD BE GOOD TO GO ############
###############################################################
# make folders if they don't exist
# if the folder doesn't exist, make it
saveTo=base_folder+"ANALYSIS/"+step1_folder+"/"
os.makedirs(saveTo, exist_ok=True)
print("processing started...")

# convert study area to WGS
arcpy.management.Project(
    in_dataset=study_area_path,
    out_dataset=saveTo+"study_area_WGS.shp",
    out_coor_system=coordinate_system,
    transform_method=None,
    in_coor_system='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]',
    preserve_shape="NO_PRESERVE_SHAPE",
    max_deviation=None,
    vertical="NO_VERTICAL")

study_area_path=saveTo+"study_area_WGS.shp"
    
# add "ones" col
arcpy.management.AddField(study_area_path,"ones","LONG")
arcpy.management.CalculateField(study_area_path,"ones",1,"PYTHON3")

# dissolve by ones
arcpy.management.Dissolve(study_area_path, saveTo+"study_area_dissolve.shp", "ones", "", "MULTI_PART", "DISSOLVE_LINES")

# buffer by 10 km for final study area
arcpy.analysis.Buffer(saveTo+"study_area_dissolve.shp", saveTo+"study_area_dissolve_10km.shp", "10 Kilometers")

print("DONE!")
