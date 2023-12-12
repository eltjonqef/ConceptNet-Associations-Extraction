from neo4j import GraphDatabase
import time
from readLabels import readLabels
import sys
import yaml
import os

HOP=1

if len(sys.argv)!=2:
    print("Missing config folder")
    exit()

CONFIG_FOLDER=sys.argv[1]
with open(f"{CONFIG_FOLDER}/config.yml", "r") as configFile:
    configuration=yaml.safe_load(configFile)
    LABELS=configuration["LABELS"]
    MAX_HOP=configuration["MAX_HOP"]
    configuration=configuration["neo4j"]
    ROOT_DIRECTORY=configuration["ROOT_DIRECTORY"]
    OUTPUT_FOLDER=configuration["OUTPUT_FOLDER"]
    URI = configuration["URI"]
    AUTH = (configuration["USERNAME"],configuration["PASSWORD"])
    DATABASE= configuration["DATABASE"]

current_directory = os.getcwd()
for i in range(0,MAX_HOP):
    final_directory = os.path.join(current_directory, f"{OUTPUT_FOLDER}/hop{i+1}")
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)

action_labels, object_labels, state_labels=readLabels(f"{CONFIG_FOLDER}/{LABELS}")


def emptyDB(session):
    queryEraseDB = "match (n) detach delete n"
    session.run(queryEraseDB)

# Calculates the number of paths that start from a given node
# Stores the result (integer) in a list
def calculateAllPaths(inputFilePath, inputLabelsList, outputList, session):
    output=[]
    for label in inputLabelsList:
        print(label)
        #queryLoadData = "LOAD CSV FROM \""+inputFilePath+label+"_triplets.txt\" AS row fieldterminator ; merge (n:Node {label: row[0]}) merge (m:Node {label: row[2]}) merge (n)-[:Property {label: row[1]}]->(m)"
        # This query ignores triples when the subject or the object part of a triple is null
        queryLoadData = "LOAD CSV FROM \""+inputFilePath+label+".txt\" AS row fieldterminator ';' FOREACH (x IN CASE WHEN row[2] IS NULL OR row[0] IS NULL THEN [] ELSE [1] END | merge (n:Node {label: row[0]}) merge (m:Node {label: row[2]}) merge (n)-[:Property {label: row[1]}]->(m) )"
        session.run(queryLoadData)
        #queryCountPaths = "MATCH path = (start:Node {label:'attach'})-[*]-(end:Node {label:'ring'}) where size(apoc.coll.toSet(nodes(path))) = size(nodes(path)) return count(path)"
        queryCountPaths = "MATCH path = (start:Node {label:'"+label+"'})-[*1..2]-() where size(apoc.coll.toSet(nodes(path))) = size(nodes(path)) return count(path)"
        respond = session.run(queryCountPaths)
        numOfPaths = int(list(respond.values())[0][0])
        outputList.append(int(numOfPaths))
        output.append(f"{label};{str(numOfPaths)}")

        emptyDB(session)
    return output


def calculatePairPaths(inputFile1Path, inputLabels1List, inputFile2Path, inputLabels2List, outputList, session):
    output=[]
    for objectLabel in inputLabels1List:
        print(f"object {objectLabel}")
        for label in inputLabels2List:
            print(f"inuut {label}")
            queryLoadObjects = "LOAD CSV FROM \""+inputFile1Path+objectLabel+".txt\" AS row fieldterminator ';' FOREACH (x IN CASE WHEN row[2] IS NULL OR row[0] IS NULL THEN [] ELSE [1] END | merge (n:Node {label: row[0]}) merge (m:Node {label: row[2]}) merge (n)-[:Property {label: row[1]}]->(m) )"
            session.run(queryLoadObjects)
            queryLoadLabels = "LOAD CSV FROM \""+inputFile2Path+label+".txt\" AS row fieldterminator ';' FOREACH (x IN CASE WHEN row[2] IS NULL OR row[0] IS NULL THEN [] ELSE [1] END | merge (n:Node {label: row[0]}) merge (m:Node {label: row[2]}) merge (n)-[:Property {label: row[1]}]->(m) )"
            session.run(queryLoadLabels)

            queryCountC1Paths ="MATCH path = (start:Node {label:'"+objectLabel+"'})-[*1..4]->(end:Node {label:'"+label+"'}) where size(apoc.coll.toSet(nodes(path))) = size(nodes(path)) return count(path)" 
            queryCountC2Paths ="MATCH path = (start:Node {label:'"+label+"'})-[*1..4]->(end:Node {label:'"+objectLabel+"'}) where size(apoc.coll.toSet(nodes(path))) = size(nodes(path)) return count(path)" 

            respondC1 = session.run(queryCountC1Paths)
            numOfC1Paths = int(list(respondC1.values())[0][0])
            respondC2 = session.run(queryCountC2Paths)
            numOfC2Paths = int(list(respondC2.values())[0][0])
            
            outputList.append(numOfC1Paths+numOfC2Paths)
            output.append(f"{objectLabel};{label};{str(numOfC2Paths)}")

            emptyDB(session)
    return output



# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"



driver = GraphDatabase.driver(URI, auth=AUTH)
driver.verify_connectivity()

with driver.session(database=DATABASE) as session:
    for HOP in range(3,MAX_HOP+1):
        objPathCounts = []
        actPathCounts = []
        sttPathCounts = []
        objActPathCounts = []
        objSttPathCounts = []
        emptyDB(session)
        timers=[]
        # Calculate the number of all paths starting from a given node label
        print("\nactionLabel:allPaths")
        startTimer = time.time()
        output=calculateAllPaths(f"{ROOT_DIRECTORY}/hop{HOP}/actions/", action_labels, actPathCounts, session)
        endTimer = time.time()
        with open(f"{OUTPUT_FOLDER}/hop{HOP}/actionAllPaths.txt",'w') as output_measurement:
            output_measurement.write('\n'.join(output))
        timers.append(f"{endTimer};{startTimer}")
        

        print("\nobjectLabel:allPaths")
        startTimer = time.time()
        output=calculateAllPaths(f"{ROOT_DIRECTORY}/hop{HOP}/objects/", object_labels, objPathCounts, session)
        endTimer = time.time()
        with open(f"{OUTPUT_FOLDER}/hop{HOP}/objectAllPaths.txt",'w') as output_measurement:
            output_measurement.write('\n'.join(output))
        timers.append(f"{endTimer};{startTimer}")
        

        print("\nstateLabel:allPaths")
        startTimer = time.time()
        output=calculateAllPaths(f"{ROOT_DIRECTORY}/hop{HOP}/states/", state_labels, sttPathCounts, session)
        endTimer = time.time()
        with open(f"{OUTPUT_FOLDER}/hop{HOP}/stateAllPaths.txt",'w') as output_measurement:
            output_measurement.write('\n'.join(output))
        timers.append(f"{endTimer};{startTimer}")
        
        # print the scores as a list
        #print(objPathCounts)
        #print(actPathCounts)
        #print(sttPathCounts)


        # Calculate the number of paths between two node labels
        print("\nobject:action:connectingPaths")
        startTimer = time.time()
        output=calculatePairPaths(f"{ROOT_DIRECTORY}/hop{HOP}/objects/", object_labels, f"{ROOT_DIRECTORY}/hop{HOP}/actions/", action_labels, objActPathCounts, session)
        endTimer = time.time()
        with open(f"{OUTPUT_FOLDER}/hop{HOP}/objectActionPaths.txt",'w') as output_measurement:
            output_measurement.write('\n'.join(output))
        timers.append(f"{endTimer};{startTimer}")
        

        print("\nobject:state:connectingPaths")
        startTimer = time.time()
        output=calculatePairPaths(f"{ROOT_DIRECTORY}/hop{HOP}/objects/", object_labels, f"{ROOT_DIRECTORY}/hop{HOP}/states/", state_labels, objSttPathCounts, session)
        endTimer = time.time()
        with open(f"{OUTPUT_FOLDER}/hop{HOP}/objectStatePaths.txt",'w') as output_measurement:
            output_measurement.write('\n'.join(output))
        timers.append(f"{endTimer};{startTimer}")
        

        #print(objActPathCounts)
        #print(objSttPathCounts)


        # Calculate and print the connPaths final score
        #Testing - ERASE
        #objPathCounts = [32, 20]
        #actPathCounts = [28, 15]
        #objActPathCounts = [15,15,5,5]
        #sttPathCounts = [28, 15]
        #objSttPathCounts = [15,15,5,5]
        # print(objPathCounts)
        # print(actPathCounts)
        # print(objActPathCounts)
        with open(f"{OUTPUT_FOLDER}/hop{HOP}/timers.txt",'w') as output_measurement:
            output_measurement.write('\n'.join(timers))
        scores=[]
        print("\nobject:action:connectPathScore")
        counter = 0
        for objCounter in range(len(objPathCounts)):
            for actCounter in range(len(actPathCounts)):
                try:
                    p1CupP2 = objPathCounts[objCounter] + actPathCounts[actCounter]
                    scores.append(f"{object_labels[objCounter]};{action_labels[actCounter]};{str(objActPathCounts[counter]/p1CupP2)}")
                    counter+=1
                except:
                    print(f"FAIL OBJ{objCounter}LEN{len(objPathCounts)} ACT{actCounter}{len(actPathCounts)}")
        with open(f"{OUTPUT_FOLDER}/hop{HOP}/objectActionScores.txt",'w') as output_measurement:
            output_measurement.write('\n'.join(scores))
        scores=[]
        print("\nobject:state:connectPathScore")
        # print(objPathCounts)
        # print(sttPathCounts)
        # print(objSttPathCounts)
        counter = 0
        for objCounter in range(len(objPathCounts)):
            for sttCounter in range(len(sttPathCounts)):
                p1CupP2 = objPathCounts[objCounter] + sttPathCounts[sttCounter]
                scores.append(f"{object_labels[objCounter]};{state_labels[sttCounter]};{str(objSttPathCounts[counter]/p1CupP2)}")
                counter+=1
        with open(f"{OUTPUT_FOLDER}/hop{HOP}/objectStateScores.txt",'w') as output_measurement:
            output_measurement.write('\n'.join(scores))
    driver.close()