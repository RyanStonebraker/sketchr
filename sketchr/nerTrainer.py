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

def train(trainingData, model=None, output_dir=None, n_iter=100):
    if model:
        nlp = spacy.load(model)
    else:
        nlp = spacy.blank("en")

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
        for itn in range(n_iter):
            random.shuffle(trainingData)
            losses = {}
            batches = minibatch(trainingData, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, drop=0.5, losses=losses)
            print("Losses", losses)

    for text, _ in trainingData:
        doc = nlp(text)
        print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
        print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

    if output_dir:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        for text, _ in trainingData:
            doc = nlp2(text)
            print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
            print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])


if __name__ == "__main__":
    print(getTrainingData())
    # train(trainingData)
