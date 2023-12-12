from nltk.tokenize import word_tokenize
from conceptnet_lite import Label, edges_for
from nltk.corpus import wordnet as wn
def removeStopwords(label,stop_words):
    node=''
    for w in word_tokenize(label):
        if w not in stop_words:
            node+="_%s"%w                    
    return node[1:]
def checkSuperclassCategories(label, superclassCategories):
    sysnets=wn.synsets(label)
    for sysnet in sysnets:
        category=sysnet.lexname().split('.')[1]
        if category in superclassCategories:
            return True
    return False

def getConcepts(label,types):
    startingConcepts=[]
    concepts=Label.get(text=label.lower(), language='en').concepts   
    for concept in concepts:
        if concept.sense_label in types:
            startingConcepts.append(concept)
    return startingConcepts

def findTriplets(label, types, relations, maxHop, edgeWeighThreshold,stop_words,superclassCategories, typePruningRelations):
    triplets=[[0 for i in range(0,0)] for i in range(0,maxHop)]
    thrownTriplets=[[0 for i in range(0,0)] for i in range(0,maxHop)]
    currHop=1
    currConcepts=getConcepts(label,types)
    labels=[]
    labels.append(label)
    print(f"Making triplets for {label}")
    while currHop<=maxHop:
        if currHop!=1:
            triplets[currHop-1]=triplets[currHop-2][:]
        if currConcepts==[]:
            break
        edges=edges_for(currConcepts, same_language=True)
        newConcepts=[]
        for edge in edges:
            if edge.relation.name not in relations or edge.etc['weight']<edgeWeighThreshold:
                continue
            newNode=None
            oldNode=None
            if(edge.start.text not in labels):
                newNode=edge.start
                oldNode=edge.end
            else:
                newNode=edge.end
                oldNode=edge.start
            node1=removeStopwords(edge.start.text,stop_words)
            node2=removeStopwords(edge.end.text,stop_words)
            if node1=="" or node2=="":
                continue
            relation=removeStopwords(edge.relation.name,stop_words)
            if currHop!=1:
                if edge.relation.name in typePruningRelations:
                    type1=edge.start.sense_label
                    type2=edge.end.sense_label
                    if type1 not in types or type2 not in types:
                        continue   
                else:
                    if(edge.start.text not in labels):
                        newNode=edge.start
                    else:
                        newNode=edge.end
                    if not checkSuperclassCategories(newNode.text, superclassCategories):
                        continue
            triplet="{node1};/r/{relation};{node2}".format(node1=node1,relation=relation,node2=node2)
            if triplet not in triplets[currHop-1]:
                triplets[currHop-1].append(triplet)
            newConcepts.append(newNode)
        currConcepts=newConcepts
        currHop+=1
    return triplets