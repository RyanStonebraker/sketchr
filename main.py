from flask import Flask, render_template, request, Markup
from sketchr import classifier
import pprint

app = Flask(__name__)

global classifyEngine

@app.route("/", methods = ['POST', 'GET'])
def home():
    output=""
    query=""
    if request.method == "POST":
        for input, value in request.form.items():
            if input == "natlang":
                query = value
        output = classifyEngine.classify(query)

    return render_template("main.html", output=Markup(pprint.pformat(output, indent=4)), input=query)

if __name__ == "__main__":
    classifyEngine = classifier.Classifier()
    app.run(debug=True)
