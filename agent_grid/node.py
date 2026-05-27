"""GridNode: a single node in the agent grid."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeStatus(Enum):
    """Health status of a grid node."""

    HEALTHY = "healthy"
    SUSPECT = "suspect"
    FAILED = "failed"
    OFFLINE = "offline"


@dataclass
class GridNode:
    """Represents a single agent node in the grid.

    Attributes:
        id: Unique identifier (auto-generated if not provided).
        name: Human-readable name.
        capacity: Maximum concurrent tasks this node can handle.
        current_load: Number of tasks currently assigned.
        status: Current health status.
        tags: Arbitrary labels for filtering/routing.
        metadata: Extra key-value data.
        last_heartbeat: Timestamp of the most recent heartbeat.
        neighbors: IDs of directly connected nodes in the topology.
    """

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    capacity: int = 10
    current_load: int = 0
    status: NodeStatus = NodeStatus.HEALTHY
    tags: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)
    last_heartbeat: float = field(default_factory=time.monotonic)
    neighbors: set[str] = field(default_factory=set)

    # ---- convenience helpers ----

    @property
    def available_capacity(self) -> int:
        """How many more tasks this node can accept."""
        return max(0, self.capacity - self.current_load)

    @property
    def utilization(self) -> float:
        """Load as a fraction of capacity (0.0 – 1.0)."""
        return self.current_load / self.capacity if self.capacity else 0.0

    def heartbeat(self) -> None:
        """Record a heartbeat, marking the node healthy."""
        self.last_heartbeat = time.monotonic()
        if self.status == NodeStatus.SUSPECT:
            self.status = NodeStatus.HEALTHY

    def assign_task(self, count: int = 1) -> None:
        """Increment the load counter."""
        self.current_load += count

    def release_task(self, count: int = 1) -> None:
        """Decrement the load counter (floor-clamped at 0)."""
        self.current_load = max(0, self.current_load - count)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "capacity": self.capacity,
            "current_load": self.current_load,
            "status": self.status.value,
            "tags": sorted(self.tags),
            "available_capacity": self.available_capacity,
            "utilization": round(self.utilization, 3),
        }
