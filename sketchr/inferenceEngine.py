import spacy
import random
from collections import OrderedDict

class InferenceEngine():
    def __init__(self, *corpora):
        self.nlp = spacy.load("en")
        self.descriptions = {}
        for corpusFile in corpora:
            with open(corpusFile) as corpusReader:
                for i, _ in enumerate(corpusReader):
                    pass
            fileLineCount = i + 1
            with open(corpusFile, "r") as corpusReader:
                paragraph = ""
                lastPercent = 0.0
                for currentLineCount, line in enumerate(corpusReader):
                    line = line.lower().strip()
                    if line:
                        paragraph += " {}".format(line)
                    else:
                        self.classifyParagraph(paragraph)
                        paragraph = ""

                    percentComplete = currentLineCount/fileLineCount
                    if percentComplete - lastPercent > 0.25:
                        print("Processing: {0} - {1}%".format(corpusFile, int(percentComplete * 10000)/100))
                        lastPercent = float(currentLineCount/fileLineCount)

    def classifyParagraph(self, paragraph):
        doc = self.nlp(paragraph)
        for chunk in doc.noun_chunks:
            adjBuffer = []
            for word in chunk:
                if word.pos_ == "ADJ":
                    adjBuffer.append(word.text)
                elif word.pos_ == "NOUN":
                    self.addDescriptors(word.lemma_, adjBuffer)
                    adjBuffer = []

    def addDescriptors(self, noun, adjectives):
        for adjective in adjectives:
            if noun in self.descriptions:
                if adjective in self.descriptions[noun]:
                    self.descriptions[noun][adjective] += 1
                else:
                    self.descriptions[noun][adjective] = 1
            else:
                self.descriptions[noun] = {}
                self.descriptions[noun][adjective] = 1

    def getDescriptiveWords(self, word, numberWords=None):
        if word not in self.descriptions:
            return []

        describingWords = self.descriptions[word]
        describingWords = OrderedDict(sorted(describingWords.items(), key=lambda w: w[1], reverse=True))

        if numberWords is None:
            numberWords = len(describingWords)

        totalAdjectiveCount = 0
        for _, count in describingWords.items():
            totalAdjectiveCount += count

        descriptions = []
        for i, adjCount in enumerate(describingWords.items()):
            adjective, count = adjCount
            if len(descriptions) >= numberWords:
                break

            normalizedFreq = count/totalAdjectiveCount
            remainingAdjectives = len(describingWords) - i
            if (numberWords and remainingAdjectives <= numberWords - len(descriptions)) or random.random() < normalizedFreq:
                descriptions.append(adjective)
        return descriptions

if __name__ == "__main__":
    inferenceEngine = InferenceEngine("corpora/mobydick.txt")
    while True:
        user = input("Enter Word: ")
        print(inferenceEngine.getDescriptiveWords(user))
