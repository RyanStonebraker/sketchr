import classifier
import cbir
import uuid

class Visualizer():
    def __init__(self, scene):
        self.scene = scene
        self.cbir = cbir.CBIR()
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
        style["top"] = pos["x"]
        style["left"] = pos["y"]
        style["z-index"] = pos["z"]
        props += self.getStyleString(style)
        self.queryDom("html body")["inner"][id] = self.createElement("img", props)

    def generate(self):
        for i, background in enumerate(self.scene["backgrounds"]):
            backgroundImage = self.cbir.retrieveImage(background["subject"])
            self.addImage(backgroundImage, {"x": 0, "y": 0, "z": 0})
            # self.queryDom("html body")["inner"]["background" + str(i)] = self.createElement("img", "src='{}'".format(backgroundImage))
        for i, object in enumerate(self.scene["objects"]):
            objectImage = self.cbir.retrieveImage(object["subject"])
        print(self.getStructure(self.dom))

if __name__ == "__main__":
    classifyEngine = classifier.Classifier()
    query = "A yellow dog is chasing a car in Anchorage. A red dog is walking. The red dog is humungous. 2 dogs ran."
    output = classifyEngine.classify(query)
    visualEngine = Visualizer(output)
    visualEngine.generate()
