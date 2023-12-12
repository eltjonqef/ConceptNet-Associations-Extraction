import conceptnet_lite
from readLabels import readLabels
from findTriplets import findTriplets
import nltk
from nltk.corpus import stopwords
import os
import sys
import yaml

if len(sys.argv)!=2:
    print("Missing config folder")
    exit()

conceptnet_lite.connect("conceptnet.db",db_download_url=None)
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

CONFIG_FOLDER=sys.argv[1]
with open(f"{CONFIG_FOLDER}/config.yml", "r") as configFile:
    configuration=yaml.safe_load(configFile)
    LABELS=configuration["LABELS"]
    MAX_HOP=configuration["MAX_HOP"]
    configuration=configuration["conceptNet"]
    EDGE_WEIGHT_THRESHOLD=configuration["EDGE_WEIGHT_THRESHOLD"]
    OUTPUT_FOLDER=configuration["OUTPUT_FOLDER"]

current_directory = os.getcwd()
for i in range(0,MAX_HOP):
    final_directory_actions = os.path.join(current_directory, f"{OUTPUT_FOLDER}/hop{i+1}/actions")
    final_directory_objects = os.path.join(current_directory, f"{OUTPUT_FOLDER}/hop{i+1}/objects")
    final_directory_states = os.path.join(current_directory, f"{OUTPUT_FOLDER}/hop{i+1}/states")
    if not os.path.exists(final_directory_actions):
        os.makedirs(final_directory_actions)
    if not os.path.exists(final_directory_objects):
        os.makedirs(final_directory_objects)
    if not os.path.exists(final_directory_states):
        os.makedirs(final_directory_states)

action_labels, object_labels, state_labels=readLabels(f"{CONFIG_FOLDER}/{LABELS}")
action_labels=["attach","pull"]
object_labels=[]
state_labels=[]
with open(f"{CONFIG_FOLDER}/{configuration['RELATIONS_FILE']}",'r') as relationsFile:
    relations=relationsFile.read().splitlines()
with open(f"{CONFIG_FOLDER}/{configuration['TYPE_PRUNING_RELATIONS_FILE']}",'r') as typePruningRelationsFile:
    typePruningRelations=typePruningRelationsFile.read().splitlines()
with open(f"{CONFIG_FOLDER}/{configuration['WORNDET_PRUNING_FILE']}",'r') as wordnetPruningFile:
    wordnetPruning=wordnetPruningFile.read().splitlines()
with open(f"{CONFIG_FOLDER}/{configuration['ACTION_TYPES_FILE']}",'r') as typesFile:
    actionTypes=typesFile.read().splitlines()
with open(f"{CONFIG_FOLDER}/{configuration['OBJECT_TYPES_FILE']}",'r') as typesFile:
    objectTypes=typesFile.read().splitlines()
with open(f"{CONFIG_FOLDER}/{configuration['STATE_TYPES_FILE']}",'r') as typesFile:
    stateTypes=typesFile.read().splitlines()

def makeTriplets(label, types, relations, MAX_HOP, EDGE_WEIGHT_THRESHOLD,stop_words,wordnetPruning, typePruningRelations, labelType):
    triplets=findTriplets(label, types, relations, MAX_HOP, EDGE_WEIGHT_THRESHOLD,stop_words,wordnetPruning, typePruningRelations)
    for i in range(0, len(triplets)):
        with open(f"{OUTPUT_FOLDER}/hop{i+1}/{labelType}/{label}.txt",'w') as output_triplet:
            output_triplet.write('\n'.join(triplets[i]))

for label in action_labels:
    makeTriplets(label, actionTypes, relations, MAX_HOP, EDGE_WEIGHT_THRESHOLD,stop_words,wordnetPruning, typePruningRelations, "actions")     
for label in object_labels:
    makeTriplets(label, objectTypes, relations, MAX_HOP, EDGE_WEIGHT_THRESHOLD,stop_words,wordnetPruning, typePruningRelations, "objects")
for label in state_labels:
    #if label=="switch_on" or label=="switch_off":
    #    continue
    makeTriplets(label, actionTypes, relations, MAX_HOP, EDGE_WEIGHT_THRESHOLD,stop_words,wordnetPruning, typePruningRelations, "states")


