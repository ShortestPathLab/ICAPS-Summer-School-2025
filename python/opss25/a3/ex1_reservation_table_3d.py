# This module defines constraints, constraints table and reservation table for grid map.

from itertools import pairwise
from typing import TypeAlias
from piglet.lib_piglet.domains.robotrunners import robotrunners_state

Timestep: TypeAlias = int
AgentId: TypeAlias = int


class reservation_table_3d:

    width_: int
    height_: int
    vertex_table: list[list[dict[Timestep, AgentId]]]
    edge_table: dict[tuple[int, int, int, int], dict[Timestep, AgentId]]

    def __init__(self, width, height):
        self.width_ = width
        self.height_ = height
        self.clear()

    def reserve(self, id: int, *states: robotrunners_state):
        # 🏷️ A3 EXERCISE: IMPLEMENT RESERVE
        # This method should reserve the given states for
        # agent @param id.
        # region ANSWER A3:
        for state in states:
            self.add_vertex(state, id)
        for prev, next in pairwise(states):
            self.add_edge(prev, next, id)
        # endregion

    def unreserve(self, id: int, *states: robotrunners_state):
        # 🏷️ A3 EXERCISE: IMPLEMENT UNRESERVE
        # This method should unreserve the given states for
        # agent @param id.
        # region ANSWER A3:
        for state in states:
            self.remove_vertex(state, id)
        for prev, next in pairwise(states):
            self.remove_edge(prev, next, id)
        # endregion

    # Check if a temporal reservation exists at a given vertex
    # @param state A tuple of (x,y,t) coordinates.
    # @param agent_id An int of agent_id.
    # @return bool True if reserved.
    def is_vertex_reserved(
        self, state: robotrunners_state, current_agent_id: AgentId = -1
    ):
        x, y, direction, t = state

        v = self.vertex_table[x][y].get(t, -1) if t in self.vertex_table[x][y] else -1
        return v != -1 and v != current_agent_id

    # Add a single vertex reservation to reservation table
    # @param state A tuple of (x,y,t) coordinates.
    # @param agent_id An int of agent_id.
    # @return success True if add successful, false if the location reserved by other agent.
    def add_vertex(self, state: robotrunners_state, id: AgentId):
        x, y, direction, t = state

        self.vertex_table[x][y] = self.vertex_table[x][y] or dict()
        v = self.vertex_table[x][y].get(t, -1)

        if v == -1:
            self.vertex_table[x][y][t] = id
            return True

        return False

    # Delete a vertex reservation from reservation table
    # @param state A tuple of (x,y,t) coordinates.
    # @param agent_id An int of agent_id.
    # @return success True if delete successful, False if reserve doesn't exist
    def del_vertex(self, state: robotrunners_state, agent_id: AgentId):
        x, y, direction, t = state

        v = self.vertex_table[x][y].get(t, -1) if self.vertex_table[x][y] else -1

        # delete temporal reservation (x, y, t) but only
        # if it belongs to agent @agent_id
        if v == agent_id:
            del self.vertex_table[x][y][t]
            return True

        # reservation doesn't exist or belongs to another
        # agent. cannot delete
        return False

    def is_edge_reserved(
        self,
        state: robotrunners_state,
        new_state: robotrunners_state,
        current_agent_id: AgentId = -1,
    ):
        x, y, direction, t = state
        nx, ny, n_direction, arrival_t = new_state
        for key in ((x, y, nx, ny), (nx, ny, x, y)):
            bucket = self.edge_table.get(key)
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
        bucket = self.edge_table.setdefault(key, {})

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

        bucket = self.edge_table.get(key)  # <-- safe

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

    # clear the reservation table
    def clear(self):
        self.vertex_table = [
            [None for _ in range(int(self.width_))] for _ in range(int(self.height_))
        ]
        self.edge_table = {}


# Theoretically only the code in this folder should ever
# Interact with the reservation table
