from flask import Flask, render_template, request
from sketchr import classifier

app = Flask(__name__)

global classifyEngine

@app.route("/", methods = ['POST', 'GET'])
def home():
    output=""
    if request.method == "POST":
        for input, value in request.form.items():
            if input == "natlang":
                query = value
        output = classifyEngine.classify(query)

    return render_template("main.html", output=output)

if __name__ == "__main__":
    classifyEngine = classifier.Classifier()
    app.run(debug=True)
