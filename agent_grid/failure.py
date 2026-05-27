"""FailureDetector: heartbeat-based health monitoring for grid nodes."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from .grid import Grid
from .node import NodeStatus


@dataclass
class FailureDetectorConfig:
    """Tuning knobs for the failure detector.

    Attributes:
        suspect_timeout: Seconds without a heartbeat before marking SUSPECT.
        fail_timeout: Seconds without a heartbeat before marking FAILED.
        check_interval: How often (in seconds) :meth:`check` should be called
            in a polling loop.  (Informational only — callers are responsible
            for scheduling.)
    """

    suspect_timeout: float = 5.0
    fail_timeout: float = 15.0
    check_interval: float = 2.0


class FailureDetector:
    """Monitors grid nodes via heartbeat timestamps.

    Nodes that haven't sent a heartbeat within ``suspect_timeout`` are marked
    :attr:`NodeStatus.SUSPECT`; after ``fail_timeout`` they become
    :attr:`NodeStatus.FAILED`.

    Example::

        grid = Grid()
        grid.add_node(name="w1")
        fd = FailureDetector(grid, config=FailureDetectorConfig(suspect_timeout=3, fail_timeout=10))
        fd.check()  # call periodically
    """

    def __init__(
        self,
        grid: Grid,
        config: Optional[FailureDetectorConfig] = None,
        clock: Optional[float] = None,
    ) -> None:
        self.grid = grid
        self.config = config or FailureDetectorConfig()
        # Allow injecting a clock for deterministic testing
        self._clock = clock if clock is not None else time.monotonic()

    def check(self, now: Optional[float] = None) -> Dict[str, NodeStatus]:
        """Scan all nodes and update statuses.

        Returns a mapping of node_id → new status (only nodes whose status
        actually changed).
        """
        t = now if now is not None else self._clock()
        changes: Dict[str, NodeStatus] = {}

        for node in self.grid.nodes.values():
            if node.status == NodeStatus.OFFLINE:
                continue  # manually taken offline; skip

            elapsed = t - node.last_heartbeat
            if elapsed >= self.config.fail_timeout:
                new = NodeStatus.FAILED
            elif elapsed >= self.config.suspect_timeout:
                new = NodeStatus.SUSPECT
            else:
                new = NodeStatus.HEALTHY

            if new != node.status:
                node.status = new
                changes[node.id] = new

        return changes

    def revive(self, node_id: str) -> bool:
        """Manually revive a FAILED node back to HEALTHY."""
        node = self.grid.get_node(node_id)
        if node is None:
            return False
        node.status = NodeStatus.HEALTHY
        node.heartbeat()
        return True

    def take_offline(self, node_id: str) -> bool:
        """Mark a node OFFLINE so the detector skips it."""
        node = self.grid.get_node(node_id)
        if node is None:
            return False
        node.status = NodeStatus.OFFLINE
        return True
