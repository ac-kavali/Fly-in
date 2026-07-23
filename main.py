from models import ZoneType
from parser import Parser
from cli import cla_parser
import heapq

arguments = cla_parser()
parser = Parser(arguments.map)
graph = parser.parse_data()


start = graph.start_hub.name

all_candidate_hubs = {_hub.name : _hub for _hub in graph.hubs if _hub.metadata.zone != ZoneType.BLOCKED}
all_candidate_hubs[graph.end_hub.name] = graph.end_hub
all_candidate_hubs[graph.start_hub.name] = graph.start_hub

visited = []
shortest_paths = []

links_table = {
    hub_obj.name: (None, float("inf"))
    for hub,hub_obj in all_candidate_hubs.items()
}

zone_cost_dict = {
    ZoneType.PRIORITY: 1,
    ZoneType.RESTRICTED: 2,
    ZoneType.NORMAL: 1
}

links_table[start] = (None, 0)
current = start
while all_candidate_hubs:
    print(f"All_candidate: {all_candidate_hubs.keys()}")
    if current in visited:
        continue
    visited.append(current)
    print(f"visited: {visited}")
    last, last_cost = links_table[current]

    for hub_name, hub_ob in all_candidate_hubs.items():
        if frozenset((current, hub_name)) in parser.check_conn:
            zone_cost = zone_cost_dict[hub_ob.metadata.zone]
            new_cost = zone_cost + last_cost if last_cost != float("inf") else zone_cost
            if new_cost < links_table[hub_name][1]:
                priority = 0 if hub_ob.metadata.zone == ZoneType.PRIORITY else 1
                links_table[hub_name] = (current, new_cost)
                heapq.heappush(shortest_paths, (new_cost, priority, hub_name))
                print(shortest_paths)

    all_candidate_hubs.pop(current)
    if not shortest_paths:
        break
    print(f"shortest Paths: {shortest_paths}")
    current = heapq.heappop(shortest_paths)[2]
    print(f"current: {current}")


path = [graph.end_hub.name]
current = graph.end_hub.name
print(links_table)

while current != start :
    last, _ = links_table[current]
    path.append(last)
    current = last

print(path[::-1])



# except Exception as e:
#     print(e)