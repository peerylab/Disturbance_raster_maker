# Anu Kramer - hakramer@wisc.edu
# Updated 6-9-2025


# PURPOSE: 
#               o	Project federal ownership
#               o	Convert to raster (of 0s and 1s), maintaining alignment with MMI
#               o	Multiply by study_area_rast.tif (usfs_final.tif, non_usfs_final.tif, usfs_final_OsNull, federal_final.tif, non_federal_final.tif)

# SPEED: 3 min
#
# TYPE THE FOLLOWING INTO CMD:
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 4_prep_ownership.py

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
MMI_folder = master_variables.MMI_folder_master
tiles = master_variables.tiles_master
snap_tile = master_variables.snap_path_master
coordinate_system = master_variables.coordinate_system_master
geographic_transform = master_variables.geographic_transform_master
step1_folder = master_variables.step1_master
step2_folder = master_variables.step2_master
step4_folder = master_variables.step4_master

###############################################################
############ EVERYTHING BELOW SHOULD BE GOOD TO GO ############
###############################################################
MMI_raster_path = base_folder+"ANALYSIS/"+step2_folder+"/2010/"+snap_tile+"_2010_WGS.tif"
# if the folder doesn't exist, make it
saveTo=base_folder+"ANALYSIS/"+step4_folder+"/"
os.makedirs(saveTo, exist_ok=True)
study_area = base_folder+"ANALYSIS/"+step2_folder+"/2010/study_area_rast.tif"
study_area_shp = base_folder+"ANALYSIS/"+step1_folder+"/study_area_dissolve_10km.shp"

print("projecting ownership...")
# project ownership
arcpy.management.Project(
    in_dataset=base_folder+"DATA/USA Federal Lands_2024.shp",
    out_dataset=saveTo+"Federal_ownership_WGS.shp",
    out_coor_system=coordinate_system,
    transform_method=None,
    in_coor_system='PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],UNIT["Meter",1.0]]',
    preserve_shape="NO_PRESERVE_SHAPE",
    max_deviation=None,
    vertical="NO_VERTICAL")

# select USA Federal Lands_2024.shp that overlap with study_area.shp
select_study_area_ownership = arcpy.management.SelectLayerByLocation(
    in_layer=saveTo+"Federal_ownership_WGS.shp",
    overlap_type="INTERSECT",
    select_features=study_area_shp,
    search_distance=None,
    selection_type="NEW_SELECTION",
    invert_spatial_relationship="NOT_INVERT")

arcpy.management.CopyFeatures(select_study_area_ownership,saveTo+"Federal_ownership_WGS_study_area.shp")

# add ones col and populate with 200s
arcpy.management.AddField(saveTo+"Federal_ownership_WGS_study_area.shp","ones","LONG")
arcpy.management.CalculateField(saveTo+"Federal_ownership_WGS_study_area.shp","ones",1,"PYTHON3")

# select USFS ownership from USA Federal Lands_2024.shp
select_USFS_ownership = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=saveTo+"Federal_ownership_WGS_study_area.shp",
    selection_type="NEW_SELECTION",
    where_clause="Agency = 'Forest Service'",
    invert_where_clause=None)

print("ownership to raster...")
with arcpy.EnvManager(snapRaster=MMI_raster_path):
    # usfs
    arcpy.conversion.PolygonToRaster(
        in_features=select_USFS_ownership,
        value_field="ones",
        out_rasterdataset=saveTo+"USFS_ownership_WGS.tif",
        cell_assignment="CELL_CENTER",
        priority_field="NONE",
        cellsize=MMI_raster_path,
        build_rat="BUILD")
    out_raster = arcpy.sa.Reclassify(
        in_raster=saveTo+"USFS_ownership_WGS.tif",
        reclass_field="Value", remap="NODATA 0",
        missing_values="DATA")
    out_raster.save(saveTo+"USFS_ownership_WGS_0s.tif")
    # clip to study area
    ownership_study_area = Times(saveTo+"USFS_ownership_WGS_0s.tif",study_area)
    ownership_study_area.save(saveTo+"usfs_final.tif")
    out_raster = arcpy.sa.Reclassify(
        in_raster=saveTo+"usfs_final.tif",
        reclass_field="Value", remap="0 0 1;1 1 0",
        missing_values="DATA")
    out_raster.save(saveTo+"non_usfs_final.tif")
    out_raster = arcpy.sa.Reclassify(
        in_raster=saveTo+"usfs_final.tif",
        reclass_field="Value", remap="0 0 NODATA",
        missing_values="DATA")
    out_raster.save(saveTo+"usfs_final_OsNull.tif")
    
    # federal
    arcpy.conversion.PolygonToRaster(
        in_features=saveTo+"Federal_ownership_WGS_study_area.shp",
        value_field="ones",
        out_rasterdataset=saveTo+"federal_ownership_WGS_rast.tif",
        cell_assignment="CELL_CENTER",
        priority_field="NONE",
        cellsize=MMI_raster_path,
        build_rat="BUILD")
    out_raster = arcpy.sa.Reclassify(
        in_raster=saveTo+"federal_ownership_WGS_rast.tif",
        reclass_field="Value", remap="NODATA 0",
        missing_values="DATA")
    out_raster.save(saveTo+"federal_ownership_WGS_0s.tif")
    # clip to study area
    ownership_study_area = Times(saveTo+"federal_ownership_WGS_0s.tif",study_area)
    ownership_study_area.save(saveTo+"federal_final.tif")
    out_raster = arcpy.sa.Reclassify(
        in_raster=saveTo+"federal_final.tif",
        reclass_field="Value", remap="0 0 1;1 1 0",
        missing_values="DATA")
    out_raster.save(saveTo+"non_federal_final.tif")

print("DONE!")
