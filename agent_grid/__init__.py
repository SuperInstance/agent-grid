"""agent-grid: Mesh topology for distributed agent communication and workload distribution."""

from .node import GridNode, NodeStatus
from .grid import Grid
from .topology import Topology, MeshTopology, RingTopology, StarTopology, TreeTopology
from .dispatch import WorkDispatcher, Task
from .failure import FailureDetector

__version__ = "0.1.0"
__all__ = [
    "Grid",
    "GridNode",
    "NodeStatus",
    "Topology",
    "MeshTopology",
    "RingTopology",
    "StarTopology",
    "TreeTopology",
    "WorkDispatcher",
    "Task",
    "FailureDetector",
]
