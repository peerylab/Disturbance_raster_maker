# Anu Kramer
# 11-13-2024

# PURPOSE: prep CBI data
#               o	Project COVA fires, maintaining alignment with MMI
#               o	Reclass NODATA -> 150
#               o	Multiply by study_area_rast.tif (fire_CBI_yyyy.tif)
#               o	Reclass 0-2 -> 0; 3 -> 1; 150 -> 0 (fire_hisev_yyyy_final.tif)
#               o	Reclass 1-3 -> 1; 150 -> 1 (fire_allsev_yyyy_final.tif)
#               o	Build multi-year all severity fire history, using fire_longevity (fire_allsev_yyyytoyyyy_final.tif)
# SPEED: 30 min (75 min single year + 20 min multi-year)
#
# TYPE THE FOLLOWING INTO CMD:
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 3_prep_fires.py

import arcpy  
from arcpy import env  
from arcpy.sa import *
import sys
import os
import master

#################################################
############ ADJUST THE VALUES BELOW ############
#################################################
base_folder = master.base_folder_master
coordinate_system = master.coordinate_system_master
geographic_transform = master.geographic_transform_master
fires_path = master.fires_path_master
fire_perimeters_path = master.fire_perimeters_path_master
snap_tile = master.snap_path_master
fire_longevity = master.fire_longevity_master

#extract_by_mask_coordinates = master.extract_by_mask_coordinates_master
step2_folder = master.step2_master
step3_folder = master.step3_master
###############################################################
############ EVERYTHING BELOW SHOULD BE GOOD TO GO ############
###############################################################

####################################################
### pull in older fire perimeters from 1982-1984 ###
####################################################
print("processing older fires with FRAP...")
for year in range(1985-fire_longevity,1985):
    str_year=str(year)
    print(year)
    saveTo=base_folder+"ANALYSIS/"+step3_folder+"/"+str_year+"/"
    os.makedirs(saveTo, exist_ok=True)
    MMI_raster_path = base_folder+"ANALYSIS/"+step2_folder+"/2010/"+snap_tile+"_2010_WGS.tif"
    study_area = base_folder+"ANALYSIS/"+step2_folder+"/"+str_year+"/study_area_rast.tif"
    #project
    arcpy.management.Project(
        in_dataset=fire_perimeters_path,
        out_dataset=saveTo+"CA_FIRES_1950_2023_WGS",
        out_coor_system=coordinate_system,
        transform_method=geographic_transform,
        in_coor_system='PROJCS["NAD_1983_California_Teale_Albers",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",-4000000.0],PARAMETER["Central_Meridian",-120.0],PARAMETER["Standard_Parallel_1",34.0],PARAMETER["Standard_Parallel_2",40.5],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]',
        preserve_shape="NO_PRESERVE_SHAPE",
        max_deviation=None,
        vertical="NO_VERTICAL")
    
    # add "BIG_cons" column and assign value 200
    arcpy.management.AddField(saveTo+"CA_FIRES_1950_2023_WGS.shp","ones","LONG")
    arcpy.management.CalculateField(saveTo+"CA_FIRES_1950_2023_WGS.shp","ones",1,"PYTHON3")
    
    # convert CA_FIRES_1980_2022_WGS.shp to raster (snapped to each MMI tile)
    select_fires = arcpy.management.SelectLayerByAttribute(
        in_layer_or_view=saveTo+"CA_FIRES_1950_2023_WGS",
        selection_type="NEW_SELECTION",
        where_clause="YEAR_ = "+str_year,
        invert_where_clause=None)
    with arcpy.EnvManager(snapRaster=MMI_raster_path):
        arcpy.conversion.PolygonToRaster(
            in_features=select_fires,
            value_field="ones",
            #out_rasterdataset=saveTo+"oldfire_allsev_"+str_year+"_toRast.tif",
            out_rasterdataset=saveTo+"oldfire_allsev_"+str_year+"_final.tif",
            cell_assignment="CELL_CENTER",
            priority_field="NONE",
            build_rat="BUILD")
    # # need to run this to get cells aligned with habitat raster
    # with arcpy.EnvManager(cellSizeProjectionMethod="PRESERVE_RESOLUTION", snapRaster=snap_tile, cellSize=snap_tile):
    #     out_raster = arcpy.sa.ExtractByMask(
    #         in_raster=saveTo+"oldfire_allsev_"+str_year+"_toRast.tif",
    #         in_mask_data=snap_tile,
    #         extraction_area="INSIDE",
    #         analysis_extent=extract_by_mask_coordinates+' GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
    #     )
    #     out_raster.save(saveTo+"oldfire_allsev_"+str_year+"_final.tif")
    
    #print("clipping to study area...")
    MMI_study_area = Times(saveTo+"oldfire_allsev_"+str_year+"_final.tif",study_area)
    MMI_study_area.save(saveTo+"fire_allsev_"+str_year+"_final.tif")    


#################
### cbi fires ###
#################
print("processing CBI fires...")
for year in range(1985,2024):
    str_year=str(year)
    print(year)
    saveTo=base_folder+"ANALYSIS/"+step3_folder+"/"+str_year+"/"
    os.makedirs(saveTo, exist_ok=True)
    MMI_raster_path = base_folder+"ANALYSIS/"+step2_folder+"/2010/"+snap_tile+"_2010_WGS.tif"
    study_area = base_folder+"ANALYSIS/"+step2_folder+"/"+str_year+"/study_area_rast.tif"
    # print("projecting CBI...")
    with arcpy.EnvManager(snapRaster=MMI_raster_path):
        arcpy.management.ProjectRaster(
            in_raster=fires_path+"/cbi_cat_"+str_year+".tif",
            #out_raster=saveTo+"CBI_"+str_year+"_WGS_intermediate.tif",
            out_raster=saveTo+"CBI_"+str_year+"_WGS.tif",
            out_coor_system=coordinate_system,
            resampling_type="NEAREST",
            cell_size=None,
            geographic_transform=geographic_transform,
            Registration_Point=None,
            in_coor_system='PROJCS["NAD_1983_California_Teale_Albers",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",-4000000.0],PARAMETER["Central_Meridian",-120.0],PARAMETER["Standard_Parallel_1",34.0],PARAMETER["Standard_Parallel_2",40.5],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]',
            vertical="NO_VERTICAL")
    # # need to run this to get cells aligned with habitat raster
    # with arcpy.EnvManager(cellSizeProjectionMethod="PRESERVE_RESOLUTION", snapRaster=snap_tile, cellSize=snap_tile):
    #     out_raster = arcpy.sa.ExtractByMask(
    #         in_raster=saveTo+"CBI_"+str_year+"_WGS_intermediate.tif",
    #         in_mask_data=snap_tile,
    #         extraction_area="INSIDE",
    #         analysis_extent=extract_by_mask_coordinates+' GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
    #     )
    #     out_raster.save(saveTo+"CBI_"+str_year+"_WGS.tif")
    # reclassify NODATA -> 150
    out_raster = arcpy.sa.Reclassify(
        in_raster=saveTo+"CBI_"+str_year+"_WGS.tif",
        reclass_field="Value", remap="NODATA 150",
        missing_values="DATA")
    out_raster.save(saveTo+"cbi_cat_"+str_year+"_NODATA150.tif")
    
    # print("clipping to study area...")
    MMI_study_area = Times(saveTo+"cbi_cat_"+str_year+"_NODATA150.tif",study_area)
    MMI_study_area.save(saveTo+"cbi_cat_"+str_year+"_study_area_NODATA150.tif")
    
    # print("reclassifying...")
    # reclassify 0-2 -> 0; 3 -> 1; 150 -> 0 
    out_raster = arcpy.sa.Reclassify(
        in_raster=saveTo+"cbi_cat_"+str_year+"_study_area_NODATA150.tif",
        reclass_field="Value", remap="0 2 0;3 3 1;150 150 0",
        missing_values="DATA")
    out_raster.save(saveTo+"fire_hisev_"+str_year+"_final.tif")
    
    # reclassify 0-3 -> 1; 150 -> 0 
    out_raster = arcpy.sa.Reclassify(
        in_raster=saveTo+"cbi_cat_"+str_year+"_study_area_NODATA150.tif",
        reclass_field="Value", remap="0 3 1;150 150 0",
        missing_values="DATA")
    out_raster.save(saveTo+"fire_allsev_"+str_year+"_final.tif")


print("mosaicing multi-year fire histories")
saveTo=base_folder+"ANALYSIS/"+step3_folder+"/multi_year_fire/"
os.makedirs(saveTo, exist_ok=True)
MMI_raster_path = base_folder+"ANALYSIS/"+step2_folder+"/2010/"+snap_tile+"_2010_WGS.tif"
#for year in range(2014,2018):
for year in range(1985,2024):
    print(year)
    
    for working_year in range(year-fire_longevity,year+1):
        if working_year == (year-fire_longevity):
            input_rasters_string = base_folder+"ANALYSIS/"+step3_folder+"/"+str(working_year)+"/fire_allsev_"+str(working_year)+"_final.tif"
        else:
            input_rasters_string = input_rasters_string + ";" + base_folder+"ANALYSIS/"+step3_folder+"/"+str(working_year)+"/fire_allsev_"+str(working_year)+"_final.tif"
    with arcpy.EnvManager(snapRaster=MMI_raster_path):
        arcpy.management.MosaicToNewRaster(
            input_rasters=input_rasters_string,
            output_location=saveTo,
            raster_dataset_name_with_extension="fire_allsev_"+str(year-fire_longevity)+"to"+str(year)+"_final.tif",
            coordinate_system_for_the_raster=coordinate_system, pixel_type="8_BIT_UNSIGNED", cellsize=None, number_of_bands=1, mosaic_method="MAXIMUM", mosaic_colormap_mode="FIRST")
        
print("mosaicing multi-year high sev fire histories") # NEW
for year in range(1985+fire_longevity,2024):
    print(year)
    
    for working_year in range(year-fire_longevity,year+1):
        if working_year == (year-fire_longevity):
            input_HiSev_rasters_string = base_folder+"ANALYSIS/"+step3_folder+"/"+str(working_year)+"/fire_hisev_"+str(working_year)+"_final.tif" # NEW
        else:
            input_HiSev_rasters_string = input_HiSev_rasters_string + ";" + base_folder+"ANALYSIS/"+step3_folder+"/"+str(working_year)+"/fire_hisev_"+str(working_year)+"_final.tif" # NEW
    with arcpy.EnvManager(snapRaster=MMI_raster_path):
        arcpy.management.MosaicToNewRaster(
            input_rasters=input_HiSev_rasters_string,
            output_location=saveTo,
            raster_dataset_name_with_extension="fire_hisev_"+str(year-fire_longevity)+"to"+str(year)+"_final.tif",
            coordinate_system_for_the_raster=coordinate_system, pixel_type="8_BIT_UNSIGNED", cellsize=None, number_of_bands=1, mosaic_method="MAXIMUM", mosaic_colormap_mode="FIRST")


print("DONE!")