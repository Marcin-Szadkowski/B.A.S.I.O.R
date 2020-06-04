from basior.client_pkg.client import Client
import random
import ast
import json

from basior.logic_pkg.comunicate_manager import ComuinicateManager
from flask import Flask, Response, render_template, url_for, request, flash
from basior.logic_pkg.comunicate_manager import ComuinicateManager
from datetime import datetime
import time

app = Flask(__name__)
TestClient = Client(2137, '127.0.0.1')

tramList = ['stop']


@app.route('/')
def index():
    if request.method == 'POST':
        manufacturer = request.form['manu']
        flash(str(manufacturer))
    return render_template("index.html", tramList=tramList)


# @app.route("/", methods=['POST'])
@app.route("/animation")
def load():
    return render_template('load_animation.html')


def create():
    if not TestClient.is_alive():
        TestClient.start()
        time.sleep(0.2)
        TestClient.message_to_server('START')
        start = False


@app.route('/time_feed')
def time_feed():
    create()

    def generate(temp):
        yield json.dumps(temp)

    def send_instruction(instruction):

        print("wysylam")
        print(instruction)
        list = []
        list.append(instruction)
        return Response(generate(list), mimetype='text')

    # time.sleep(1)
    temp = TestClient.check_changes()
    print(temp)

    if temp is not False:
        print("length", len(temp))
        print(json.loads(temp[0])["type"])

        if json.loads(temp[0])["type"] == "ready":
            index()
        elif json.loads(temp[0])["type"] == "bus_lines":
            for tram in json.loads(temp[0])["lines"]:
                if tram not in tramList:
                    tramList.append(tram)

    if temp is not False and len(temp) > 1:
        for i in range(len(temp)):
            print(i)
            print("temp aktualny ", temp[i])
            send_instruction(temp[i])
            # return Response(generate(temp[i]), mimetype='text')

    else:
        return Response(generate(temp), mimetype='text')


@app.route('/', methods=["POST"])
def some_function():
    text = request.form['text']

    if len(text) == 0:
        text = request.form['text2']

        if text == 'stop':
            info = {}
            info["type"] = "stop_showing_path"
            TestClient.message_to_server(info)
        else:
            info = {}
            info["type"] = "get_tram_path"
            info["line"] = text
            TestClient.message_to_server(info)
    else:

        TestClient.message_to_server(ComuinicateManager.send_destroy(text))

    return render_template('index.html', tramList=tramList)


def run():
    app.run(debug=True, threaded=True)


if __name__ == '__main__':
    run()
""" info["type"] = "tram"
                temp = random.choice(self.trams).current_route
               # info["lines"] = ["1","2","3","11","33","70"]
                #info["coordinates"] = [[random.uniform(51.100,51.113), 17.03408718109131], [51.11633355911742, 17.03333616256714],
                 #                [51.11827317886492, 17.03850746154785], [random.uniform(51.100,51.113), random.uniform(17,17.1)]]


                #{"type": "ready"}
                #info['type'] = 'update'"""
