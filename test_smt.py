import unittest
import random
import vars
import z3
import smt
from test_vars import NUM_PRINT, NUM_TRIES, RANDOM_SEED


class TestGetMethods(unittest.TestCase):

    def test_get_menu_constraints(self):
        num_goods = 3
        goods = vars.get_goods(num_goods)
        agent_types = vars.get_agent_types(num_goods)
        solver = z3.Solver()
        num_stud = dict()
        for agent_type in agent_types:
            num_stud[agent_type] = z3.Int(f"x{agent_type}")
            solver.add(num_stud[agent_type] >= 0)

        t = z3.Int("t")
        u = 2 * t - 1
        menu_constraints = smt.get_menu_constraints(
            (1,), goods, num_stud, agent_types, t, u
        )

        menu_constraints_manual = [
            z3.Not(sum(list(num_stud.values())) >= t),
            z3.Not(
                sum([num_stud[(2, 1, 3)], num_stud[(2, 3, 1)], num_stud[(3, 2, 1)]]) < u
            ),
            z3.Not(
                sum([num_stud[(2, 3, 1)], num_stud[(3, 1, 2)], num_stud[(3, 2, 1)]]) < u
            ),
        ]
        self.assertEqual(menu_constraints, menu_constraints_manual)


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
            solver = z3.Solver()

            # Define variables for t,u and implement their constraint
            t, u = z3.Ints("t u")
            solver.add(
                t >= 1, u >= 2 * t - 2
            )  # weakened constraint -- should be sat now
            random_t = random.choice(range(1, 10))
            solver.add(t == z3.IntVal(random_t))

            # Define variables for the student body (one per student type)
            var = dict()
            for agent_type in agent_types:
                var[agent_type] = z3.Int(f"x{agent_type}")
                solver.add(var[agent_type] >= 0)

            for menu in vars.powerset(goods):
                menu_constraints = smt.get_menu_constraints(
                    menu, goods, var, agent_types, t, u
                )
                solver.add(z3.Or(menu_constraints))

            self.assertEqual(z3.sat, solver.check())
            # sanity check by printing models for the small c=3 cases
            if z3.sat == solver.check() and num_goods == 3 and num_printed < NUM_PRINT:
                num_printed += 1
                m = solver.model()
                print("Test type: relaxing t,u constraint to u >= 2t-2")
                print(f"Model (t={m[t]}, u={m[u]}): {m}")
                print()


class TestPolyhedra(unittest.TestCase):
    def test_remove_1(self):
        """
        Remove 1 polyhedron at random, and check that the resulting
        constraints are satisfiable.
        """
        random.seed(RANDOM_SEED)

        num_printed = 0
        for num_goods in range(2, 5):  # num_goods = 5 takes 20s to test
            goods = vars.get_goods(num_goods)
            agent_types = vars.get_agent_types(num_goods)
            for elim_menu in vars.powerset(goods):
                solver = z3.Solver()

                # Define variables for t,u and implement their constraint
                t, u = z3.Ints("t u")
                solver.add(t >= 1, u >= 2 * t - 1)
                random_t = random.choice(range(1, 10))
                solver.add(t == z3.IntVal(random_t))

                # Define variables for the student body (one per student type)
                var = dict()
                for agent_type in agent_types:
                    var[agent_type] = z3.Int(f"x{agent_type}")
                    solver.add(var[agent_type] >= 0)

                # Add constraints for all polyhedra except elim_menu
                for menu in vars.powerset(goods):
                    if menu != elim_menu:
                        menu_constraints = smt.get_menu_constraints(
                            menu, goods, var, agent_types, t, u
                        )
                        solver.add(z3.Or(menu_constraints))

                self.assertEqual(z3.sat, solver.check())

                # Sanity check by printing models (=variable values which satisfy constraints) for the small c<=3 cases
                if (
                    z3.sat == solver.check()
                    and num_goods <= 3
                    and num_printed < NUM_PRINT
                ):
                    num_printed += 1
                    m = solver.model()
                    print("Test type: removing 1 polyhedron")
                    print(f"Model (t={m[t]}, removed={elim_menu}): {m}")
                    print()


if __name__ == "__main__":
    unittest.main()
