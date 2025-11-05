# TODO Do the introduction comment

import MAPF
from .ex2_reservation_table_2d import reservation_table_2d
from opss25.utils.types import BindStartKit
from piglet.lib_piglet.domains.robotrunners import robotrunners
from .ex3_create_search_w_reservations import create_search_w_reservations


def reserved_planner(domain: robotrunners, use_with_startkit: BindStartKit):
    """
    Creates a planner that'll maintain a basic reservation table so that
    agents don't bump into each other.
    We do not replan on unsuccessful commits.
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
        pass
        # region ANSWER A2:
        # TODO Do the pipe routing planner!!!!
        pass
        # endregion

    return plan
