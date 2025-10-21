# Anu Kramer - hakramer@wisc.edu
# Updated 6-9-2025

# PURPOSE: project and reclassify MMI tiles
#               o	project each MMI tile to target coord system
#               o	mosaic all MMI into annual MMI layers
#               o	study_area -> raster, maintaining alignment with MMI (0s and 1s; study_area_rast.tif)
#               o	reclass MMI 0-10 -> 0; 101-200-> 0; NODATA -> 0 (MMI_yyyy0s.tif)
#               o	MMI_ yyyy0s.tif * study_area_rast.tif (MMI_yyyy0s_study_area.tif)

# SPEED: 5 min - Be sure to run the MMI years first, then run any pre-MMI years
#
# TYPE THE FOLLOWING INTO CMD:
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 2_prep_MMI.py 2002
#       ...
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 2_prep_MMI.py 2023
#       ... after run above, run below ...
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 2_prep_MMI.py 1980
#       ...
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 2_prep_MMI.py 2001

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
tiles = master_variables.tiles_master
snap_tile = master_variables.snap_path_master
coordinate_system = master_variables.coordinate_system_master
geographic_transform = master_variables.geographic_transform_master
step1_folder = master_variables.step1_master
step2_folder = master_variables.step2_master

study_area_path = base_folder+"ANALYSIS/"+step1_folder+"/"+"study_area_dissolve_10km.shp"
###############################################################
############ EVERYTHING BELOW SHOULD BE GOOD TO GO ############
###############################################################
# make folders if they don't exist
# if the folder doesn't exist, make it
saveTo=base_folder+"ANALYSIS/"+step2_folder+"/"+str_year+"/"
os.makedirs(saveTo, exist_ok=True)

# copy over study_area
arcpy.management.CopyFeatures(study_area_path, saveTo+"study_area_dissolve_10km.shp")
study_area_path=saveTo+"study_area_dissolve_10km.shp"

# project MMI tiles (if there's MMI for that year)
if year >= master_variables.MMI_min_year_master:
    for tile in tiles:
        print(tile)
        if tile == tiles[0]:
            input_rasters_string = saveTo+tile+"_"+str_year+"_WGS_reclass.tif"
        else:
            input_rasters_string = input_rasters_string + ";" + saveTo+tile+"_"+str_year+"_WGS_reclass.tif"
        file = "mmi_"+tile+"_"+str_year+".bsq"
        arcpy.management.ProjectRaster(
            in_raster=MMI_folder+tile+"/"+tile+"_Yearly/mmi/"+file,
            out_raster=saveTo+tile+"_"+str_year+"_WGS.tif",
            out_coor_system=coordinate_system,
            resampling_type="NEAREST",
            geographic_transform=None,
            Registration_Point=None,
            in_coor_system='PROJCS["WGS_1984_UTM_Zone_10N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-123.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]',
            vertical="NO_VERTICAL")
        out_raster = arcpy.sa.Reclassify(
            in_raster=saveTo+tile+"_"+str_year+"_WGS.tif",
            reclass_field="Value", remap="101 150 150; NODATA 150",
            missing_values="DATA")
        out_raster.save(saveTo+tile+"_"+str_year+"_WGS_reclass.tif")
        
    # combine MMI tiles into a single layer
    print("building mosaic")
    MMI_raster_path = saveTo+snap_tile+"_"+str_year+"_WGS.tif"
    with arcpy.EnvManager(snapRaster=MMI_raster_path):
        arcpy.management.MosaicToNewRaster(
            input_rasters=input_rasters_string,
            output_location=saveTo,
            raster_dataset_name_with_extension="MMI_mosaic_"+str_year+"_WGS.tif",
            coordinate_system_for_the_raster=coordinate_system, pixel_type="8_BIT_UNSIGNED", cellsize=None, number_of_bands=1, mosaic_method="MAXIMUM", mosaic_colormap_mode="FIRST")
    
    print("making study area raster")
    with arcpy.EnvManager(snapRaster=MMI_raster_path):  
        arcpy.conversion.PolygonToRaster(
            in_features=study_area_path,
            value_field="ones",
            out_rasterdataset=saveTo+"study_area_rast.tif",
            cell_assignment="CELL_CENTER",
            priority_field="NONE",
            cellsize=MMI_raster_path,
            build_rat="BUILD")     
    
    print("clipping to study area")
    MMI_study_area = Times(saveTo+"MMI_mosaic_"+str_year+"_WGS.tif",saveTo+"study_area_rast.tif")
    MMI_study_area.save(saveTo+"MMI_150s_"+str_year+"_study_area.tif")
else:
    print("making study area raster with 2010")
    MMI_raster_path = base_folder+"ANALYSIS/"+step2_folder+"/2010/"+snap_tile+"_2010_WGS.tif"
    with arcpy.EnvManager(snapRaster=MMI_raster_path):  
        arcpy.conversion.PolygonToRaster(
            in_features=study_area_path,
            value_field="ones",
            out_rasterdataset=saveTo+"study_area_rast.tif",
            cell_assignment="CELL_CENTER",
            priority_field="NONE",
            cellsize=MMI_raster_path,
            build_rat="BUILD")

print("DONE!")
