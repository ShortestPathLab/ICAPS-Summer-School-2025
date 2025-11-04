from typing import Callable

import MAPF
from piglet.lib_piglet.search.base_search import base_search

GetPath = Callable[[MAPF.SharedEnvironment, int], list | None]

BindStartKit = Callable[[base_search], GetPath]

Planner = Callable[[MAPF.SharedEnvironment, list[list], bool], list[list]]
