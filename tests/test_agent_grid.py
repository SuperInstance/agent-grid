"""Comprehensive tests for agent_grid."""

import time
import uuid
from unittest.mock import patch

import pytest

from agent_grid import (
    FailureDetector,
    Grid,
    GridNode,
    MeshTopology,
    NodeStatus,
    RingTopology,
    StarTopology,
    TreeTopology,
    WorkDispatcher,
)
from agent_grid.dispatch import Task, TaskStatus
from agent_grid.failure import FailureDetectorConfig


# ── GridNode ──────────────────────────────────────────────────────────────

class TestGridNode:
    def test_defaults(self):
        node = GridNode()
        assert node.id
        assert node.capacity == 10
        assert node.current_load == 0
        assert node.status == NodeStatus.HEALTHY
        assert node.available_capacity == 10
        assert node.utilization == 0.0

    def test_available_capacity(self):
        node = GridNode(capacity=5, current_load=3)
        assert node.available_capacity == 2

    def test_utilization(self):
        node = GridNode(capacity=4, current_load=3)
        assert node.utilization == 0.75

    def test_assign_and_release(self):
        node = GridNode(capacity=5)
        node.assign_task(3)
        assert node.current_load == 3
        node.release_task(1)
        assert node.current_load == 2
        # release clamps at 0
        node.release_task(99)
        assert node.current_load == 0

    def test_heartbeat_clears_suspect(self):
        node = GridNode(status=NodeStatus.SUSPECT)
        node.heartbeat()
        assert node.status == NodeStatus.HEALTHY

    def test_to_dict(self):
        node = GridNode(name="x", capacity=10, tags={"gpu"})
        d = node.to_dict()
        assert d["name"] == "x"
        assert d["status"] == "healthy"
        assert "gpu" in d["tags"]

    def test_unique_ids(self):
        ids = {GridNode().id for _ in range(100)}
        assert len(ids) == 100


# ── Topologies ────────────────────────────────────────────────────────────

class TestMeshTopology:
    def test_fully_connected(self):
        ids = ["a", "b", "c"]
        adj = MeshTopology().connect(ids)
        for nid in ids:
            assert adj[nid] == set(ids) - {nid}

    def test_single_node(self):
        adj = MeshTopology().connect(["solo"])
        assert adj["solo"] == set()

    def test_diameter(self):
        adj = MeshTopology().connect(["a", "b", "c"])
        assert MeshTopology().diameter(adj) == 1


class TestRingTopology:
    def test_ring(self):
        ids = ["a", "b", "c", "d"]
        adj = RingTopology().connect(ids)
        assert adj["a"] == {"d", "b"}
        assert adj["b"] == {"a", "c"}
        assert adj["c"] == {"b", "d"}
        assert adj["d"] == {"c", "a"}

    def test_diameter(self):
        adj = RingTopology().connect(["a", "b", "c", "d"])
        assert RingTopology().diameter(adj) == 2


class TestStarTopology:
    def test_star(self):
        ids = ["hub", "l1", "l2", "l3"]
        adj = StarTopology().connect(ids)
        assert adj["hub"] == {"l1", "l2", "l3"}
        for leaf in ["l1", "l2", "l3"]:
            assert adj[leaf] == {"hub"}

    def test_custom_hub(self):
        ids = ["a", "b", "c"]
        adj = StarTopology(hub_id="b").connect(ids)
        assert adj["b"] == {"a", "c"}

    def test_diameter(self):
        adj = StarTopology().connect(["hub", "l1", "l2"])
        assert StarTopology().diameter(adj) == 2


class TestTreeTopology:
    def test_binary_tree(self):
        ids = ["root", "l", "r", "ll", "lr"]
        adj = TreeTopology(branching_factor=2).connect(ids)
        assert "l" in adj["root"]
        assert "r" in adj["root"]
        assert "ll" in adj["l"]
        assert "lr" in adj["l"]
        assert "root" in adj["l"]  # parent link (tree is bidirectional)

    def test_branching_factor_1(self):
        ids = ["a", "b", "c"]
        adj = TreeTopology(branching_factor=1).connect(ids)
        assert adj["a"] == {"b"}
        assert adj["b"] == {"a", "c"}

    def test_invalid_branching(self):
        with pytest.raises(ValueError):
            TreeTopology(branching_factor=0)


class TestRouting:
    def test_route_same_node(self):
        adj = MeshTopology().connect(["a", "b"])
        assert MeshTopology().route(adj, "a", "a") == ["a"]

    def test_route_no_path(self):
        adj = {"x": set(), "y": set()}
        assert MeshTopology().route(adj, "x", "y") == []

    def test_route_mesh(self):
        adj = MeshTopology().connect(["a", "b", "c"])
        path = MeshTopology().route(adj, "a", "c")
        assert path[0] == "a"
        assert path[-1] == "c"
        assert len(path) == 2


# ── Grid ──────────────────────────────────────────────────────────────────

class TestGrid:
    def test_add_remove_node(self):
        grid = Grid()
        n = grid.add_node(name="w1", capacity=5)
        assert grid.get_node(n.id) is n
        assert grid.remove_node(n.id) is True
        assert grid.get_node(n.id) is None

    def test_rebuild_topology_mesh(self):
        grid = Grid(topology=MeshTopology())
        n1 = grid.add_node(name="a")
        n2 = grid.add_node(name="b")
        grid.rebuild_topology()
        assert n2.id in n1.neighbors
        assert n1.id in n2.neighbors

    def test_route(self):
        grid = Grid(topology=RingTopology())
        ids = [grid.add_node(name=f"n{i}").id for i in range(5)]
        grid.rebuild_topology()
        path = grid.route(ids[0], ids[2])
        assert path[0] == ids[0]
        assert path[-1] == ids[2]
        assert len(path) == 3  # 0->1->2

    def test_healthy_nodes(self):
        grid = Grid()
        n1 = grid.add_node(name="h")
        n2 = grid.add_node(name="f")
        n2.status = NodeStatus.FAILED
        assert len(grid.healthy_nodes()) == 1

    def test_nodes_by_tag(self):
        grid = Grid()
        grid.add_node(name="gpu1", tags={"gpu", "fast"})
        grid.add_node(name="cpu1", tags={"cpu"})
        grid.add_node(name="gpu2", tags={"gpu"})
        assert len(grid.nodes_by_tag("gpu")) == 2

    def test_least_loaded(self):
        grid = Grid()
        a = grid.add_node(name="a", capacity=10)
        b = grid.add_node(name="b", capacity=10)
        a.assign_task(8)
        b.assign_task(2)
        result = grid.least_loaded(1)
        assert result[0] is b

    def test_stats(self):
        grid = Grid()
        grid.add_node(name="a", capacity=10)
        grid.add_node(name="b", capacity=10)
        s = grid.stats()
        assert s["total"] == 2
        assert s["healthy"] == 2
        assert s["capacity"] == 20

    def test_stats_empty(self):
        assert Grid().stats()["total"] == 0


# ── WorkDispatcher ────────────────────────────────────────────────────────

class TestWorkDispatcher:
    def _make_grid(self, n: int = 3, capacity: int = 5, tags=None):
        grid = Grid()
        tag_set = tags or set()
        for i in range(n):
            grid.add_node(name=f"w{i}", capacity=capacity, tags=tag_set)
        grid.rebuild_topology()
        return grid

    def test_submit_and_dispatch(self):
        grid = self._make_grid()
        d = WorkDispatcher(grid)
        t = d.submit(Task(payload="work"))
        assert t.status == TaskStatus.PENDING
        assigned = d.dispatch()
        assert len(assigned) == 1
        assert assigned[0].status == TaskStatus.ASSIGNED

    def test_priority_order(self):
        grid = self._make_grid(n=1, capacity=1)
        d = WorkDispatcher(grid)
        lo = d.submit(Task(payload="lo", priority=1))
        hi = d.submit(Task(payload="hi", priority=10))
        assigned = d.dispatch()
        assert len(assigned) == 1
        assert assigned[0] is hi
        assert lo in d.pending

    def test_required_tags(self):
        grid = Grid()
        grid.add_node(name="gpu1", capacity=5, tags={"gpu"})
        grid.add_node(name="cpu1", capacity=5, tags=set())
        grid.rebuild_topology()
        d = WorkDispatcher(grid)
        t = d.submit(Task(payload="train", required_tags={"gpu"}))
        assigned = d.dispatch()
        assert len(assigned) == 1
        assert assigned[0].assigned_to == grid.nodes_by_tag("gpu")[0].id

    def test_no_capacity_stays_pending(self):
        grid = self._make_grid(n=1, capacity=1)
        d = WorkDispatcher(grid)
        d.submit(Task(payload="t1"))
        d.submit(Task(payload="t2"))
        assigned = d.dispatch()
        assert len(assigned) == 1
        assert len(d.pending) == 1

    def test_complete_releases_load(self):
        grid = self._make_grid(n=1, capacity=5)
        d = WorkDispatcher(grid)
        t = d.submit(Task(payload="t"))
        d.dispatch()
        node = list(grid.nodes.values())[0]
        assert node.current_load == 1
        d.complete(t)
        assert node.current_load == 0
        assert t.status == TaskStatus.COMPLETED

    def test_fail_releases_load(self):
        grid = self._make_grid(n=1, capacity=5)
        d = WorkDispatcher(grid)
        t = d.submit(Task(payload="t"))
        d.dispatch()
        node = list(grid.nodes.values())[0]
        d.fail(t)
        assert node.current_load == 0
        assert t.status == TaskStatus.FAILED

    def test_strategies(self):
        for strat in ("least-loaded", "round-robin"):
            grid = self._make_grid(n=3, capacity=10)
            d = WorkDispatcher(grid, strategy=strat)
            d.submit(Task(payload="t"))
            assigned = d.dispatch()
            assert len(assigned) == 1

    def test_unknown_strategy_raises(self):
        grid = self._make_grid()
        d = WorkDispatcher(grid, strategy="bogus")
        d.submit(Task(payload="t"))
        with pytest.raises(ValueError, match="Unknown strategy"):
            d.dispatch()


# ── FailureDetector ───────────────────────────────────────────────────────

class TestFailureDetector:
    def test_healthy_within_timeout(self):
        grid = Grid()
        grid.add_node(name="w1")
        fd = FailureDetector(grid, config=FailureDetectorConfig(suspect_timeout=5, fail_timeout=15))
        changes = fd.check(now=0)
        assert len(changes) == 0

    def test_suspect_after_timeout(self):
        grid = Grid()
        node = grid.add_node(name="w1")
        node.last_heartbeat = 0  # set heartbeat to time 0
        fd = FailureDetector(grid, config=FailureDetectorConfig(suspect_timeout=5, fail_timeout=15))
        changes = fd.check(now=6)
        assert changes  # should flag suspect
        node = list(grid.nodes.values())[0]
        assert node.status == NodeStatus.SUSPECT

    def test_failed_after_long_timeout(self):
        grid = Grid()
        node = grid.add_node(name="w1")
        node.last_heartbeat = 0
        fd = FailureDetector(grid, config=FailureDetectorConfig(suspect_timeout=5, fail_timeout=15))
        changes = fd.check(now=20)
        assert changes
        node = list(grid.nodes.values())[0]
        assert node.status == NodeStatus.FAILED

    def test_heartbeat_revives(self):
        grid = Grid()
        n = grid.add_node(name="w1")
        fd = FailureDetector(grid, config=FailureDetectorConfig(suspect_timeout=5, fail_timeout=15))
        fd.check(now=6)  # suspect
        n.heartbeat()
        fd.check(now=7)  # should be healthy again
        assert n.status == NodeStatus.HEALTHY

    def test_manual_revive(self):
        grid = Grid()
        n = grid.add_node(name="w1")
        n.status = NodeStatus.FAILED
        fd = FailureDetector(grid)
        assert fd.revive(n.id) is True
        assert n.status == NodeStatus.HEALTHY

    def test_take_offline_skipped(self):
        grid = Grid()
        n = grid.add_node(name="w1")
        fd = FailureDetector(grid, config=FailureDetectorConfig(suspect_timeout=5, fail_timeout=15))
        fd.take_offline(n.id)
        assert n.status == NodeStatus.OFFLINE
        changes = fd.check(now=999)
        assert n.id not in changes

    def test_revive_nonexistent(self):
        fd = FailureDetector(Grid())
        assert fd.revive("nope") is False

    def test_offline_nonexistent(self):
        fd = FailureDetector(Grid())
        assert fd.take_offline("nope") is False


# ── Integration ───────────────────────────────────────────────────────────

class TestIntegration:
    def test_full_workflow(self):
        """End-to-end: create grid, add nodes, dispatch work, detect failures."""
        grid = Grid(topology=MeshTopology())
        n1 = grid.add_node(name="worker-1", capacity=3, tags={"compute"})
        n2 = grid.add_node(name="worker-2", capacity=5, tags={"compute", "gpu"})
        grid.rebuild_topology()

        # Dispatch tasks
        d = WorkDispatcher(grid, strategy="least-loaded")
        tasks = [d.submit(Task(payload=f"job-{i}", priority=i)) for i in range(5)]
        assigned = d.dispatch()
        assert len(assigned) == 5

        # Complete some
        for t in assigned[:3]:
            d.complete(t)
        assert len(d.completed) == 3

        # Failure detection
        fd = FailureDetector(grid, config=FailureDetectorConfig(suspect_timeout=5, fail_timeout=10))
        changes = fd.check(now=1000)
        assert len(changes) == 0

        # Simulate time passing
        changes = fd.check(now=1012)
        for node in grid.nodes.values():
            assert node.status in (NodeStatus.SUSPECT, NodeStatus.HEALTHY)

    def test_grid_with_ring_topology_routing(self):
        grid = Grid(topology=RingTopology())
        ids = [grid.add_node(name=f"n{i}").id for i in range(6)]
        grid.rebuild_topology()

        # In a ring of 6, max distance is 3
        path = grid.route(ids[0], ids[3])
        assert len(path) == 4  # 0->1->2->3
        assert path[0] == ids[0]
        assert path[-1] == ids[3]
