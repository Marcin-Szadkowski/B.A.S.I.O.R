import json
import os


class MapDataLoader(object):

    """class responsible for extracting data created by mapper tool, as well as
    clearing, appending data in existing json files"""

    def __init__(self):
        self.loops = self.get_loop_data()
        self.deleted_edges = self.get_deleted_edges()

    def create_edges_json(self, dict):
        """creates json file for removed edges"""

        with open("edges.json", "w") as output:
            json.dump(dict, output)

    def create_loops_json(self, dict):
        """creates json file chosen tram loops"""

        with open("tram_loops.json", "w") as output:
            json.dump(dict, output)

    def get_loop_data(self):
        """extract actual list of edges coordinates from edges file"""

        if self.check_if_exist('edges.json'):
            file = open('edges.json', )
            data = json.load(file)
            file.close()

            return data['data']


    def get_deleted_edges(self):
        """extract actual list of loop coordinates from tram_loops file"""

        if self.check_if_exist('tram_loops.json'):
            file = open('tram_loops.json', )
            data = json.load(file)
            file.close()

            return data['data']


    def write_json(self, data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f)

    def append_to_edges(self, arr, filename):
        """append data about chosen edges to given file,
         useful when data collecting lasts more than one application session
        """

        with open(filename) as json_file:
            data = json.load(json_file)

            temp = data['data']

            for i in range(len(arr)):
                temp.append(arr[i])

        self.write_json(data, filename)

    def check_if_exist(self, filename):
        """function checks if file is empty"""

        if os.stat(filename).st_size == 0:
            return False
        else:
            return True

    def create_json(self, filename, dict):
        with open(filename, "w") as output:
            json.dump(dict, output)


    def remove_file_content(self, filename):
        """function removes  content of given file"""

        file = open(filename, "r+")
        file.truncate(0)
        file.close()