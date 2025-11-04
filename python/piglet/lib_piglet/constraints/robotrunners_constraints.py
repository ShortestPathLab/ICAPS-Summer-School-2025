# constraints/robotrunners_constraints.py
# This module defines constraints, constraints table and reservation table for grid map.

from typing import TypeAlias
from piglet.lib_piglet.domains.robotrunners import robotrunners_state

Timestep: TypeAlias = int
AgentId: TypeAlias = int


class robotrunners_reservation_table:

    width_: int
    height_: int
    vertextable_: list[list[AgentId]]
    edgetable_: dict[robotrunners_state, dict[Timestep, AgentId]]

    def __init__(self, width, height):
        self.width_ = width
        self.height_ = height
        self.clear()

    # Check if a temporal reservation exists at a given vertex
    # @param state A tuple of (x,y,t) coordinates.
    # @param agent_id An int of agent_id.
    # @return bool True if reserved.
    def is_reserved(self, state: robotrunners_state, current_agent_id: AgentId = -1):
        x, y, direction, t = state
        if self.vertextable_[x][y] is None:
            return False
        if t not in self.vertextable_[x][y]:
            return False

        if self.vertextable_[x][y][t] == -1:
            return False

        if self.vertextable_[x][y][t] == current_agent_id and current_agent_id != -1:
            return False

        return True

    # Add a single vertex reservation to reservation table
    # @param state A tuple of (x,y,t) coordinates.
    # @param agent_id An int of agent_id.
    # @return success True if add successful, false if the location reserved by other agent.
    def add_vertex(self, state: robotrunners_state, agent_id: AgentId):
        x, y, direction, t = state

        # allocate memory for the reservation table (x, y)
        if self.vertextable_[x][y] is None:
            self.vertextable_[x][y] = {}

        # reserve (x, y, t) for agent @agent_id
        if t not in self.vertextable_[x][y]:
            self.vertextable_[x][y][t] = agent_id
            return True

        return False

    # Delete a vertex reservation from reservation table
    # @param state A tuple of (x,y,t) coordinates.
    # @param agent_id An int of agent_id.
    # @return success True if delete successful, False if reserve doesn't exist
    def del_vertex(self, state: robotrunners_state, agent_id: AgentId):
        x, y, direction, t = state

        # is the reservation table for cell (x, y) initialised?
        # if not, there's nothing to delete
        if self.vertextable_[x][y] is None:
            return False

        # delete temporal reservation (x, y, t) but only
        # if it belongs to agent @agent_id
        if t in self.vertextable_[x][y]:
            if self.vertextable_[x][y][t] == agent_id:
                del self.vertextable_[x][y][t]
                return True

        # reservation doesn't exist or belongs to another
        # agent. cannot delete
        return False

    # Check for edge collision
    # @param state The first vertex (x, y, t)
    # @param new_state The second vertex (nx, ny, t)
    # @param agent_id An int of agent_id.
    # @return bool True if reserved.
    # def is_edge_collision(self, state: tuple, new_state: tuple, current_agent_id: AgentId = -1):
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
    def is_edge_collision(
        self,
        state: robotrunners_state,
        new_state: robotrunners_state,
        current_agent_id: AgentId = -1,
    ):
        x, y, direction, t = state
        nx, ny, n_direction, arrival_t = new_state
        for key in ((x, y, nx, ny), (nx, ny, x, y)):
            bucket = self.edgetable_.get(key)
            if not bucket:
                continue
            val = bucket.get(arrival_t)
            if val in (None, current_agent_id):
                continue
            if current_agent_id is None:
                continue
            return True

        return False

    def add_edge(
        self,
        state: robotrunners_state,
        new_state: robotrunners_state,
        agent_id: AgentId,
    ):
        x, y, direction, t = state
        nx, ny, n_direction, arrival_t = new_state
        key = (x, y, nx, ny)

        # <-- no KeyError
        bucket = self.edgetable_.setdefault(key, {})

        # conflict; someone else already reserved the edge
        if arrival_t in bucket and bucket[arrival_t] != agent_id:
            return False

        # reservation successful
        bucket[arrival_t] = agent_id
        return True

    def del_edge(
        self,
        state: robotrunners_state,
        new_state: robotrunners_state,
        agent_id: AgentId,
    ):
        x, y, direction, t = state
        nx, ny, n_direction, arrival_t = new_state
        key = (x, y, nx, ny)

        bucket = self.edgetable_.get(key)  # <-- safe

        # nothing to delete
        if not bucket:
            return False

        # delete reservation if it exists and
        # it is held by agent @param agent_id
        if arrival_t in bucket and bucket[arrival_t] == agent_id:
            del bucket[arrival_t]
            return True

        # delete failed (reservation held by another agent)
        return False

    # # Add an single reservation to reservation table
    # # @param state A tuple of (x,y,t) coordinates.
    # # @param agent_id An int of agent_id.
    # # @return success True if add successful, false if the location reserved by other agent.
    # def add_edge(self, state: tuple, new_state: tuple, agent_id: AgentId):
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
    # def del_edge(self, state: tuple, new_state: tuple, agent_id: AgentId):
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
        self.vertextable_ = [
            [None] * int(self.width_) for _ in range(int(self.height_))
        ]
        self.edgetable_ = {}
