from . import classifier
from . import cbir
import uuid

class Visualizer():
    def __init__(self, scene, wordMapping="corpora/wordMapping.txt", cache="corpora/cache.txt"):
        self.scene = scene
        self.cbir = cbir.CBIR(wordMapping, cache)
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

    def queryDom(self, query):
        if not query:
            return self.dom

        query = query.split(" ")
        element = self.dom
        for el in query:
            element = element["inner"][el]
        return element

    def getStyleString(self, style):
        output = "style='position:absolute;"
        for name, prop in style.items():
            output += "{0}:{1};".format(name, prop)
        output += "'"
        return output

    def addImage(self, src, pos, style={}):
        id = uuid.uuid4()
        props = "src='{}'".format(src)
        style["top"] = str(pos["x"]) + "px"
        style["left"] = str(pos["y"]) + "px"
        style["z-index"] = pos["z"]
        props += self.getStyleString(style)
        self.queryDom("html body")["inner"][id] = self.createElement("img", props)

    def generate(self):
        for i, background in enumerate(self.scene["backgrounds"]):
            backgroundImage = self.cbir.retrieveImage(background["subject"])
            pos = {
                "x": 0,
                "y": 0,
                "z": 0
            }
            style = {
                "width": "100%",
                "height": "100%"
            }
            self.addImage(backgroundImage, pos, style)
        for i, object in enumerate(self.scene["objects"]):
            objectImage = self.cbir.retrieveImage(object["subject"])
            pos = {
                "x": i * 200,
                "y": i * 100,
                "z": 1
            }
            style = {
                "width": "100px",
                "height": "100px"
            }
            self.addImage(objectImage, pos, style)
        return self.getStructure(self.dom)

if __name__ == "__main__":
    classifyEngine = classifier.Classifier()
    query = "A yellow dog is chasing a car in Anchorage. A red dog is walking. The red dog is humungous. 2 dogs ran."
    output = classifyEngine.classify(query)
    visualEngine = Visualizer(output)
    visualEngine.generate()
