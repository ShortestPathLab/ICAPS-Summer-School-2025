# expander/robotrunners.py
#
# Expand function for the robot runners domain.
#
# Given a current search node, the expander checks the set of valid robot runners actions
# and generates search node successors for each.

from lib_piglet.search.search_node import search_node
from lib_piglet.expanders.base_expander import base_expander
from lib_piglet.domains.robotrunners import (
    Move_Actions,
    robotrunners_action,
    Directions,
    robotrunners,
)
from lib_piglet.constraints.robotrunners_constraints import (
    robotrunners_reservation_table,
)


class robotrunners_expander(base_expander):

    def __init__(
        self,
        map: robotrunners,
        reservation_table: robotrunners_reservation_table = None,
    ):
        self.domain_: robotrunners = map
        self.effects_: list = [self.domain_.height_ * -1, self.domain_.height_, -1, 1]
        self.reservation_table_ = reservation_table

        # memory for storing successor (state, action) pairs
        self.succ_: list = []

    # identify successors of the current node
    #
    # @param current: The current node
    # @return : Possible next
    def expand(self, current: search_node):
        self.succ_.clear()
        for a in self.get_actions(current.state_):
            # NB: we only initialise the state and action attributes.
            # The search will initialise the rest, assuming it decides
            # to add the corresponding successor to OPEN
            new_state = self.__move(current.state_, a.move_)
            # check that an action is valid given reservation tables
            if self.reservation_table_ is not None:
                if self.reservation_table_.is_reserved(new_state):
                    continue
                if self.reservation_table_.is_edge_collision(current.state_, new_state):
                    continue
            self.succ_.append((new_state, a))
        return self.succ_[:]

    # return a list with all the applicable/valid actions
    # at tile (x, y)
    # @param loc A (x,y) coordinate tuple
    # @return a list of gridaction object.
    def get_actions(self, state: tuple):
        x, y, direction, t = state
        retval = []

        if (
            x < 0
            or x >= int(self.domain_.height_)
            or y < 0
            or y >= int(self.domain_.width_)
        ):
            return retval

        if self.domain_.get_tile((x, y)) == False:
            return retval

        if direction == Directions.NORTH and self.domain_.get_tile((x - 1, y)):
            retval.append(robotrunners_action())
            retval[-1].move_ = Move_Actions.MOVE_FORWARD
            retval[-1].cost_ = 1
        elif direction == Directions.EAST and self.domain_.get_tile((x, y + 1)):
            retval.append(robotrunners_action())
            retval[-1].move_ = Move_Actions.MOVE_FORWARD
            retval[-1].cost_ = 1
        elif direction == Directions.SOUTH and self.domain_.get_tile((x + 1, y)):
            retval.append(robotrunners_action())
            retval[-1].move_ = Move_Actions.MOVE_FORWARD
            retval[-1].cost_ = 1
        elif direction == Directions.WEST and self.domain_.get_tile((x, y - 1)):
            retval.append(robotrunners_action())
            retval[-1].move_ = Move_Actions.MOVE_FORWARD
            retval[-1].cost_ = 1

        if self.domain_.get_tile((x, y)):
            retval.append(robotrunners_action())
            retval[-1].move_ = Move_Actions.ROTATE_CW
            retval[-1].cost_ = 1
            retval.append(robotrunners_action())
            retval[-1].move_ = Move_Actions.ROTATE_CCW
            retval[-1].cost_ = 1
            retval.append(robotrunners_action())
            retval[-1].move_ = Move_Actions.WAIT
            retval[-1].cost_ = 1

        return retval

    def __move(self, curr_state: tuple, move):
        x, y, direction, t = curr_state
        if move == Move_Actions.ROTATE_CW:
            direction = Directions((direction.value + 1) % 4)
        elif move == Move_Actions.ROTATE_CCW:
            direction = Directions((direction.value - 1) % 4)
        elif move == Move_Actions.MOVE_FORWARD:
            if direction == Directions.NORTH:
                x -= 1
            elif direction == Directions.EAST:
                y += 1
            elif direction == Directions.SOUTH:
                x += 1
            elif direction == Directions.WEST:
                y -= 1

        return x, y, direction, t + 1

    def __str__(self):
        return str(self.domain_)
