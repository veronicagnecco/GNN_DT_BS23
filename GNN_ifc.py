import os
import pandas as pd
#from py2neo import Graph
import neo4j
from neo4j import GraphDatabase
#from graphdatascience import GraphDataScience
import fileinput
import sys

#error user/password: https://community.neo4j.com/t/connect-neo-clienterror-security-unauthorized-the-client-is-unauthorized-due-to-authentication-failure/11801/8
#https://neo4j.com/docs/operations-manual/4.0/configuration/password-and-user-recovery/
#https://neo4j.com/docs/python-manual/current/

os.chdir("C:/Users/Martins Gnecco/Testroom Lab Dropbox/Veronica Martins Gnecco/BS2023/01. Data Acquisition Files/DigitalTwinImportFiles")
custom_date_parser = lambda x: datetime.strptime(x,"%Y/%m/%d %H:%M:%S")

#Connectivity (writing credentials and checking connectivity)
host = "bolt://localhost:7687"
user = "neo4j"
password = "mynewpass"

matrix_survey = pd.read_csv('Questionnario_Freddo_per_soggetto.csv', sep=';')
subjects = list(matrix_survey['Subject'])
TC_list = list(matrix_survey['TC'])
TS_list = list(matrix_survey['TS'])
PTC_list = list(matrix_survey['PTC'])
VC_list = list(matrix_survey['VC'])
VS_list = list(matrix_survey['VS'])
PVC_list = list(matrix_survey['PVC'])
AC_list = list(matrix_survey['AC'])
AS_list = list(matrix_survey['AS'])
PAC_list = list(matrix_survey['PAC'])
AIC_list = list(matrix_survey['AIC'])
AIS_list = list(matrix_survey['AIS'])
PAI_list = list(matrix_survey['PAI'])

room_elem = ['NextRoom','Experiment_XX','PC_NextRoom']
RvtID =['Facility_N_XX','Experiment_N_XX','849243']

with GraphDatabase.driver(host, auth=(user, password)) as driver:
    driver.verify_connectivity()

#defining our functions:
#Defining subjects
def create_person_nodes(tx,subject,name,TC,TS,PTC,VC,VS,PVC,AC,AS,PAC,AIC,AIS,PAI):
    result = tx.run(
        "CREATE (p:Subject {subject:$subject, name:$name,TC:$TC,TS:$TS,PTC:$PTC,VC:$VC,VS:$VS,PVC:$PVC,AC:$AC,AS:$AS,PAC:$PAC,AIC:$AIC,AIC:$AIC,AIS:$AIS,PAI:$PAI}) "
        "RETURN p.subject AS subject, p.name AS name, p.TC AS TC, p.TS AS TS, p.PTC AS PTC, p.VC AS VC, p.VS AS VS, p.PVC AS PVC, p.AC AS AC, p.AS AS AS, p.PAC AS PAC, p.AIC AS AIC, p.AIS AS AIS, p.PAI AS PAI",
        subject=subject,name=name,TC=TC,TS=TS,PTC=PTC,VC=VC,VS=VS,PVC=PVC,AC=AC,AS=AS,PAC=PAC,AIC=AIC,AIS=AIS,PAI=PAI)
    records = list(result)
    summary = result.consume()
    return records, summary

for a,b,c,d,e,f,g,h,i,j,k,l,m in zip(subjects,TC_list,TS_list,PTC_list,VC_list,VS_list,PVC_list,AC_list,AS_list,PAC_list,AIC_list,AIS_list,PAI_list):
    with driver.session(database="neo4j") as session:
        session.execute_write(create_person_nodes,subject=a,name=a,TC=b,TS=c,PTC=d,VC=e,VS=f,PVC=g,AC=h,AS=i,PAC=j,AIC=k,AIS=l,PAI=m)


#Create nodes: Facility, computer, experiment
def create_room(tx):
    result = tx.run(
        "CREATE(DJ:Facility {name:'NextRoom', RevitID:'Facility_N_XX'})"
        "CREATE(DK:Experiment {name:'Experiment_XX', RevitID:'Experiment_N_XX'})"
        "CREATE(DL:Computer {name:'PC_NextRoom',RevitID: '849243'})"
        "RETURN DJ, DK, DL")
    return result

#Create nodes: wearables (using file already done)
with open('2_WearableSensors.txt', 'r') as file:
    read_wearables = file.read()

with open('3_EnvironmentalSensors.txt', 'r') as file:
    read_env = file.read()

def create_match_wearables(tx): #when the file is ready doesn't need to be executed with driver
    result = tx.run(read_wearables)
    return result

def create_match_env(tx):
    result = tx.run(read_env)
    return result

#Defining functions and relationships

def MatchComputerFacility(tx):
    result = tx.run(
        "MATCH (DJ:Facility),(DL:Computer)"
        "CREATE (DL)-[rel:IsPartOf]->(DJ)"
        "RETURN  DJ,rel,DL")
    return result

def MatchDAQComputer(tx):
    result = tx.run(
        "MATCH (BN:DaqHardwareSystem),(DL:Computer)"
        "CREATE (BN)-[rel:IsLinkedTo]->(DL)"
        "RETURN  BN,rel,DL")
    return result

def MatchDAQFacility(tx):
    result = tx.run(
        "MATCH (BN:DaqHardwareSystem),(DJ:Facility)"
        "CREATE (BN)-[rel:IsPartOf]->(DJ)"
        "RETURN  BN,rel,DJ")
    return result

def MatchEnvironmentalSensorsAndLaboratory(tx):
    result = tx.run(
        "MATCH (BL:EnvironmentalSensor),(DJ:Facility)"
        "CREATE (BL)-[rel:IsPartOf]->(DJ)"
        "RETURN  BL,rel,DJ")
    return result

def MatchExpEnvironmental(tx):
    result = tx.run(
        "MATCH (BL:EnvironmentalSensor),(DK:Experiment)"
        "CREATE (BL)-[rel:IsPartOf]->(DK)"
        "RETURN  BL,rel,DK")
    return result

def MatchExperimentFacility(tx):
    result = tx.run(
        "MATCH (DK:Experiment),(DJ:Facility)"
        "CREATE (DK)-[rel:TakesPartIn]->(DJ)"
        "RETURN  DK,rel,DJ")
    return result

def MatchExpPc(tx):
    result = tx.run(
        "MATCH (DK:Experiment),(DL:Computer)"
        "CREATE (DL)-[rel:IsPartOf]->(DK)"
        "RETURN  DK,rel,DL")
    return result

def MatchExpPeople(tx):
    result = tx.run(
        "MATCH (p:Subject),(DK:Experiment)"
        "CREATE (p)-[rel:IsPartOf]->(DK)"
        "RETURN  p,rel,DK")
    return result

def MatchPeopleAndWearables(tx):
    result = tx.run(
        "MATCH (p:Subject),(BS:WearableSensor)"
        "CREATE (p)-[rel:IsMonitoredBy]->(BS)"
        "RETURN  p,rel,BS")
    return result


with driver.session(database="neo4j") as session:
    session.execute_write(create_room)
    session.execute_write(create_match_wearables)
    session.execute_write(create_match_env)
    session.execute_write(MatchComputerFacility)
    session.execute_write(MatchDAQComputer)
    session.execute_write(MatchDAQFacility)
    session.execute_write(MatchEnvironmentalSensorsAndLaboratory)
    session.execute_write(MatchExpEnvironmental)
    session.execute_write(MatchExperimentFacility)
    session.execute_write(MatchExpPc)
    session.execute_write(MatchExpPeople)
    session.execute_write(MatchPeopleAndWearables)

quit()

#Reading wearable sensors data
for s in range(len(subjects)):
    subject = subjects[s]
    globals()["df_" + str(subject)] = pd.read_csv(subject+"_data_phys_env_total.csv")#creatingdataframes
    globals()["Timestamps_" + str(subject)] = list(globals()["df_" + str(subject)]['Timestamp'])#collecting timestamps

    if s == 0:
        all_headers = list(globals()["df_" + str(subject)].columns)
        headers = all_headers[49:]

    for header in headers:
        globals()[header + "_" + str(subject)] = list(globals()["df_" + str(subject)][header])  # collecting columns values

wearables = [h.split("_")[0] for h in all_headers[49:]]

control0 = []
control = []
control1 = []

for subject in subjects:
    for i in range(len(globals()["Timestamps_" + str(subject)])):

        for header in headers:
            timestamp = globals()["Timestamps_" + str(subject)][i]
            sens_value = globals()[header + "_" + str(subject)][i]
            control0.append(subject + "_" + str(timestamp).replace(" ", "_").replace("-", "_").replace(":", "_").replace("/","_") + "_" + header + ":")
            control1.append(sens_value)

data = []

for c in control0:
    control.append(c.replace("/", "_"))

for sensor in headers:
    data_rough0 = ""
    for i in range(len(control)):
        prop = control[i] #column value
        value = str(control1[i]) #column name
        if sensor + ":" in prop:
            data_rough0 += f" {prop} '{value}',"

    data.append(data_rough0[:-1])

keys_list = headers
values_list = data
zip_iterator = zip(keys_list, values_list)
ass_sens_data = dict(zip_iterator)

#OUT=Timestamps_S05,Timestamps_S06,Timestamps_S07,Timestamps_S08, headers,control,control1,ass_sens_data,data,wearables

quit()






quit()

#records, summary =
# Summary information
print("The query `{query}` returned {records_count} records in {time} ms.".format(
    query=summary.query, records_count=len(records),
    time=summary.result_available_after,
))

# Loop through results and do something with them
for person in records:
    print(person)


def match_person_wearables(tx,subject,wearable): #defines the unit of work to be executed in the transaction
    result1 = tx.run(
        "MATCH path = (a:wearable)-[rel:Monitor]->(s:subject {subject:$subject}) "
        "RETURN path, s.subject AS subject, a.wearable AS wearable, rel.relation AS relation",
        subject=subject,wearable=wearable)
    records1 = list(result1)
    #summary1 = result1.consume()
    relation1 = result1.value('relation')
    return records1, relation1

with driver.session(database="neo4j") as session:
    records1, relation1 = session.execute_write(match_person_wearables, subject='Giulia',wearable='Empatica')

'''# Summary information
print("The query `{query}` returned {records_count} records in {time} ms.".format(
    query=summary1.query, records_count=len(records1),
    time=summary1.result_available_after,
))'''

# Loop through results and do something with them
for person in records1:
    print(person)










quit()

driver = GraphDatabase.driver(host, auth=(user, password))
driver.verify_connectivity()

with driver.session() as session:
    records, summary = session.execute_read(create_person, name="Michael")

# Summary information
print("The query `{query}` returned {records_count} records in {time} ms.".format(
    query=summary.query, records_count=len(records),
    time=summary.result_available_after,
))

# Loop through results and do something with them
for person in records:
    print(person)

session.close()


quit()
graph = Graph(host, auth=(user, password))
#Check connectivity Python - Neo4J
try:
    graph.run("Match () Return 1 Limit 1")
    print('ok')
except Exception:
    print('not ok')



gds = GraphDataScience(host, auth=(user, password))
print(gds.version())

uri = "bolt://127.0.0.1:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "Password"))
driver.verify_connectivity()


AuraDBId = 'neo4j'
dbUsername = 'neo4j' #Default neo4j for Aura
password = 'mynewpass'
boltUrl = f"neo4j+ssc://{AuraDBId}.databases.neo4j.io:7687"

graphDBDriver = GraphDatabase.driver(boltUrl,auth=(dbUsername, password))
graphDBDriver.verify_connectivity()




