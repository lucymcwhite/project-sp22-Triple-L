"""Solves an instance.

Modify this file to implement your own solvers.

For usage, run `python3 solve.py --help`.
"""
import numpy as np
import argparse
from pathlib import Path
import sys
from typing import Callable, Dict
from point import Point

from instance import Instance
from solution import Solution
from file_wrappers import StdinFileWrapper, StdoutFileWrapper


def solve_naive(instance: Instance) -> Solution:
    return Solution(
        instance=instance,
        towers=instance.cities,
    )

def num_new_cities(instance: Instance, coord: Point, uncovered: set):
    res = 0
    r_sq = instance.R_s**2
    for x in range(coord.x - instance.R_s, coord.x + instance.R_s + 1):
        for y in range(coord.y - instance.R_s, coord.y + instance.R_s + 1):
            if x >= 0 and x < instance.D and y >= 0 and y < instance.D:
                if Point.distance_sq(Point(x, y), coord) <= r_sq and Point(x,y) in uncovered:
                    res += 1
    return res

    

def solve_greedy(instance: Instance) -> Solution:
    #O(D^2*(R_s)^2*N)
    uncovered = set(instance.cities)
    towers = []
    while uncovered:
        #For every point in the grid, compute number of new cities that will be covered if
        #a tower was placed there. Then place a tower at the best point.
        potential = []
        arr = np.array([[num_new_cities(instance, Point(x,y), uncovered) for y in range(instance.D)] for x in range(instance.D)])
        max_cities = np.max(arr)
        for x in range(len(arr)):
            for y in range(len(arr[0])):
                if arr[x][y] == max_cities:
                    potential.append(Point(x, y))
        city = np.random.choice(potential)
        r_sq = instance.R_s**2
        for x in range(city.x - instance.R_s, city.x + instance.R_s + 1):
            for y in range(city.y - instance.R_s, city.y + instance.R_s + 1):
                if x >= 0 and x < instance.D and y >= 0 and y < instance.D:
                    if Point.distance_sq(Point(x, y), city) <=  r_sq and Point(x,y) in uncovered:
                        uncovered.remove(Point(x, y))
        towers.append(city)
    return Solution(instance=instance, towers=towers)



        

SOLVERS: Dict[str, Callable[[Instance], Solution]] = {
    "naive": solve_naive,
    "greedy": solve_greedy
}


# You shouldn't need to modify anything below this line.
def infile(args):
    if args.input == "-":
        return StdinFileWrapper()

    return Path(args.input).open("r")

def outfile(args):
    if args.output == "-":
        return StdoutFileWrapper()

    return Path(args.output).open("w")

def main(args):
    with infile(args) as f:
        instance = Instance.parse(f.readlines())
        solver = SOLVERS[args.solver]
        solution = solver(instance)
        assert solution.valid()
        with outfile(args) as g:
            print("# Penalty: ", solution.penalty(), file=g)
            solution.serialize(g)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve a problem instance.")
    parser.add_argument("input", type=str, help="The input instance file to "
                        "read an instance from. Use - for stdin.")
    parser.add_argument("--solver", required=True, type=str,
                        help="The solver type.", choices=SOLVERS.keys())
    parser.add_argument("output", type=str, 
                        help="The output file. Use - for stdout.", 
                        default="-")
    main(parser.parse_args())
