from collections import namedtuple


Agent = namedtuple('Agent', 'id, start, goal')

def get_plan(
    solution,
    domain,
    agents_to_plan:list[Agent],
    reservation_table,
):
    # shuffle agent ordering
    # write a loop
    # inside the loop
    # call ex3 from a2 with reservation table
    # edit solution
    # return solution
    pass

def random_walk(
    reservation_table,
    agent,
) -> list[Agent]:
    pass

def select_agents_to_destroy(k: int):
    # choose a subset of agents
    # edit solution
    # return solution
    pass
    
def destroy_and_replan(
    solution,
    domain,
    agents_to_plan:list[Agent],
    reservation_table
):
    # Chooses a subset of agents to destroy
    # Destroys them
    # Replan them
    # edit and return solution
    pass
