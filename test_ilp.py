import unittest
import random
import vars
from gurobipy import Model, GRB, quicksum
import ilp
from test_vars import NUM_PRINT, NUM_TRIES, RANDOM_SEED


class TestWeaken(unittest.TestCase):
    def test_weaken(self):
        """
        Weaken the t,u relation to u >= 2*t-2. Check that the resulting constraints
        are always satisfiable.
        """
        random.seed(RANDOM_SEED)

        num_printed = 0
        for _ in range(NUM_TRIES):
            num_goods = random.choice(range(3, 6))
            goods = vars.get_goods(num_goods)
            agent_types = vars.get_agent_types(num_goods)
            model = Model("satisfiability")
            model.Params.LogToConsole = 0

            # Define variables for t,u and implement their constraint

            # set t to be a specific value (otherwise the solver is lazy and just does t=u=0)
            random_t = random.choice(range(1, 10))
            t = model.addVar(lb=random_t, vtype=GRB.INTEGER, name="t")
            u = model.addVar(lb=0, vtype=GRB.INTEGER, name="u")
            model.addConstr(u >= 2 * t - 2)  # weaker constraint -- should be sat now

            # Define variables for the agent body (one per agent type)
            num_agents = dict()
            for agent_type in agent_types:
                num_agents[agent_type] = model.addVar(
                    lb=0, vtype=GRB.INTEGER, name=f"x{agent_type}"
                )

            menu_to_c_to_binary_var = dict()
            for menu in vars.powerset(goods):
                menu_to_c_to_binary_var[menu] = dict()
                for c in goods:
                    menu_to_c_to_binary_var[menu][c] = model.addVar(
                        vtype=GRB.BINARY, name=f"{menu}_{c}"
                    )
                model.addConstr(
                    quicksum(menu_to_c_to_binary_var[menu].values()) >= 1,
                    f"{menu}_or_condition",
                )

                menu_constraints = ilp.get_menu_constraints(
                    menu,
                    goods,
                    num_agents,
                    agent_types,
                    t,
                    u,
                    menu_to_c_to_binary_var[menu],
                )
                for constraint in menu_constraints:
                    model.addConstr(constraint)

            model.optimize()
            status = model.Status

            self.assertEqual(GRB.Status.OPTIMAL, status)


class TestPolyhedra(unittest.TestCase):
    def test_remove_1(self):
        """
        Remove 1 polyhedron at random, and check that the resulting
        constraints are satisfiable.
        """
        random.seed(RANDOM_SEED)

        for num_goods in range(2, 5):  # num_goods = 5 takes 20s to test
            goods = vars.get_goods(num_goods)
            agent_types = vars.get_agent_types(num_goods)
            for elim_menu in vars.powerset(goods):
                model = Model("satisfiability")
                model.Params.LogToConsole = 0

                # Define variables for t,u and implement their constraint

                # set t to be a specific value (otherwise the solver is lazy and just does t=u=0)
                random_t = random.choice(range(1, 10))
                t = model.addVar(lb=random_t, vtype=GRB.INTEGER, name="t")
                u = model.addVar(lb=0, vtype=GRB.INTEGER, name="u")

                model.addConstr(eval("u >= 2 * t - 1"))

                # Define variables for the agent body (one per agent type)
                num_agents = dict()
                for agent_type in agent_types:
                    num_agents[agent_type] = model.addVar(
                        lb=0, vtype=GRB.INTEGER, name=f"x{agent_type}"
                    )

                menu_to_c_to_binary_var = dict()
                for menu in vars.powerset(goods):
                    if menu != elim_menu:
                        menu_to_c_to_binary_var[menu] = dict()
                        for c in goods:
                            menu_to_c_to_binary_var[menu][c] = model.addVar(
                                vtype=GRB.BINARY, name=f"{menu}_{c}"
                            )
                        model.addConstr(
                            quicksum(menu_to_c_to_binary_var[menu].values()) >= 1,
                            f"{menu}_or_condition",
                        )

                        menu_constraints = ilp.get_menu_constraints(
                            menu,
                            goods,
                            num_agents,
                            agent_types,
                            t,
                            u,
                            menu_to_c_to_binary_var[menu],
                        )
                        for constraint in menu_constraints:
                            model.addConstr(constraint)

                model.optimize()
                status = model.Status

                self.assertEqual(GRB.Status.OPTIMAL, status)


if __name__ == "__main__":
    unittest.main()
