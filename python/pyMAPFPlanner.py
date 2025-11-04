from functools import lru_cache
from itertools import zip_longest
from typing import Callable

# League of Robot Runners imports
import MAPF

# # OPSS25 imports
import opss25.a1.ex3_create_search
from environment import EX
from opss25.utils import interop

# Piglet imports
from piglet.lib_piglet.constraints.robotrunners_constraints import (
    robotrunners_reservation_table,
)
from piglet.lib_piglet.domains.robotrunners import (
    Directions,
    robotrunners_state_is_equal,
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

from python.opss25.utils import planners

# 0=Action.FW, 1=Action.CR, 2=Action.CCR, 3=Action.W

LOG_ENABLED = False
REPLAN_ENABLED = True


class pyMAPFPlanner:

    _search_engine: base_search.base_search = None
    _expander: base_expander = None
    _domain = None
    _heuristic = None
    _default_res_table = None
    _map_file = None
    front_buffer: list[list[robotrunners_state]] = []
    # Back buffer only stores 1 past timestep's snapshot
    back_buffer: list[robotrunners_state] = None

    def __init__(self, env: MAPF.SharedEnvironment = None) -> None:
        if env is not None:
            self.env: MAPF.SharedEnvironment = env

    def initialize(self, _):
        """_summary_

        Args:
            preprocess_time_limit (_type_): _description_
        """
        self.reset()

        return True

    def reset(self):
        self.front_buffer = [[] for _ in range(self.env.num_of_agents)]
        self._default_res_table = robotrunners_reservation_table(
            self.env.rows, self.env.cols
        )

    def did_error(self):
        return self.back_buffer and not all(
            robotrunners_state_is_equal(a, b)
            for a, b in zip_longest(
                self.back_buffer,
                interop.to_piglet_state_list(self.env),
            )
        )

    def plan(self, _):
        plan_agents = self.get_planner()
        # plan_agent will either mutate self.buffer and return it
        # or create another buffer and return that.
        self.front_buffer = plan_agents(self.env, self.front_buffer, self.did_error())
        # Get and pop the next action.
        return self.get_upcoming_actions(pop=True)

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
                        env.curr_states[id].location,
                        env.curr_states[id].orientation,
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
    def get_engine(self, init: Callable[[], base_search.base_search]):
        search_engine = init()

        def run(start: int, direction: Directions, goal: int):
            search_engine.open_list_.clear()
            solution = search_engine.get_path(
                interop.to_piglet_state(self.env, start, direction),
                interop.to_piglet_state(self.env, goal),
            )
            return solution.get_solution()[1:] if solution else []

        return run

    def get_upcoming_actions(self, pop: bool = False):
        state_pairs = zip_longest(
            interop.to_piglet_state_list(self.env),
            [a[0] if len(a) else None for a in self.front_buffer],
        )

        def infer_action(prev: robotrunners_state, next: robotrunners_state):
            cx, cy, cr, *_ = prev
            nx, ny, nr, *_ = next
            if (cx, cy) != (nx, ny):
                # Location changed
                return MAPF.Action.FW
            elif nr != cr:
                # Orientation changed
                delta = nr - cr
                if delta == 1 or delta == -3:
                    return MAPF.Action.CR
                elif delta == -1 or delta == 3:
                    return MAPF.Action.CCR
            # Did nothing, or something went really wrong.
            return MAPF.Action.W

        actions = [infer_action(prev, next or prev) for prev, next in state_pairs]
        if pop:
            # Pop current action
            self.back_buffer = [
                # Mutates the front buffer!
                agent.pop(0) if len(agent) else None
                for agent in self.front_buffer
            ]

        return actions


if __name__ == "__main__":
    test_planner = pyMAPFPlanner()
    test_planner.initialize(100)
