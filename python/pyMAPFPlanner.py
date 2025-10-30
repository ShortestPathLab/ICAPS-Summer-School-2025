import datetime
import random
from typing import Dict, List, Optional, Tuple, Union

# This import will be available when running within the start-kit environment
import MAPF

import opss25

from piglet.lib_piglet.constraints.robotrunners_constraints import (
    robotrunners_reservation_table,
)
from piglet.lib_piglet.domains.gridmap import gridmap
from piglet.lib_piglet.domains.robotrunners import Directions, robotrunners

# Piglet imports
from piglet.lib_piglet.expanders import (
    base_expander,
    grid_expander,
    robotrunners_expander,
)
from piglet.lib_piglet.heuristics import gridmap_h
from piglet.lib_piglet.search import (
    base_search,
    graph_search,
    search_node,
)
from piglet.lib_piglet.utils.data_structure import bin_heap

# 0=Action.FW, 1=Action.CR, 2=Action.CCR, 3=Action.W


class pyMAPFPlanner:

    _search_engine: base_search = None
    _expander: base_expander = None
    _domain = None
    _heuristic = None
    _default_res_table = None
    _map_file = None
    _path_pool: Dict = {}

    def __init__(self, env=None) -> None:
        if env is not None:
            self.env: MAPF.SharedEnvironment = env

    def initialize(self, preprocess_time_limit: int):
        """_summary_

        Args:
            preprocess_time_limit (_type_): _description_
        """
        self._default_res_table = robotrunners_reservation_table(
            self.env.rows, self.env.cols
        )
        return True

    def plan(self, time_limit):
        """_summary_

        Return:
            actions ([Action]): the next actions

        Args:
            time_limit (int): time limit in milliseconds

        The time limit (ms) starts from the time when the Entr::compute() was called.
        You could read start time from self.env.plan_start_time,
        which is a datetime.timedelta measures the time from the start-kit clocks epoch to start time.
        This means that the function should return the planned actions before
        self.env.plan_start_time + datetime.timedelta(milliseconds=time_limit) - self.env.plan_current_time()
        The start-kit uses its own c++ clock (not system clock or wall clock), the function self.env.plan_current_time() returns the C++ clock now time.
        """

        time_remaining = (
            self.env.plan_start_time
            + datetime.timedelta(milliseconds=time_limit)
            - self.env.plan_current_time()
        )

        # ---------------------------------------------------------------------
        # PATH PLANNING EXERCISE
        # ---------------------------------------------------------------------
        # Each agent will plan its path using three approaches:
        #   1. Standard A* search
        #   2. Time-extended A* search (TX-A*)
        #   3. Prioritized Planning (PP Planner)
        # ---------------------------------------------------------------------

        # # --- Plan with normal A* -------------------------------------------------
        # for agent_id in range(self.env.num_of_agents):
        #     start_loc = self.env.curr_states[agent_id].location
        #     start_dir = self.env.curr_states[agent_id].orientation
        #     goal = self.env.goal_locations[agent_id][0][0]

        #     self._path_pool[agent_id] = self.get_Astar_path(
        #         start_loc,
        #         start_dir,
        #         goal
        #     )

        # # --- Plan with time-extended A* (TX-A*) ----------------------------------
        # for agent_id in range(self.env.num_of_agents):
        #     start_loc = self.env.curr_states[agent_id].location
        #     start_dir = self.env.curr_states[agent_id].orientation
        #     goal = self.env.goal_locations[agent_id][0][0]
        #     print("Start loc:", start_loc, "Start dir:", start_dir, "Goal:", goal)
        #     self._path_pool[agent_id] = self.get_TXAstar_path(
        #         start_loc,
        #         start_dir,
        #         start_time=0,
        #         goal=goal
        #     )

        # ---  Plan with Prioritized Planning (PP) ---------------------------------
        # Here we allow 10 seconds (10,000 ms) of planning time for all agents.
        self.run_PP_planner(10000)

        return self.execute_action_from_path_pool()

    def get_astar_path(self, start: int, start_direct: int, goal: int):
        """Get path from Piglet Astar planner

        Args:
            start (int): start location
            start_direct (int): start direction
            goal (int): goal location
        Returns:
            path (List[Tuple[int,int]]): list of (location, direction) tuples
        """
        if self._search_engine is None:
            # Create the gridmap
            self._domain = gridmap.from_list(self.env.cols, self.env.rows, self.env.map)

            # ℹ️ INFO
            # Look, your search engine is called here!
            self._search_engine = opss25.a1.ex3_create_search.create_search(
                self._domain
            )

        self._search_engine.open_list_.clear()
        return self._search_engine.get_path(
            self._to_piglet_state(start, direction=start_direct),
            self._to_piglet_state(goal),
        )

    def get_txastar_path(
        self, start: int, start_direct: int, start_time: int, goal: int
    ):
        """Get path from Piglet TXAstar planner

        Args:
            start (int): start location
            start_direct (int): start direction
            goal (int): goal location
        Returns:
            path (List[Tuple[int,int]]): list of (location, direction) tuples
        """
        if self._search_engine is None:
            # Initialize Piglet TXAstar planner
            # print(self.env.map)
            self._domain = robotrunners(
                "example_problems/random.domain/maps/random-32-32-20.map"
            )
            self._expander = robotrunners_expander.robotrunners_expander(
                self._domain, self._default_res_table
            )
            self._heuristic = gridmap_h.piglet_heuristic
            open_list = bin_heap(search_node.compare_node_f)
            engine = graph_search.graph_search
            self._search_engine = engine(
                open_list, self._expander, heuristic_function=self._heuristic
            )

        self._search_engine.open_list_.clear()
        return self._search_engine.get_path(
            self._to_piglet_state(start, direction=start_direct, time=start_time),
            self._to_piglet_state(goal, time=-1),
        )

    def _plan_in_sequence(self, agent_ids: List[int], start_time: int = 0):
        """
        Try to plan paths sequentially for the given agent_ids.
        Returns:
            dict {agent_id: mapf_state_list} on success, or None if any agent fails.
        NOTE: This function does NOT commit reservations; caller commits on success.
        """
        self._default_res_table.clear()
        for i in agent_ids:

            # Build a piglet path for agent i
            if not self.env.goal_locations[i]:
                # No goal: keep position/orientation, advance time by 1 (WAIT-like)
                current_piglet_state = self._to_piglet_state(
                    self.env.curr_states[i].location,
                    direction=self.env.curr_states[i].orientation,
                    time=start_time,
                )
                next_piglet_state = self._to_piglet_state(
                    self.env.curr_states[i].location,
                    direction=self.env.curr_states[i].orientation,
                    time=start_time + 1,
                )
                self._path_pool[i] = [
                    (
                        self.env.curr_states[i].location,
                        self.env.curr_states[i].orientation,
                    )
                ]
                self.reserve_path(
                    [current_piglet_state, next_piglet_state], agent_id=i, start_time=0
                )
            else:
                piglet_path = self.get_txastar_path(
                    self.env.curr_states[i].location,
                    self.env.curr_states[i].orientation,
                    start_time,
                    self.env.goal_locations[i][0][0],
                )

                if piglet_path is None:
                    # pp could have not path for this agent set to wait in this case
                    return False
                else:
                    self._path_pool[i] = self.solution_to_mapf_state_list(piglet_path)[
                        1:
                    ]
                    self.reserve_path(
                        self.solution_to_piglet_state_list(piglet_path),
                        agent_id=i,
                        start_time=0,
                    )

            # self._path_pool[i] = self.solution_to_mapf_state_list(piglet_path)[1:]
            # self.reserve_path(self.solution_to_piglet_state_list(piglet_path), agent_id = i, start_time=0)

        return True

    def run_PP_planner(self, time_limit: int):
        """Run Piglet planner within time limit

        Args:
            time_limit (int): time limit in milliseconds
        Returns:
            path (List[Tuple[int,int]]): list of (location, direction) tuples for all agents
        """

        # print(self.env.num_of_agents)
        agent_ids = list(range(self.env.num_of_agents))
        random.shuffle(agent_ids)  # rando
        success = False
        while not success:
            success = self._plan_in_sequence(agent_ids, start_time=0)

    def execute_action_from_path_pool(self):
        actions = [MAPF.Action.W] * len(self.env.curr_states)
        # print("Path pool:", self._path_pool)
        for i in range(len(self.env.curr_states)):
            current_path = self._path_pool[i]
            if current_path[0][0] != self.env.curr_states[i].location:
                actions[i] = MAPF.Action.FW
            elif current_path[0][1] != self.env.curr_states[i].orientation:
                incr = current_path[0][1] - self.env.curr_states[i].orientation
                if incr == 1 or incr == -3:
                    actions[i] = MAPF.Action.CR
                elif incr == -1 or incr == 3:
                    actions[i] = MAPF.Action.CCR
        # print("Actions from path pool:", actions)
        return actions

    def solution_to_mapf_state_list(self, solution):
        return [self._to_mapf_state(node.state_) for node in solution.paths_]

    def solution_to_piglet_state_list(self, solution):
        return [node.state_ for node in solution.paths_]

    # -------- Reserve path forward (start → goal) --------
    def reserve_path(
        self,
        piglet_path: List[Tuple[int, int, Directions, int]],
        agent_id: int,
        start_time: int,
    ):
        """
        Reserve the path forward (start→goal), ignoring collisions.
        tuple of (x,y,d,t)
        """

        self._default_res_table.add_vertex(piglet_path[0], agent_id)
        for i in range(1, len(piglet_path)):
            if (
                piglet_path[i - 1][0] == piglet_path[i][0]
                and piglet_path[i - 1][1] == piglet_path[i][1]
            ):
                # same vertex
                self._default_res_table.add_vertex(piglet_path[i], agent_id)
            else:
                self._default_res_table.add_edge(
                    piglet_path[i - 1], piglet_path[i], agent_id
                )
                self._default_res_table.add_vertex(piglet_path[i], agent_id)

    # --- helpers --------------------------------------------------------
    def _loc_to_rc(self, loc: int) -> Tuple[int, int]:
        """Convert a flattened map index to (row, col)."""
        r = loc // self.env.cols
        c = loc % self.env.cols
        return r, c

    def _rc_to_loc(self, r: int, c: int) -> int:
        """Convert (row, col) back to single index."""
        return r * self.env.cols + c

    def _dir_to_piglet(self, direction: Optional[int]) -> Directions:
        """Convert integer direction to Directions enum."""
        if direction is None:
            return Directions.NONE
        mapping = {
            0: Directions.EAST,
            1: Directions.SOUTH,
            2: Directions.WEST,
            3: Directions.NORTH,
        }
        return mapping.get(direction, Directions.NONE)

    def _dir_to_mapf(self, direction: Directions) -> int:
        """Convert Directions enum back to MAPF integer representation."""
        reverse_map = {
            Directions.EAST: 0,
            Directions.SOUTH: 1,
            Directions.WEST: 2,
            Directions.NORTH: 3,
            Directions.NONE: -1,
        }
        return reverse_map.get(direction, -1)

    # --- piglet ---------------------------------------------------------
    def _to_piglet_state(
        self, loc: int, direction: Optional[int] = None, time: Optional[int] = None
    ) -> Union[Tuple[int, int, Directions], Tuple[int, int, Directions, int]]:
        # convert flat index -> (row, col)
        r, c = self._loc_to_rc(loc)

        # map direction int -> Directions enum
        if direction is None:
            d = Directions.NONE
        else:
            d = self._dir_to_piglet(direction)  # must return a Directions member

        # ALWAYS return something
        return (r, c, d) if time is None else (r, c, d, time)

    # --- mapf -----------------------------------------------------------
    def _to_mapf_state(
        self,
        piglet_state: Union[
            Tuple[int, int, Directions], Tuple[int, int, Directions, int]
        ],
    ) -> Tuple[int, int]:
        """
        Convert Piglet-style (r, c, d, [time]) → MAPF-style (loc, direction_index).
        Ignores the last element if present (e.g., time).
        """
        r, c, d = piglet_state[:3]
        loc = self._rc_to_loc(r, c)
        d_idx = self._dir_to_mapf(d)
        return (loc, d_idx)


if __name__ == "__main__":
    test_planner = pyMAPFPlanner()
    test_planner.initialize(100)
