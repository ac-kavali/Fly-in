*This project has been created by as part of the 42 curriculum by achahi

# Drone Fleet Pathfinding Simulator

## Description

This project simulates the routing of a fleet of autonomous drones through a network of hubs (zones) connected by links. Given a map description file, the program computes a conflict-free path for every drone — from a shared **start hub** to a shared **end hub** — while respecting:

- **Zone capacities** (how many drones can occupy a hub at the same time),
- **Connection capacities** (how many drones can travel along a given link at the same time),
- **Zone types**, which affect traversal cost and priority (`normal`, `priority`, `restricted`, `blocked`),
- **Time-based reservations**, so that no two drones ever collide in the same zone or on the same connection at the same turn.

The result is a turn-by-turn simulation showing where every drone is at every point in time, printed directly to the terminal with color-coded zones.

The project is composed of four main parts:

| Module | Responsibility |
|---|---|
| `cli.py` | Parses command-line arguments (the map file path). |
| `parser.py` | Reads and validates the map configuration file, builds the `Graph`. |
| `models.py` | Defines the core data structures: `Hub`, `HubMetadata`, `Connection`, `Graph`, `ZoneType`. |
| `path_finding.py` | Implements the `ReservationTable` and the Dijkstra-based `Pathfinder`. |
| `terminal_output.py` | Renders the simulation turn by turn in the terminal, with colorized zones. |
| `main.py` | Orchestrates the whole simulation: parsing → pathfinding → reservation → output. |

## Instructions

### Requirements

- Python 3.10+ (the project uses modern type hints such as `str | None` and `list[tuple[str, int]]`).

### Running the project

```bash
python main.py <path_to_map_file>
```

For example:

```bash
python main.py maps/example.map
```

If the map file is invalid (missing sections, duplicate hubs, malformed connections, etc.), the program prints a descriptive error and exits with a non-zero status code instead of running the simulation.

### Map file format

A map file is a plain text file describing:

- The number of drones to route (`nb_drones:`), which must be the first non-comment line.
- Exactly one `start_hub:` and one `end_hub:`.
- Any number of intermediate `hub:` lines.
- Any number of `connection:` lines linking two hubs together.
- Optional `#` comments, either on their own line or trailing after content.

Each hub line follows the pattern:

```
hub: <name> <x> <y> [zone=<type> color=<name> max_drones=<n>]
```

Each connection line follows the pattern:

```
connection: <HubA>-<HubB> [max_link_capacity=<n>]
```

Metadata blocks (in `[...]`) are optional; sensible defaults are used when omitted (`zone=normal`, `max_drones=1`, `max_link_capacity=1`).

## Algorithm explanation

The pathfinding approach is a **modified Dijkstra's algorithm operating over time**, rather than only over space. Each state explored by the algorithm is a pair `(zone_name, turn)` instead of just a zone, which is what allows the algorithm to reason about *when* a drone is somewhere, not just *where*.

For every drone (processed one at a time, in order):

1. A priority queue (min-heap) is initialized with the start hub at turn 0.
2. At each step, the algorithm pops the state with the lowest `(turn, priority)` — `priority` favors `PRIORITY`-type zones, letting drones prefer priority routes when the cost is otherwise equal.
3. From the current zone, the algorithm considers two kinds of moves:
   - **Waiting** one turn in the current zone (useful when a path is temporarily congested).
   - **Moving** to each neighboring zone that isn't `BLOCKED`, at a cost in turns equal to that neighbor's movement cost (derived from its `ZoneType`).
4. Before a move is accepted, the algorithm checks the shared **`ReservationTable`**:
   - Is there capacity left in the destination zone at the arrival turn?
   - Is there capacity left on the connection for every intermediate turn the drone would occupy it?
5. Once a drone reaches the end hub, its full path (as a list of `(zone_name, turn)` pairs) is returned, and every zone/connection it uses is immediately reserved in the shared table — so the *next* drone's search already accounts for it.

This turn-aware, reservation-based design is what prevents collisions between drones without needing a fully centralized joint-state search (which would be exponential in the number of drones). Instead, each drone solves a single-agent shortest path problem against a reservation table that accumulates the commitments of every drone processed before it — a common and efficient approach to multi-agent pathfinding.

## Visual representation

The `TerminalOutput` module turns the raw turn-by-turn data into a readable, color-coded terminal simulation:

- Each drone's movement is grouped **by turn**, so the user sees, turn after turn, which drones are where.
- Zones are **colorized** based on either an explicit `color=` metadata value, or a fallback color derived from the zone's `ZoneType`:
  - Restricted zones → red
  - Priority zones → green
  - Blocked zones → gray
  - Normal zones → white (default)
- Multi-turn movements (zones that cost more than one turn to traverse) are shown as an explicit `DroneID-From-To` transition on the turn *before* arrival, in addition to the arrival itself — making it clear when a drone is "in transit" versus stationary at a hub.
- A final summary line reports the total number of turns needed to route the entire fleet.

This visual layer matters because the underlying data is otherwise just a list of coordinates and turn numbers — the colorization and per-turn grouping let a user immediately see congestion points, priority routing in action, and how drones share the network over time, without having to manually cross-reference zone types or timestamps.

## Example

### Example input (`example.map`)

```
nb_drones: 2
start_hub: A 0 0
hub: B 1 0 [zone=priority]
hub: C 1 1 [zone=restricted max_drones=1]
end_hub: D 2 0
connection: A-B
connection: B-D
connection: A-C
connection: C-D [max_link_capacity=1]
```

### Expected output

```
Turn 1: D1-B D2-C
Turn 2: D1-D D2-C-D
Turn 3: D2-D

Total turns: 3
```

*(In an actual terminal, zone names such as `B`, `C`, and `D` are printed in color according to their zone type — green for the priority zone `B`, red for the restricted zone `C`, and white for the default-type hubs.)*

The first drone takes the priority route through `B` and reaches `D` in 2 turns. The second drone, unable to share the single-capacity restricted zone `C` at the same time, is naturally staggered by the reservation table and reaches `D` one turn later — demonstrating how the reservation system resolves contention without any explicit conflict-avoidance code path per drone.