import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding

def getTrainingData(dataFile="corpora/nerTrainingData.txt", locFile="corpora/locationLabels.txt", gpeFile="corpora/gpeLabels.txt"):
    labels = []
    with open(locFile, "r") as labelReader:
        labels = [(label.strip(), "LOC") for label in labelReader]
    with open(gpeFile, "r") as labelReader:
        labels += [(label.strip(), "GPE") for label in labelReader]
    trainingData = []
    with open(dataFile, "r") as sentenceReader:
        for sentence in sentenceReader:
            sentence = sentence.strip()
            trainingSentence = (sentence, {"entities": []})
            sentence = sentence.lower()
            for label in labels:
                if label[0] in sentence:
                    start = sentence.find(label[0])
                    trainingSentence[1]["entities"].append((start, start + len(label[0]), label[1]))
            trainingData.append(trainingSentence)
    return trainingData

def train(trainingData, model=None, outputDir=None, trainingIteration=100, testDataFile="corpora/unlabeledData.txt"):
    nlp = spacy.load(model) if model else spacy.blank("en")
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last=True)
    else:
        ner = nlp.get_pipe("ner")
    for _, annotations in trainingData:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        if model is None:
            nlp.begin_training()
        for itn in range(trainingIteration):
            random.shuffle(trainingData)
            losses = {}
            batches = minibatch(trainingData, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, drop=0.5, losses=losses)
    if outputDir:
        outputDir = Path(outputDir)
        if not outputDir.exists():
            outputDir.mkdir()
        nlp.to_disk(outputDir)
    with open(testDataFile, "r") as testReader:
        for sentence in testReader:
            sentence = sentence.strip()
            doc = nlp(sentence)
            print("Entities:", [(ent.text, ent.label_) for ent in doc.ents])
            print("Tokens:", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

def test(testFile, model, outputFile):
    nlp = spacy.load(model) if model else spacy.load("en")
    with open(outputFile, "w") as outputWriter:
        outputWriter.write("correctly_identified, wrongly_identified, expected\n")
        with open(testFile, "r") as testReader:
            for line in testReader:
                line = line.strip().split(",, ")
                expected = line[0].lower().split(", ")
                sentence = line[1].strip()
                doc = nlp(sentence)
                entities = [(ent.text, ent.label_) for ent in doc.ents]
                print("Expected:", expected, " Actual:", entities)
                correctIdentified = 0
                wronglyIdentified = 0
                if not expected[0] and not entities:
                    correctIdentified = 1
                    wronglyIdentified = 1
                for entity in entities:
                    if entity[0].lower() in expected:
                        correctIdentified += 1
                    else:
                        wronglyIdentified += 1
                outputWriter.write("{0}, {1}, {2}\n".format(correctIdentified, wronglyIdentified, len(expected)))
                print("Score:", float(correctIdentified/len(expected)))


if __name__ == "__main__":
    trainingData = getTrainingData()
    # train(trainingData, trainingIteration=100)
    test("corpora/nerCorpus.txt", None, "corpora/builtin_results.txt")
