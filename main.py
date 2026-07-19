from parser import Parser
from parser import Graph

parser = Parser("texto.txt")

graph = parser.parse_data()
print(graph)
