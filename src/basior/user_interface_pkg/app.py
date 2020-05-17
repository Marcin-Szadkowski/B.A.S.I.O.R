
import flask
import pykafka
from flask import Flask, render_template, Response, request
from pykafka import KafkaClient

def get_kafka_client():
    return KafkaClient(hosts='127.0.0.1:2137')

app = Flask(__name__)

@app.route('/')
def index():
    return(render_template('index.html'))

@app.route('/')
def loader():
    return(render_template('load_animation.html'))

#text fields
@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    print(text)
    return text

#Consumer API
@app.route('/topic/<topicname>')
def get_messages(topicname):
    client = get_kafka_client()
    def events():
        for i in client.topics[topicname].get_simple_consumer():

            yield 'data:{0}\n\n'.format(i.value.decode())
    return Response(events(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True, port=5001)
