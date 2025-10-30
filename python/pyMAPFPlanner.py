import MAPF

from typing import Dict, List, Tuple, Set, Optional, Union
from queue import PriorityQueue
import numpy as np
import datetime
import sys, os
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "piglet")))
# Piglet imports
from lib_piglet.expanders import (
    grid_expander,
    robotrunners_expander,
    base_expander,
)
from lib_piglet.search import (
    tree_search,
    graph_search,
    base_search,
    search_node,
)
from lib_piglet.domains import (
    robotrunners,
    gridmap
)
from lib_piglet.utils.data_structure import bin_heap
from lib_piglet.heuristics import gridmap_h
from lib_piglet.domains.robotrunners import Directions
from lib_piglet.constraints.robotrunners_constraints import robotrunners_reservation_table


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
            self.env = env
        # self._default_res_table = robotrunners_reservation_table(self.env.rows, self.env.cols)
        #TODO: NEED to wrapper this to proper name.
        map_file = "example_problems/random.domain/maps/random-32-32-20.map"


    def initialize(self, preprocess_time_limit: int):
        """_summary_

        Args:
            preprocess_time_limit (_type_): _description_
        """
        self._default_res_table = robotrunners_reservation_table(self.env.rows, self.env.cols)
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

        time_remaining = self.env.plan_start_time + datetime.timedelta(milliseconds=time_limit) - self.env.plan_current_time()
        return self.execute_action_from_path_pool()
    

    

    def get_Astar_path(self, start: int, start_direct: int, goal: int):
        """ Get path from Piglet Astar planner

        Args:
            start (int): start location
            start_direct (int): start direction
            goal (int): goal location
        Returns:
            path (List[Tuple[int,int]]): list of (location, direction) tuples
        """ 
        if self._search_engine is None:
            # Initialize Piglet Astar planner
            self._domain = gridmap.gridmap("example_problems/random.domain/maps/random-32-32-20.map")
            self._expander = grid_expander.grid_expander(self._domain)
            self._heuristic = gridmap_h.piglet_heuristic
            open_list = bin_heap(search_node.compare_node_f)
            engine = graph_search.graph_search
            self._search_engine = engine(open_list, self._expander, heuristic_function=self._heuristic)

        self._search_engine.open_list_.clear()
        return self._search_engine.get_path(self._to_piglet_state(start,direction=start_direct),
                                           self._to_piglet_state(goal))

    def get_TXAstar_path(self, start: int, start_direct: int, start_time: int, goal: int):
        """ Get path from Piglet TXAstar planner

        Args:
            start (int): start location
            start_direct (int): start direction
            goal (int): goal location
        Returns:
            path (List[Tuple[int,int]]): list of (location, direction) tuples
        """ 
        if self._search_engine is None:
            # Initialize Piglet TXAstar planner
            self._domain = robotrunners.robotrunners("example_problems/random.domain/maps/random-32-32-20.map")
            self._expander = robotrunners_expander.robotrunners_expander(self._domain, self._default_res_table)
            self._heuristic = gridmap_h.piglet_heuristic
            open_list = bin_heap(search_node.compare_node_f)
            engine = graph_search.graph_search
            self._search_engine = engine(open_list, self._expander, heuristic_function=self._heuristic)

        self._search_engine.open_list_.clear()
        return self._search_engine.get_path(self._to_piglet_state(start,direction=start_direct,time=start_time),
                                           self._to_piglet_state(goal,time=-1))

    def run_PP_planner(self, time_limit: int):
        """ Run Piglet planner within time limit

        Args:
            time_limit (int): time limit in milliseconds
        Returns:
            path (List[Tuple[int,int]]): list of (location, direction) tuples for all agents
        """ 
        self._default_res_table.clear()
        for i in range(self.env.num_of_agents):
            piglet_path = self.get_TXAstar_path(
                self.env.curr_states[i].location,
                self.env.curr_states[i].orientation,
                0,
                self.env.goal_locations[i][0][0],
            )
            self._path_pool[i] = self.solution_to_mapf_state_list(piglet_path)
            #TODO: Bugs here: need to be fixed.
            # self.reserve_path(self.solution_to_piglet_state_list(piglet_path), agent_id = i, start_time=0)
    
    
    def execute_action_from_path_pool(self):
        self.run_PP_planner(10000)
        actions = [MAPF.Action.W] * len(self.env.curr_states)
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
        return actions


    def solution_to_mapf_state_list(self, solution):
        return [self._to_mapf_state(node.state_) for node in solution.paths_]

    def solution_to_piglet_state_list(self, solution):
        return [node.state_ for node in solution.paths_]
    
    def test_TXAstar(self,time_limit:int):
        actions = [MAPF.Action.W] * len(self.env.curr_states)
        run_PP_planner = self.run_PP_planner(time_limit)

        return actions
    

        # -------- Reserve path forward (start → goal) --------
    def reserve_path(
        self,
        piglet_path: List[Tuple[int, int, Directions, int]],
        agent_id: int,
        start_time: int
    ):
        """
        Reserve the path forward (start→goal), ignoring collisions.
        tuple of (x,y,d,t)
        """

        self._default_res_table.add_vertex(piglet_path[0], agent_id)
        for i in range(1, len(piglet_path)):
            if piglet_path[i - 1][0] == piglet_path[i][0] and piglet_path[i - 1][1] == piglet_path[i][1]:
                #same vertex
                self._default_res_table.add_vertex(piglet_path[i], agent_id)
            else:
                self._default_res_table.add_edge(piglet_path[i - 1], piglet_path[i], agent_id)
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
            Directions.NONE: -1
        }
        return reverse_map.get(direction, -1)

    # --- piglet ---------------------------------------------------------
    def _to_piglet_state(
        self,
        loc: int,
        direction: Optional[int] = None,
        time: Optional[int] = None
    ) -> Union[Tuple[int, int, Directions], Tuple[int, int, Directions, int]]:
        # convert flat index -> (row, col)
        r , c = self._loc_to_rc(loc)    

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
        piglet_state: Union[Tuple[int, int, Directions], Tuple[int, int, Directions, int]]
    ) -> Tuple[int, int]:
        """
        Convert Piglet-style (r, c, d, [time]) → MAPF-style (loc, direction_index).
        Ignores the last element if present (e.g., time).
        """
        r, c, d = piglet_state[:3]
        loc = self._rc_to_loc(r, c)   
        d_idx = self._dir_to_mapf(d)
        return (loc, d_idx)



    




    



























    def naive_a_star(self,time_limit):
        actions = [MAPF.Action.W for i in range(len(self.env.curr_states))]
        for i in range(0, self.env.num_of_agents):
            path = []
            if len(self.env.goal_locations[i]) == 0:
                path.append((self.env.curr_states[i].location, self.env.curr_states[i].orientation))
            else:
                path = self.single_agent_plan(
                    self.env.curr_states[i].location, self.env.curr_states[i].orientation, self.env.goal_locations[i][0][0])

            if path[0][0] != self.env.curr_states[i].location:
                actions[i] = MAPF.Action.FW
            elif path[0][1] != self.env.curr_states[i].orientation:
                incr = path[0][1]-self.env.curr_states[i].orientation
                if incr == 1 or incr == -3:
                    actions[i] = MAPF.Action.CR
                elif incr == -1 or incr == 3:
                    actions[i] = MAPF.Action.CCR
        actions = [int(a) for a in actions]
        return np.array(actions, dtype=int)

    def single_agent_plan(self, start: int, start_direct: int, end: int):
        path = []
        open_list = PriorityQueue()
        s = (start, start_direct, 0, self.getManhattanDistance(start, end))
        open_list.put([0, s])
        all_nodes = dict()
        close_list = set()
        parent = {(start, start_direct): None}
        all_nodes[start*4+start_direct] = s
        while not open_list.empty():
            curr = (open_list.get())[1]
            close_list.add(curr[0]*4+curr[1])
            if curr[0] == end:
                curr = (curr[0], curr[1])
                while curr != None:
                    path.append(curr)
                    curr = parent[curr]
                path.pop()
                path.reverse()

                break
            neighbors = self.getNeighbors(curr[0], curr[1])
            for neighbor in neighbors:
                if (neighbor[0]*4+neighbor[1]) in close_list:
                    continue
                next_node = (neighbor[0], neighbor[1], curr[2]+1,
                             self.getManhattanDistance(neighbor[0], end))
                parent[(next_node[0], next_node[1])] = (curr[0], curr[1])
                open_list.put([next_node[3]+next_node[2], next_node])
        return path

    def getManhattanDistance(self, loc1: int, loc2: int) -> int:
        loc1_x = loc1//self.env.cols
        loc1_y = loc1 % self.env.cols
        loc2_x = loc2//self.env.cols
        loc2_y = loc2 % self.env.cols
        return abs(loc1_x-loc2_x)+abs(loc1_y-loc2_y)

    def validateMove(self, loc: int, loc2: int) -> bool:
        loc_x = loc//self.env.cols
        loc_y = loc % self.env.cols
        if(loc_x >= self.env.rows or loc_y >= self.env.cols or self.env.map[loc] == 1):
            return False
        loc2_x = loc2//self.env.cols
        loc2_y = loc2 % self.env.cols
        if(abs(loc_x-loc2_x)+abs(loc_y-loc2_y) > 1):
            return False
        return True

    def getNeighbors(self, location: int, direction: int):
        neighbors = []
        # forward
        candidates = [location+1, location+self.env.cols,
                      location-1, location-self.env.cols]
        forward = candidates[direction]
        new_direction = direction
        if (forward >= 0 and forward < len(self.env.map) and self.validateMove(forward, location)):
            neighbors.append((forward, new_direction))
        # turn left
        new_direction = direction-1
        if (new_direction == -1):
            new_direction = 3
        neighbors.append((location, new_direction))
        # turn right
        new_direction = direction+1
        if (new_direction == 4):
            new_direction = 0
        neighbors.append((location, new_direction))
        return neighbors

    def space_time_plan(self,start: int, start_direct: int, end: int, reservation: Set[Tuple[int, int, int]]) -> List[Tuple[int, int]]:
        path = []
        open_list = PriorityQueue()
        all_nodes = {}  # loc+dict, t
        parent={}
        s = (start, start_direct, 0, self.getManhattanDistance(start, end))
        open_list.put((s[3], id(s), s))
        parent[(start * 4 + start_direct, 0)]=None

        while not open_list.empty():
            n=open_list.get()
            _, _, curr = n
        
            curr_location, curr_direction, curr_g, _ = curr

            if (curr_location*4+curr_direction,curr_g) in all_nodes:
                continue
            all_nodes[(curr_location*4+curr_direction,curr_g)]=curr
            if curr_location == end:
                while True:
                    path.append((curr[0], curr[1]))
                    curr=parent[(curr[0]*4+curr[1],curr[2])]
                    if curr is None:
                        break
                path.pop()
                path.reverse()
                break
            
            neighbors = self.getNeighbors(curr_location, curr_direction)

            for neighbor in neighbors:
                neighbor_location, neighbor_direction = neighbor

                if (neighbor_location, -1, curr[2] + 1) in reservation:
                    continue

                if (neighbor_location, curr_location, curr[2] + 1) in reservation:
                    continue

                neighbor_key = (neighbor_location * 4 +
                                neighbor_direction, curr[2] + 1)

                if neighbor_key in all_nodes:
                    old = all_nodes[neighbor_key]
                    if curr_g + 1 < old[2]:
                        old = (old[0], old[1], curr_g + 1, old[3], old[4])
                else:
                    next_node = (neighbor_location, neighbor_direction, curr_g + 1,
                                self.getManhattanDistance(neighbor_location, end))
        
                    open_list.put(
                        (next_node[3] + next_node[2], id(next_node), next_node))
                
                    parent[(neighbor_location * 4 +
                            neighbor_direction, next_node[2])]=curr
        return path

    def sample_priority_planner(self,time_limit:int):
        actions = [MAPF.Action.W] * len(self.env.curr_states)
        reservation = set()  # loc1, loc2, t

        for i in range(self.env.num_of_agents):
            path = []
            if not self.env.goal_locations[i]:
                path.append((self.env.curr_states[i].location, self.env.curr_states[i].orientation))
                reservation.add((self.env.curr_states[i].location, -1, 1))

        for i in range(self.env.num_of_agents):
            path = []
            if self.env.goal_locations[i]:
                path = self.space_time_plan(
                    self.env.curr_states[i].location,
                    self.env.curr_states[i].orientation,
                    self.env.goal_locations[i][0][0],
                    reservation
                )
            
            if path:
                if path[0][0] != self.env.curr_states[i].location:
                    actions[i] = MAPF.Action.FW
                elif path[0][1] != self.env.curr_states[i].orientation:
                    incr = path[0][1] - self.env.curr_states[i].orientation
                    if incr == 1 or incr == -3:
                        actions[i] = MAPF.Action.CR
                    elif incr == -1 or incr == 3:
                        actions[i] = MAPF.Action.CCR

                last_loc = -1
                t = 1
                for p in path:
                    reservation.add((p[0], -1, t))
                    if last_loc != -1:
                        reservation.add((last_loc, p[0], t))
                    last_loc = p[0]
                    t += 1

        return actions
    

    # def sample_priority_planner(self, time_limit: int):
    #     print("inside the planner")
    #     actions = [MAPF.Action.W] * len(self.env.curr_states)

    #     for i in range(self.env.num_of_agents):
    #         if not self.env.goal_locations[i]:e
    #             continue

    #         start = self.env.curr_states[i].location
    #         start_dir = self.env.curr_states[i].orientation
    #         goal = self.env.goal_locations[i][0][0]

    #         path = self.piglet.search_path(start, start_dir, goal)
    #         # print(path)
    #         # print(type(path))
    #         if path:
    #             print("hahdfhsdhfadshfdsahfd")
    #             next_loc, next_dir = path[0]
    #             cur_loc = start
    #             cur_dir = start_dir
    #             print (f"Agent {i}: from loc {cur_loc} dir {cur_dir} to next loc {next_loc} dir {next_dir}")
    #             if next_loc != cur_loc:
    #                 actions[i] = MAPF.Action.FW
    #             elif next_dir != cur_dir:
    #                 incr = (next_dir - cur_dir) % 4
    #                 if incr == 1:
    #                     actions[i] = MAPF.Action.CR
    #                 elif incr == 3:
    #                     actions[i] = MAPF.Action.CCR

    #             self.piglet.reserve_forward(path, start, i, start_time=0)

    #     return np.array([int(a) for a in actions], dtype=int)



if __name__ == "__main__":
    test_planner = pyMAPFPlanner()
    test_planner.initialize(100)
