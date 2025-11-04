import MAPF
from .types import GetPath


def naive(get_path: GetPath):
    """Creates a planner that plans for all agents, any time there's a missing path, even if other agents are already planned"""

    def plan(
        env: MAPF.SharedEnvironment,
        paths: list[list],
    ):
        # If there's ANY paths that's not planned, plan entire thing
        # Should return new paths
        if any(not p for p in paths):
            return [get_path(env, i) for i, _ in enumerate(paths)]
        else:
            return paths

    return plan


def unplanned_only(get_path: GetPath):
    """Creates a planner that plans for only agents with missing paths"""

    def plan(
        env: MAPF.SharedEnvironment,
        paths: list[list],
    ):
        return [p if p else get_path(env, i) for i, p in enumerate(paths)]

    return plan
