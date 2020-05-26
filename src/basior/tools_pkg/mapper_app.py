from flask import *
from functools import wraps
import sqlite3

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('graph.html')


@app.route('/', methods=["POST"])
def some_function():
    text = request.form.get('text')
    print(text)
    text = text.split(',')
    print(text)
    banned = ['LatLng', '']
    for t in text:
        if t in banned:
            text.remove(t)
    for t in text:
        if t in banned:
            text.remove(t)

    with open("chosen_coordinates.txt", "w") as output:
        output.write(str(text))

    return render_template('graph.html')


def run():
    app.run(debug=True, threaded=True)


if __name__ == '__main__':
    run()
