from parser import Parser
from parser import Graph

parser = Parser("texto.txt")

try:
    graph = parser.parse_data()
    print(graph)
    print(graph.nb_drones)
    print(graph.start_hub.x)
except Exception as e:
    print(e)


