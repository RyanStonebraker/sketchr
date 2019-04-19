import nltk
import spacy
from spacy import displacy

# Structure
# [
#     {
#         "subject": "",
#         "type": "object|background",
#         "modifiers": [
#             "color": [],
#             "shape": [],
#             "size": []
#         ],
#         "placement": {
#             "rel": "origin", # ex. item is next to door, position rel to door
#             "x": 0, # relative to rel
#             "y": 0, # relative to rel
#             "z": 0 # z-index above items
#         }
#     }
# ]

class Classifier():
    def __init__(self):
        self.query = ""
        self.nlp = spacy.load('en')

    def classify(self, query):
        # tokens = nltk.word_tokenize(query)
        # taggedTokens = nltk.pos_tag(tokens)
        doc = self.nlp(query)
        classification = []
        for chunk in doc.noun_chunks:
            children = []
            for child in chunk.root.children:
                children.append({"word": child, "type": child.tag_, "dep": child.dep_})

            classification.append({
                "root": chunk.root.text,
                "full": chunk.text,
                "dependency": chunk.root.dep_,
                "children": children
            })
        return classification


if __name__ == "__main__":
    classifier = Classifier()
    query = "A yellow dog chasing a car."
    print(classifier.classify(query))
