import pandas as pd

def readLabels(labelFile):
    df=pd.read_excel(labelFile)

    action_labels=df['action labels']
    action_labels=action_labels.dropna()
    for i, label in enumerate(action_labels):
        if " (verb)" in label:
            action_labels[i]=label[:-7]

    object_labels=df['oject labels']
    for i, label in enumerate(object_labels):
        if " (verb)" in label:
            object_labels[i]=label[:-7]

    state_labels=df['state labels']
    state_labels=state_labels.dropna()

    return action_labels, object_labels, state_labels