"""Solves an instance.

Modify this file to implement your own solvers.

For usage, run `python3 solve.py --help`.
"""
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
    for x in range(coord[0] - instance.R_s(), coord[0] + instance.R_s() + 1):
        for y in range(coord[1] - instance.R_s(), coord[1] + instance.R_s() + 1):
            if x >= 0 and x < instance.D() and y >= 0 and y < instance.D():
                if Point.distance_sq(Point(x, y), coord) <= r_sq and Point(x,y) in uncovered:
                    res += 1
    return res

    
#while there are uncovered cities, goes through each city coordinate and records have many other cities
# there are within the service radius. chooses the city with the most neighboring uncovered cities to place the tower 
def solve_greedy(instance: Instance) -> Solution:
    uncovered = set(instance.cities)
    towers = []
    while uncovered:
        #For every city, compute number of new cities that will be covered if
        #a tower was placed there. Then place a tower at the best point.
        city_dict = {}
        best_city = None
        most_neighbors = 0
        for city in instance.cities:
            neighbors = num_new_cities(instance, city, uncovered)
            city_dict[city] = neighbors
            if neighbors > most_neighbors:
                most_neighbors = neighbors
                best_city = city
        city_tower = best_city
        r_sq = instance.R_s**2
        for x in range(city_tower.x - instance.R_s, city_tower.x + instance.R_s + 1):
            for y in range(city_tower.y - instance.R_s, city_tower.y + instance.R_s + 1):
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