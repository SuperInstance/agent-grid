# agent-grid

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-47%20passing-green.svg)]()

Mesh topology for distributed agent communication and workload distribution.

> **Note:** This repo also contains a TypeScript/React UI component library under `src/`. The Python package lives in `agent_grid/`.

## Install

```bash
pip install agent-grid
# or for dev
pip install -e ".[dev]"
```

No external dependencies beyond the standard library (pytest for tests).

## Quick Start

```python
from agent_grid import Grid, MeshTopology, WorkDispatcher, Task, FailureDetector

# 1. Create a grid with mesh topology
grid = Grid(topology=MeshTopology())
n1 = grid.add_node(name="worker-1", capacity=5, tags={"compute"})
n2 = grid.add_node(name="worker-2", capacity=10, tags={"compute", "gpu"})
n3 = grid.add_node(name="worker-3", capacity=8, tags={"storage"})
grid.rebuild_topology()

# 2. Check routing
path = grid.route(n1, n3)
print(f"Route: {' → '.join(path)}")  # Route: worker-1 → worker-3 (mesh = direct)

# 3. Dispatch work
dispatcher = WorkDispatcher(grid, strategy="least-loaded")
tasks = [
    dispatcher.submit(Task(payload="train model", priority=5, required_tags={"gpu"})),
    dispatcher.submit(Task(payload="process data", priority=2)),
    dispatcher.submit(Task(payload="store results", required_tags={"storage"})),
]
assigned = dispatcher.dispatch()
for t in assigned:
    print(f"Task '{t.payload}' → node {t.assigned_to}")

# 4. Monitor health
fd = FailureDetector(grid)
changes = fd.check()
for node_id, status in changes.items():
    print(f"Node {node_id} → {status.value}")
```

## Topologies

```python
from agent_grid import RingTopology, StarTopology, TreeTopology

# Ring: each node connects to 2 neighbors
ring_grid = Grid(topology=RingTopology())

# Star: hub-and-spoke (first node is hub by default)
star_grid = Grid(topology=StarTopology())
# or specify a hub:
star_grid = Grid(topology=StarTopology(hub_id="my-hub"))

# Tree: hierarchical with configurable branching
tree_grid = Grid(topology=TreeTopology(branching_factor=3))
```

## Work Dispatcher Strategies

| Strategy | Description |
|---|---|
| `"least-loaded"` | Picks the eligible node with lowest utilization (default) |
| `"round-robin"` | Cycles through eligible nodes in order |
| `"random"` | Picks randomly from eligible nodes |

## Failure Detection

```python
from agent_grid.failure import FailureDetectorConfig

config = FailureDetectorConfig(
    suspect_timeout=5.0,   # seconds before marking SUSPECT
    fail_timeout=15.0,     # seconds before marking FAILED
    check_interval=2.0,    # suggested polling interval
)

fd = FailureDetector(grid, config=config)

# Call periodically in your event loop
changes = fd.check()  # returns {node_id: new_status} for changed nodes

# Manual control
fd.revive("node-id")        # FAILED → HEALTHY
fd.take_offline("node-id")  # skip this node in checks
```

## API Reference

### `GridNode`

| Property | Type | Description |
|---|---|---|
| `id` | `str` | Unique identifier (auto-generated) |
| `name` | `str` | Human-readable name |
| `capacity` | `int` | Max concurrent tasks (default: 10) |
| `current_load` | `int` | Currently assigned tasks |
| `status` | `NodeStatus` | HEALTHY / SUSPECT / FAILED / OFFLINE |
| `tags` | `set[str]` | Labels for filtering and routing |
| `neighbors` | `set[str]` | Connected node IDs |
| `available_capacity` | `int` | `capacity - current_load` |
| `utilization` | `float` | `current_load / capacity` (0.0–1.0) |

### `Grid`

| Method | Description |
|---|---|
| `add_node(name, capacity, tags)` | Register a new node |
| `remove_node(node_id)` | Remove a node |
| `rebuild_topology()` | Re-wire neighbor connections |
| `route(src, dst)` | Shortest path between nodes |
| `healthy_nodes()` | List of HEALTHY nodes |
| `nodes_by_tag(tag)` | Filter by tag |
| `least_loaded(n)` | N least-utilized nodes |
| `stats()` | Grid-wide statistics dict |

### `Task`

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Auto-generated unique ID |
| `payload` | `Any` | Task data / description |
| `priority` | `int` | Higher = dispatched first |
| `required_tags` | `set[str]` | Node must have all these tags |
| `status` | `TaskStatus` | PENDING / ASSIGNED / COMPLETED / FAILED |

## Development

```bash
pip install -e ".[dev]"
python -m pytest tests/ -q
```

## License

MIT
