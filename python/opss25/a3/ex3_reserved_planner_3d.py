import MAPF
from opss25.a3.ex3_create_search_w_reservations_and_wait import (
    create_search_w_reservations_and_wait,
)
from opss25.utils import interop
from opss25.utils.types import BindStartKit
from piglet.lib_piglet.domains.robotrunners import robotrunners

from .ex1_reservation_table_3d import reservation_table_3d


def reserved_planner_3d(domain: robotrunners, use_with_startkit: BindStartKit):
    """
    Creates a planner that plans for all agents, any time there's a missing path, even if other agents are already planned.
    We do not replan on unsuccessful commits.
    """

    # Create reservation table
    table = reservation_table_3d(domain.width_, domain.height_)
    engine = create_search_w_reservations_and_wait(domain, table)
    # Create search
    run_search = use_with_startkit(engine)

    def plan(
        env: MAPF.SharedEnvironment,
        paths: list[list],
        last_did_error: bool = False,
    ):
        #first clear the reservation table
        # table.clear()
        if any(not p for p in paths):
            #plan for each agent
            for i in range(len(paths)):
                # plan path for agent i
                paths[i] = run_search(env, i)
                table.reserve(i, interop.get_agent_state(env, i), *paths[i])
            return paths
        else:
            return paths

    return plan
