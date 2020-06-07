from flask import *
import osmnx as ox
from IPython.display import IFrame
from bs4 import BeautifulSoup
import shutil
from polyline_string import PolyLine_String
from mapper_data_loader import MapDataLoader


"""program shows behaviour of graph after deleting node and
   visualise chosen edges as a tram loop for a testing purposes"""

"""store as G osmnx Wroclaw tramline graph as a base for computation"""

app = Flask(__name__)
shutil.copy('data/osmnx_graph_origin.graphml', 'data/osmnx_graph.graphml')
G = ox.load_graphml('osmnx_graph.graphml')
ox.config(log_console=True, use_cache=True)

# Polyline object stores loops chosen during usage
polyline_string = PolyLine_String()

# MapDataLodaer object
data_loader = MapDataLoader()


@app.route('/')
def home():
    make_updated_graph_model()
    return render_template('index.html', string=polyline_string.polyline_string)


@app.route('/', methods=["POST"])
def get_data():
    """function gets data from  template, and runs osmnx methods on them"""

    text = request.form['text']

    if len(text) == 0:
        text = request.form.get('text2')

        if text == "stop":
            polyline_string.polyline_string = ""
            return render_template('index.html', string=polyline_string.polyline_string)

        if text == "clear":
            data_loader.remove_file_content("tram_loops.json")
            return render_template('index.html', string=polyline_string.polyline_string)

        else:
            text = remove_banned_words_from_input(text.split(','))
            dict = osmnx_response(text, "loop")

            if data_loader.check_if_exist('tram_loops.json'):
                data_loader.append_to_edges(dict['data'], "tram_loops.json")

            else:
                data_loader.create_json("tram_loops.json", dict)

            ox.save_graphml(G, filename='osmnx_graph.graphml')
            make_updated_graph_model()

            return render_template('index.html', string=polyline_string.polyline_string)

    else:

        text = request.form.get('text')
        if text == "clear":
            data_loader.remove_file_content("edges.json")
            return render_template('index.html', string=polyline_string.polyline_string)

        text = remove_banned_words_from_input(text.split(','))
        dict = osmnx_response(text, "remove_edge")

        if data_loader.check_if_exist('edges.json'):
            data_loader.append_to_edges(dict['data'], "edges.json")
        else:
            data_loader.create_json("edges.json", dict)

        ox.save_graphml(G, filename='osmnx_graph.graphml')
        make_updated_graph_model()

        return render_template('index.html', string=polyline_string.polyline_string)


def osmnx_response(coordinates, type):
    """function removes nodes nearest to chosen and saves graph"""

    dict = {}
    dict["type"] = "edges"
    edges = []
    touple = []

    if type == "loop":
        # iterate over  input coordinates and find key for each edge
        for i in range(0, len(coordinates), 2):
            nr_edge = ox.get_nearest_edge(G, (float(coordinates[i]), float(coordinates[i + 1])))

            touple.append([nr_edge[1], nr_edge[2]])

            for i in range(len(G[nr_edge[1]][nr_edge[2]])):
                if str(G[nr_edge[1]][nr_edge[2]][i]['geometry']) == str(nr_edge[0]):
                    key = i
                    touple[-1].append(key)

            # store loop edges in pairs
            if len(touple) == 2:
                edges.append(touple)
                touple = []

            # add chosen loop to poluline_string to visualize it on map
            polyline_string.update_polyline(nr_edge[0])

    else:
        # iterate over  input coordinates and find key for each edge
        for i in range(0, len(coordinates), 2):
            nr_edge = ox.get_nearest_edge(G, (float(coordinates[i]), float(coordinates[i + 1])))

            touple = [nr_edge[1], nr_edge[2]]

            for i in range(len(G[nr_edge[1]][nr_edge[2]])):
                if str(G[nr_edge[1]][nr_edge[2]][i]['geometry']) == str(nr_edge[0]):
                    key = i
                    touple.insert(len(touple), key)

            # add chosen edge to file
            edges.append(touple)
            # remove edge from graph
            G.remove_edge(nr_edge[1], nr_edge[2], key)
            touple = []

    dict["data"] = edges
    print(edges)

    return dict


def make_updated_graph_model():
    """function create updated template (after user modification)  based on graph. Extends graph.html by
        additional html extensions """

    ox.config(log_console=True, use_cache=True)

    G_2 = ox.load_graphml('osmnx_graph.graphml')

    # plot the street network with folium
    graph_map = ox.plot_graph_folium(G_2, edge_width=2)

    # autogenerating html file with graph visualization uased on graph
    filepath = 'templates/graph.html'
    graph_map.save(filepath)
    IFrame(filepath, width=600, height=500)

    soup = BeautifulSoup(open('templates/graph.html'), 'html.parser')

    # given above template is autogenerated so we have to manually insert additional  structures using BeaufifulSoup
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

    # add additional body and style to autogenerated graph template
    data_body = '{% block body %} {% endblock %}'
    data_style = '{% block style %} {% endblock %}'

    soup.body.append(data_body)

    soup.style.append(data_style)
    with open("templates/final_graph.html", "w") as file:
        file.write(str(soup))


def remove_banned_words_from_input(text):
    """removes unnecessary words from input line"""

    banned = ['LatLng', '']
    for t in text:
        if t in banned:
            text.remove(t)
    for t in text:
        if t in banned:
            text.remove(t)
    return text


def run():
    app.run(debug=True, threaded=True)


if __name__ == '__main__':
    run()