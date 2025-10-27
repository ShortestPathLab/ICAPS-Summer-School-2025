# constraints/robotrunners_constraints.py
# This module defines constraints, constraints table and reservation table for grid map.

class robotrunners_reservation_table:

    width_: int
    height_: int
    table_: list

    def __init__(self,width, height):
        self.width_ = width
        self.height_ = height
        self.vertextable_ = [[None] * int(self.width_) for x in range(int(self.height_))]
        self.edgetable_ = {}

    # Check is an location reserved by any other agent
    # @param state A tuple of (x,y,t) coordinates.
    # @param agent_id An int of agent_id.
    # @return bool True if reserved.
    def is_reserved(self, state: tuple, current_agent_id: int = -1):
        x = state[0]
        y = state[1]
        time = state[2]
        if self.table_[x][y] is None:
            return False
        if time not in self.table_[x][y]:
            return False

        if self.table_[x][y][time]==-1:
            return False

        if self.table_[x][y][time] == current_agent_id and current_agent_id != -1:
            return False

        return True

    # Add an single reservation to reservation table
    # @param state A tuple of (x,y,t) coordinates.
    # @param agent_id An int of agent_id.
    # @return success True if add successful, false if the location reserved by other agent.
    def add_vertex(self, state: tuple, agent_id: int):
        x = state[0]
        y = state[1]
        time = state[2]
        if self.table_[x][y] is None:
            self.table_[x][y] = {}

        if time not in self.table_[x][y]:
            self.table_[x][y][time] = agent_id
            return True

        if self.table_[x][y][time] != agent_id and self.table_[x][y][time]!=-1:
            return False
        else:
            self.table_[x][y][time] = agent_id
            return True

    # Delete a reserve from reservation table
    # @param state A tuple of (x,y,t) coordinates.
    # @param agent_id An int of agent_id.
    # @return success True if delete successful, False if reserve doesn't exist
    def del_vertex(self, state: tuple, agent_id: int):
        x = state[0]
        y = state[1]
        time = state[2]
        if self.table_[x][y] is None:
            return False

        if time in self.table_[x][y]:
            if self.table_[x][y][time]== agent_id:
                self.table_[x][y][time] = -1
                return True
            else:
                return False
        else:
            return False

    # Check is an location reserved by any other agent
    # @param state A tuple of (x,y,t) coordinates.
    # @param agent_id An int of agent_id.
    # @return bool True if reserved.
    def is_edge_collision(self, state: tuple, new_state: tuple, current_agent_id: int = -1):
        x = state[0]
        y = state[1]
        nx = new_state[0]
        ny = new_state[1]
        arrival_time = new_state[2]
        if self.table_[(x,y,nx,ny)] is None:
            return False
        if arrival_time not in self.table_[(x,y,nx,ny)]:
            return False

        if self.table_[(x,y,nx,ny)][arrival_time]==-1:
            return False

        if self.table_[(x,y,nx,ny)][arrival_time] == current_agent_id and current_agent_id != -1:
            return False

        return True

    # Add an single reservation to reservation table
    # @param state A tuple of (x,y,t) coordinates.
    # @param agent_id An int of agent_id.
    # @return success True if add successful, false if the location reserved by other agent.
    def add_edge(self, state: tuple, new_state: tuple, agent_id: int):
        x = state[0]
        y = state[1]
        nx = new_state[0]
        ny = new_state[1]
        arrival_time = new_state[2]
        if self.table_[(x,y,nx,ny)] is None:
            self.table_[(x,y,nx,ny)] = {}

        if arrival_time not in self.table_[(x,y,nx,ny)]:
            self.table_[(x,y,nx,ny)][arrival_time] = agent_id
            return True

        if self.table_[(x,y,nx,ny)][arrival_time] != agent_id and self.table_[(x,y,nx,ny)][arrival_time]!=-1:
            return False
        else:
            self.table_[(x,y,nx,ny)][arrival_time] = agent_id
            return True

    # Delete a reserve from reservation table
    # @param state A tuple of (x,y,t) coordinates.
    # @param agent_id An int of agent_id.
    # @return success True if delete successful, False if reserve doesn't exist
    def del_edge(self, state: tuple, new_state: tuple, agent_id: int):
        x = state[0]
        y = state[1]
        nx = new_state[0]
        ny = new_state[1]
        arrival_time = new_state[2]
        if self.table_[(x,y,nx,ny)] is None:
            return False

        if arrival_time in self.table_[(x,y,nx,ny)]:
            if self.table_[(x,y,nx,ny)][arrival_time]== agent_id:
                self.table_[(x,y,nx,ny)][arrival_time] = -1
                return True
            else:
                return False
        else:
            return False

    # clear the reservation table
    def clear(self):
        self.table_ = [[None] * int(self.width_) for x in range(int(self.height_))]

