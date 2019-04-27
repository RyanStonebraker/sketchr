import nltk
import spacy
from spacy import displacy
from spacy.matcher import Matcher
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
import re
import random
import sys

# TODO: Add pipeline with a custom model for pastRef

class Classifier():
    def __init__(self, inferenceEngine, colorFile="corpora/colors.csv", sizeFile="corpora/sizes.txt", shapeFile="corpora/shapes.txt", nerModel="models/nerModel"):
        self.query = ""
        self.nlp = spacy.load('en')
        ner = spacy.load(nerModel).pipeline[0][1]
        self.nlp.replace_pipe("ner", ner)

        self.inferenceEngine = inferenceEngine

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

        self.sizes = {}
        with open(sizeFile, "r") as sizeReader:
            for line in sizeReader:
                line = line.strip().lower()
                sizeValue = line.split(",")
                self.sizes[sizeValue[0]] = sizeValue[1].strip("\n")

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
            lemma = descriptor.lemma_.lower()
            if lemma in self.referenceWords:
                pastRef = True
            elif descriptor.text.lower() in self.colors:
                classifiedDescriptors["color"].add(self.colors[descriptor.text.lower()])
            elif lemma in self.sizes:
                classifiedDescriptors["size"].add(float(self.sizes[lemma]))
            elif lemma in self.shapes:
                classifiedDescriptors["shape"].add(lemma)
            elif descriptor.pos_ == "NUM":
                classifiedDescriptors["quantity"] = descriptor.lemma_
        return (classifiedDescriptors, pastRef)

    def addSubjectDescriptors(self, subject, descriptors, subjectEntType=None):
        subject = self.lemmatizer(subject, "NOUN")[0]
        descriptors, pastRef = self.classifyDescriptors(descriptors)
        if subject not in self.subjects:
            self.subjects[subject] = [descriptors]
        else:
            # TODO: If past ref and referring to multiple quantities, then get lemma of subject and modify all subjects being referred to
            # TODO: Compare descriptors to existing descriptors and choose the one that best fits, preferring the most recent
            if pastRef:
                for propertyName, props in self.subjects[subject][-1].items():
                    if isinstance(props, set):
                        self.subjects[subject][-1][propertyName] = self.subjects[subject][-1][propertyName].union(descriptors[propertyName])
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
            descriptiveWords = self.inferenceEngine.getDescriptiveWords(object["subject"])
            matchingColors = []
            matchingSizes = []
            for word in descriptiveWords:
                word = word.lower()
                lemma = self.lemmatizer(word, "ADJ")[0]
                if word in self.colors:
                    matchingColors.append(self.colors[word])
                if not object["modifiers"]["size"] and lemma in self.sizes:
                    matchingSizes.append(float(self.sizes[lemma]))
            if matchingColors and not object["modifiers"]["color"]:
                object["modifiers"]["color"] = {random.choice(matchingColors)}
            if matchingSizes and not object["modifiers"]["size"]:
                object["modifiers"]["size"] = {random.choice(matchingSizes)}


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

            doc = self.nlp(sentence.text)
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
    import inferenceEngine
    inferenceEngine = inferenceEngine.InferenceEngine(modelFile="models/inference/large")
    classifier = Classifier(inferenceEngine)
    query = "Look at the 5 large whales."
    print(classifier.classify(query))
