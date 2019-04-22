import nltk
import spacy
from spacy import displacy
from spacy.matcher import Matcher
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
import re
import random

class Classifier():
    def __init__(self, colorFile="corpora/colors.csv", sizeFile="corpora/sizes.txt", shapeFile="corpora/shapes.txt"):
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
        self.colors = {}
        with open(colorFile, "r") as colorReader:
            for line in colorReader:
                colorValue = line.split(",")
                self.colors[colorValue[0].lower()] = colorValue[1].strip("\n")

        self.sizes = []
        with open(sizeFile, "r") as sizeReader:
            self.sizes = [size.strip().lower() for size in sizeReader]

        self.shapes = []
        with open(shapeFile, "r")  as shapeReader:
            self.shapes = [shape.strip().lower() for shape in shapeReader]

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
        # for i, descriptor in enumerate(descriptors):
            # if descriptor.pos_ != "SUBJ":
            #     if hasattr(descriptor, "pos_") and descriptor.pos_ == "ADJ" and (descriptors[i-1].pos_ == "ADJ" or descriptors[i-1].pos_ == "NOUN"):
            #         descriptors[i-1].text += " " + descriptor.text
            #         del descriptors[i]
        classifiedDescriptors = {}
        pastRef = False
        classifiedDescriptors["color"] = set()
        classifiedDescriptors["size"] = set()
        classifiedDescriptors["shape"] = set()
        classifiedDescriptors["quantity"] = 1
        classifiedDescriptors["entity"] = None
        for descriptor in descriptors:
            if descriptor.lemma_.lower() in self.referenceWords:
                pastRef = True
            elif descriptor.text.lower() in self.colors:
                classifiedDescriptors["color"].add(self.colors[descriptor.text.lower()])
            elif descriptor.lemma_.lower() in self.sizes:
                classifiedDescriptors["size"].add(descriptor.lemma_)
            elif descriptor.lemma_.lower() in self.shapes:
                classifiedDescriptors["shape"].add(descriptor.lemma_)
            elif descriptor.pos_ == "NUM":
                classifiedDescriptors["quantity"] = descriptor.text
        return (classifiedDescriptors, pastRef)

    def addSubjectDescriptors(self, subject, descriptors, subjectEntType=None):
        subject = self.lemmatizer(subject, "NOUN")[0]
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
                if "entity" not in individual or not individual["entity"]:
                    individual["entity"] = subjectEntType

    def addSubjectsToScene(self):
        for subject, matches in self.subjects.items():
            for match in matches:
                appendTo = "objects"
                if "entity" in match and match["entity"] in ["GPE", "LOC", "EVENT", "FAC"]:
                    appendTo = "backgrounds"
                match.pop("entity", None)
                self.scene[appendTo].append({
                    "subject": subject,
                    "modifiers": match
                })

    def inferContext(self):
        for object in self.scene["objects"]:
            if not object["modifiers"]["color"]:
                # TODO: Make this better by finding n-grams of adjectives that commonly describe nouns and selecting from these
                object["modifiers"]["color"] = {self.colors[random.choice(list(self.colors))]}
            # print(object)


    def classify(self, query):
        self.scene = {
            "objects": [],
            "backgrounds": []
        }
        self.subjects = {}
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
        self.inferContext()
        return self.scene


if __name__ == "__main__":
    classifier = Classifier()
    query = "An amarillo yellow dog is chasing a car in Canada. A red dog is walking. The red dog is humungous. 2 dogs ran."
    classifier.classify(query)
