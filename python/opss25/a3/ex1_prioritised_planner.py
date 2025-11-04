def naive(get_path: GetPath):
    """Creates a planner that plans for all agents, any time there's a missing path, even if other agents are already planned"""

    def plan(
        env: MAPF.SharedEnvironment,
        paths: list[list],
    ):

        # Prioritised planning here
        pass

    return plan
