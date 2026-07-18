from parser import Parser
from parser import Graph

parser = Parser("texto.txt")

try:
    graph = parser.parse_data()
    print(graph)
except Exception as e:
    print(e)


