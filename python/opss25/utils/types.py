from typing import Callable

import MAPF


GetPath = Callable[[MAPF.SharedEnvironment, int], list | None]

Planner = Callable[[MAPF.SharedEnvironment, list[list]], list[list]]
