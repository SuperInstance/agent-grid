"""WorkDispatcher: load-aware task distribution across grid nodes."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .grid import Grid
from .node import GridNode, NodeStatus


class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """A unit of work to be dispatched to a grid node.

    Attributes:
        id: Unique task identifier.
        payload: Arbitrary task description / data.
        priority: Higher number = higher priority (default 0).
        required_tags: Node must have ALL these tags to be eligible.
        assigned_to: ID of the node this task is assigned to (set after dispatch).
        status: Current lifecycle status.
        created_at: Timestamp when the task was created.
    """

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    payload: Any = None
    priority: int = 0
    required_tags: set[str] = field(default_factory=set)
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.monotonic)


class WorkDispatcher:
    """Distributes tasks across grid nodes based on load and eligibility.

    Strategies:
      - ``"least-loaded"`` (default): pick the eligible node with the lowest
        utilization.
      - ``"random"``: pick uniformly at random from eligible nodes.
      - ``"round-robin"``: cycle through eligible nodes in order.

    Example::

        grid = Grid()
        grid.add_node(name="w1", capacity=5)
        grid.add_node(name="w2", capacity=10)
        grid.rebuild_topology()

        dispatcher = WorkDispatcher(grid)
        t = dispatcher.submit(Task(payload="crawl page", required_tags={"scraper"}))
        dispatcher.dispatch()
    """

    def __init__(
        self,
        grid: Grid,
        strategy: str = "least-loaded",
    ) -> None:
        self.grid = grid
        self.strategy = strategy
        self.pending: List[Task] = []
        self.completed: List[Task] = []
        self._rr_index = 0

    # ---- submit / dispatch ----

    def submit(self, task: Task) -> Task:
        """Add a task to the pending queue."""
        self.pending.append(task)
        return task

    def dispatch(self) -> List[Task]:
        """Attempt to assign all pending tasks to eligible nodes.

        Tasks that cannot be assigned (no eligible node has capacity) remain
        in ``self.pending``.  Returns the list of newly-assigned tasks.
        """
        assigned: List[Task] = []
        still_pending: List[Task] = []

        # Process highest-priority first
        self.pending.sort(key=lambda t: -t.priority)

        for task in self.pending:
            node = self._select_node(task)
            if node is not None:
                task.assigned_to = node.id
                task.status = TaskStatus.ASSIGNED
                node.assign_task()
                assigned.append(task)
            else:
                still_pending.append(task)

        self.pending = still_pending
        return assigned

    def complete(self, task: Task) -> None:
        """Mark a task as completed and release the node's load."""
        if task.assigned_to:
            node = self.grid.get_node(task.assigned_to)
            if node:
                node.release_task()
        task.status = TaskStatus.COMPLETED
        self.completed.append(task)

    def fail(self, task: Task) -> None:
        """Mark a task as failed and release the node's load."""
        if task.assigned_to:
            node = self.grid.get_node(task.assigned_to)
            if node:
                node.release_task()
        task.status = TaskStatus.FAILED

    # ---- internal ----

    def _eligible_nodes(self, task: Task) -> List[GridNode]:
        """Healthy nodes with capacity and matching tags."""
        results: List[GridNode] = []
        for n in self.grid.healthy_nodes():
            if n.available_capacity <= 0:
                continue
            if task.required_tags and not task.required_tags.issubset(n.tags):
                continue
            results.append(n)
        return results

    def _select_node(self, task: Task) -> Optional[GridNode]:
        eligible = self._eligible_nodes(task)
        if not eligible:
            return None

        if self.strategy == "least-loaded":
            return min(eligible, key=lambda n: n.utilization)
        elif self.strategy == "random":
            import random
            return random.choice(eligible)
        elif self.strategy == "round-robin":
            node = eligible[self._rr_index % len(eligible)]
            self._rr_index += 1
            return node
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
