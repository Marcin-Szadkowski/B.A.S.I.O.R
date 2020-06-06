from basior.client_pkg.client import Client
import json
from flask import Flask, Response, render_template, url_for, request, flash,redirect
from basior.logic_pkg.comunicate_manager import ComuinicateManager
import time

app = Flask(__name__)
TestClient = Client(2137, '127.0.0.1')

tramList = []
tramList.append('None')
delays = []


@app.route('/')
def index():

    return render_template("index.html", tramList=tramList, delays=delays)


@app.route("/animation")
def load():
    return render_template('load_animation.html')

@app.route("/manual")
def manual():
    return render_template('manual.html')


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
        list = []
        list.append(instruction)
        return Response(generate(list), mimetype='text')

    temp = TestClient.check_changes()

    if temp is not False:

        if json.loads(temp[0])["type"] == "bus_lines":
            for tram in json.loads(temp[0])["lines"]:
                if tram not in tramList:
                    tramList.append(tram)
        elif json.loads(temp[0])["type"] == "delays":
            for delay in json.loads(temp[0])["delays"]:
                if delay not in tramList:
                    delays.append(delay)

    if temp is not False and len(temp) > 1:
        for i in range(len(temp)):
            send_instruction(temp[i])

    else:
        return Response(generate(temp), mimetype='text')


@app.route('/', methods=["POST"])
def request_handler():

    if 'submit_route' in request.form:
        text = request.form['text2']
        info = {}

        if text == 'None':

            info["type"] = "stop_showing_path"
            TestClient.message_to_server(info)
        else:

            info["type"] = "get_tram_path"
            info["line"] = text
            TestClient.message_to_server(info)

    elif 'submit_destroy' in request.form:

        text = request.form['text']
        TestClient.message_to_server(ComuinicateManager.send_destroy(text))

    elif 'submit_delay' in request.form:

        text = request.form['text3']
        TestClient.message_to_server(ComuinicateManager.send_delay(text))

    elif 'submit_manual' in request.form:

        return render_template('manual.html')


    return render_template('index.html', tramList=tramList, delays=delays)


def run():
    app.run(debug=True, threaded=True)


if __name__ == '__main__':
    run()
