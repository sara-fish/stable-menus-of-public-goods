# Stable Menus of Public Goods

This repo contains code used to obtain the computational results in our paper [*Stable Menus of Public Goods*](https://arxiv.org/abs/2402.11370).

## Installation instructions 

Install required dependencies:

```
pip install z3-solver
pip install gurobipy
```

Z3 is open-source ([GitHub link here](https://github.com/Z3Prover/z3)). A license is required to use Gurobi, see [here](https://www.gurobi.com/academia/academic-program-and-licenses/) for information on academic licenses.

## Replicating results from paper

Our results can be replicated in two ways: with the SMT solver z3, or with the ILP solver Gurobi. **Using the SMT approach is recommended, as the ILP approach is more computationally demanding.** To run with z3, use `smt.py`. To run with Gurobi, use `ilp.py`. In either case, select the number of goods with the `-c` flag, and specify the constraint between $u$ and $t$ with the `-u` flag. To search over all preferences (including truncated ones, as opposed to complete preferences only), enable the flag `--include_trunc`. 

### Replicating results with SMT solver (z3)

To replicate on complete preferences:

```
python3 smt.py -g 3 -u "u >= 2*t-1"
python3 smt.py -g 4 -u "u >= 2*t-1"
python3 smt.py -g 5 -u "u >= 2*t-1"
python3 smt.py -g 6 -u "u >= 2*t-1"
```

To replicate on incomplete preferences:
```
python3 smt.py -g 3 -u "u >= 2*t-1" --include_trunc
python3 smt.py -g 4 -u "u >= 2*t-1" --include_trunc
python3 smt.py -g 5 -u "u >= 2*t-1" --include_trunc
python3 smt.py -g 6 -u "u >= 2*t-1" --include_trunc
```

In all cases, the expected output should be `unsat`. 

| $g$ | SMT      | SMT with `--include_trunc`        |
|---|----------|------------|
| 3 |   0.02s  |  0.13s     |
| 4 |    0.06s |  0.22s     |
| 5 |   2.54s  |    10.46s   |
| 6 |   659.02s      |   1293.84s      |

### Replicating results with ILP solver (Gurobi)

Instructions are included below for completeness. However, for $g \ge 5$, Gurobi is significantly slower. 

```
python3 ilp.py -g 3 -u "u >= 2*t-1"
python3 ilp.py -g 4 -u "u >= 2*t-1"
python3 ilp.py -g 5 -u "u >= 2*t-1"
python3 ilp.py -g 6 -u "u >= 2*t-1"
```
In all cases, the expected output should be `Model is infeasible`. 

### Beyond $g=6$ 

To show there exists a menu selection problem on $g=7$ public goods for which there exists no $(t,u)$-stable menu (for $t,u$ satisfying $u \ge 2t-1$):

```
python3 smt.py -g 7 -u "u >= 2*t-1"
```

This is expected to return `sat` after about 9 days (and save the variable assignments to a `.pkl` file). 

To check whether there exists a counterexample better than the one described in the paper (this is an open question), one would have to run:

```
python3 smt.py -g 7 -u "11*u >= 23*(t-1) + 1"
```

Letting this run for 30 days was not sufficient to determine satisfiability.


## More details

Description of individual files:
- `vars.py` contains simple methods used by both the SMT and ILP solvers. 
- `arg_parser.py` defines the command-line interface used by both the SMT and ILP scripts.
- `smt.py` sets up the constraints to feed into the SMT solver, and also invokes the SMT solver. 
- `ilp.py` sets up the constraints to feed into the ILP solver, and also invokes the ILP solver.
- `test_vars.py` contains unit tests for `vars.py`.
- `test_smt.py` and `test_ilp.py` have (very similar) unit tests for each solver.

To run unit tests:
```
python3 test_smt.py
python3 test_ilp.py
python3 test_vars.py 
```
