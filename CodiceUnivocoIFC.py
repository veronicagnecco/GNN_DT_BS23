import sys
import clr
import System
import os
import pandas as pd
from math import *


###COLLECTING ELEMENTS, LOCATIONS AND REAL ID PARAMETER############################################################################################################


elements1 = #VERFIL_AllObjectsOfIFCCategoryThatInRevitAreDataDevices-FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DataDevices).WhereElementIsNotElementType().ToElements()
elements2 = #VERFIL_AllObjectsOfIFCCategoryThatInRevitAreElectricalEquipment-FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ElectricalEquipment).WhereElementIsNotElementType().ToElements()
#need to point in both casesto the instances of elements (all the objects)

lista= list(elements1)+list(elements2)
ElementsLocations= [] #VERFIL_list with all the locations of the elements (in string format)
RealSensorIDs=[] #VERFIL_list with all the RealSensorIDs of the elements (in string format)

###COLLECTING SUBJECTS' DATA############################################################################################################


subjects=["S05","S06","S07","S08"]


for s in range(len(subjects)):
    subject=subjects[s]
    globals()["df_" + str(subject)] = pd.read_csv("C:/Dropbox (Testroom Lab)/BIM-DigitalTwin/06. Experimental Data/"+subject+"_data_phys_env_total.csv")#creatingdataframes
    globals()["Timestamps_" + str(subject)]=list(globals()["df_" + str(subject)]['Timestamp'])#collecting timestamps
    
    if s == 0:
        all_headers=list(globals()["df_" + str(subject)].columns)
        headers=all_headers[1:48]
    for header in headers:
        globals()[header+"_" + str(subject)]=list(globals()["df_" + str(subject)][header])#collecting columnsvalues
        

control0=[]
control=[]
control1=[]

for subject in subjects:   
    for  i in range(len(globals()["Timestamps_" + str(subject)])):
        
        for header in headers:
            timestamp=globals()["Timestamps_" + str(subject)][i]
            sens_value=globals()[header+"_" + str(subject)][i]
            control0.append(subject+"_"+str(timestamp).replace(" ", "_").replace("-", "_").replace(":", "_").replace("/", "_")+"_"+header+":")
            control1.append(sens_value)
   
data=[]   

for c in control0:
    control.append(c.replace("/", "_"))
    
for sensor in headers:
    data_rough0=""
    for i in range(len(control)):
        prop=control[i]
        value=str(control1[i])
        if sensor+":" in prop:
            data_rough0+=f" {prop} '{value}',"
        
    data.append(data_rough0[:-1])

keys_list = headers
values_list = data
zip_iterator = zip(keys_list, values_list)
ass_sens_data = dict(zip_iterator)   
    
#OUT=Timestamps_S05,Timestamps_S06,Timestamps_S07,Timestamps_S08, headers,control,control1,ass_sens_data


###DATA PROCESSING############################################################################################################


Locations=ElementsLocations
SensorData=ass_sens_data

ID=[]
Names=[]
Panels=[]
Nature=[]


for e in lista:
    ID.append(e.Id)#VERFIL_Prendere ID Revit degli elementi IFC. Attualmente non c'è nel csv, possiamo includerlo? sennò lo faccio scrivere automaticamente nei parametri e lo portiamo poi nel csv
    Names.append(e.Name)#VERFIL_Prendere Nome del tipo Revit degli elementi IFC (Altro.Tipo	nel file csv ottenuto)
    param= e.get_Parameter(BuiltInParameter.ELEM_CATEGORY_PARAM).AsValueString()#VERFIL_Prendere categoria Revit degli elementi IFC (Altro.Categoria nel file csv ottenuto)
    if param == "Data Devices":#VERFIL_Da controllare se la categoria rimane così o in italiano (come per esempio è sul csv)
        param1=e.get_Parameter(BuiltInParameter.RBS_ELEC_CIRCUIT_PANEL_PARAM).AsValueString()#VERFIL_Prendere parametro Panel degli elementi Revit degli elementi IFC. Attualmente non c'è nel csv, possiamo includerlo? sennò lo faccio scrivere automaticamente nei parametri e lo portiamo poi nel csv
        Panels.append(param1)
        Nature.append("EnvironmentalSensor")        
    else:
        Panels.append("Computer")
        Nature.append("DaqHardwareSystem")
        
def lette_code(numint):
    """
    This function generates progressive
    n letters codes
    """
    import string
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)

    output=[]
    # A Python program to print all
    # permutations of given length
    from itertools import permutations
    
    # Get all permutations of length 2
    # and length 2
    perm = permutations(alphabet_list, numint)
    

    for h in list(perm):
        output.append(''.join(h))
        
    start= numint*"A"
    end= numint*"Z"
    
    return([start]+output+[end])    

letter_code=lette_code(2)
rel_lettercode=lette_code(3)
relationships=[]
letter_code_for_conclusion=[]
letter_code_counter=0
rel_lettercode_counter=0
casoparticolare=[]

with open('C:/Dropbox (Testroom Lab)/BIM-DigitalTwin/06. Experimental Data/DigitalTwinImportFiles/3_EnvironmentalSensors.txt', 'w') as h:
    for id in ID:
        ind=ID.index(id)        
        alias=letter_code[ind]
        aliasrel=rel_lettercode[ind]
        name=Names[ind]
        panel=Panels[ind]
        nature=Nature[ind]
        location=Locations[ind]
        RealSensorID=RealSensorIDs[ind]
        
        if "," in RealSensorID:
            RealSensorData0=""            
            for c in range(len(RealSensorID.split(","))):
                code=RealSensorID.split(",")[c]
                
                if c<len(RealSensorID.split(","))-1:
                    RealSensorData0+= SensorData[code]+","
                else:
                    RealSensorData0+= SensorData[code]
                    
            RealSensorID=RealSensorID.replace(",","_")
            RealSensorData=RealSensorData0#.join(",")
            casoparticolare.append(RealSensorData)
            
        elif len(RealSensorID)<2:
            RealSensorData="IP_computer: 'IP_computer'"
            
        else:
                RealSensorData=SensorData[RealSensorID]
                
                
        h.write(f"CREATE ({alias}:{nature} {{name: '{name}', panel: '{panel}', RevitID: '{id}', location: '{location}', RealSensorID: '{RealSensorID}',{RealSensorData}}})\n")
        letter_code_counter+=1
        if panel in Names:
            relationships.append(f"CREATE ({alias})-[{aliasrel}:IsLinkedTo {{action: 'SendData'}}]->({letter_code[Names.index(panel)]})")
            rel_lettercode_counter+=1
        letter_code_for_conclusion.append(alias)
            
    for rel in relationships:
        h.write("%s\n" % rel)
        
    to_graph_in_N4J= ", ".join(letter_code_for_conclusion)
    conclusion="RETURN "+to_graph_in_N4J
    h.write(conclusion)

#OUT=ID,Names,Panels,letter_code_for_conclusion,letter_code_counter,rel_lettercode_counter,casoparticolare

###DATA PROCESSING############################################################################################################


relationships=[]
letter_code_for_conclusion=[]


subjects_df=pd.read_csv("C:/Dropbox (Testroom Lab)/BIM-DigitalTwin/06. Experimental Data/Questionnario_Freddo_per soggetto.csv")
subjects=list(subjects_df["Soggetto"])
headers=list(subjects_df.columns)[:-1]
headers.remove("Soggetto")   
subject_data=[subjects_df[header] for header in headers]


data0=[]

for s in range(len(subjects)):
    data_rough0=""
    for i in range(len(headers)):
        prop=headers[i]
        column=subject_data[i]
        value=str(column[s])
        data_rough0+=f" {prop}: '{value}',"
        
    data0.append(data_rough0[:-1])

with open('C:/Dropbox (Testroom Lab)/BIM-DigitalTwin/06. Experimental Data/DigitalTwinImportFiles/1_People.txt', 'w') as h:
    for s in range(len(subjects)):
        nature="Subject"        
        alias=letter_code[letter_code_counter]
        
        name=subjects[s]
        data=data0[s]              
                
        h.write(f"CREATE ({alias}:{nature} {{name: '{name}',{data}}})\n")
        letter_code_counter+=1
        
        
        
        letter_code_for_conclusion.append(alias)
            
 
        
    to_graph_in_N4J= ", ".join(letter_code_for_conclusion)
        
    conclusion="RETURN "+to_graph_in_N4J
    h.write(conclusion)

#OUT=subjects,headers,subject_data,data,letter_code_counter

###COLLECTING WEARABLE SUBJECTS' DATA############################################################################################################


for s in range(len(subjects)):
    subject=subjects[s]
    globals()["df_" + str(subject)] = pd.read_csv("C:/Dropbox (Testroom Lab)/BIM-DigitalTwin/06. Experimental Data/"+subject+"_data_phys_env_total.csv")#creatingdataframes
    globals()["Timestamps_" + str(subject)]=list(globals()["df_" + str(subject)]['Timestamp'])#collecting timestamps
    
    if s == 0:
        all_headers=list(globals()["df_" + str(subject)].columns)
        headers=all_headers[49:]
        
    for header in headers:
        globals()[header+"_" + str(subject)]=list(globals()["df_" + str(subject)][header])#collecting columnsvalues
        
wearables=[h.split("_")[0] for h in all_headers[49:]]

control0=[]
control=[]
control1=[]

for subject in subjects:   
    for  i in range(len(globals()["Timestamps_" + str(subject)])):
        
        for header in headers:
            timestamp=globals()["Timestamps_" + str(subject)][i]
            sens_value=globals()[header+"_" + str(subject)][i]
            control0.append(subject+"_"+str(timestamp).replace(" ", "_").replace("-", "_").replace(":", "_").replace("/", "_")+"_"+header+":")
            control1.append(sens_value)
   
data=[]   

for c in control0:
    control.append(c.replace("/", "_"))
    
for sensor in headers:
    data_rough0=""
    for i in range(len(control)):
        prop=control[i]
        value=str(control1[i])
        if sensor+":" in prop:
            data_rough0+=f" {prop} '{value}',"
        
    data.append(data_rough0[:-1])

keys_list = headers
values_list = data
zip_iterator = zip(keys_list, values_list)
ass_sens_data = dict(zip_iterator)   
   
#OUT=Timestamps_S05,Timestamps_S06,Timestamps_S07,Timestamps_S08, headers,control,control1,ass_sens_data,data,wearables

############################################################################################################IMPORT_INTERNAL_DATA
WearableIntegratedSensor=headers
SensorData=ass_sens_data
#letter_code_counter=IN[2]
Wearables=wearables#VERFIL_Dobbiamo prendere gli elementi univoci della lista wearables
#rel_lettercode_counter=IN[4]

Nature0=[]
Nature1=[]

for name in Wearables:
    Nature0.append("WearableSensor")

for name in WearableIntegratedSensor:
    Nature1.append("WearableIntegratedSensor")

Names=Wearables+WearableIntegratedSensor
Nature=Nature0+Nature1

relationships=[]
letter_code_for_conclusion=[]
WearaBlesAssociation={}

with open('C:/Dropbox (Testroom Lab)/BIM-DigitalTwin/06. Experimental Data/DigitalTwinImportFiles//2_WearableSensors.txt', 'w') as h:
    for n in range(len(Names)):
        name=Names[n]
        alias=letter_code[letter_code_counter]        
        nature=Nature[n]
        try:
            RealSensorData=SensorData[name]    
        except:
            RealSensorData="data:'ReferToIntegratedLinkedSensor'"
            WearaBlesAssociation[name]=alias
        h.write(f"CREATE ({alias}:{nature} {{name: '{name}',{RealSensorData}}})\n")
        letter_code_counter+=1
        
        for w in Wearables:
            if w in name and w!=name:
                aliasrel=rel_lettercode[rel_lettercode_counter]
                relationships.append(f"CREATE ({alias})-[{aliasrel}:IsPartOf {{action: 'SendData'}}]->({WearaBlesAssociation[w]})")
                rel_lettercode_counter+=1
        letter_code_for_conclusion.append(alias)
            
    for rel in relationships:
        h.write("%s\n" % rel)
        
    to_graph_in_N4J= ", ".join(letter_code_for_conclusion)
    conclusion="RETURN "+to_graph_in_N4J
    h.write(conclusion)



#OUT=letter_code_counter,Names,Nature


############################################################################################################CREATE PC AND NEXTROOM


Computers = #VERFIL_AllObjectsOfIFCCategoryThatInRevitAreSpecialityEquipment-FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_SpecialityEquipment).WhereElementIsNotElementType().ToElements()

ComputerNames=[e.Name for e in Computers]#VERFIL Stesso discorso fatto all'inizio, a preso il tipo ovvero (Altro.Tipo nel file csv ottenuto), va sostuito nella list comprehension al posto di e.Name
ComputerNatures=["Computer" for e in Computers]
ComputerIds=[e.Id for e in Computers] #VERFIL Stesso discorso fatto all'inizio, a preso l'ID di revit che attualmente non c'è nel csv ottenuto, va sostuito nella list comprehension al posto di e.Id

Names0=["NextRoom","Experiment_XX"]
Natures0=["Facility","Experiment"]
Ids0=["Facility_N_XX","Experiment_N_XX"]

Names=Names0+ComputerNames
Natures=Natures0+ComputerNatures
Ids=Ids0+ComputerIds

relationships=[]
letter_code_for_conclusion=[]


with open('C:/Dropbox (Testroom Lab)/BIM-DigitalTwin/06. Experimental Data/DigitalTwinImportFiles/0_PCAndNextRoom.txt', 'w') as h:
    for s in range(len(Names)):
        nature=Natures[s]        
        alias=letter_code[letter_code_counter]
        
        name=Names[s]
        id=Ids[s]
                
        h.write(f"CREATE ({alias}:{nature} {{name: '{name}', RevitID: '{id}'}})\n")
        letter_code_counter+=1

        
        letter_code_for_conclusion.append(alias)
            
 
        
    to_graph_in_N4J= ", ".join(letter_code_for_conclusion)
        
    conclusion="RETURN "+to_graph_in_N4J
    h.write(conclusion)