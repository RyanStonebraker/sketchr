from flask import Flask, render_template, request, Markup
from sketchr import classifier
from sketchr import visualizer
import pprint

app = Flask(__name__)

global classifyEngine

@app.route("/viewer", methods = ['GET'])
def viewer():
    return render_template("output.html")

@app.route("/", methods = ['POST', 'GET'])
def home():
    output=""
    query=""
    scene=""
    if request.method == "POST":
        for input, value in request.form.items():
            if input == "natlang":
                query = value
        output = classifyEngine.classify(query)
        visualEngine = visualizer.Visualizer(output, "sketchr/corpora/wordMapping.txt", "sketchr/corpora/cache.txt")
        scene = visualEngine.generate().strip()
        with open("templates/output.html", "w") as outputWriter:
            outputWriter.write(scene)

    return render_template("main.html", output=Markup(pprint.pformat(output, indent=4)), input=query, visual=Markup(scene))

if __name__ == "__main__":
    classifyEngine = classifier.Classifier("sketchr/corpora/colors.csv", "sketchr/corpora/sizes.txt", "sketchr/corpora/shapes.txt", "sketchr/models/nerModel")
    app.run(debug=True)
