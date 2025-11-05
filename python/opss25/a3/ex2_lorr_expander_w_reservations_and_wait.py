from ..a2.ex2_lorr_expander_w_reservations import lorr_expander_w_reservations
from piglet.lib_piglet.domains.robotrunners import (
    Move_Actions,
    robotrunners,
    robotrunners_action,
    robotrunners_state,
)
from .ex1_reservation_table_3d import (
    reservation_table_3d,
)


class lorr_expander_w_reservations_and_wait(lorr_expander_w_reservations):
    def __init__(
        self,
        map: robotrunners,
        reservation_table: reservation_table_3d,
    ):
        super().__init__(map, reservation_table)
        self.reservation_table_ = reservation_table

    def move(self, curr_state: robotrunners_state, move):
        x, y, d, t = curr_state
        return (*super().move(curr_state, move), t + 1)

    def expand(self, current):
        self.succ_.clear()
        for a in self.get_actions(current.state_):
            # NB: we only initialise the state and action attributes.
            # The search will initialise the rest, assuming it decides
            # to add the corresponding successor to OPEN
            new_state = self.move(current.state_, a.move_)

            # 🏷️ A3 EXERCISE: CHECK THE RESERVATION TABLE
            #
            # Now that we have a reservation table, we need to check that
            # we're not bumping into other agents by checking the reservation table.
            #
            # We must check for both edge and vertex collisions.
            #
            # region ANSWER A3:
            if self.reservation_table_.is_vertex_reserved(new_state):
                continue
            if self.reservation_table_.is_edge_reserved(current.state_, new_state):
                continue
            # endregion

            self.succ_.append((new_state, a))
        return self.succ_[:]

    def get_actions(self, state: tuple):
        x, y, direction, *_ = state
        actions = super().get_actions(state)

        # 🏷️ A3 EXERCISE: IMPLEMENT THE WAIT ACTION
        #
        # Now we're dealing with the time dimension, robots can now wait.
        # Here, we need to determine if the robot can wait on a tile.
        # If so, we need to add a wait action to the list.
        #
        # region ANSWER A3:
        if self.domain_.get_tile((x, y)):
            actions.append(robotrunners_action())
            actions[-1].move_ = Move_Actions.WAIT
            actions[-1].cost_ = 1
        # endregion
        return actions
