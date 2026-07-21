from parser import Parser
from cli import cla_parser

arguments = cla_parser()
parser = Parser(arguments.map)

graph = parser.parse_data()



print(f"number of drones: {graph.nb_drones}")
print(f"Start hub : name: {graph.start_hub.name}  x={graph.start_hub.x} , y={graph.start_hub.y} , "
      f"\nmetadata: zone type: {graph.start_hub.metadata.zone.value}"
      f"\ncolor: {graph.start_hub.metadata.color}"
      f"\nmax drones: {graph.start_hub.metadata.max_drones}\n")


print(f"End hub : name: {graph.end_hub.name}  x={graph.end_hub.x} , y={graph.end_hub.y}, "
      f"\nmetadata: zone type: {graph.end_hub.metadata.zone.value}"
      f"\ncolor: {graph.end_hub.metadata.color}"
      f"\nmax drones: {graph.end_hub.metadata.max_drones}\n")
print()

for hub in graph.hubs:
    print(f"hub : name: {hub.name}  x={hub.x} , y={hub.y}, "
          f"\nmetadata: zone type: {hub.metadata.zone.value}"
          f"\ncolor: {hub.metadata.color}"
          f"\nmax drones: {hub.metadata.max_drones}\n")

for connection in graph.connections:
    print(f"Connection {connection.HubA}<->{connection.HubB} max_link: {connection.max_link_capacity}")
