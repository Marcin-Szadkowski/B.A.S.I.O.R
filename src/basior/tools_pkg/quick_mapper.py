import osmnx as ox
from IPython.display import IFrame
#quick_mapper.py
from scrapy.http import HtmlResponse
import bs4 as bs
from bs4 import BeautifulSoup


def make_updated_graph_model():
    ox.config(log_console=True, use_cache=True)

    G = ox.load_graphml('osmnx_graph.graphml')

    # plot the street network with folium
    graph_map = ox.plot_graph_folium(G, edge_width=2)

    filepath = 'templates/graph.html'
    graph_map.save(filepath)
    IFrame(filepath, width=600, height=500)


    soup = BeautifulSoup(open('templates/graph.html'), 'html.parser')

    js_tag = soup.find_all("script")
    js_tag[5].append('{% block script %} {% endblock %}')
    print(js_tag[5])

    with open("templates/graph.html", "w") as file:
        file.write(str(soup))

    soup.find("div")
    div = soup.find("div")
    div = str(div).split()
    map_id = div[2][4:-8]

    fin = open("templates/graph.html", "rt")
    #output file to write the result to
    fout = open("templates/final_graph.html", "wt")
    #for each line in the input file
    for line in fin:
        #read replace the string and write to output file
        fout.write(line.replace(map_id, 'map_id'))
    #close input and output files
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
    #fig,ax = ox.plot_graph(G)"""
