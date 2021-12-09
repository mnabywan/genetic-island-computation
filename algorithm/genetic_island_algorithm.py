import json

from jmetal.algorithm.singleobjective.genetic_algorithm import GeneticAlgorithm
from typing import TypeVar, List

from jmetal.config import store
from jmetal.core.operator import Mutation, Crossover, Selection
from jmetal.core.problem import Problem
from jmetal.util.evaluator import Evaluator
from jmetal.util.generator import Generator
from jmetal.util.termination_criterion import TerminationCriterion
import random
import pika
from solution.float_island_solution import FloatIslandSolution

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
                 rabbitmq_delays: dict,

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

        self.rabbitmq_delays = rabbitmq_delays
        self.queue_name = f'island-{self.island}'

        # Configure queue for that island

        self.channel.queue_bind(exchange='amq.direct',
                           queue=self.queue_name)

        # Configure delay queues for that island
        self.delay_channel = self.connection.channel()

        delays = rabbitmq_delays[str(self.island)]
        print(delays)
        for i in range(0, self.number_of_islands):
            if i != self.island:
                self.delay_channel.queue_bind(exchange='amq.direct',
                                              queue=f'island-from-{self.island}-to-{i}')


    def get_individuals_to_migrate(self, population: List[S], number_of_emigrants: int) -> List[S]:
        if len(population) < number_of_emigrants:
            raise ValueError("Population is too small")

        emigrants = [population.pop(random.randrange(len(population))) for _ in range(0, number_of_emigrants)]
        return emigrants


    def migrate_individuals(self):
        if self.evaluations - self.last_migration_evolution >= self.migration_interval:
            try:
                print(f"Number of evaluations {self.evaluations}")
                individuals_to_migrate = self.get_individuals_to_migrate(self.solutions, self.number_of_emigrants)
                self.last_migration_evolution = self.evaluations
            except ValueError:
                return

            #TODO: migrate every chosen individual
            import time
            for i in individuals_to_migrate:
                print(i.__dict__)
                destination = random.choice([i for i in range(0, self.number_of_islands) if i != self.island])
                print(f"Destination {destination}")
                self.channel.basic_publish(exchange='',
                                           routing_key=f"island-from-{self.island}-to-{destination}",
                                           body=json.dumps(i.__dict__))


    def add_new_individuals(self):
        new_individuals = []
        for i in range(0, 10):
            method, properties, body = self.channel.basic_get(f'island-{self.island}')

            if body:
                print('addddd')
                data_str = body.decode("utf-8")

                data = json.loads(data_str)
                print(data)
                print(type(data))
                float_solution = FloatIslandSolution(data['lower_bound'], data['upper_bound'],
                                               data['number_of_variables'], data['number_of_objectives'],
                                                     constraints=data['constraints'], variables=data['variables'], objectives=data['objectives'],
                                                     from_island=data["from_island"],from_evaluation=data["from_evaluation"]
                                               )
                print(f"float ")
                float_solution.objectives = data['objectives']
                float_solution.variables = data['variables']
                float_solution.number_of_constraints = data['number_of_constraints']
                print("AAADDDDDEEEEEEEDDDDDD")
                print(float_solution.__str__())
                new_individuals.append(float_solution)

        self.solutions += new_individuals

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


        #print("Number of evaluations: {}".format(self.evaluations))


    def update_min_fitness_per_evaluation(self):
        min_fitness = min(self.solutions, key=lambda x: x.objectives[0])
        self.min_fitness_per_evaluation[self.evaluations] = min_fitness.objectives[0]
