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
        x, y, direction, t = state
        if self.vertextable_[x][y] is None:
            return False
        if t not in self.vertextable_[x][y]:
            return False

        if self.vertextable_[x][y][t]==-1:
            return False

        if self.vertextable_[x][y][t] == current_agent_id and current_agent_id != -1:
            return False

        return True

    # Add an single reservation to reservation table
    # @param state A tuple of (x,y,t) coordinates.
    # @param agent_id An int of agent_id.
    # @return success True if add successful, false if the location reserved by other agent.
    def add_vertex(self, state: tuple, agent_id: int):
        x, y, direction, t = state
        if self.vertextable_[x][y] is None:
            self.vertextable_[x][y] = {}

        if t not in self.vertextable_[x][y]:
            self.vertextable_[x][y][t] = agent_id
            return True

        if self.vertextable_[x][y][t] != agent_id and self.vertextable_[x][y][t]!=-1:
            return False
        else:
            self.vertextable_[x][y][t] = agent_id
            return True

    # Delete a reserve from reservation table
    # @param state A tuple of (x,y,t) coordinates.
    # @param agent_id An int of agent_id.
    # @return success True if delete successful, False if reserve doesn't exist
    def del_vertex(self, state: tuple, agent_id: int):
        x, y, direction, t = state
        if self.vertextable_[x][y] is None:
            return False

        if t in self.vertextable_[x][y]:
            if self.vertextable_[x][y][t]== agent_id:
                self.vertextable_[x][y][t] = -1
                return True
            else:
                return False
        else:
            return False

    # Check is an location reserved by any other agent
    # @param state A tuple of (x,y,t) coordinates.
    # @param agent_id An int of agent_id.
    # @return bool True if reserved.
    # def is_edge_collision(self, state: tuple, new_state: tuple, current_agent_id: int = -1):
    #     x, y, direction, t = state
    #     nx, ny, n_direction, arrival_t = new_state
    #     if not (x,y,nx,ny) in self.edgetable_:
    #         return False
    #     if arrival_t not in self.edgetable_[(x,y,nx,ny)]:
    #         return False

    #     if self.edgetable_[(x,y,nx,ny)][arrival_t]==-1:
    #         return False

    #     if self.edgetable_[(x,y,nx,ny)][arrival_t] == current_agent_id and current_agent_id != -1:
    #         return False

    #     return True
    def is_edge_collision(self, state: tuple, new_state: tuple, current_agent_id: int = -1):
        x, y, direction, t = state
        nx, ny, n_direction, arrival_t = new_state
        for key in ((x, y, nx, ny), (nx, ny, x, y)):
            bucket = self.edgetable_.get(key)
            if not bucket:
                continue
            val = bucket.get(arrival_t)
            if val in (None, -1):
                continue
            if current_agent_id != -1 and val == current_agent_id:
                continue
            return True

        return False

    def add_edge(self, state: tuple, new_state: tuple, agent_id: int):
        x, y, direction, t = state
        nx, ny, n_direction, arrival_t = new_state
        key = (x, y, nx, ny)

        bucket = self.edgetable_.setdefault(key, {})  # <-- no KeyError
        # Conflict if someone else already holds this time slot (and it’s not the tombstone -1)
        if arrival_t in bucket and bucket[arrival_t] not in (-1, agent_id):
            return False

        bucket[arrival_t] = agent_id
        return True


    def del_edge(self, state: tuple, new_state: tuple, agent_id: int):
        x, y, direction, t = state
        nx, ny, n_direction, arrival_t = new_state
        key = (x, y, nx, ny)

        bucket = self.edgetable_.get(key)  # <-- safe
        if not bucket:
            return False

        if arrival_t in bucket and bucket[arrival_t] == agent_id:
            bucket[arrival_t] = -1  # tombstone
            # Optional cleanup: remove empty buckets if they only contain -1
            # if all(v == -1 for v in bucket.values()):
            #     del self.edgetable_[key]
            return True

        return False
    # # Add an single reservation to reservation table
    # # @param state A tuple of (x,y,t) coordinates.
    # # @param agent_id An int of agent_id.
    # # @return success True if add successful, false if the location reserved by other agent.
    # def add_edge(self, state: tuple, new_state: tuple, agent_id: int):
    #     x, y, direction, t = state
    #     nx, ny, n_direction, arrival_t = new_state
    #     if self.edgetable_[(x,y,nx,ny)] is None:
    #         self.edgetable_[(x,y,nx,ny)] = {}

    #     if arrival_t not in self.edgetable_[(x,y,nx,ny)]:
    #         self.edgetable_[(x,y,nx,ny)][arrival_t] = agent_id
    #         return True

    #     if self.edgetable_[(x,y,nx,ny)][arrival_t] != agent_id and self.edgetable_[(x,y,nx,ny)][arrival_t]!=-1:
    #         return False
    #     else:
    #         self.edgetable_[(x,y,nx,ny)][arrival_t] = agent_id
    #         return True

    # # Delete a reserve from reservation table
    # # @param state A tuple of (x,y,t) coordinates.
    # # @param agent_id An int of agent_id.
    # # @return success True if delete successful, False if reserve doesn't exist
    # def del_edge(self, state: tuple, new_state: tuple, agent_id: int):
    #     x, y, direction, t = state
    #     nx, ny, n_direction, arrival_t = new_state
    #     if self.edgetable_[(x,y,nx,ny)] is None:
    #         return False

    #     if arrival_t in self.edgetable_[(x,y,nx,ny)]:
    #         if self.edgetable_[(x,y,nx,ny)][arrival_t]== agent_id:
    #             self.edgetable_[(x,y,nx,ny)][arrival_t] = -1
    #             return True
    #         else:
    #             return False
    #     else:
    #         return False

    # clear the reservation table
    def clear(self):
        self.vertextable_ = [[None] * int(self.width_) for x in range(int(self.height_))]
        self.edgetable_ = {}

