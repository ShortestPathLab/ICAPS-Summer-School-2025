import MAPF
from .types import GetPath


def naive(get_path: GetPath):
    """
    Creates a planner that plans for all agents, any time there's a missing path, even if other agents are already planned.
    This planner does not replan on unsuccessful commits.
    """

    def plan(
        env: MAPF.SharedEnvironment, paths: list[list], last_did_error: bool = False
    ):
        if last_did_error:
            raise RuntimeError("Error: Last action did not successfully commit.")
        # If there's ANY paths that's not planned, plan entire thing
        # Should return new paths
        if any(not p for p in paths):
            return [get_path(env, i) for i, _ in enumerate(paths)]
        else:
            return paths

    return plan


def unplanned_only(get_path: GetPath):
    """
    Creates a planner that plans for only agents with missing paths.
    This planner does not replan on unsuccessful commits.
    """

    def plan(
        env: MAPF.SharedEnvironment, paths: list[list], last_did_error: bool = False
    ):
        if last_did_error:
            raise RuntimeError("Error: Last action did not successfully commit.")
        return [p if p else get_path(env, i) for i, p in enumerate(paths)]

    return plan
