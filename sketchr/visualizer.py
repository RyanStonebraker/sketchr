import classifier
import cbir

class Visualizer():
    def __init__(self, scene):
        self.scene = scene
        # self.cbir = cbir.CBIR()
        self.dom = self.initDom()

    def initDom(self):
        dom = {}
        dom = self.createElement("!DOCTYPE", "html", close=False)
        dom["start"] = "<!DOCTYPE html>"
        dom["inner"]["html"] = self.createElement("html", 'lang="en" dir="ltr"')
        dom["inner"]["html"]["inner"]["head"] = self.createElement("head")
        dom["inner"]["html"]["inner"]["body"] = self.createElement("body")
        return dom

    def createElement(self, tag, props="", close=True):
        element = {
            "start": "<{0} {1}>".format(tag, props),
            "inner": {}
        }
        if close:
            element["end"] = "</{0}>".format(tag)
        return element


    def getStructure(self, structureHead):
        html = ""
        if not structureHead:
            return html

        for head, tags in structureHead.items():
            if head == "start" or head == "end":
                html += structureHead[head] + "\n"
            elif structureHead[head]:
                html += self.getStructure(structureHead[head])
        return html

    def generate(self):
        # for background in self.scene["backgrounds"]:
            # backgroundImage = self.cbir.retrieveImage(background["subject"])
        print(self.getStructure(self.dom))

if __name__ == "__main__":
    # classifyEngine = classifier.Classifier()
    # query = "A yellow dog is chasing a car in Anchorage. A red dog is walking. The red dog is humungous. 2 dogs ran."
    # output = classifyEngine.classify(query)
    output = "Test"
    visualEngine = Visualizer(output)
    visualEngine.generate()
