import requests

class CBIR():
    def __init__(self, wordNetMapping="corpora/wordMapping.txt", cache="corpora/cache.txt"):
        self.imageNetUrl = "http://www.image-net.org/api/text/imagenet.synset.geturls.getmapping?wnid="
        self.wordnet = {}
        with open(wordNetMapping, "r") as wordMapper:
            for line in wordMapper:
                wnPair = line.split("\t")
                wnPair[1] = wnPair[1].split(", ")
                for index, word in enumerate(wnPair[1]):
                    word = word.replace("\n", "")
                    if word in self.wordnet:
                        self.wordnet[word].append((wnPair[0], index))
                    else:
                        self.wordnet[word] = [(wnPair[0], index)]
        self.cacheFile = cache
        self.cache = {}
        with open(cache, "r") as cacheReader:
            for line in cacheReader:
                wordUrl = line.split(", ")
                self.cache[wordUrl[0]] = wordUrl[1].strip("\n")

    def checkUrl(self, url):
        try:
            response = requests.get(url, timeout=1)
            if response and "not found" not in response.text:
                return url
        except:
            return False
        return False

    def getWorkingUrl(self, urls):
        for url in urls:
            validUrl = self.checkUrl(url.split(" ")[1])
            if validUrl:
                return validUrl

    def writeToCache(self, name, url):
        with open(self.cacheFile, "a+") as cacheWriter:
            cacheWriter.write("{0}, {1}\n".format(name, url))

    def rewriteCache(self):
        with open(self.cacheFile, "w") as cacheWriter:
            for name, url in self.cache.items():
                cacheWriter.write("{0}, {1}\n".format(name, url))

    def retrieveImage(self, name):
        if name in self.cache:
            if self.checkUrl(self.cache[name]):
                return self.cache[name]
            else:
                self.cache.pop(name, None)
                self.rewriteCache()

        wordIds = self.wordnet[name]
        wordIds.sort(key=lambda x: x[1])
        for id, freq in wordIds:
            imagesUrl = self.imageNetUrl + id
            response = requests.get(imagesUrl)
            if response.text:
                urls = response.text.split("\n")
                workingUrl = self.getWorkingUrl(urls)
                self.writeToCache(name, workingUrl)
                return workingUrl

if __name__ == "__main__":
    cbir =  CBIR()
    print(cbir.retrieveImage(input("Enter item to get picture: ")))
