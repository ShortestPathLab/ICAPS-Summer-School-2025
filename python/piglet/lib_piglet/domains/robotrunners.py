# domains/robotrunners_action.py
#
# describes a valid action in a robot runners domain and specifies its cost

from enum import IntEnum

from lib_piglet.domains.base_domain import base_domain
from lib_piglet.domains.gridmap import gridmap


class Move_Actions(IntEnum):
    MOVE_FORWARD = 0
    ROTATE_CW = 1
    ROTATE_CCW = 2
    WAIT = 3


class Directions(IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    NONE = 4

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class robotrunners_action:

    def __init__(self):
        self.move_ = Move_Actions.WAIT
        self.cost_ = 1

    def print(self):
        if self.move_ == Move_Actions.MOVE_FORWARD:
            print("FORWARD " + str(self.cost_))
        elif self.move_ == Move_Actions.ROTATE_CW:
            print("ROTATE CW " + str(self.cost_))
        elif self.move_ == Move_Actions.ROTATE_CCW:
            print("ROTATE CCW " + str(self.cost_))
        else:
            print("WAIT " + str(self.cost_))


robotrunners_state = tuple


class robotrunners(gridmap):
    def get_name(self):
        return "robotrunners"

    def is_goal(self, current_state, goal_state):
        x1, y1 = current_state[:2]
        x2, y2 = goal_state[:2]
        return x1 == x2 and y1 == y2

    @staticmethod
    def from_list(width: int, height: int, map: list[int], name: str | None = None):
        # TODO Check if this is right
        m = robotrunners()
        m.width_ = width
        m.height_ = height
        m.domain_file_ = name
        m.map_ = [([map[x * width + y] for y in range(width)]) for x in range(height)]
        m.map_ = [[1 - v for v in row] for row in m.map_]
        return m
