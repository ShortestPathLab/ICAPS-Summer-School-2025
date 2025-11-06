# ──────────────────────────────────────────────────────────────────────────────
#
# TASK 2: BUILD AN EXPANDER WITH RESERVATIONS
#
# Now, you'll need to build an expander that uses a reservation table.
# It should check for collisions on the reservation table before adding
# successors to OPEN.
#
# Look out for the 🏷️ EXERCISE label in the code below.
# The code sections marked with this label are where you need to implement your
# solution.
#
# ──────────────────────────────────────────────────────────────────────────────

from piglet.lib_piglet.domains.robotrunners import (
    robotrunners,
)

from ..a1.ex1_lorr_expander import lorr_expander
from .ex1_reservation_table_2d import reservation_table_2d


class lorr_expander_w_reservations(lorr_expander):
    def __init__(
        self,
        map: robotrunners,
        reservation_table: reservation_table_2d,
    ):
        super().__init__(map)
        self.reservation_table_ = reservation_table

    def expand(self, current):
        self.succ_.clear()
        for a in self.get_actions(current.state_):
            # NB: we only initialise the state and action attributes.
            # The search will initialise the rest, assuming it decides
            # to add the corresponding successor to OPEN
            new_state = self.move(current.state_, a.move_)

            # 🏷️ A2 EXERCISE: CHECK THE RESERVATION TABLE
            #
            # Now that we have a reservation table, we need to check that
            # we're not bumping into other agents by checking the
            # reservation table.
            #
            pass

            self.succ_.append((new_state, a))
        return self.succ_[:]
