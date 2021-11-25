import sys

from genetic_island_algorithm import GeneticIslandAlgorithm
from jmetal.problem.singleobjective.unconstrained import Rastrigin
from jmetal.operator import BinaryTournamentSelection, PolynomialMutation, SBXCrossover, BestSolutionSelection
from jmetal.util.termination_criterion import StoppingByEvaluations
import matplotlib.pyplot as plt
import json
import shutil
import os


def run():
    conf_file = sys.argv[1]
    island = sys.argv[2]
    with open(conf_file) as file:
        configuration = json.loads(file.read())

    NUMBER_OF_VARIABLES = 5
    NUMBER_OF_EVALUATIONS = 10000
    problem = Rastrigin(NUMBER_OF_VARIABLES)

    print(configuration["number_of_islands"])
    genetic_island_algorithm = GeneticIslandAlgorithm(
        problem=problem,
        population_size=100,
        offspring_population_size=20,
        mutation=PolynomialMutation(
            1.0 / problem.number_of_variables, 20.0),
        crossover=SBXCrossover(0.9, 20.0),
        selection=BinaryTournamentSelection(),
        migration_interval=configuration["migration_interval"],
        number_of_islands=configuration["number_of_islands"],
        number_of_emigrants=configuration["number_of_migrants"],
        island=1,
        termination_criterion=StoppingByEvaluations(
            max_evaluations=NUMBER_OF_EVALUATIONS),
    )

    genetic_island_algorithm.run()

    result = genetic_island_algorithm.get_result()

    print(f'Solution: {result}')
    print(f'Fitness: {result.objectives[0]}')

if __name__ == '__main__':
    run()