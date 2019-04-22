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
#                 "size": [],
#                 "quantity": 1
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
        self.referenceWords = ["the", "it", "that", "his", "hers", "theirs"]
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
        classifiedDescriptors["quantity"] = 1
        classifiedDescriptors["entity"] = None
        for descriptor in descriptors:
            if descriptor.text.lower() in self.referenceWords:
                pastRef = True
            elif descriptor.text.lower() in self.colors:
                classifiedDescriptors["color"].add(descriptor)
            elif descriptor.text.lower() in self.sizes:
                classifiedDescriptors["size"].add(descriptor)
            elif descriptor.text.lower() in self.shapes:
                classifiedDescriptors["shape"].add(descriptor)
            elif descriptor.pos_ == "NUM":
                classifiedDescriptors["quantity"] = descriptor.text
        return (classifiedDescriptors, pastRef)

    def addSubjectDescriptors(self, subject, descriptors, subjectEntType=None):
        descriptors, pastRef = self.classifyDescriptors(descriptors)
        if subject not in self.subjects:
            self.subjects[subject] = [descriptors]
        else:
            # TODO: If past ref and referring to multiple quantities, then get lemma of subject and modify all subjects being referred to
            if pastRef:
                for propertyName, props in self.subjects[subject][-1].items():
                    if isinstance(props, set):
                        self.subjects[subject][-1][propertyName] = props.union(descriptors[propertyName])
            else:
                self.subjects[subject].append(descriptors)
        if subjectEntType:
            for individual in self.subjects[subject]:
                if not individual["entity"]:
                    individual["entity"] = subjectEntType

    def addSubjectsToScene(self):
        for subject, matches in self.subjects.items():
            for match in matches:
                appendTo = "objects"
                if match["entity"] in ["GPE", "LOC", "EVENT", "FAC"]:
                    appendTo = "backgrounds"
                self.scene[appendTo].append({
                    "subject": subject,
                    "modifiers": match
                })

    def classify(self, query):
        doc = self.nlp(query)
        for i, sentence in enumerate(doc.sents):
            for chunk in sentence.noun_chunks:
                subject = chunk.root.text
                descriptors = [word for word in chunk if word.text != subject]
                self.addSubjectDescriptors(subject, descriptors, chunk.root.ent_type_)
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
                self.addSubjectDescriptors(subject, [token for token in doc[start:end] if token.text != subject])
            self.matcher.remove(subject)
        self.addSubjectsToScene()
        return self.scene


if __name__ == "__main__":
    classifier = Classifier()
    query = "A yellow dog is chasing a car in Canada. A red dog is walking. The red dog is large. 2 dogs ran."
    print(classifier.classify(query))
