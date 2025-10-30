from a1.ex1_robotrunners_expander import robotrunners_expander
from piglet.lib_piglet.domains.robotrunners import (
    Move_Actions,
    robotrunners,
    robotrunners_action,
)
from piglet.lib_piglet.constraints.robotrunners_constraints import (
    robotrunners_reservation_table,
)


class robotrunners_expander_with_wait(robotrunners_expander):
    def __init__(
        self,
        map: robotrunners,
        reservation_table: robotrunners_reservation_table = None,
    ):
        super().__init__(map)
        self.reservation_table_ = reservation_table

    def get_actions(self, state: tuple):
        x, y, direction, t = state
        actions = []

        # 🏷️ A2 EXERCISE: USE THE RESERVATION TABLE
        #
        # We're going to redo the `get_actions`` logic.
        # Now that we have a reservation table, we need to check that
        # we're not colliding into other agents in the reservation table.
        #
        # Populate the 'actions' list with valid robotrunners_action objects.
        # region ANSWER A2:
        # TODO
        # endregion

        # 🏷️ A2 EXERCISE: IMPLEMENT THE WAIT ACTION
        #
        # Now we're dealing with the time dimension, robots can now wait.
        # Here, we need to determine if the robot can wait on a tile.
        # If so, we need to add a wait action to the list.
        #
        # region ANSWER A2:
        if self.domain_.get_tile((x, y)):
            actions.append(robotrunners_action())
            actions[-1].move_ = Move_Actions.WAIT
            actions[-1].cost_ = 1
        # endregion

        return actions
