# ──────────────────────────────────────────────────────────────────────────────
#
# TASK 1: BUILD THE ROBOT RUNNERS EXPANDER
#
# An expander is responsible for generating all valid successor states
# for a given state and action. In this task, you will implement the expander
# for the robot runners domain.
#
# In the robot runners domain, a robot can perform the following actions:
# - Move Forward: The robot moves one tile in the direction it is currently facing.
# - Rotate Clockwise: The robot rotates clockwise by 90 degrees.
# - Rotate Counter-Clockwise: The robot rotates counter-clockwise by 90 degrees.
# - Wait: The robot does nothing. However for task 1, we'll ignore this action.
#
# Look out for the 🏷️ EXERCISE label in the code below.
# The code sections marked with this label are where you need to implement your solution.
#
# ──────────────────────────────────────────────────────────────────────────────

# expander/robotrunners.py
#
# Expand function for the robot runners domain.
#
# Given a current search node, the expander checks the set of valid robot runners actions
# and generates search node successors for each.

from piglet.lib_piglet.search.search_node import search_node
from piglet.lib_piglet.expanders.base_expander import base_expander
from piglet.lib_piglet.domains.robotrunners import (
    Move_Actions,
    robotrunners_action,
    Directions,
    robotrunners,
)


class robotrunners_expander(base_expander):

    def __init__(
        self,
        map: robotrunners,
    ):
        self.domain_: robotrunners = map
        self.effects_: list = [self.domain_.height_ * -1, self.domain_.height_, -1, 1]

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
            self.succ_.append((new_state, a))
        return self.succ_[:]

    # return a list with all the applicable/valid actions
    # at tile (x, y)
    # @param loc A (x,y) coordinate tuple
    # @return a list of gridaction object.
    def get_actions(self, state: tuple):
        x, y, direction, t = state
        actions = []

        # 🏷️ A1 EXERCISE: IMPLEMENT THE LOGIC TO DETERMINE VALID ACTIONS
        #
        # Here, we need to determine which actions are valid based on the robot's
        # current position and direction. The robot can only move forward if the tile
        # in the direction it is facing is free. Of course, the robot shouldn't
        # move outside the boundaries of the map or onto an obstacle.
        #
        # Populate the 'actions' list with valid robotrunners_action objects.
        #
        # region ANSWER A1:
        if (
            x < 0
            or x >= int(self.domain_.height_)
            or y < 0
            or y >= int(self.domain_.width_)
        ):
            return actions

        if not self.domain_.get_tile((x, y)):
            return actions

        if direction == Directions.NORTH and self.domain_.get_tile((x - 1, y)):
            actions.append(robotrunners_action())
            actions[-1].move_ = Move_Actions.MOVE_FORWARD
            actions[-1].cost_ = 1
        elif direction == Directions.EAST and self.domain_.get_tile((x, y + 1)):
            actions.append(robotrunners_action())
            actions[-1].move_ = Move_Actions.MOVE_FORWARD
            actions[-1].cost_ = 1
        elif direction == Directions.SOUTH and self.domain_.get_tile((x + 1, y)):
            actions.append(robotrunners_action())
            actions[-1].move_ = Move_Actions.MOVE_FORWARD
            actions[-1].cost_ = 1
        elif direction == Directions.WEST and self.domain_.get_tile((x, y - 1)):
            actions.append(robotrunners_action())
            actions[-1].move_ = Move_Actions.MOVE_FORWARD
            actions[-1].cost_ = 1

        if self.domain_.get_tile((x, y)):
            actions.append(robotrunners_action())
            actions[-1].move_ = Move_Actions.ROTATE_CW
            actions[-1].cost_ = 1
            actions.append(robotrunners_action())
            actions[-1].move_ = Move_Actions.ROTATE_CCW
            actions[-1].cost_ = 1
        # endregion

        return actions

    def __move(self, curr_state: tuple, move):
        x, y, direction, t = curr_state

        # 🏷️ A1 EXERCISE: IMPLEMENT THE LOGIC TO UPDATE THE STATE GIVEN THE ACTION
        #
        # Here, we need to update the robot's current position and direction
        # based on the action it is taking.
        #
        # Mutate the values of x, y, direction and t according to the action.
        #
        # region ANSWER A1:

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

        # endregion

        return x, y, direction, t + 1

    def __str__(self):
        return str(self.domain_)
