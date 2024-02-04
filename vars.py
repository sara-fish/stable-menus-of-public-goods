import itertools


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itertools.chain.from_iterable(
        itertools.combinations(s, r) for r in range(len(s) + 1)
    )


def get_agent_types_pref_c(c, other, agent_types: list) -> list:
    """
    Find which agent_types would pick good `c` over any public good in `other`.

    Keyword arguments:
    c -- a public good
    other -- some goods
    agent_types -- list of agent types
    """
    l = []
    for agent_type in agent_types:
        if agent_type_pref_list(agent_type, c, other):
            l.append(agent_type)
    return l


def agent_type_pref_list(agent_type, c, other) -> bool:
    """
    True if agent_type prefers c > o for all o in other, otherwise false.
    This just calls `agent_type_pref()`, agnostic to underlying
    data structures in case I change later

    Keyword arguments:
    agent_type -- a agent type
    c -- a good
    other -- list of goods
    """
    for o in other:
        if not agent_type_pref(agent_type, c, o):
            return False
    return True


def agent_type_pref(agent_type, c1, c2) -> bool:
    """
    True if agent_type prefers c1 > c2. False otherwise.

    Keyword arguments:
    agent_type -- a agent type (ordered tuple of goods, listed best to worst)
    c1, c2 -- each a good (some element of `agent_type`)

    Examples: agent_type is (1,2,4)
    1 > 3: True
    2 > 4: True
    3 > 5: False
    5 > 3: False
    """
    if c1 == c2:
        raise ValueError("Cannot compare identical goods")
    else:
        for c in agent_type:
            if c1 == c:
                return True
            elif c2 == c:
                return False
        # If neither public good appears in agent_type, return false
        return False


def get_goods(num_goods: int) -> list:
    """
    Given `num_goods`, return list containing all good names.
    """
    return list(range(1, num_goods + 1))


def get_agent_types(
    num_goods: int, num_unranked: int = 0, include_all_nonstrict: bool = False
) -> list:
    """
    Given `num_goods`, return list containing all agent types
    (= preference relations over goods.)

    Example:
    num_goods = 4:
    returns (1,2,3,4), (1,2,4,3), ...
    num_goods = 4, num_unranked = 2:
    returns (1, 2), (1, 3), (1, 4), (2, 1), ...
    num_goods = 4, include_all_nonstrict = True:
    (1,2,3,4), (1,2,3), (1,2), (1), (), (1,2,4,3), ... [not in this order]
    """
    if not include_all_nonstrict:
        agent_types = list(
            itertools.permutations(get_goods(num_goods), num_goods - num_unranked)
        )
    else:
        agent_types = list(
            itertools.chain(
                *[
                    itertools.permutations(range(1, num_goods + 1), r)
                    for r in range(num_goods + 1)
                ]
            )
        )
    return agent_types
