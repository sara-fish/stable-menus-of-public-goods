import unittest
import vars
import random

NUM_PRINT = 0
NUM_TRIES = 3
RANDOM_SEED = 1999


class TestGetMethods(unittest.TestCase):
    def test_get_goods(self):
        self.assertEqual(vars.get_goods(2), [1, 2])
        self.assertEqual(vars.get_goods(3), [1, 2, 3])
        self.assertEqual(vars.get_goods(4), [1, 2, 3, 4])
        self.assertEqual(vars.get_goods(5), [1, 2, 3, 4, 5])
        self.assertEqual(vars.get_goods(6), [1, 2, 3, 4, 5, 6])

    def test_get_agent_types(self):
        self.assertEqual(vars.get_agent_types(2), [(1, 2), (2, 1)])
        self.assertEqual(
            vars.get_agent_types(3),
            [(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)],
        )

    def test_get_agent_types_trunc(self):
        self.assertEqual(vars.get_agent_types(2, 1), [(1,), (2,)])
        self.assertEqual(
            vars.get_agent_types(3, 1), [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]
        )
        self.assertEqual(vars.get_agent_types(3, 2), [(1,), (2,), (3,)])
        self.assertEqual(
            vars.get_agent_types(4, 2),
            [
                (1, 2),
                (1, 3),
                (1, 4),
                (2, 1),
                (2, 3),
                (2, 4),
                (3, 1),
                (3, 2),
                (3, 4),
                (4, 1),
                (4, 2),
                (4, 3),
            ],
        )

    def test_get_agent_types_all(self):
        self.assertEqual(
            vars.get_agent_types(1, include_all_nonstrict=True), [(), (1,)]
        )
        self.assertEqual(
            vars.get_agent_types(2, include_all_nonstrict=True),
            [(), (1,), (2,), (1, 2), (2, 1)],
        )
        self.assertEqual(
            vars.get_agent_types(3, include_all_nonstrict=True),
            [
                (),
                (1,),
                (2,),
                (3,),
                (1, 2),
                (1, 3),
                (2, 1),
                (2, 3),
                (3, 1),
                (3, 2),
                (1, 2, 3),
                (1, 3, 2),
                (2, 1, 3),
                (2, 3, 1),
                (3, 1, 2),
                (3, 2, 1),
            ],
        )

    def get_agent_types_all_random(self):
        for _ in range(NUM_TRIES):
            num_goods = random.choice([4, 5, 6, 7, 8])
            cset_len = random.choice(range(num_goods + 1))
            random_cset = tuple(random.sample(vars.get_goods(num_goods), cset_len))
            vars.assertEqual(
                True,
                random_cset
                in vars.get_agent_types(num_goods, include_all_nonstrict=True),
            )

    def get_agent_types_all_length_test(self):
        def factorial(n):
            prod = 1
            for i in range(1, n + 1):
                prod *= i
            return prod

        for num_goods in range(1, 9):
            expected_length = sum([factorial(i) for i in range(num_goods + 1)])
            actual_length = len(
                vars.get_agent_types(num_goods, include_all_nonstrict=True)
            )
            self.assertEqual(expected_length, actual_length)

    def test_get_agent_types_pref_c(self):
        agent_types = vars.get_agent_types(3)
        self.assertEqual(
            vars.get_agent_types_pref_c(1, [2, 3], agent_types), [(1, 2, 3), (1, 3, 2)]
        )
        self.assertEqual(
            vars.get_agent_types_pref_c(2, [1], agent_types),
            [(2, 1, 3), (2, 3, 1), (3, 2, 1)],
        )

        agent_types = vars.get_agent_types(4)
        self.assertEqual(
            vars.get_agent_types_pref_c(1, [2, 3, 4], agent_types),
            [
                (1, 2, 3, 4),
                (1, 2, 4, 3),
                (1, 3, 2, 4),
                (1, 3, 4, 2),
                (1, 4, 2, 3),
                (1, 4, 3, 2),
            ],
        )


class TestPrefMethods(unittest.TestCase):
    def test_agent_type_pref1(self):
        random.seed(RANDOM_SEED)

        agent_type = tuple(range(10, 0, -1))
        for _ in range(NUM_TRIES):
            c1 = random.choice(agent_type)
            c2 = random.choice(agent_type)
            if c1 != c2:
                self.assertEqual(c1 > c2, vars.agent_type_pref(agent_type, c1, c2))

    def test_agent_type_pref2(self):
        agent_type = (1, 4, 3, 2, 5)
        self.assertEqual(True, vars.agent_type_pref(agent_type, 1, 4))
        self.assertEqual(True, vars.agent_type_pref(agent_type, 1, 3))
        self.assertEqual(True, vars.agent_type_pref(agent_type, 1, 2))
        self.assertEqual(True, vars.agent_type_pref(agent_type, 1, 5))
        self.assertEqual(False, vars.agent_type_pref(agent_type, 3, 4))
        self.assertEqual(False, vars.agent_type_pref(agent_type, 2, 4))
        self.assertEqual(False, vars.agent_type_pref(agent_type, 5, 4))
        self.assertEqual(False, vars.agent_type_pref(agent_type, 2, 3))
        self.assertEqual(False, vars.agent_type_pref(agent_type, 5, 3))
        self.assertEqual(False, vars.agent_type_pref(agent_type, 5, 2))

    def test_agent_type_pref_trunc(self):
        agent_type = (1, 5, 3)
        self.assertEqual(True, vars.agent_type_pref(agent_type, 1, 2))
        self.assertEqual(True, vars.agent_type_pref(agent_type, 1, 3))
        self.assertEqual(True, vars.agent_type_pref(agent_type, 1, 4))
        self.assertEqual(True, vars.agent_type_pref(agent_type, 1, 5))
        self.assertEqual(True, vars.agent_type_pref(agent_type, 5, 2))
        self.assertEqual(True, vars.agent_type_pref(agent_type, 5, 3))
        self.assertEqual(True, vars.agent_type_pref(agent_type, 5, 4))
        self.assertEqual(True, vars.agent_type_pref(agent_type, 3, 2))
        self.assertEqual(True, vars.agent_type_pref(agent_type, 3, 4))
        self.assertEqual(False, vars.agent_type_pref(agent_type, 2, 1))
        self.assertEqual(False, vars.agent_type_pref(agent_type, 2, 5))
        self.assertEqual(False, vars.agent_type_pref(agent_type, 2, 3))
        self.assertEqual(False, vars.agent_type_pref(agent_type, 2, 4))
        self.assertEqual(False, vars.agent_type_pref(agent_type, 5, 1))
        self.assertEqual(False, vars.agent_type_pref(agent_type, 3, 5))

    def test_agent_type_pref_list1(self):
        random.seed(RANDOM_SEED)

        agent_type = tuple(range(10, 0, -1))
        for _ in range(NUM_TRIES):
            # Pick random subset `other`
            other = set()
            for _ in range(4):
                other.add(random.choice(agent_type))
            # Pick random c not in other
            c = random.choice(list(set(agent_type).difference(other)))
            self.assertEqual(
                c > max(other), vars.agent_type_pref_list(agent_type, c, other)
            )

    def test_agent_type_pref_list2(self):
        agent_type = (1, 4, 3, 2, 5)
        self.assertEqual(True, vars.agent_type_pref_list(agent_type, 1, {4, 3, 2, 5}))
        self.assertEqual(True, vars.agent_type_pref_list(agent_type, 1, [4, 3]))
        self.assertEqual(True, vars.agent_type_pref_list(agent_type, 4, {3, 2}))
        self.assertEqual(False, vars.agent_type_pref_list(agent_type, 5, [1, 2]))
        self.assertEqual(False, vars.agent_type_pref_list(agent_type, 2, {4, 5}))

    def test_agent_type_pref_list_trunc1(self):
        random.seed(RANDOM_SEED)

        agent_type = tuple(range(10, 5, -1))
        for _ in range(NUM_TRIES):
            # Pick random subset `other`
            other = set()
            for _ in range(4):
                other.add(random.choice(range(1, 11)))
            # Pick random c not in other
            c = random.choice(list(set(range(1, 11)).difference(other)))
            self.assertEqual(
                c in agent_type and c > max(other.intersection(agent_type)),
                vars.agent_type_pref_list(agent_type, c, other),
            )

    def test_agent_type_pref_list_trunc2(self):
        agent_type = (1, 5, 3)
        self.assertEqual(True, vars.agent_type_pref_list(agent_type, 1, {2, 3, 4, 5}))
        self.assertEqual(True, vars.agent_type_pref_list(agent_type, 1, {2, 4}))
        self.assertEqual(True, vars.agent_type_pref_list(agent_type, 5, {2, 3}))
        self.assertEqual(True, vars.agent_type_pref_list(agent_type, 3, {2, 4}))
        self.assertEqual(True, vars.agent_type_pref_list(agent_type, 1, {2, 5}))
        self.assertEqual(False, vars.agent_type_pref_list(agent_type, 5, {1, 2}))
        self.assertEqual(False, vars.agent_type_pref_list(agent_type, 3, {2, 5}))
        self.assertEqual(False, vars.agent_type_pref_list(agent_type, 2, {4, 6}))
        self.assertEqual(False, vars.agent_type_pref_list(agent_type, 2, {5, 4}))


if __name__ == "__main__":
    unittest.main()
