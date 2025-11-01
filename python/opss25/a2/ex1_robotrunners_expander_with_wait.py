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
        reservation_table: robotrunners_reservation_table,
    ):
        super().__init__(map)
        self.reservation_table_ = reservation_table

    def expand(self, current):
        self.succ_.clear()
        for a in self.get_actions(current.state_):
            # NB: we only initialise the state and action attributes.
            # The search will initialise the rest, assuming it decides
            # to add the corresponding successor to OPEN
            new_state = self.__move(current.state_, a.move_)

            # 🏷️ A2 EXERCISE: CHECK THE RESERVATION TABLE
            #
            # Now that we have a reservation table, we need to check that
            # we're not bumping into other agents by checking the reservation table.
            #
            # We must check for both edge and vertex collisions.
            #
            pass

            self.succ_.append((new_state, a))
        return self.succ_[:]

    def get_actions(self, state: tuple):
        x, y, direction, t = state
        actions = super().get_actions(state)

        # 🏷️ A2 EXERCISE: IMPLEMENT THE WAIT ACTION
        #
        # Now we're dealing with the time dimension, robots can now wait.
        # Here, we need to determine if the robot can wait on a tile.
        # If so, we need to add a wait action to the list.
        #
        pass

        return actions
