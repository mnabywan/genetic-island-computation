import pika
import json

conf_file = '../algorithm/configurations/algorithm_configuration.json'

connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
channel = connection.channel()
delay_channel = connection.channel()


with open(conf_file) as file:
    configuration = json.loads(file.read())

rabbitmq_delays = configuration["island_delays"]

def remove_queues():
    for island in range(0, 5):
        channel.queue_delete(queue=f'island-{island}')
        for i in range(0, 5):
            channel.queue_delete(f'island-from-{island}-to-{i}')


def create_queues():
    for island in range(0, 3):
        queue_name = f'island-{island}'
        channel.queue_declare(queue=queue_name)
        for i in range(0, 3):
            if i != island:
                delay_channel.queue_declare(queue=f'island-from-{island}-to-{i}', arguments={
                    'x-message-ttl': rabbitmq_delays[str(island)][i],  # Delay until the message is transferred in milliseconds.
                    'x-dead-letter-exchange': 'amq.direct',  # Exchange used to transfer the message from A to B.
                    'x-dead-letter-routing-key': f'island-{i}'  # Name of the queue we want the message transferred to.
                })

    connection.close()