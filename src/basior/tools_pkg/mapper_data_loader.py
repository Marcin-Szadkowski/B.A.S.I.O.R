import json
import os


class MapDataLoader(object):

    def __init__(self):
        self.loops = self.get_loop_data()
        self.deleted_edges = self.get_deleted_edges()

    def append_to_loops_data(self, data):
        for i in range(len(data)):
            self.loops.append(data[i])


        file = open('tram_loops.json.json', )
        f = json.load(file)
        f['data'] = self.loops
        file.close()

    def append_to_edges_data(self, data):
        for i in range(len(data)):
            self.deleted_edges.append(data[i])

        file = open('edges.json', )
        f = json.load(file)
        f['data'] = self.deleted_edges
        file.close()

    def create_edges_json(self,dict):
        with open("edges.json", "w") as output:
            json.dump(dict, output)

    def create_loops_json(self, dict):
        with open("tram_loops.json", "w") as output:
            json.dump(dict, output)


    def get_loop_data(self):
        file = open('edges.json', )
        data = json.load(file)
        file.close()

        return data['data']

    def get_deleted_edges(self):
        file = open('tram_loops.json', )
        data = json.load(file)
        file.close()

        return data['data']




loader = MapDataLoader()
print(loader.loops)
print(loader.deleted_edges)
