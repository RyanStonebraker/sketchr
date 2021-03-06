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
        props = ""
        style["top"] = str(pos["y"]) + "px"
        style["left"] = str(pos["x"]) + "px"
        style["z-index"] = pos["z"]
        if "background" not in style:
            style["background-image"] = "url(\"{}\")".format(src.strip())
            style["background-size"] = "contain"
        style["background-position"] = "center"
        style["background-repeat"] = "no-repeat"

        props += self.getStyleString(style)
        self.queryDom("html body")["inner"][id] = self.createElement("div", props)

    def generate(self):
        for i, background in enumerate(self.scene["backgrounds"]):
            backgroundImage = self.cbir.retrieveImage(background["subject"])
            if not backgroundImage:
                continue
            pos = {
                "x": 0,
                "y": 0,
                "z": 0
            }
            style = {
                "width": "1000px",
                "height": "500px"
            }
            if background["modifiers"]["color"]:
                style["filter"] = "opacity(0.6) drop-shadow(0 0 0 {})".format(list(background["modifiers"]["color"])[0])
                style["background"] = "url(\"{}\")".format(backgroundImage.strip())
            else:
                style["background"] = "url(\"{}\")".format(backgroundImage.strip())
                style["background-size"] = "cover"

            self.addImage(backgroundImage, pos, style)
        for i, object in enumerate(self.scene["objects"]):
            objectImage = self.cbir.retrieveImage(object["subject"])
            if not objectImage:
                continue

            sizeMod = 1
            if object["modifiers"]["size"]:
                sizeMod = 0
                for size in object["modifiers"]["size"]:
                    sizeMod += size
                sizeMod /= len(object["modifiers"]["size"])

            style = {
                "width": str(200 * sizeMod) + "px",
                "height": str(200 * sizeMod) + "px"
            }
            if object["modifiers"]["color"]:
                style["filter"] = "opacity(0.6) drop-shadow(0 0 0 {})".format(list(object["modifiers"]["color"])[0])
                style["background"] = "url(\"{}\")".format(objectImage.strip())
                style["background-size"] = "contain"

            for j in range(0, int(object["modifiers"]["quantity"])):
                pos = {
                    "x": i * int(float(style["width"].strip("px"))) + j * 100,
                    "y": 500 - int(float(style["height"].strip("px"))) - 10,
                    "z": 1
                }
                self.addImage(objectImage, pos, style)
        return self.getStructure(self.dom)

if __name__ == "__main__":
    classifyEngine = classifier.Classifier()
    query = "A yellow dog is chasing a car in Anchorage. A red dog is walking. The red dog is humungous. 2 dogs ran."
    output = classifyEngine.classify(query)
    visualEngine = Visualizer(output)
    visualEngine.generate()
