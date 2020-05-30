from flask import *
import osmnx as ox
from IPython.display import IFrame
from bs4 import BeautifulSoup
import shutil


"""program shows behaviour of graph after deleting node"""

app = Flask(__name__)
shutil.copy('data/osmnx_graph_origin.graphml','data/osmnx_graph.graphml')
G = ox.load_graphml('osmnx_graph.graphml')
ox.config(log_console=True, use_cache=True)


@app.route('/')
def home():
    make_updated_graph_model()
    return render_template('index.html')


"""function gets data from  template"""


@app.route('/', methods=["POST"])
def get_data():
    text = request.form.get('text')

    text = text.split(',')

    banned = ['LatLng', '']
    for t in text:
        if t in banned:
            text.remove(t)
    for t in text:
        if t in banned:
            text.remove(t)

    with open("chosen_coordinates_destory_documentation.txt", "w") as output:
        output.write(str(text))

    print(text)
    osmnx_response(text)
    return render_template('index.html')


"""function removes nodes nearest to chosen and saves graph"""


def osmnx_response(coordinates):

    dict = {}
    dict["type"] = "edges"
    edges = []
    touple = []

    for i in range(0, len(coordinates), 2):
        nr_edge = ox.get_nearest_edge(G, (float(coordinates[i]), float(coordinates[i + 1])))

        touple.append([nr_edge[1],nr_edge[2]])

        if len(touple) == 2:
            edges.append(touple)
            touple = []

        G.remove_edge(nr_edge[1], nr_edge[2])

    dict["data"] = edges
    with open("edges.txt", "w") as output:
        output.write(str(dict))

    ox.save_graphml(G, filename='osmnx_graph.graphml')
    make_updated_graph_model()

    return render_template('index.html')


"""function create template updated based on graph"""


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


def run():
    app.run(debug=True, threaded=True)


if __name__ == '__main__':
    run()
