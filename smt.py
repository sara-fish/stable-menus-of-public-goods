from vars import get_agent_types_pref_c, get_agent_types, get_goods, powerset
from z3 import Not, Solver, Or, Ints, Int, sat
from arg_parser import parse_args
import time
from datetime import datetime
import pickle


def get_menu_t_constraints(
    menu: tuple, goods: list, num_agents: dict, agent_types: list, t
) -> list:
    menu_t_constraints = []
    for c in menu:
        # Checking that there are >=t agents with c > (all other goods in menu)
        other = set(menu).difference({c})
        agent_types_pref_c = get_agent_types_pref_c(c, other, agent_types)
        cond = Not(
            sum([num_agents[agent_type] for agent_type in agent_types_pref_c]) >= t
        )
        menu_t_constraints.append(cond)
    return menu_t_constraints


def get_menu_u_constraints(
    menu: tuple, goods: list, num_agents: dict, agent_types: list, u
) -> list:
    menu_u_constraints = []
    for c in goods:
        if c not in menu:
            # Checking that there are < u agents with c > (all goods in menu)
            other = menu
            agent_types_pref_c = get_agent_types_pref_c(c, other, agent_types)
            cond = Not(
                sum([num_agents[agent_type] for agent_type in agent_types_pref_c]) < u
            )
            menu_u_constraints.append(cond)
    return menu_u_constraints


def get_menu_constraints(
    menu: tuple, goods: list, num_agents: dict, agent_types: list, t, u
) -> list:
    """
    Given menu (good set), generate a list of constraints which determine the
    complement of the corresponding polyhedron.

    So, Or(get_menu_constraints(menu, goods, num_agents)) is the region not covered by
    menu's polyhedron.
    """
    menu_constraints = []
    menu_constraints.extend(
        get_menu_t_constraints(menu, goods, num_agents, agent_types, t)
    )
    menu_constraints.extend(
        get_menu_u_constraints(menu, goods, num_agents, agent_types, u)
    )
    return menu_constraints


def model_to_dict(model) -> dict:
    """
    Convert model (output of running solver.model() in z3) to a Python dict.
    """
    d = dict()
    for var in model:
        # var and model[var] are weird z3 ctypes, need to explicitly convert to python types for pickling
        d[str(var)] = int(str(model[var]))
    return d


if __name__ == "__main__":

    args = parse_args()

    num_goods = args.num_goods
    u_condition = args.u_condition
    include_trunc = args.include_trunc

    goods = get_goods(num_goods)
    agent_types = get_agent_types(num_goods, include_all_nonstrict=include_trunc)

    print(
        f"Solving good assignment problem for c={num_goods}, u>={u_condition}, include_all_nonstrict={include_trunc}",
        flush=True,
    )
    start_time = time.time()

    # Set up solver
    print("Inputting constraints into solver...", end="", flush=True)
    solver = Solver()

    # Define variables for t,u and implement their constraint
    t, u = Ints("t u")
    solver.add(t >= 1, eval(u_condition))

    # Define variables for the agent body (one per agent type)
    num_agents = dict()
    for agent_type in agent_types:
        num_agents[agent_type] = Int(f"x{agent_type}")
        solver.add(num_agents[agent_type] >= 0)
        # solver.add(num_agents[agent_type] < t) # suffices, but confusingly is slower

    for menu in powerset(goods):
        menu_constraints = get_menu_constraints(
            menu, goods, num_agents, agent_types, t, u
        )
        solver.add(Or(menu_constraints))
    print("done.", flush=True)

    # Evaluate
    print("Checking if constraints are sat or unsat...", end="", flush=True)
    check = solver.check()
    check_end_time = time.time()
    print("done.", flush=True)
    print(f"Result: {check}", flush=True)
    print(f"Time needed: {check_end_time - start_time:0.2f}s", flush=True)
    if check == sat:
        print("Finding model...", flush=True, end="")
        model = solver.model()
        model_end_time = time.time()
        filename = (
            datetime.now().strftime("%Y%m%d%H%M%S%f") + f"_c_{num_goods}_model.pkl"
        )
        print(f"done. (See {filename} for output)", flush=True)
        print(
            f"Time needed to compute model: {time.time() - check_end_time:0.2f}s",
            flush=True,
        )
        # Make dict with model information
        model_dict = model_to_dict(model)
        with open(filename, "wb") as f:
            pickle.dump(model_dict, f)
