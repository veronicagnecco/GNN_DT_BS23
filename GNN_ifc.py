import os
import sys
import clr
#clr.AddReference('ProtoGeometry') #module not found
import System
import ifcopenshell
from Autodesk.DesignScript.Geometry import *
dirAppLoc = System.Environment.GetFolderPath(System.Environment.SpecialFolder.LocalApplicationData)
sys.path.append(dirAppLoc + r'\python-3.8.3-embed-amd64\Lib\site-packages')
import pandas as pd
from math import *

#Gestire con Gitpython: https://gitpython.readthedocs.io/en/stable/intro.html


os.chdir("C:/Users/Martins Gnecco/Testroom Lab Dropbox/Veronica Martins Gnecco/BS2023/01. Data Acquisition Files")

#upload ifc files and information
#https://thinkmoult.com/using-ifcopenshell-parse-ifc-files-python.html
ifc_file = ifcopenshell.open('NextRoomSensors.ifc')
print(ifc_file)

wall = ifc_file.by_type('IfcWall')[1]
print(wall.is_a('IfcWall'))

'''
#environmental sensors data

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

dirAppLoc = System.Environment.GetFolderPath(System.Environment.SpecialFolder.LocalApplicationData)
sys.path.append(dirAppLoc + r'\python-3.8.3-embed-amd64\Lib\site-packages')
import pandas as pd
from math import *

# df =pd.read_csv("enth_tabular_merged.csv")

subjects = ["S05", "S06", "S07", "S08"]

for s in range(len(subjects)):
    subject = subjects[s]
    globals()["df_" + str(subject)] = pd.read_csv(
        "C:/Dropbox (Testroom Lab)/BIM-DigitalTwin/06. Experimental Data/" + subject + "_data_phys_env_total.csv")  # creatingdataframes
    globals()["Timestamps_" + str(subject)] = list(
        globals()["df_" + str(subject)]['Timestamp'])  # collecting timestamps

    if s == 0:
        all_headers = list(globals()["df_" + str(subject)].columns)
        headers = all_headers[1:48]
    for header in headers:
        globals()[header + "_" + str(subject)] = list(
            globals()["df_" + str(subject)][header])  # collecting columnsvalues

control0 = []
control = []
control1 = []

for subject in subjects:
    for i in range(len(globals()["Timestamps_" + str(subject)])):

        for header in headers:
            timestamp = globals()["Timestamps_" + str(subject)][i]
            sens_value = globals()[header + "_" + str(subject)][i]
            control0.append(
                subject + "_" + str(timestamp).replace(" ", "_").replace("-", "_").replace(":", "_").replace("/",
                                                                                                             "_") + "_" + header + ":")
            control1.append(sens_value)

data = []

for c in control0:
    control.append(c.replace("/", "_"))

for sensor in headers:
    data_rough0 = ""
    for i in range(len(control)):
        prop = control[i]
        value = str(control1[i])
        if sensor + ":" in prop:
            data_rough0 += f" {prop} '{value}',"

    data.append(data_rough0[:-1])

keys_list = headers
values_list = data
zip_iterator = zip(keys_list, values_list)
ass_sens_data = dict(zip_iterator)

OUT = Timestamps_S05, Timestamps_S06, Timestamps_S07, Timestamps_S08, headers, control, control1, ass_sens_data
'''