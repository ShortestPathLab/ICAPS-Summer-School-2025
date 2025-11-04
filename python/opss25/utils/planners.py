import MAPF
from .types import BindStartKit


def naive(create_search_engine: BindStartKit):
    """
    Creates a planner that plans for all agents, any time there's a missing path, even if other agents are already planned.
    This planner does not replan on unsuccessful commits.
    """

    run_search = create_search_engine()

    def plan(
        env: MAPF.SharedEnvironment, paths: list[list], last_did_error: bool = False
    ):
        if last_did_error:
            raise RuntimeError("Error: Last action did not successfully commit.")
        # If there's ANY paths that's not planned, plan entire thing
        # Should return new paths
        if any(not p for p in paths):
            return [run_search(env, i) for i, _ in enumerate(paths)]
        else:
            return paths

    return plan


def unplanned_only(create_search_engine: BindStartKit):
    """
    Creates a planner that plans for only agents with missing paths.
    This planner does not replan on unsuccessful commits.
    """

    run_search = create_search_engine()

    def plan(
        env: MAPF.SharedEnvironment, paths: list[list], last_did_error: bool = False
    ):
        if last_did_error:
            raise RuntimeError("Error: Last action did not successfully commit.")
        return [p if p else run_search(env, i) for i, p in enumerate(paths)]

    return plan
