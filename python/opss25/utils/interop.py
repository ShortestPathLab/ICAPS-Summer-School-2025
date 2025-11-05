# --- piglet ---------------------------------------------------------
from typing import Optional, Tuple, Union

import MAPF
from piglet.lib_piglet.domains.robotrunners import Directions


def to_piglet_state_list(
    env: MAPF.SharedEnvironment,
):
    return [
        to_piglet_state(
            env,
            a.location,
            a.orientation,
        )
        for a in env.curr_states
    ]


def get_agent_state(env: MAPF.SharedEnvironment, id: int):
    return to_piglet_state(
        env,
        env.curr_states[id].location,
        env.curr_states[id].orientation,
    )


def to_piglet_state(
    env: MAPF.SharedEnvironment,
    loc: int,
    direction: Optional[int] = None,
    time: Optional[int] = None,
) -> Union[Tuple[int, int, Directions], Tuple[int, int, Directions, int]]:
    # convert flat index -> (row, col)
    r, c = loc_to_rc(env.cols, loc)

    # map direction int -> Directions enum
    if direction is None:
        d = Directions.NONE
    else:
        d = dir_to_piglet(direction)  # must return a Directions member

    # ALWAYS return something
    return (r, c, d) if time is None else (r, c, d, time)


# --- mapf -----------------------------------------------------------
def to_mapf_state(
    cols,
    piglet_state: Union[Tuple[int, int, Directions], Tuple[int, int, Directions, int]],
) -> Tuple[int, int]:
    """
    Convert Piglet-style (r, c, d, [time]) → MAPF-style (loc, direction_index).
    Ignores the last element if present (e.g., time).
    """
    r, c, d = piglet_state[:3]
    loc = rc_to_loc(cols, r, c)
    d_idx = dir_to_mapf(d)
    return (loc, d_idx)


# --- helpers --------------------------------------------------------
def loc_to_rc(cols: int, loc: int) -> Tuple[int, int]:
    """Convert a flattened map index to (row, col)."""
    r = loc // cols
    c = loc % cols
    return r, c


def rc_to_loc(cols: int, r: int, c: int) -> int:
    """Convert (row, col) back to single index."""
    return r * cols + c


def dir_to_piglet(direction: Optional[int]) -> Directions:
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


def dir_to_mapf(direction: Directions) -> int:
    """Convert Directions enum back to MAPF integer representation."""
    reverse_map = {
        Directions.EAST: 0,
        Directions.SOUTH: 1,
        Directions.WEST: 2,
        Directions.NORTH: 3,
        Directions.NONE: -1,
    }
    return reverse_map.get(direction, -1)
