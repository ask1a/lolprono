
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1> Hello!! </h1>"

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True,host="127.0.0.1", port=5000)

