Codes to read .ifc files and create Cypher files to run Graph Neural Networks in the building environment

Current version: 1 (24/02/2022)
Including the geometry, people information (general information and physiological data collected during experiments) and one sample sensor
.ifc created from original file created in Revit 2023, including the sensors ID, defined by the authors (which should be syncronised with the signals collected during the experiment)

Methodology: how to create an GNN using an .ifc file
Step-by-step

1. Creating an .ifc file  from an .rvt file: xxxxxx
P.S. Different .ifc viewers can be used to check if all the instances and object attributes needed were included in the model. One viable option is BIMvision ifc model viewer.
2. Creation of input Cypher files: two text files are generated, written in Cypher language, one containing the environmental information gathered during the experimental campaign and another the general and physiological data from the subjects. Each subject should have a singular ID and each sensor a singular name. 
3. Associating BIM objects ID: the BIM objects received an attribute describing the real name of the sensor, which will be associated with the Cypher file of environmental data generated before. Information gathered from the BIM model will be included in the Cypher documents.
4. Connection with Neo4J platform and net creation: Python environment is connected with Neo4J. Participants' subjective answers are used to create the subject nodes. Room nodes are created (Facility, computer, experiment...). Then, functions to generate the relationships were generated and executed.



Routines included in the Repository to carry out the method:
/ifc_association: association the relevant information of the BIM model objects with the environmental information collected during experimental campaigns.     
/env_phys_data_cypher: creation of two text files in Cypher language, one with environmental information during test periods and another physiological data from the subjects. The files were created using .csv document generated from experimental campaigns. Environmental data depends on the sensors included in the test room; physiological data regards to the wearable sensors employed in the campaign.  
/net_creation: connection of the python engine with Neo4J and creation of nodes/relationships. The subjects' and facility's nodes are also generated in this step; the former gets the participants' subjective votes of comfort from a .csv file, compiled and organized during experimental campaigns. 
