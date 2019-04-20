import requests

class CBIR():
    def __init__(self, wordNetMapping="corpora/wordMapping.txt"):
        self.imageNetUrl = "http://www.image-net.org/api/text/imagenet.synset.geturls.getmapping?wnid="
        with open(wordNetMapping, "r") as wordMapper:
            self.wordnet = {}
            for line in wordMapper:
                wnPair = line.split("\t")
                wnPair[1] = wnPair[1].split(", ")
                for index, word in enumerate(wnPair[1]):
                    word = word.replace("\n", "")
                    if word in self.wordnet:
                        self.wordnet[word].append((wnPair[0], index))
                    else:
                        self.wordnet[word] = [(wnPair[0], index)]
    def retrieveImage(self, name):
        wordIds = self.wordnet[name]
        wordIds.sort(key=lambda x: x[1])
        for id, freq in wordIds:
            imagesUrl = self.imageNetUrl + id
            response = requests.get(imagesUrl)
            if response.text:
                urls = response.text.split("\n")
                return urls[0].split(" ")[1]

if __name__ == "__main__":
    cbir =  CBIR()
    print(cbir.retrieveImage(input("Enter item to get picture: ")))
