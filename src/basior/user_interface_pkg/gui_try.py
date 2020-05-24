from basior.client_pkg.client import Client
import random
import ast
import json
from flask import Flask, Response, render_template, url_for, request, flash
from datetime import datetime
import time



app = Flask(__name__)
TestClient = Client(2137, '127.0.0.1')

tramList = []


@app.route('/')
def index():

    if request.method == 'POST':
        manufacturer = request.form['manu']
        flash(str(manufacturer))
    return render_template("index.html",tramList = tramList)


#@app.route("/", methods=['POST'])
@app.route("/animation")
def load():
    return render_template('load_animation.html')


def create():
    if not TestClient.is_alive():
        TestClient.start()
        time.sleep(2)
        TestClient.message_to_server('START')
        start = False


@app.route('/time_feed')
def time_feed():
    create()

    def generate(temp):
        yield json.dumps(temp)

    time.sleep(2)
    temp = TestClient.check_changes()
    print(temp)

    if temp is not False:
        print(json.loads(temp[0])["type"])

        if json.loads(temp[0])["type"] == "ready":
            index()
        elif json.loads(temp[0])["type"] == "bus_lines":
            for tram in json.loads(temp[0])["lines"]:
                if tram not in tramList:
                    tramList.append(tram)




    return Response(generate(temp), mimetype='text')



@app.route('/', methods=["POST"])
def some_function():
    text = request.form.get('text')




    TestClient.message_to_server(ComuinicateManager.send_destroy(text))

    return render_template('index.html',tramList = tramList)




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