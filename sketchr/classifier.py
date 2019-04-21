import nltk
import spacy
from spacy import displacy
from spacy.matcher import Matcher
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
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
        self.matcher = Matcher(self.nlp.vocab)
        self.lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)
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

    def addSubjectDescriptors(self, subject, descriptors):
        descriptors, pastRef = self.classifyDescriptors(descriptors)
        if subject not in self.subjects:
            self.subjects[subject] = [descriptors]
        else:
            if pastRef:
                for propertyName, props in self.subjects[subject][-1].items():
                    self.subjects[subject][-1][propertyName] = props.union(descriptors[propertyName])
            else:
                self.subjects[subject].append(descriptors)

    def classify(self, query):
        doc = self.nlp(query)
        for i, sentence in enumerate(doc.sents):
            # TODO: match other patterns for descriptors (ex. the dog is BIG. ), could do this by identifying non-matched descriptors in a sentence w/subject.
            for chunk in sentence.noun_chunks:
                subject = chunk.root.text
                descriptors = [word.text for word in chunk if word.text != subject]
                self.addSubjectDescriptors(subject, descriptors)
        for subject in self.subjects:
            pattern = [{'POS': 'DET', 'OP': '?'}, {'POS': 'ADJ', 'OP': '*'}, {'LOWER': subject}, {'LEMMA': 'be'}, {'POS': 'ADJ'}]
            self.matcher.add(subject, None, pattern)
            matches = self.matcher(doc)
            matchedRanges = []
            for match_id, start, end in self.matcher(doc):
                skipMatch = False
                for prevStart, prevEnd in matchedRanges:
                    if start >= prevStart and end <= prevEnd:
                        skipMatch = True
                        break
                if skipMatch:
                    continue
                matchedRanges.append((start, end))
                self.addSubjectDescriptors(subject, [token.text for token in doc[start:end] if token.text != subject])
            self.matcher.remove(subject)
        print(self.subjects)

        return self.scene


if __name__ == "__main__":
    classifier = Classifier()
    query = "A yellow dog is chasing a car in Canada. A red dog is walking. The red dog is large."
    classifier.classify(query)
