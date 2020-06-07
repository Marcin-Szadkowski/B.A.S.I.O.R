import string
import random

"""class creates string with leaflet content based on LineString. Generated  string
    is injected into html template and shows graph edges chosen as tram loops in blue"""


class PolyLine_String(object):

    def __init__(self):
        self.polyline_string = ""

    def random_string(self, stringLength):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    def add_to_polyline_string(self, string):
        self.polyline_string = self.polyline_string + string

    def convert_line_string_to_array(self, line_string):
        x = line_string.xy[0]
        y = line_string.xy[1]
        data = []
        for i in range(0, len(x)):
            temp = []
            temp.append(y[i])
            temp.append(x[i])
            data.append(temp)
        return data

    def get_polyline_string(self):
        return self.polyline_string

    def update_polyline(self, linestring):
        arr = self.convert_line_string_to_array(linestring)
        string = self.get_polyline_scheme(arr)
        self.add_to_polyline_string(string)

    def get_polyline_scheme(self, coordinates):
        string = "var poly_line_" + self.random_string(32) + " = L.polyline(" + str(coordinates) + ").addTo(map_id);"
        return string