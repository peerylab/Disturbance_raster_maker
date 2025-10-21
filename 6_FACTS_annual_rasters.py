# Anu Kramer - hakramer@wisc.edu
# Updated 6-9-2025

# PURPOSE: prepares FACTS data by adding and populating YR_FINAL col, which can be used to date FACTS polygons from here onward
#               o	Project all FACTS
#               o	Select FACTS: (FACTS_study_area.shp)
#                      	intersect with study_area.shp
#                      	appropriate activity codes 
#               o	Calc yr_compl, yr_award, award_yr
#               o	Make YR_FINAL and assign where can


# SPEED: 66 min
#
# TYPE THE FOLLOWING INTO CMD: 
#       start c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat 6_FACTS_annual_rasters.py

import arcpy  
from arcpy import env  
from arcpy.sa import *
import os
import master_variables

#################################################
############ ADJUST THE VALUES BELOW ############
#################################################
base_folder = master_variables.base_folder_master
MMI_folder = master_variables.MMI_folder_master
tiles = master_variables.tiles_master
coordinate_system = master_variables.coordinate_system_master
geographic_transform = master_variables.geographic_transform_master
FACTS_CommonAttribute_reduceCols = master_variables.FACTS_CommonAttribute_reduceCols_master
step1_folder = master_variables.step1_master
step5_folder = master_variables.step5_master
step6_folder = master_variables.step6_master

###############################################################
############ EVERYTHING BELOW SHOULD BE GOOD TO GO ############
###############################################################
# make folders if they don't exist
# if the folder doesn't exist, make it
saveTo=base_folder+"ANALYSIS/"+step6_folder+"/"
os.makedirs(saveTo, exist_ok=True)
print("prepping FACTS...")

#PREP DATA
#select FACTS that overlap study area (makes intersect faster if do it this way...)
FACTS_study_area_overlap = arcpy.management.SelectLayerByLocation(FACTS_CommonAttribute_reduceCols, "WITHIN_A_DISTANCE", base_folder+"ANALYSIS/"+step1_folder+"/study_area_dissolve_10km.shp", '10 Kilometers')
arcpy.management.CopyFeatures(FACTS_study_area_overlap, saveTo+"Actv_CommonAttribute_PL_CA_reducedCols_STUDY_AREA10km.shp")

#create orig_FID column that links to old data FID
arcpy.management.CalculateField(
    in_table=saveTo+"Actv_CommonAttribute_PL_CA_reducedCols_STUDY_AREA10km.shp",
    field="orig_FID",
    expression="!FID!",
    expression_type="PYTHON3",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS")

#copy data to new folder (and then delete a bunch of cols)
FACTS_filepath = saveTo+"Actv_CommonAttribute_PL_CA_reducedCols_minCols.shp"
arcpy.management.CopyFeatures(saveTo+"Actv_CommonAttribute_PL_CA_reducedCols_STUDY_AREA10km.shp", FACTS_filepath)

#delete all but a few columns
arcpy.management.DeleteField(FACTS_filepath, ["FACTS_ID", "ACTIVITY_C", "ACTIVITY", "DATE_AWARD", "DATE_COMPL", "AWARD_DATE", "OWNERSHIP", "STATE_ABBR", "orig_FID"], "KEEP_FIELDS")

#add fuel_mngmt code
FACTS_fuel_mngmt = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=FACTS_filepath,
    selection_type="NEW_SELECTION",
    where_clause="ACTIVITY_C = '1102' Or ACTIVITY_C = '1111' Or ACTIVITY_C = '1112' Or ACTIVITY_C = '1113' Or ACTIVITY_C = '1120' Or ACTIVITY_C = '1130' Or ACTIVITY_C = '1136' Or ACTIVITY_C = '1139' Or ACTIVITY_C = '1150' Or ACTIVITY_C = '1152' Or ACTIVITY_C = '1153' Or ACTIVITY_C = '1154' Or ACTIVITY_C = '1160' Or ACTIVITY_C = '1180' Or ACTIVITY_C = '2000' Or ACTIVITY_C = '2341' Or ACTIVITY_C = '2360' Or ACTIVITY_C = '2370' Or ACTIVITY_C = '2510' Or ACTIVITY_C = '2530' Or ACTIVITY_C = '2540' Or ACTIVITY_C = '2560' Or ACTIVITY_C = '3132' Or ACTIVITY_C = '3340' Or ACTIVITY_C = '3370' Or ACTIVITY_C = '3380' Or ACTIVITY_C = '4101' Or ACTIVITY_C = '4102' Or ACTIVITY_C = '4111' Or ACTIVITY_C = '4113' Or ACTIVITY_C = '4115' Or ACTIVITY_C = '4117' Or ACTIVITY_C = '4121' Or ACTIVITY_C = '4122' Or ACTIVITY_C = '4131' Or ACTIVITY_C = '4132' Or ACTIVITY_C = '4141' Or ACTIVITY_C = '4142' Or ACTIVITY_C = '4143' Or ACTIVITY_C = '4145' Or ACTIVITY_C = '4146' Or ACTIVITY_C = '4148' Or ACTIVITY_C = '4151' Or ACTIVITY_C = '4152' Or ACTIVITY_C = '4162' Or ACTIVITY_C = '4175' Or ACTIVITY_C = '4177' Or ACTIVITY_C = '4183' Or ACTIVITY_C = '4192' Or ACTIVITY_C = '4193' Or ACTIVITY_C = '4194' Or ACTIVITY_C = '4196' Or ACTIVITY_C = '4210' Or ACTIVITY_C = '4211' Or ACTIVITY_C = '4220' Or ACTIVITY_C = '4231' Or ACTIVITY_C = '4232' Or ACTIVITY_C = '4241' Or ACTIVITY_C = '4242' Or ACTIVITY_C = '4270' Or ACTIVITY_C = '4455' Or ACTIVITY_C = '4471' Or ACTIVITY_C = '4472' Or ACTIVITY_C = '4473' Or ACTIVITY_C = '4474' Or ACTIVITY_C = '4475' Or ACTIVITY_C = '4481' Or ACTIVITY_C = '4482' Or ACTIVITY_C = '4483' Or ACTIVITY_C = '4484' Or ACTIVITY_C = '4485' Or ACTIVITY_C = '4491' Or ACTIVITY_C = '4492' Or ACTIVITY_C = '4493' Or ACTIVITY_C = '4494' Or ACTIVITY_C = '4495' Or ACTIVITY_C = '4511' Or ACTIVITY_C = '4521' Or ACTIVITY_C = '4530' Or ACTIVITY_C = '4541' Or ACTIVITY_C = '6101' Or ACTIVITY_C = '6103' Or ACTIVITY_C = '6104' Or ACTIVITY_C = '6105' Or ACTIVITY_C = '6106' Or ACTIVITY_C = '6107' Or ACTIVITY_C = '6133' Or ACTIVITY_C = '6584' Or ACTIVITY_C = '6684' Or ACTIVITY_C = '7015' Or ACTIVITY_C = '7050' Or ACTIVITY_C = '7065' Or ACTIVITY_C = '7067' Or ACTIVITY_C = '9008' Or ACTIVITY_C = '9400'",    
    invert_where_clause=None)

arcpy.management.CalculateField(
    in_table=FACTS_fuel_mngmt,
    field="FUEL_MNGMT",
    expression="1",
    expression_type="ARCADE",
    code_block="",
    field_type="LONG",
    enforce_domains="NO_ENFORCE_DOMAINS")

#add salvage code
FACTS_fuel_mngmt = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=FACTS_filepath,
    selection_type="NEW_SELECTION",
    where_clause="ACTIVITY_C = '3132' Or ACTIVITY_C = '4231' Or ACTIVITY_C = '4232'",    
    invert_where_clause=None)

arcpy.management.CalculateField(
    in_table=FACTS_fuel_mngmt,
    field="SALVAGE",
    expression="1",
    expression_type="ARCADE",
    code_block="",
    field_type="LONG",
    enforce_domains="NO_ENFORCE_DOMAINS")

#add fire code
FACTS_fires = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=FACTS_filepath,
    selection_type="NEW_SELECTION",
    where_clause="ACTIVITY_C = '1115' Or ACTIVITY_C = '1116' Or ACTIVITY_C = '1117' Or ACTIVITY_C = '1118' Or ACTIVITY_C = '1119'",
    invert_where_clause=None)

arcpy.management.CalculateField(
    in_table=FACTS_fires,
    field="fire",
    expression="1",
    expression_type="ARCADE",
    code_block="",
    field_type="LONG",
    enforce_domains="NO_ENFORCE_DOMAINS")

print("projecting FACTS...")
#project - 2.5 min
arcpy.management.Project(
    in_dataset=FACTS_filepath,
    out_dataset=saveTo+"Actv_CommonAttribute_PL_CA_reducedCols_minCols_WGS.shp",
    out_coor_system=coordinate_system,
    transform_method=geographic_transform,
    in_coor_system='GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]',
    preserve_shape="NO_PRESERVE_SHAPE",
    max_deviation=None,
    vertical="NO_VERTICAL")

#select non-wildfire polygons
FACTS_nofires = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=saveTo+"Actv_CommonAttribute_PL_CA_reducedCols_minCols_WGS.shp",
    selection_type="NEW_SELECTION",
    where_clause="fire = 0",
    invert_where_clause=None)

final_FACTS_filepath = saveTo+"Actv_CommonAttribute_PL_CA_reducedCols_minCols_WGS.shp"

# Add fields for YR_AWARD, AWARD_YR, YR_COMPL, and YrComposit and populate (28- ## min) - REPEATE FOR EACH:
def add_and_calc_field (shapefile_path, field_name, field_expression):
    # assign the field 0 in case it already has data
    arcpy.management.CalculateField(
        in_table=shapefile_path,
        field=field_name,
        expression=0,
        expression_type="ARCADE",
        code_block="",
        field_type="LONG",
        enforce_domains="NO_ENFORCE_DOMAINS")
    # now that you know the field is clean, assign the actual value 
    arcpy.management.CalculateField(
        in_table=shapefile_path,
        field=field_name,
        expression=field_expression,
        expression_type="ARCADE",
        code_block="",
        field_type="LONG",
        enforce_domains="NO_ENFORCE_DOMAINS")

print("adding YR_AWARD")
add_and_calc_field(final_FACTS_filepath, "YR_AWARD", "Year($feature.DATE_AWARD)")
print("adding AWARD_YR")
add_and_calc_field(final_FACTS_filepath, "AWARD_YR", "Year($feature.AWARD_DATE)")
print("adding YR_COMPL")
add_and_calc_field(final_FACTS_filepath, "YR_COMPL", "Year($feature.DATE_COMPL)")
add_and_calc_field(final_FACTS_filepath, "YrComposit", "Year($feature.DATE_COMPL)")

# select where FACTS_YR = null and assign max(YR_AWARD, AWARD_YR)
FACTS_polys = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=final_FACTS_filepath,
    selection_type="NEW_SELECTION",
    where_clause="YrComposit = 0",
    invert_where_clause=None)

arcpy.management.CalculateField(
    in_table=FACTS_polys,
    field="YrComposit",
    expression="Max($feature.YR_AWARD, $feature.AWARD_YR)",
    expression_type="ARCADE",
    code_block="",
    field_type="LONG",
    enforce_domains="NO_ENFORCE_DOMAINS")

# add "BIG_cons" column and assign value 200
arcpy.management.AddField(final_FACTS_filepath,"ones","LONG")
arcpy.management.CalculateField(final_FACTS_filepath,"ones",1,"PYTHON3")
salvage_polys = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=final_FACTS_filepath,
    selection_type="NEW_SELECTION",
    where_clause="SALVAGE = 1",
    invert_where_clause=None)
arcpy.management.CalculateField(salvage_polys,"ones",2,"PYTHON3")

# erase extra columns
arcpy.management.DeleteField(final_FACTS_filepath, ["DATE_COMPL", "AWARD_DATE", "Shape_Leng", "Shape_Area", "DATE_AWARD", "YR_AWARD", "AWARD_YR"])


# copy any FACTS polygons for fuels managment polygons only
fuels_management_polys = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=final_FACTS_filepath,
    selection_type="NEW_SELECTION",
    where_clause="FUEL_MNGMT = 1",
    invert_where_clause=None)

arcpy.management.CopyFeatures(fuels_management_polys, saveTo+"Actv_CommonAttribute_PL_CA_reducedCols_minCols_WGS_FUEL_MNGMT.shp")
FACTS_path = saveTo+"Actv_CommonAttribute_PL_CA_reducedCols_minCols_WGS_FUEL_MNGMT.shp"

print("calculating YrFINAL for treatments with a completion date...")
# add YrFINAL attribute and assign the year for DATE_COMPL
arcpy.management.CalculateField(
        in_table=FACTS_path,
        field="YrFINAL",
        expression=0,
        expression_type="ARCADE",
        code_block="",
        field_type="LONG",
        enforce_domains="NO_ENFORCE_DOMAINS")

# now that you know the field is clean, assign the actual value
FACTS_polys = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=FACTS_path,
    selection_type="NEW_SELECTION",
    where_clause="YR_COMPL > 1950",
    invert_where_clause=None)

arcpy.management.CalculateField(
    in_table=FACTS_polys,
    field="YrFINAL",
    expression="$feature.YR_COMPL",
    expression_type="ARCADE",
    code_block="",
    field_type="LONG",
    enforce_domains="NO_ENFORCE_DOMAINS")

print("calculating YrFINAL for treatments where completion was null...")
# use YrComposit to populate YrFINAL for older treatments where YrComplete is null
#               - if max("YR_AWARD", "AWARD_YR") <= 2013
#                       - "YrFINAL" = max("YR_AWARD", "AWARD_YR")+2
#                       - NOTE that the above makes sense because "YrFINAL" will be buffered by -2 to +1 years, and treatment effects will never begin before the award
FACTS_polys = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=FACTS_path,
    selection_type="NEW_SELECTION",
    #where_clause="YR_COMPL = 0 And YrComposit <= 2013 And YrComposit > 0",
    where_clause="YR_COMPL = 0 And YrComposit > 0",
    invert_where_clause=None)

arcpy.management.CalculateField(
    in_table=FACTS_polys,
    field="YrFINAL",
    expression="!YrComposit! + 2",
    expression_type="PYTHON3",
    code_block="",
    field_type="LONG",
    enforce_domains="NO_ENFORCE_DOMAINS")

# save
# select only FACTS polygons with a YrFINAL
FACTS_polys = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=FACTS_path,
    selection_type="NEW_SELECTION",
    where_clause="YrFINAL > 0",
    invert_where_clause=None)

arcpy.management.CopyFeatures(FACTS_polys, saveTo+"FACTS_FINAL.shp")

print("DONE!")
