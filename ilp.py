from vars import get_agent_types_pref_c, get_agent_types, get_goods, powerset
from gurobipy import Model, GRB, quicksum
from arg_parser import parse_args
import time
from datetime import datetime
import pickle


def get_menu_constraints(
    menu: tuple,
    goods: list,
    num_agents: dict,
    agent_types: list,
    t,
    u,
    c_to_binary_var: dict,
) -> list:
    """
    Given menu (good set), generate a list of constraints which determine the
    complement of the corresponding polyhedron.

    So, Or(get_menu_constraints(menu, goods, num_agents)) is the region not covered by
    menu's polyhedron.

    To implement the Or() in Gurobi, we introduce an auxiliary binary variable for each constraint. These are given by c_to_binary_var. For a constraint given by good c, c_to_binary_var[c] is true (1) if that constraint should be the true one in the Or, and false (0) otherwise.
    """
    menu_constraints = []
    # Because num_agents[agent_type] <= t-1 for each agent_type, for sure an upper bound on quicksum(num_agents[agent_type]) is len(agent_types) * t
    # M just needs to be really big to implement Or (see below)
    M = 10 * t * (len(agent_types) + 1)

    # Generate constraints which come from t-feasibility
    for c in menu:
        # Checking that there are >=t agents with c > (all other goods in menu)
        other = set(menu).difference({c})
        agent_types_pref_c = get_agent_types_pref_c(c, other, agent_types)
        b = c_to_binary_var[c]
        # This says: sum-t <= -1 when b=1 (constraint active), else sum-t <= -1-M (constraint vacuously true)
        cond = (
            quicksum([num_agents[agent_type] for agent_type in agent_types_pref_c]) - t
            <= (1 - b) * M - 1
        )
        menu_constraints.append(cond)

    # Generate constraints which come from u-contestability
    for c in goods:
        if c not in menu:
            # Checking that there are < u agents with c > (all goods in menu)
            other = menu
            agent_types_pref_c = get_agent_types_pref_c(c, other, agent_types)
            b = c_to_binary_var[c]
            # This says: sum-u >=0 when b=1 (constraint active), else sum-u >=-M (constraint vacuously true)
            cond = (
                quicksum([num_agents[agent_type] for agent_type in agent_types_pref_c])
                - u
                >= b * M - M
            )
            menu_constraints.append(cond)

    return menu_constraints


if __name__ == "__main__":

    args = parse_args()

    num_goods = args.num_goods
    u_condition = args.u_condition
    include_trunc = args.include_trunc

    goods = get_goods(num_goods)
    agent_types = get_agent_types(num_goods, include_all_nonstrict=include_trunc)

    print(
        f"Solving menu selection problem for c={num_goods}, u>={u_condition}, include_all_nonstrict={include_trunc}",
        flush=True,
    )
    start_time = time.time()

    # Set up solver
    print("Inputting constraints into solver...", end="", flush=True)
    model = Model("satisfiability")

    # Define variables for t,u and implement their constraint
    t = model.addVar(lb=0, vtype=GRB.INTEGER, name="t")
    u = model.addVar(lb=0, vtype=GRB.INTEGER, name="u")

    model.addConstr(eval(u_condition))

    # Define variables for the agent body (one per agent type)
    num_agents = dict()
    for agent_type in agent_types:
        num_agents[agent_type] = model.addVar(
            lb=0, vtype=GRB.INTEGER, name=f"x{agent_type}"
        )
        # By lemma in appendix A of paper, can assume each type has <=t-1 agents
        model.addConstr(num_agents[agent_type] <= t - 1)

    # What we want to do is this:
    # for menu in powerset(goods):
    #     menu_constraints = get_menu_constraints(
    #         menu, goods, num_agents, agent_types, t, u
    #     )
    #     solver.add(Or(menu_constraints))
    # However, Gurobi can't just do Or, so instead we create a dummy binary variable,
    # one for each menu in powerset(goods), which is 1 if it's true and 0 if false.
    menu_to_c_to_binary_var = dict()
    for menu in powerset(goods):
        menu_to_c_to_binary_var[menu] = dict()
        for c in goods:
            menu_to_c_to_binary_var[menu][c] = model.addVar(
                vtype=GRB.BINARY, name=f"{menu}_{c}"
            )
        model.addConstr(
            quicksum(menu_to_c_to_binary_var[menu].values()) >= 1,
            f"{menu}_or_condition",
        )

        menu_constraints = get_menu_constraints(
            menu, goods, num_agents, agent_types, t, u, menu_to_c_to_binary_var[menu]
        )
        for constraint in menu_constraints:
            model.addConstr(constraint)

    print("done.", flush=True)

    # Evaluate
    print("Checking if constraints are sat or unsat...", end="", flush=True)
    model.optimize()
    status = model.Status
    check_end_time = time.time()
    print("done.", flush=True)
    print(f"Result: {status}", flush=True)
    print(f"Time needed: {check_end_time - start_time:0.2f}s", flush=True)
    if status == GRB.Status.OPTIMAL:
        filename = (
            datetime.now().strftime("%Y%m%d%H%M%S%f") + f"_c_{num_goods}_model.pkl"
        )
        print(f"See {filename} for model.", flush=True)
        # Make dict with model information
        model_dict = {var.VarName: var.X for var in model.getVars()}
        with open(filename, "wb") as f:
            pickle.dump(model_dict, f)
