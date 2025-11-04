import MAPF
from ..a3.ex2_reservation_table_3d import reservation_table_3d
from opss25.utils.types import BindStartKit
from piglet.lib_piglet.domains.robotrunners import robotrunners
from python.opss25.a2.ex3_create_search_w_reservations import (
    create_search_w_reservations,
)


def prioritised_planner(domain: robotrunners, use_with_startkit: BindStartKit):
    """
    Creates a planner that plans for all agents, any time there's a missing path, even if other agents are already planned.
    We do not replan on unsuccessful commits.
    """

    # Create reservation table
    table = reservation_table_3d(domain.width_, domain.height_)
    engine = create_search_w_reservations(domain, table)
    # Create search
    run_search = use_with_startkit(engine)

    def plan(
        env: MAPF.SharedEnvironment,
        paths: list[list],
        last_did_error: bool = False,
    ):

        # TODO This one maybe make it replan on error
        if last_did_error:
            raise RuntimeError("Error: Last action did not successfully commit.")

        # 🏷️ A3 EXERCISE: WRITE THE PRIORITISED PLANNER
        pass
        # region ANSWER A3:
        # TODO Do the prioritised planner!!!!
        pass
        # endregion

    return plan
