import json

from jmetal.algorithm.singleobjective.genetic_algorithm import GeneticAlgorithm
from typing import TypeVar, Generic, List

from jmetal.config import store
from jmetal.core.operator import Mutation, Crossover, Selection
from jmetal.core.problem import Problem
from jmetal.util.evaluator import Evaluator
from jmetal.util.generator import Generator
from jmetal.util.termination_criterion import TerminationCriterion
import random
import pika

S = TypeVar('S')
R = TypeVar('R')


class GeneticIslandAlgorithm(GeneticAlgorithm):
    def __init__(self,
                 problem: Problem,
                 population_size: int,
                 offspring_population_size: int,
                 mutation: Mutation,
                 crossover: Crossover,
                 selection: Selection,

                 migration_interval: int,
                 number_of_islands: int,
                 number_of_emigrants: int,
                 island: int,  # island identifier

                 termination_criterion: TerminationCriterion = store.default_termination_criteria,
                 population_generator: Generator = store.default_generator,
                 population_evaluator: Evaluator = store.default_evaluator):
        super(GeneticIslandAlgorithm, self).__init__(problem, population_size, offspring_population_size,
                                                              mutation, crossover, selection, termination_criterion,
                                                              population_generator, population_evaluator)
        self.min_fitness_per_evaluation = dict()
        self.migration_interval = migration_interval
        self.number_of_emigrants = number_of_emigrants
        self.number_of_islands = number_of_islands
        self.island = island
        self.last_migration_evolution = 0

        #TODO change connection to rabitmq from Docker
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        for i in range(0, self.number_of_islands ):
            self.channel.queue_declare(queue=f'island-from-{self.island}-to-{i}')

        self.rabbitmq_configuration = {}
        self.queue_name = f'island-{self.island}'


    def get_individuals_to_migrate(self, population: List[S], number_of_emigrants: int) -> List[S]:
        if len(population) < number_of_emigrants:
            raise ValueError("Ppulation is too small")

        emigrants = [population.pop(random.randrange(len(population))) for _ in range(0, number_of_emigrants)]
        return emigrants

    def migrate_individuals(self):
        if self.evaluations - self.last_migration_evolution >= self.migration_interval:
            try:
                individuals_to_migrate = self.get_individuals_to_migrate(self.solutions, self.number_of_emigrants)
            except ValueError:
                return

            #TODO: migrate every chosen individual
            for i in individuals_to_migrate:
                island_to_migrate = [i for i in range(0, self.number_of_islands) if i != self.island].random()
                pass
                # self.channel.basic_publish(exchange='',
                #                       routing_key='hello',
                #                       body=json.loads(i.__dict__))
                pass

    def add_new_individuals(self):
        pass


    def step(self):
        self.migrate_individuals()
        try:
            self.add_new_individuals()
        except:
            pass

        mating_population = self.selection(self.solutions)
        offspring_population = self.reproduction(mating_population)
        offspring_population = self.evaluate(offspring_population)

        self.solutions = self.replacement(self.solutions, offspring_population)

    def update_min_fitness_per_evaluation(self):
        min_fitness = min(self.solutions, key=lambda x: x.objectives[0])
        self.min_fitness_per_evaluation[self.evaluations] = min_fitness.objectives[0]
