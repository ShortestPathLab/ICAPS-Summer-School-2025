from functools import lru_cache
from itertools import zip_longest

# League of Robot Runners imports
import MAPF

# OPSS25 imports
import opss25.a1.ex4_basic_planner
import opss25.a2.ex4_reserved_planner
import opss25.a3.ex3_prioritised_planner
import opss25.a4.ex1_lns_planner

# Utils imports
from environment import EX
from opss25.utils import interop

# Piglet imports
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
from piglet.lib_piglet.search.base_search import (
    base_search,
)

# 0=Action.FW, 1=Action.CR, 2=Action.CCR, 3=Action.W

LOG_ENABLED = False


class pyMAPFPlanner:

    _search_engine: base_search = None
    _expander: base_expander = None
    _domain = None
    _heuristic = None
    _default_res_table = None
    _map_file = None
    front_buffer: list[list[robotrunners_state]] = []
    # Back buffer only stores 1 past timestep's snapshot
    back_buffer: list[robotrunners_state] = []

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

    def plan(self, _):
        plan_agents = self.get_planner()
        # plan_agent will either mutate self.buffer and return it
        # or create another buffer and return that.
        self.front_buffer = plan_agents(self.env, self.front_buffer, self.did_error())

        # Get and pop the next action.
        return self.get_upcoming_actions(pop=True)

    # ─── Utils ────────────────────────────────────────────────────────────

    def reset(self):
        self.front_buffer = [[] for _ in range(self.env.num_of_agents)]

    def did_error(self):
        did_error = self.back_buffer and not all(
            robotrunners_state_is_equal(a, b)
            for a, b in zip_longest(
                self.back_buffer,
                interop.to_piglet_state_list(self.env),
            )
        )
        if did_error:
            print(
                "ERROR",
                self.back_buffer,
                interop.to_piglet_state_list(self.env),
                flush=True,
            )
        return did_error

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
                next.pop(0) if len(next) else prev
                for prev, next in zip_longest(self.back_buffer, self.front_buffer)
            ]

        return actions

    # ─── Planner ──────────────────────────────────────────────────────────

    @lru_cache
    def get_planner(self):
        return self.bind_planner(
            {
                1: opss25.a1.ex4_basic_planner.chosen_planner,
                2: opss25.a2.ex4_reserved_planner.reserved_planner,
                3: opss25.a3.ex3_prioritised_planner.prioritised_planner,
                4: opss25.a4.ex1_lns_planner.lns_planner,
                # This one runs when you're in the main branch
                5: opss25.a1.ex4_basic_planner.chosen_planner,
            }[EX]
        )

    def bind_planner(self, planner):
        domain = robotrunners.from_list(
            self.env.cols,
            self.env.rows,
            self.env.map,
            self.env.map_name,
        )

        def use_with_startkit(piglet_engine: base_search):
            if LOG_ENABLED:
                logger = search_logger(logger=trace_output(file="output.trace.yaml"))
                bind(piglet_engine, logger).head()

            def run(start: int, direction: Directions, goal: int):
                piglet_engine.open_list_.clear()
                solution = piglet_engine.get_path(
                    interop.to_piglet_state(self.env, start, direction),
                    interop.to_piglet_state(self.env, goal),
                )
                return solution.get_solution()[1:] if solution else []

            return lambda env, id: run(
                env.curr_states[id].location,
                env.curr_states[id].orientation,
                env.goal_locations[id][0][0],
            )

        return planner(
            domain,
            use_with_startkit,
        )


if __name__ == "__main__":
    test_planner = pyMAPFPlanner()
    test_planner.initialize(100)
