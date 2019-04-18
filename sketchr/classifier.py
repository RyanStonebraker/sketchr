import nltk

class Classifier():
    def __init__(self):
        self.query = ""

    def classify(self, query):
        return nltk.pos_tag(nltk.word_tokenize(query))

if __name__ == "__main__":
    classifier = Classifier()
    query = "This is a test."
    print(classifier.classify(query))
