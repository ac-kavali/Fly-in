from parser import Parser
from parser import Graph

parser = Parser("texto.txt")

graph = parser.parse_data()


for connection in graph.connections:
    print(connection.HubA + ":" + connection.HubB)
    if connection.metadata :
        print( "metadata: "+ connection.metadata , end=" \n")
