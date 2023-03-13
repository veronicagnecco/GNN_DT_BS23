import os
import pandas as pd
import ifcopenshell
import ifcopenshell.util.element as Element
import ifcopenshell.util.placement as Placement
import pprint

os.chdir("C:/Users/Veronica/Testroom Lab Dropbox/Veronica Martins Gnecco/BS2023/01. Data Acquisition Files")

file = ifcopenshell.open('C:/Users/Veronica/Testroom Lab Dropbox/Veronica Martins Gnecco/BS2023/01. Data Acquisition Files/NextRoomSensors_2023.ifc')
pp = pprint.PrettyPrinter()

def get_objects_data_by_class(file,class_type):
    def add_pset_attributes(pset):
        for pset_name, pset_data in psets.items():
            for property_name in pset_data.keys():
                pset_attributes.add(f'{pset_name}.{property_name}')

    pset_attributes = set()
    objects_data = []
    objects = file.by_type(class_type)

    for object in objects:
        #print(Element.get_psets(object))
        psets = Element.get_psets(object,psets_only=True)
        add_pset_attributes(psets)
        qtos = Element.get_psets(object, qtos_only=True)
        add_pset_attributes(qtos)

        object_id = object.id()
        objects_data.append({
            "ExpressId": object.id(),
            "GlobalId": object.GlobalId,
            "Class": object.is_a(),
            "PredefinedType": Element.get_predefined_type(object),
            "Name": object.Name,
            "Level": Element.get_container(object).Name,
            "Location": (Placement.get_local_placement(object.ObjectPlacement).T)[3]
            #We still need to do configure this Location output (it's an array line) and create a column with "Real SensorID" data (probably considering a project parameter), if it exists)
            if Element.get_container(object)
            else "",
            "Type": Element.get_type(object).Name
            if Element.get_type(object)
            else "",
            "QuantitySets": qtos,
            "PropertySets": psets,
        })    return objects_data, list(pset_attributes)

def get_attribute_value(object_data,attribute):
    if "." not in attribute:
        return object_data[attribute]
    elif "." in attribute:
        pset_name = attribute.split(".",1)[0]
        prop_name = attribute.split(".",-1)[1]
        if pset_name in object_data["PropertySets"].keys():
            if prop_name in object_data["PropertySets"][pset_name].keys():
                return object_data["PropertySets"][pset_name][prop_name]
            else:
                return None
        if pset_name in object_data["QuantitySets"].keys():
            if prop_name in object_data["QuantitySets"][pset_name].keys():
                return object_data["QuantitySets"][pset_name][prop_name]
            else:
                return None
    else:
        return None

data, pset_attributes = get_objects_data_by_class(file,"IfcFlowTerminal")

attributes = ["ExpressId","GlobalId","Class","PredefinedType","Name","Level","Location","Type"] + pset_attributes

pandas_data = []
for object_data in data:
    row = []
    for attribute in attributes:
        value = get_attribute_value(object_data,attribute)
        row.append(value)
    pandas_data.append(tuple(row))

dataframe = pd.DataFrame.from_records(pandas_data,columns=attributes)
#print(dataframe)



dataframe.to_csv("df_ifc_attributes.csv")