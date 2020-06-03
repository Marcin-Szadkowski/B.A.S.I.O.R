from flask import *
import osmnx as ox
from IPython.display import IFrame
from bs4 import BeautifulSoup
import shutil
from polyline_string import PolyLine_String
import json
import os

"""program shows behaviour of graph after deleting node and
   visualise chosen edges as a tram loop for a testing purposes"""

"""store as G osmnx Wroclaw tramline graph as a base for computation"""

app = Flask(__name__)
shutil.copy('data/osmnx_graph_origin.graphml', 'data/osmnx_graph.graphml')
G = ox.load_graphml('osmnx_graph.graphml')
ox.config(log_console=True, use_cache=True)

"""Polyline object stores loops chosen during usage"""

polyline_string = PolyLine_String()


@app.route('/')
def home():
    make_updated_graph_model()
    return render_template('index.html', string=polyline_string.polyline_string)


"""function gets data from  template"""


@app.route('/', methods=["POST"])
def get_data():
    text = request.form['text']

    if len(text) == 0:
        text = request.form.get('text2')

        if text == "stop":
            polyline_string.polyline_string = ""
            return render_template('index.html', string=polyline_string.polyline_string)

        if text == "clear":
            remove_file_content("tram_loops.json")
            return render_template('index.html', string=polyline_string.polyline_string)

        else:
            text = remove_banned_words_from_input(text.split(','))
            dict = osmnx_response(text, "loop")

            if check_if_exist('tram_loops.json'):
                append_to_edges(dict['data'], "tram_loops.json")

            else:
                create_json("tram_loops.json", dict)

            ox.save_graphml(G, filename='osmnx_graph.graphml')
            make_updated_graph_model()

            return render_template('index.html', string=polyline_string.polyline_string)

    else:

        text = request.form.get('text')
        if text == "clear":
            remove_file_content("edges.json")
            return render_template('index.html', string=polyline_string.polyline_string)


        text = remove_banned_words_from_input(text.split(','))
        dict = osmnx_response(text, "remove_edge")


        if check_if_exist('edges.json'):
            append_to_edges(dict['data'], "edges.json")
        else:
            create_json("edges.json", dict)


        ox.save_graphml(G, filename='osmnx_graph.graphml')
        make_updated_graph_model()

        return render_template('index.html', string=polyline_string.polyline_string)


"""function removes nodes nearest to chosen and saves graph"""


def osmnx_response(coordinates, type):
    dict = {}
    dict["type"] = "edges"
    edges = []
    touple = []

    if type == "loop":

        for i in range(0, len(coordinates), 2):
            nr_edge = ox.get_nearest_edge(G, (float(coordinates[i]), float(coordinates[i + 1])))

            touple.append([nr_edge[1], nr_edge[2]])

            for i in range(len(G[nr_edge[1]][nr_edge[2]])):
                if str(G[nr_edge[1]][nr_edge[2]][i]['geometry']) == str(nr_edge[0]):
                    key = i
                    touple[-1].append(key)

            if len(touple) == 2:
                print("touple ", touple)
                edges.append(touple)
                touple = []

            polyline_string.update_polyline(nr_edge[0])

    else:

        for i in range(0, len(coordinates), 2):
            nr_edge = ox.get_nearest_edge(G, (float(coordinates[i]), float(coordinates[i + 1])))

            touple = [nr_edge[1], nr_edge[2]]

            for i in range(len(G[nr_edge[1]][nr_edge[2]])):
                if str(G[nr_edge[1]][nr_edge[2]][i]['geometry']) == str(nr_edge[0]):
                    key = i
                    touple.insert(len(touple), key)

            edges.append(touple)
            G.remove_edge(nr_edge[1], nr_edge[2], key)
            touple = []

    dict["data"] = edges
    print(edges)

    return dict


"""function create template updated based on graph. Extends grap.html by 
    additional html extensions """


def make_updated_graph_model():
    ox.config(log_console=True, use_cache=True)

    G_2 = ox.load_graphml('osmnx_graph.graphml')

    # plot the street network with folium
    graph_map = ox.plot_graph_folium(G_2, edge_width=2)

    filepath = 'templates/graph.html'
    graph_map.save(filepath)
    IFrame(filepath, width=600, height=500)

    soup = BeautifulSoup(open('templates/graph.html'), 'html.parser')

    js_tag = soup.find_all("script")
    js_tag[5].append('{% block script %} {% endblock %}')

    with open("templates/graph.html", "w") as file:
        file.write(str(soup))

    soup.find("div")
    div = soup.find("div")
    div = str(div).split()
    map_id = div[2][4:-8]

    fin = open("templates/graph.html", "rt")
    # output file to write the result to
    fout = open("templates/final_graph.html", "wt")
    # for each line in the input file
    for line in fin:
        # read replace the string and write to output file
        fout.write(line.replace(map_id, 'map_id'))
    # close input and output files
    fin.close()
    fout.close()

    soup = BeautifulSoup(open('templates/final_graph.html'), 'html.parser')

    data_body = '{% block body %} {% endblock %}'
    data_script = '{% block script %} {% endblock %}'
    data_style = '{% block style %} {% endblock %}'

    soup.body.append(data_body)

    soup.style.append(data_style)
    with open("templates/final_graph.html", "w") as file:
        file.write(str(soup))


def remove_banned_words_from_input(text):
    banned = ['LatLng', '']
    for t in text:
        if t in banned:
            text.remove(t)
    for t in text:
        if t in banned:
            text.remove(t)
    return text


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def append_to_edges(arr, filename):
    # function to add to JSON

    with open(filename) as json_file:
        data = json.load(json_file)

        temp = data['data']

        # python object to be appended
        for i in range(len(arr)):
            temp.append(arr[i])

    write_json(data, filename)


def check_if_exist(filename):
    if os.stat(filename).st_size == 0:
        return False
    else:
        return True


def create_json(filename, dict):
    with open(filename, "w") as output:
        json.dump(dict, output)


def remove_file_content(filename):
    file = open(filename,"r+")
    file.truncate(0)
    file.close()


def run():
    app.run(debug=True, threaded=True)


if __name__ == '__main__':
    run()
