# ──────────────────────────────────────────────────────────────────────────────
#
# TASK 4: BUILD THE PLANNER WITH RESERVATIONS
#
# Write the planner that uses the search engine that we've created. It's also
# going to need some logic on how it's going to update the reservation table.
#
# When you're done with this part, you'll get a working planner that can plan
# around other agents!
#
# Look out for the 🏷️ EXERCISE label in the code below.
# The code sections marked with this label are where you need to implement your
# solution.
#
# ──────────────────────────────────────────────────────────────────────────────


import MAPF
from python.opss25.utils import interop
from .ex1_reservation_table_2d import reservation_table_2d
from opss25.utils.types import BindStartKit
from piglet.lib_piglet.domains.robotrunners import robotrunners
from .ex3_create_search_w_reservations import create_search_w_reservations


def reserved_planner_2d(domain: robotrunners, use_with_startkit: BindStartKit):
    """
    Creates a planner that'll maintain a basic reservation table so that
    agents don't bump into each other.
    """

    # Create reservation table
    table = reservation_table_2d(domain.width_, domain.height_)
    engine = create_search_w_reservations(domain, table)

    # Create search
    run_search = use_with_startkit(engine)

    def plan(
        env: MAPF.SharedEnvironment,
        paths: list[list],
        last_did_error: bool = False,
    ):
        # 🏷️ A2 EXERCISE: WRITE THE RESERVATION TABLE PLANNER
        # Write a planning loop that drives the low planning logic,
        # and don't forget to use the reservation table!
        #
        # 🧪 Try out a few strategies that use this reservation table.
        # - Reserve the entire path as you plan for each agent
        # - Reserve only the next point on the path
        # - Reserve the current position if the search fails
        # - Don't reserve the current position if the search fails
        #
        # Refer to the basic planners in ex1 if you're stuck.
        #
        # region ANSWER A2:

        table.clear()
        for i in range(len(paths)):
            paths[i] = run_search(env, i)
            # Check if we've got a solution
            if paths[i]:
                # Reserve only the first point on the path
                table.reserve(interop.get_agent_state(env, i), paths[i][0])
        return paths

        # endregion

    return plan
