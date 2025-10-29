# piglet_space_time_wrapper.py
from __future__ import annotations
from typing import List, Tuple, Optional
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "piglet")))
# Piglet imports
from lib_piglet.domains import robotrunners
from lib_piglet.expanders.robotrunners_expander import robotrunners_expander
from lib_piglet.heuristics import gridmap_h
from lib_piglet.search import graph_search
import lib_piglet.search.search_node as sn
from lib_piglet.utils.data_structure import bin_heap
from lib_piglet.domains.robotrunners import Directions
from lib_piglet.constraints.robotrunners_constraints import robotrunners_reservation_table
import lib_piglet.solution.solution as s


class PigletSpaceTimeWrapper:
    """
    Wrapper around lib_piglet for MAPFPlanner-style planning and reservation-aware
    reverse-path construction.

    Features:
      • Initializes only from a MovingAI-format map file.
      • search_path() returns MAPFPlanner-style (loc, dir) path.
      • path_to_reverse_with_reservations() produces goal→start timed states
        (x, y, t) and uses a reservation table to avoid collisions.

    Conventions:
      - loc = row * cols + col
      - dir: 0=E, 1=S, 2=W, 3=N
      - reservation coords: (x=col, y=row, t)
    """

    def __init__(self, map_file: str) -> None:
        if not os.path.exists(map_file):
            raise FileNotFoundError(map_file)
        self.map_file = map_file

        # Parse MovingAI map header
        with open(map_file, "r") as f:
            lines = [ln.strip() for ln in f.readlines()]
        self.cols = None
        self.rows = None
        for ln in lines[:10]:
            if ln.lower().startswith("width"):
                self.cols = int(ln.split()[1])
            elif ln.lower().startswith("height"):
                self.rows = int(ln.split()[1])
        if self.cols is None or self.rows is None:
            raise ValueError("Invalid MovingAI map header: missing width/height")

        # Build Piglet environment
        self.default_res_table = robotrunners_reservation_table(self.cols, self.rows)
        self._dm = robotrunners.robotrunners(map_file)
        self._heuristic = gridmap_h.piglet_heuristic
        self._engine = graph_search.graph_search
        self._expander = robotrunners_expander(self._dm, self.default_res_table)
        self.open_list = bin_heap(sn.compare_node_f)
        self.search_engine = self._engine(self.open_list, self._expander, heuristic_function=self._heuristic)

    # ---------------------------------------------------------------------- #
    # Search path (forward, MAPFPlanner format)
    # ---------------------------------------------------------------------- #
    def search_path(self, start_loc: int, start_dir: int, start_time, goal_loc: int) -> List[Tuple[int, int]]:
        print(f"Searching path from loc {start_loc} dir {start_dir} to goal loc {goal_loc}")
        sr, sc = self._loc_to_rc(start_loc)
        er, ec = self._loc_to_rc(goal_loc)
        sdir = self._dir_to_piglet(start_dir)
        start_state = (sr, sc, sdir, start_time)
        goal_state = (er, ec, Directions.NONE,-1) # set to east for now ;
        print(f"Converted to Piglet states: start {start_state}, goal {goal_state}")
        raw_path = self._search_once((11,8,Directions.EAST,0),(10,9,Directions.NONE,-1))
        print (raw_path)
        if not raw_path:
            return []

        # print( "Raw path: ohhhhhhh path!!!!!!!!!!!!")
        # Accept either tuples or objects with .state
        converted: List[Tuple[int, int]] = []
        for st in raw_path:
            r, c, hd = st[:3]
            loc = self._rc_to_loc(r, c)
            dir_ = self._piglet_to_dir(hd)
            converted.append((loc, dir_))

        # Omit the start state so path[0] is the next step (turn or move)
        if converted and converted[0] == (start_loc, start_dir):
            converted = converted[1:]
        
        return converted

    

    # -------- Reserve path forward (start → goal) --------
    def reserve_path(
        self,
        mapf_path: List[Tuple[int, int]],
        start_loc: int,
        agent_id: int,
        start_time: int,
        reservation_table: Optional[robotrunners_reservation_table] = None,
    ):
        """
        Reserve the path forward (start→goal), ignoring collisions.
        Always continues to the goal; if a location/edge is already reserved,
        still proceeds and overwrites/records the reservation.
        Returns a timed list [(x,y,t), ...] for debugging.
        """
        res_table = reservation_table or self.default_res_table
        locs = [start_loc] + [loc for (loc, _) in mapf_path]
        if not locs:
            return []

        r0, c0 = self._loc_to_rc(locs[0])
        x0, y0 = c0, r0
        res_table.add_vertex((x0, y0, start_time), agent_id)

        t = start_time
        for i in range(1, len(locs)):
            prev_loc = locs[i - 1]
            curr_loc = locs[i]
            pr, pc = self._loc_to_rc(prev_loc)
            cr, cc = self._loc_to_rc(curr_loc)
            prev_x, prev_y = pc, pr
            curr_x, curr_y = cc, cr
            t += 1

            # Just reserve everything forward; ignore existing reservations
            res_table.add_edge((prev_x, prev_y, t - 1), (curr_x, curr_y, t), agent_id)
            res_table.add_vertex((curr_x, curr_y, t), agent_id)

    # ---- Remove (unreserve) the same forward path reservations ----
    def remove_path(
        self,
        mapf_path: List[Tuple[int, int]],
        start_loc: int,
        agent_id: int,
        start_time: int,
        reservation_table: Optional[robotrunners_reservation_table] = None,
    ) :
        """
        Undo reservations made by reserve_forward: deletes edge + vertex reservations
        at the same timestamps. Returns the same timed list [(x,y,t), ...] that was removed.
        """
        res_table = reservation_table or self.default_res_table

        locs = [start_loc] + [loc for (loc, _) in mapf_path]
        if not locs:
            return []

        r0, c0 = self._loc_to_rc(locs[0])
        x0, y0 = c0, r0


        # Now delete in a safe order: edges first for each move, then vertices.
        # t0 vertex:
        #   delete at the end so intermediate edge deletions still have their endpoints recorded if your table checks.
        t = start_time
        for i in range(1, len(locs)):
            pr, pc = self._loc_to_rc(locs[i - 1])
            cr, cc = self._loc_to_rc(locs[i])
            prev_x, prev_y = pc, pr
            curr_x, curr_y = cc, cr
            t += 1
            # Remove edge (prev -> curr) arriving at t, then the arrival vertex
            res_table.del_edge((prev_x, prev_y, t - 1), (curr_x, curr_y, t), agent_id)
            res_table.del_vertex((curr_x, curr_y, t), agent_id)

        # Finally remove the start vertex at t0
        res_table.del_vertex((x0, y0, start_time), agent_id)

    
    def solution_to_state_list(self, solution):
        return [node.state_ for node in solution.paths_]

    def _search_once(self, start_state, goal_state):
        self.search_engine.open_list_.clear()
        solution = self.search_engine.get_path(start_state, goal_state)
        return self.solution_to_state_list(solution)

    def _loc_to_rc(self, loc: int) -> Tuple[int, int]:
        return loc // self.cols, loc % self.cols

    def _rc_to_loc(self, r: int, c: int) -> int:
        return r * self.cols + c

    @staticmethod
    def _dir_to_piglet(d: int) -> Directions:
        return [Directions.EAST, Directions.SOUTH, Directions.WEST, Directions.NORTH][d % 4]

    @staticmethod
    def _piglet_to_dir(d: Directions) -> int:
        mapping = {
            Directions.EAST: 0,
            Directions.SOUTH: 1,
            Directions.WEST: 2,
            Directions.NORTH: 3,
        }
        return mapping[d]

    @staticmethod
    def _reserve_vertex(res_table, x: int, y: int, t: int, agent_id: int):
        res_table.add_vertex((x, y, t), agent_id)

    @staticmethod
    def _reserve_edge(res_table, prev_state: Tuple[int, int, int],
                      next_state: Tuple[int, int, int], agent_id: int):
        res_table.add_edge(prev_state, next_state, agent_id)

if __name__ == "__main__":
    # Simple test
    wrapper = PigletSpaceTimeWrapper("../example_problems/random.domain/maps/random-32-32-20.map")
    # Searching path from loc 360 dir 0 to goal loc 329

    # path = wrapper.get_path((11,8,Directions.NORTH,0),(10,9,Directions.NONE,-1))
    path = wrapper.search_path(360, 0, 0, 329)  # from loc 0 facing N to loc 255
    # path = wrapper.get_path((11, 8, Directions.EAST, 0),(10, 9, Directions.NONE, -1))
    print("Path:", path)

    # In utils.py

    # lorr_map_to_piglet_map

