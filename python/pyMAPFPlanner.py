import datetime
from functools import lru_cache
from typing import List, Optional, Tuple, Union

# League of Robot Runners imports
import MAPF

# # OPSS25 imports
import opss25.a1.ex3_create_search
import opss25.a2.ex3_create_search
from environment import EX
from python.opss25.utils import planners
from opss25.utils.types import Planner

# Piglet imports
from piglet.lib_piglet.constraints.robotrunners_constraints import (
    robotrunners_reservation_table,
)
from piglet.lib_piglet.domains.robotrunners import (
    Directions,
    robotrunners,
    robotrunners_state,
)
from piglet.lib_piglet.expanders import (
    base_expander,
)
from piglet.lib_piglet.logging.search_logger import bind, search_logger
from piglet.lib_piglet.output.trace_output import trace_output
from piglet.lib_piglet.search import (
    base_search,
)
from opss25.utils.interop import to_piglet_state

# 0=Action.FW, 1=Action.CR, 2=Action.CCR, 3=Action.W

LOG_ENABLED = False


class pyMAPFPlanner:

    _search_engine: base_search.base_search = None
    _expander: base_expander = None
    _domain = None
    _heuristic = None
    _default_res_table = None
    _map_file = None
    _queue: list[list[robotrunners_state]]

    def __init__(self, env: MAPF.SharedEnvironment = None) -> None:
        if env is not None:
            self.env: MAPF.SharedEnvironment = env

    def initialize(self, preprocess_time_limit: int):
        """_summary_

        Args:
            preprocess_time_limit (_type_): _description_
        """
        self._queue = [[] for _ in range(self.env.num_of_agents)]
        self._default_res_table = robotrunners_reservation_table(
            self.env.rows, self.env.cols
        )
        return True

    def plan(self, time_limit):
        return self.use_planner(self.get_planner())

    @lru_cache
    def get_planner(self):
        match EX:
            case 1:
                search = self.get_engine(
                    init=lambda: opss25.a1.ex3_create_search(
                        robotrunners.from_list(
                            self.env.cols,
                            self.env.rows,
                            self.env.map,
                            self.env.map_name,
                        )
                    )
                )
                # You can choose a planner style here
                # For example, here we use the naive planner
                # Try some other planners under `planner.*`
                return planners.naive(
                    get_path=lambda env, id: search(
                        env.curr_states[id],
                        env.curr_states[id],
                        env.goal_locations[id][0][0],
                    )
                )

            case 2:
                # TODO
                raise NotImplementedError()
            case 3:
                # TODO
                raise NotImplementedError()
            case 4:
                # TODO
                raise NotImplementedError()
            case 5:
                # TODO
                # This case is the main branch

                def create_engine():
                    engine = opss25.a1.ex3_create_search.create_search(
                        robotrunners.from_list(
                            self.env.cols,
                            self.env.rows,
                            self.env.map,
                            self.env.map_name,
                        )
                    )
                    if LOG_ENABLED:
                        logger = search_logger(
                            logger=trace_output(file="test.trace.yaml")
                        )
                        bind(engine, logger).head()
                    return engine

                search = self.get_engine(create_engine)

                # You can choose a planner style here
                # For example, here we use the naive planner
                # Try some other planners under `planner.*`
                return planners.naive(
                    get_path=lambda env, id: search(
                        env.curr_states[id].location,
                        env.curr_states[id].orientation,
                        env.goal_locations[id][0][0],
                    )
                )

    @lru_cache
    def get_engine(self, init):
        search_engine = init()

        def run(start: int, direction: Directions, goal: int):
            search_engine.open_list_.clear()
            solution = search_engine.get_path(
                to_piglet_state(self.env.cols, start, direction),
                to_piglet_state(self.env.cols, goal),
            )
            return solution.get_solution() if solution else []

        return run

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
            # Create the gridmap
            self._domain = robotrunners.from_list(
                self.env.cols, self.env.rows, self.env.map, self.env.map_name
            )

            # ℹ️ INFO
            # Look, your search engine is called here!
            self._search_engine = opss25.a2.ex3_create_search.create_search(
                self._domain, self._default_res_table
            )

        self._search_engine.open_list_.clear()
        return self._search_engine.get_path(
            self._to_piglet_state(start, direction=start_direct, time=start_time),
            self._to_piglet_state(goal, time=-1),
        )

    def put_agents_wait_in_place(self, agent_i: int, start_time: int):
        print(
            "Warning: PP could not find path for agent",
            agent_i,
            ", set to wait in place.",
            "loc",
            self.env.curr_states[agent_i].location,
            flush=True,
        )
        current_piglet_state = self._to_piglet_state(
            self.env.curr_states[agent_i].location,
            direction=self.env.curr_states[agent_i].orientation,
            time=start_time,
        )
        next_piglet_state = self._to_piglet_state(
            self.env.curr_states[agent_i].location,
            direction=self.env.curr_states[agent_i].orientation,
            time=start_time + 1,
        )
        self._queue[agent_i] = [
            (
                self.env.curr_states[agent_i].location,
                self.env.curr_states[agent_i].orientation,
            )
        ]
        self.reserve_path(
            [current_piglet_state, next_piglet_state], agent_id=agent_i, start_time=0
        )

    def _plan_in_sequence(self, replan_agent_ids: List[int], start_time: int = 0):
        """
        Try to plan paths sequentially for the given agent_ids.
        Returns:
            dict {agent_id: mapf_state_list} on success, or None if any agent fails.
        NOTE: This function does NOT commit reservations; caller commits on success.
        """
        print("PP planning for agents:", replan_agent_ids, flush=True)
        for i in replan_agent_ids:
            piglet_path = self.get_txastar_path(
                self.env.curr_states[i].location,
                self.env.curr_states[i].orientation,
                start_time,
                self.env.goal_locations[i][0][0],
            )
            if piglet_path is None:
                # pp could have not path for this agent set to wait in this case
                # return False
                self.put_agents_wait_in_place(i, start_time)
                continue
            else:
                self._queue[i] = self.solution_to_mapf_state_list(piglet_path)[1:]

                self.reserve_path(
                    self.solution_to_piglet_state_list(piglet_path),
                    agent_id=i,
                    start_time=0,
                )
        return True

    def find_replan_agents(self, agent_ids: List[int]):
        """
        Find agents that need replanning due to mismatches between current state and path pool.
        Returns:
            List of agent_ids that need replanning.
        """
        self._default_res_table.clear()
        has_collisions = False
        for i in agent_ids:
            if i not in self._queue.keys():
                continue
            if len(self._queue[i]) == 0:
                continue
            check_path = self._queue[i]
            if (
                self.env.curr_states[i].location != check_path[0][0]
                or self.env.curr_states[i].orientation != check_path[0][1]
            ):
                has_collisions = True  # replan all if we have mismatches between lcurrent state and path pool
                break
        if has_collisions:
            print("Detected path mismatch, replanning all agents.", flush=True)
            return agent_ids  # replan all agents if any mismatch detected

        # when no collisions, only replan agents with missing or empty paths
        replan_agents = []
        for i in agent_ids:
            if i not in self._queue.keys():
                replan_agents.append(i)
                continue
            if len(self._queue[i]) <= 1:
                replan_agents.append(i)
                continue
            # Reserve existing paths for agents not needing replanning
            print("Has existing path for agent", i, "reserving it.", flush=True)
            self._queue[i] = self._queue[i][1:]  # remove start
            piglet_path = self.mapf_state_list_to_piglet_state_list(
                self._queue[i],
                agent_id=i,
                start_time=0,
            )
            self.reserve_path(
                piglet_path,
                agent_id=i,
                start_time=0,
            )
        print("Agents needing replanning:", replan_agents, flush=True)
        return replan_agents

    def use_planner(self, plan_agent: Planner):
        self._queue = plan_agent(self.env, self._queue)
        return self.get_upcoming_action(pop=True)

    def get_upcoming_action(self, pop=False):
        actions = [MAPF.Action.W] * len(self.env.curr_states)
        for i in range(len(self.env.curr_states)):
            current_path = self._queue[i]
            current_state = to_piglet_state(
                self.env.cols,
                self.env.curr_states[i].location,
                self.env.curr_states[i].orientation,
            )
            cx, cy, cr, *_ = current_state

            if current_path is None or len(current_path) == 0:
                print("a", flush=True)
                # Leave as wait and continue
                actions[i] = MAPF.Action.W
            planned_next_state = current_path[0]
            nx, ny, nr, *_ = planned_next_state
            if (cx, cy) != (nx, ny):
                print("b", current_state, planned_next_state, flush=True)
                # raise BaseException()
                actions[i] = MAPF.Action.FW
            elif nr == cr:
                print("c", flush=True)
                actions[i] = MAPF.Action.W
            else:
                # Must be turn
                incr = planned_next_state[2] - current_state[2]
                if incr == 1 or incr == -3:
                    actions[i] = MAPF.Action.CR
                elif incr == -1 or incr == 3:
                    actions[i] = MAPF.Action.CCR
            if pop:
                print("r", flush=True)
                self._queue[i].pop(0)  # remove the executed action
        return actions

    def solution_to_mapf_state_list(self, solution):
        return [self._to_mapf_state(node.state_) for node in solution.paths_]

    def mapf_state_list_to_piglet_state_list(self, mapf_path, agent_id, start_time):
        piglet_path = []
        current_piglet_state = self._to_piglet_state(
            self.env.curr_states[agent_id].location,
            direction=self.env.curr_states[agent_id].orientation,
            time=start_time,
        )
        start_time += 1
        piglet_path.append(current_piglet_state)
        for state in mapf_path:
            current_piglet_state = self._to_piglet_state(
                state[0],
                direction=state[1],
                time=start_time,
            )
            piglet_path.append(current_piglet_state)
            start_time += 1
        return piglet_path

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


if __name__ == "__main__":
    test_planner = pyMAPFPlanner()
    test_planner.initialize(100)
