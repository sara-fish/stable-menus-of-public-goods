import argparse


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-g",
        "--num_goods",
        required=True,
        type=int,
        help="Number of goods",
    )

    parser.add_argument(
        "-u",
        "--u_condition",
        nargs="?",
        required=True,
        type=str,
        help='u condition to use (e.g. "u >= 2*t-2")',
    )

    parser.add_argument(
        "--include_trunc",
        action="store_true",
        help="Include all possible agent prefs, not just complete ones",
    )

    args = parser.parse_args()

    return args
