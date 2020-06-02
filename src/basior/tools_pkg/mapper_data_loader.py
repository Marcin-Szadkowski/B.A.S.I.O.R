import json


class MapDataLoader(object):

    def __init__(self):
        self.loops = self.get_loop_data()
        self.deleted_edges = self.get_deleted_edges()

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
