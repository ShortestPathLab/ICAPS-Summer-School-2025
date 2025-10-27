# expander/robotrunners.py
# 
# Expand function for the robot runners domain.
#
# Given a current search node, the expander checks the set of valid robot runners actions 
# and generates search node successors for each.

from lib_piglet.search.search_node import search_node
from lib_piglet.expanders.base_expander import base_expander
from lib_piglet.domains.robotrunners import  Move_Actions, robotrunners_action, Directions, robotrunners
from lib_piglet.constraints.grid_constraints import grid_constraint_table, grid_reservation_table
import copy

class robotrunners_expander(base_expander):


    def __init__(self, map : robotrunners, constraint_table: grid_constraint_table = None):
        self.domain_: robotrunners = map
        self.effects_: list = [self.domain_.height_*-1, self.domain_.height_, -1, 1]
        self.constraint_table_: grid_constraint_table   = constraint_table
        self.reservation_table_: grid_reservation_table = None # reservation_table_ is not used on default, decide how to use it on your own.

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
            if self.constraint_table_ is not None:
                if self.constraint_table_.get_constraint(new_state,current.timestep_+1).v_:
                    continue
                if self.constraint_table_.get_constraint(current.state_,current.timestep_).e_[a.move_]:
                    continue
            self.succ_.append((new_state, a))
        return self.succ_[:]

    # return a list with all the applicable/valid actions
    # at tile (x, y)
    # @param loc A (x,y) coordinate tuple
    # @return a list of gridaction object.
    def get_actions(self, state: tuple):
        x = state[0]
        y = state[1]
        t = state[2]
        direction = state[3]
        retval = []

        if (x < 0 or x >= int(self.domain_.height_) or y < 0 or y >= int(self.domain_.width_)):
            return retval

        if (self.domain_.get_tile(state) == False):
            return retval

        if (self.direction == Directions.NORTH and self.domain_.get_tile((x,y-1))):
            retval.append(robotrunners_action())
            retval[-1].move_ = Move_Actions.MOVE_FORWARD
            retval[-1].cost_ = 1
        elif (self.direction == Directions.EAST and self.domain_.get_tile((x+1,y))):
            retval.append(robotrunners_action())
            retval[-1].move_ = Move_Actions.MOVE_FORWARD
            retval[-1].cost_ = 1
        elif (self.direction == Directions.SOUTH and self.domain_.get_tile((x,y+1))):
            retval.append(robotrunners_action())
            retval[-1].move_ = Move_Actions.MOVE_FORWARD
            retval[-1].cost_ = 1
        elif (self.direction == Directions.WEST and self.domain_.get_tile((x-1,y))):
            retval.append(robotrunners_action())
            retval[-1].move_ = Move_Actions.MOVE_FORWARD
            retval[-1].cost_ = 1

        if (self.direction == 1 and self.domain_.get_tile((x,y,t))):
            retval.append(robotrunners_action())
            retval[-1].move_ = Move_Actions.WAIT
            retval[-1].cost_ = 1



        return retval

    def __move(self, curr_state: tuple, move):
        x = curr_state[0]
        y = curr_state[1]
        t = curr_state[2]
        direction = curr_state[3]
        
        return x, y, 

    def __str__(self):
        return str(self.domain_)
