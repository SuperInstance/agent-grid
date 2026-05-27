"""Grid: manages mesh topology and node discovery."""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Set

from .node import GridNode, NodeStatus
from .topology import Topology, MeshTopology


class Grid:
    """Central registry that owns a collection of :class:`GridNode` instances
    and wires them together with a :class:`Topology`.

    Example::

        grid = Grid(topology=MeshTopology())
        n1 = grid.add_node(name="worker-1", capacity=5)
        n2 = grid.add_node(name="worker-2", capacity=8)
        grid.rebuild_topology()
        path = grid.route(n1, n2)
    """

    def __init__(self, topology: Optional[Topology] = None) -> None:
        self.nodes: Dict[str, GridNode] = {}
        self.topology = topology or MeshTopology()
        self._adjacency: Dict[str, Set[str]] = {}

    # ---- node management ----

    def add_node(
        self,
        name: str = "",
        capacity: int = 10,
        tags: Optional[Set[str]] = None,
        node_id: Optional[str] = None,
    ) -> GridNode:
        """Create a new node and register it in the grid."""
        node = GridNode(
            id=node_id or GridNode().id,
            name=name,
            capacity=capacity,
            tags=tags or set(),
        )
        self.nodes[node.id] = node
        return node

    def remove_node(self, node_id: str) -> bool:
        """Remove a node. Returns True if the node existed."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            return True
        return False

    def get_node(self, node_id: str) -> Optional[GridNode]:
        return self.nodes.get(node_id)

    # ---- topology ----

    def rebuild_topology(self) -> None:
        """Re-wire neighbour relationships based on the current topology."""
        ids = list(self.nodes.keys())
        self._adjacency = self.topology.connect(ids)
        for nid, neighbors in self._adjacency.items():
            if nid in self.nodes:
                self.nodes[nid].neighbors = neighbors

    @property
    def adjacency(self) -> Dict[str, Set[str]]:
        if not self._adjacency:
            self.rebuild_topology()
        return self._adjacency

    def route(self, src: GridNode | str, dst: GridNode | str) -> List[str]:
        """Shortest path between two nodes (list of node IDs)."""
        src_id = src.id if isinstance(src, GridNode) else src
        dst_id = dst.id if isinstance(dst, GridNode) else dst
        return self.topology.route(self.adjacency, src_id, dst_id)

    # ---- queries ----

    def healthy_nodes(self) -> List[GridNode]:
        return [n for n in self.nodes.values() if n.status == NodeStatus.HEALTHY]

    def nodes_by_tag(self, tag: str) -> List[GridNode]:
        return [n for n in self.nodes.values() if tag in n.tags]

    def least_loaded(self, count: int = 1) -> List[GridNode]:
        """Return the *count* nodes with the lowest utilization."""
        sorted_nodes = sorted(self.nodes.values(), key=lambda n: n.utilization)
        return sorted_nodes[:count]

    def stats(self) -> Dict[str, int | float]:
        nodes = list(self.nodes.values())
        if not nodes:
            return {"total": 0, "healthy": 0, "capacity": 0, "load": 0, "utilization": 0.0}
        healthy = [n for n in nodes if n.status == NodeStatus.HEALTHY]
        total_cap = sum(n.capacity for n in nodes)
        total_load = sum(n.current_load for n in nodes)
        return {
            "total": len(nodes),
            "healthy": len(healthy),
            "capacity": total_cap,
            "load": total_load,
            "utilization": round(total_load / total_cap, 3) if total_cap else 0.0,
        }
