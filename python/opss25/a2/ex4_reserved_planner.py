# ──────────────────────────────────────────────────────────────────────────────
#
# TASK 1: BUILD A PLANNER WITH RESERVATIONS
#
# Welp, you've seen that running A* blindly without any coordination wouldn't
# work out for more than one agent. Who would've guessed? Let's try some
# techniques to get around this problem.
#
# In this task, you will implement a planner that uses a reservation table to
# ensure that agents don't bump into each other. Try experimenting with
# different ways to use the reservation table and see how it affects the search.
#
# Look out for the 🏷️ EXERCISE label in the code below.
# The code sections marked with this label are where you need to implement your
# solution.
#
# ──────────────────────────────────────────────────────────────────────────────


import MAPF
from .ex1_reservation_table_2d import reservation_table_2d
from opss25.utils.types import BindStartKit
from piglet.lib_piglet.domains.robotrunners import robotrunners
from .ex3_create_search_w_reservations import create_search_w_reservations


def reserved_planner(domain: robotrunners, use_with_startkit: BindStartKit):
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
        #
        # Refer to the basic planners in ex1 if you're stuck.
        #
        # region ANSWER A2:

        for i in range(len(paths)):
            paths[i] = run_search(env, i)
            # Reserve only the first path
            table.reserve(paths[1][0])

        # endregion

    return plan
