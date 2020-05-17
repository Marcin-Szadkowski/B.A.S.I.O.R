from basior.client_pkg.client import Client
import random
import json
from flask import Flask, Response, render_template, url_for
from datetime import datetime
import time

app = Flask(__name__)
TestClient = Client(2137, '127.0.0.1')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/')
def animation():
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
        yield str(temp)

    time.sleep(2)
    temp = json.dumps(TestClient.check_changes())


    if temp  is not None:
        if temp is not False:
            return Response(generate(temp), mimetype='text')


    """
    while True:


        def generate():
            yield str( json.dumps( [{"type" :"tram" , "33": [16.955245, 51.1336907], "11": [16.9788997, 51.0942625]}]    ) )

        return Response(generate(), mimetype='text')
    """









def run():
    app.run(debug=True, threaded=True)


if __name__ == '__main__':
    run()