"""Topology definitions: mesh, ring, star, tree."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


class Topology(ABC):
    """Base class for grid topologies.

    Subclasses must implement ``connect`` to wire up neighbour relationships
    on a mapping of node_id -> set_of_neighbor_ids.
    """

    @abstractmethod
    def connect(self, node_ids: List[str]) -> Dict[str, Set[str]]:
        """Return a dict mapping each node id to its set of neighbours."""
        ...

    def route(self, adjacency: Dict[str, Set[str]], src: str, dst: str) -> List[str]:
        """BFS shortest-path between *src* and *dst*.

        Returns an empty list when no path exists.
        """
        if src == dst:
            return [src]
        visited: Set[str] = {src}
        queue: deque[tuple[str, List[str]]] = deque([(src, [src])])
        while queue:
            current, path = queue.popleft()
            for neighbor in adjacency.get(current, set()):
                if neighbor == dst:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return []

    def diameter(self, adjacency: Dict[str, Set[str]]) -> int:
        """Longest shortest-path across all node pairs (graph diameter)."""
        node_ids = list(adjacency.keys())
        max_dist = 0
        for i, src in enumerate(node_ids):
            for dst in node_ids[i + 1 :]:
                d = len(self.route(adjacency, src, dst)) - 1
                if d > max_dist:
                    max_dist = d
        return max_dist


class MeshTopology(Topology):
    """Fully connected — every node is a neighbour of every other node."""

    def connect(self, node_ids: List[str]) -> Dict[str, Set[str]]:
        return {nid: set(node_ids) - {nid} for nid in node_ids}


class RingTopology(Topology):
    """Nodes connected in a single cycle (each has exactly 2 neighbours)."""

    def connect(self, node_ids: List[str]) -> Dict[str, Set[str]]:
        adj: Dict[str, Set[str]] = {nid: set() for nid in node_ids}
        n = len(node_ids)
        if n == 0:
            return adj
        for i, nid in enumerate(node_ids):
            adj[nid].add(node_ids[(i - 1) % n])
            adj[nid].add(node_ids[(i + 1) % n])
        return adj


class StarTopology(Topology):
    """Central hub node connected to every other (leaf) node.

    The first node in *node_ids* is the hub.
    """

    def __init__(self, hub_id: Optional[str] = None) -> None:
        self.hub_id = hub_id

    def connect(self, node_ids: List[str]) -> Dict[str, Set[str]]:
        adj: Dict[str, Set[str]] = {nid: set() for nid in node_ids}
        hub = self.hub_id or (node_ids[0] if node_ids else None)
        if hub is None:
            return adj
        for nid in node_ids:
            if nid != hub:
                adj[hub].add(nid)
                adj[nid].add(hub)
        return adj


@dataclass
class _TreeNode:
    id: str
    children: List["_TreeNode"] = field(default_factory=list)


class TreeTopology(Topology):
    """Hierarchical tree with a configurable branching factor.

    The first node in *node_ids* is the root.
    """

    def __init__(self, branching_factor: int = 2) -> None:
        if branching_factor < 1:
            raise ValueError("branching_factor must be >= 1")
        self.branching_factor = branching_factor

    def connect(self, node_ids: List[str]) -> Dict[str, Set[str]]:
        adj: Dict[str, Set[str]] = {nid: set() for nid in node_ids}
        if not node_ids:
            return adj
        # BFS-style assignment of children
        root = _TreeNode(id=node_ids[0])
        queue: deque[_TreeNode] = deque([root])
        idx = 1
        while queue and idx < len(node_ids):
            parent = queue.popleft()
            for _ in range(self.branching_factor):
                if idx >= len(node_ids):
                    break
                child = _TreeNode(id=node_ids[idx])
                parent.children.append(child)
                queue.append(child)
                adj[parent.id].add(child.id)
                adj[child.id].add(parent.id)
                idx += 1
        return adj
