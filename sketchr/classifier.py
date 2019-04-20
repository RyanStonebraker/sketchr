import nltk
import spacy
from spacy import displacy
from spacy.matcher import Matcher
import re

# Structure
# {
#     "objects": [
#         {
#             "subject": "",
#             "modifiers": {
#                 "color": [],
#                 "shape": [],
#                 "size": []
#             },
#             "placement": {
#                 "rel": "origin", # ex. item is next to door, position rel to door
#                 "x": 0, # relative to rel
#                 "y": 0, # relative to rel
#                 "z": 0 # z-index above items
#             }
#         }
#     ],
#     "backgrounds": [
#         {
#         "subject": "",
#         "modifiers": [
#             "color": [],
#             "shape": [],
#             "size": []
#         }
#     ]
# }

class Classifier():
    def __init__(self):
        self.query = ""
        self.nlp = spacy.load('en')
        self.scene = {
            "objects": [],
            "backgrounds": []
        }
        self.subjects = {}
        self.pronouns = ["the", "it", "that", "his", "hers", "theirs"]
        self.colors = ["red", "green", "yellow", "blue"]
        self.sizes = ["big", "large", "small", "medium"]
        self.shapes = ["narrow", "wide", "circular", "rectangular"]

    def getBlankObject(self):
        identifiedObject = {}
        identifiedObject["subject"] = None
        identifiedObject["modifiers"] = {}
        identifiedObject["modifiers"]["color"] = None
        identifiedObject["modifiers"]["shape"] = None
        identifiedObject["modifiers"]["size"] = None
        identifiedObject["modifiers"]["quantity"] = 1
        return identifiedObject

    def classifyDescriptors(self, descriptors):
        classifiedDescriptors = {}
        pastRef = False
        classifiedDescriptors["color"] = set()
        classifiedDescriptors["size"] = set()
        classifiedDescriptors["shape"] = set()
        for descriptor in descriptors:
            if descriptor.lower() in self.pronouns:
                pastRef = True
            elif descriptor.lower() in self.colors:
                classifiedDescriptors["color"].add(descriptor)
            elif descriptor.lower() in self.sizes:
                classifiedDescriptors["size"].add(descriptor)
            elif descriptor.lower() in self.shapes:
                classifiedDescriptors["shape"].add(descriptor)
        return (classifiedDescriptors, pastRef)

    def classify(self, query):
        doc = self.nlp(query)
        for i, sentence in enumerate(doc.sents):
            for chunk in sentence.noun_chunks:
                subject = chunk.root.text
                descriptors = [word.text for word in chunk if word.text != subject]
                descriptors, pastRef = self.classifyDescriptors(descriptors)
                if subject not in self.subjects:
                    self.subjects[subject] = [descriptors]
                else:
                    if pastRef:
                        for propertyName, props in self.subjects[subject][-1].items():
                            self.subjects[subject][-1][propertyName] = props.union(descriptors[propertyName])
                    else:
                        self.subjects[subject].append(descriptors)
        print(self.subjects)

        return self.scene


if __name__ == "__main__":
    classifier = Classifier()
    query = "A yellow dog is chasing a car in Canada. A red dog is walking. The big red dog is fast."
    classifier.classify(query)
