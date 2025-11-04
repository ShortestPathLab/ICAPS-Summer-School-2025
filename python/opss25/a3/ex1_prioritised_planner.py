from opss25.utils.types import GetPath
import MAPF


def naive(get_path: GetPath):
    """Creates a planner that plans for all agents, any time there's a missing path, even if other agents are already planned"""

    # CREATE RESERVATION TABLE HERE!!!!!

    def plan(
        env: MAPF.SharedEnvironment,
        paths: list[list],
    ):

        # Prioritised planning here
        raise NotImplementedError(get_path, env, paths)

    return plan
