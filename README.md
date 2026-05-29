# agent-grid — Mesh Topology for Distributed Agents

**Grid-based agent communication with mesh, ring, star, and tree topologies. Failure detection and workload dispatch.**

## What This Gives You

- **Grid nodes** — register agents as nodes with status tracking (ACTIVE, IDLE, OVERLOADED, OFFLINE)
- **Multiple topologies** — mesh, ring, star, tree — pick the right one for your coordination pattern
- **Work dispatching** — distribute tasks across the grid with load balancing
- **Failure detection** — heartbeat-based failure detection with configurable timeouts
- **Pure Python** — no external dependencies

## Quick Start

```bash
pip install agent-grid
```

```python
from agent_grid import Grid, GridNode, MeshTopology, WorkDispatcher

# Create a grid with mesh topology
grid = Grid(topology=MeshTopology())
grid.add_node(GridNode(id="agent-1", capabilities=["python"]))
grid.add_node(GridNode(id="agent-2", capabilities=["rust"]))
grid.add_node(GridNode(id="agent-3", capabilities=["docs"]))

# Dispatch work
dispatcher = WorkDispatcher(grid)
task = Task(title="Build API", requirements=["python"])
assigned = dispatcher.dispatch(task)
print(f"Assigned to: {assigned.node_id}")

# Topology-aware routing
neighbors = grid.get_neighbors("agent-1")
print(f"Neighbors: {[n.id for n in neighbors]}")
```

## API Reference

### `Grid(topology)` — Node management and topology queries
### `GridNode(id, capabilities, status=ACTIVE)` — Agent node representation
### `Topology` / `MeshTopology` / `RingTopology` / `StarTopology` / `TreeTopology`
### `WorkDispatcher(grid)` — Task → node assignment with load balancing
### `FailureDetector(timeout)` — Heartbeat monitoring and node liveness

## How It Fits

The network layer for the [SuperInstance fleet](https://github.com/SuperInstance). Agents register on the grid, work is dispatched by topology-aware routing.

- **[captain](https://github.com/SuperInstance/captain)** — Fleet commanding (uses grid for coordination)
- **[cluster-orchestrator](https://github.com/SuperInstance/cluster-orchestrator)** — Cluster orchestration
- **[cocapn-com](https://github.com/SuperInstance/cocapn-com)** — Message routing

## Testing

```bash
pytest tests/
```

## Installation

```bash
pip install agent-grid
```

Python 3.10+. MIT license.
