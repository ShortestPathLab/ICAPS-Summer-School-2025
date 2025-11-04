# ──────────────────────────────────────────────────────────────────────────────
#
# TASK 4: GET FAMILIAR WITH THE PLANNER INSTANTIATION CODE
#
# You don't have to do anything in this file, but take some time to familiarise
# with how we use connect your search to the start kit. We'll be working on this
# later.
#
# ──────────────────────────────────────────────────────────────────────────────


import MAPF
from opss25.utils.types import BindStartKit
from piglet.lib_piglet.domains.robotrunners import robotrunners
from .ex3_create_search import create_search


def naive_planner(domain: robotrunners, use_with_startkit: BindStartKit):
    """
    Creates a planner that plans for all agents, any time there's a missing path, even if other agents are already planned.
    This planner does not replan on unsuccessful commits.
    """

    # ℹ️ INFO We instantiate the search here.
    engine = create_search(domain)

    # ℹ️ INFO We connect the search to the start kit here.
    # It returns a function that allows you to run the search
    # in the context of the start kit.
    run_search = use_with_startkit(engine)

    # ℹ️ INFO We need to return a function that does the planning.
    # It takes in the current piglet environment, the current paths, and
    # whether the last action was successful or not.
    # The function should return the new paths.
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


def plan_unplanned_only_planner(domain: robotrunners, use_with_startkit: BindStartKit):
    """
    Creates a planner that plans for only agents with missing paths.
    This planner does not replan on unsuccessful commits.
    """

    engine = create_search(domain)
    run_search = use_with_startkit(engine)

    def plan(
        env: MAPF.SharedEnvironment, paths: list[list], last_did_error: bool = False
    ):
        if last_did_error:
            raise RuntimeError("Error: Last action did not successfully commit.")
        return [p if p else run_search(env, i) for i, p in enumerate(paths)]

    return plan


chosen_planner = naive_planner
