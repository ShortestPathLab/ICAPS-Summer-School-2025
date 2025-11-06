import random

import MAPF
from opss25.utils import interop
from opss25.utils.types import BindStartKit
from piglet.lib_piglet.domains.robotrunners import robotrunners

from ..a3.ex1_reservation_table_3d import reservation_table_3d
from ..a3.ex3_create_search_w_reservations_and_wait import (
    create_search_w_reservations_and_wait,
)


def order_agents_by_priority(agents_sequence: list[int]) -> list[int]:
    """
    Orders agents by priority. We simply use random shuffle for now.
    """
    # 🏷️ A4 EXERCISE: WRITE THE RANDOM SHUFFLING OF AGENTS ORDER
    # region ANSWER4:
    random.shuffle(agents_sequence)
    return agents_sequence
    # endregion


def check_plan_needed(paths: list[list], last_did_error: bool) -> list[int]:
    """
    Checks for each agent whether a plan is needed.
    An agent needs a plan if its path is empty. Or if last_did_error is True.
    Returns a list of agent indices that need planning.
    """
    # 🏷️ A4 EXERCISE: WRITE THE LOGIC TO DETERMINE WHICH AGENTS NEED PLANNING
    #
    # This function should return all the agents that require planning. For
    # our purposes, we'll say that an agent requires planning if its path is
    # empty. Additionally if last_did_error is True, we need to plan for all
    # agents, even if they've already been planned.
    #
    pass


def prioritised_planner(domain: robotrunners, use_with_startkit: BindStartKit):
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

        # 🏷️ A4 EXERCISE: WRITE THE PRIORITISED PLANNER
        # Plan only for agents that need replanning, in a random order.
        # First,Determine  which agents need replanning. 
        # Second, clear the table and reserve the paths of all agents that do not need replanning.
        # Then, randomise the order in which you'll plan for them.
        pass

    return plan
