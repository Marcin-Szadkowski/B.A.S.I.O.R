from basior.client_pkg.client import Client
import json
from flask import Flask, Response, render_template, request
from basior.logic_pkg.comunicate_manager import ComuinicateManager
import time

"""Flask application. Contains client initialization .
   Responsible for rendering particular html views, analysing communicates 
   sent from server and passing them info GUI"""

app = Flask(__name__)
TestClient = Client(2137, '127.0.0.1')

#constant data sent from server at begining
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


@app.route('/time_feed')
def time_feed():
    """function responsible for catching data from server and passing them info GUI"""

    create()

    def generate(temp):
        yield json.dumps(temp)

    def send_instruction(instruction):
        list = []
        list.append(instruction)
        return Response(generate(list), mimetype='text')

    # temp stores information of latest package of data sent from server
    temp = TestClient.check_changes()

    if temp is not False:

        # trying to catch data about bus_lines and delys and stores them in list
        if json.loads(temp[0])["type"] == "bus_lines":
            for tram in json.loads(temp[0])["lines"]:
                if tram not in tramList:
                    tramList.append(tram)

        elif json.loads(temp[0])["type"] == "delays":
            for delay in json.loads(temp[0])["delays"]:
                if delay not in tramList:
                    delays.append(delay)

    # if package of data sent from server contains more than one message,
    # then iterete over package to realize all comunicates
    if temp is not False and len(temp) > 1:
        for i in range(len(temp)):
            send_instruction(temp[i])

    else:
        return Response(generate(temp), mimetype='text')


@app.route('/', methods=["POST"])
def request_handler():
    """function responsible for getting post request from GUI,
        and based on them sends appriopriate comunicates defined in
        ComuinicateManager class
    """

    # checking which event was chosen based on submit buttons
    if 'submit_route' in request.form:
        text = request.form['text2']
        info = {}

        if text == 'None':
            info["type"] = "stop_showing_path"

            # infrom server when user decide to stop displaying route
            TestClient.message_to_server(info)
        else:
            info["type"] = "get_tram_path"
            info["line"] = text
            # infrom server when user decide to print particular tram route
            TestClient.message_to_server(info)

    elif 'submit_destroy' in request.form:
        text = request.form['text']
        # infrom server about chosen nodes on tram's map to destroy
        TestClient.message_to_server(ComuinicateManager.send_destroy(text))


    elif 'submit_delay' in request.form:
        text = request.form['text3']
        # infrom server when user choose different tram speed
        TestClient.message_to_server(ComuinicateManager.send_delay(text))

    elif 'submit_manual' in request.form:
        return render_template('manual.html')

    # return main template with variables that store actual tram lines and delays
    return render_template('index.html', tramList=tramList, delays=delays)


def run():
    app.run(debug=True, threaded=True)


if __name__ == '__main__':
    run()
