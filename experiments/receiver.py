import pika

connection = pika.BlockingConnection()
channel = connection.channel()

def on_message(channel, method_frame, header_frame, body):
    print(method_frame.delivery_tag)
    print(body)
    print()
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

def prepare(island_num):
    print(f"ISLAND {island_num}")
    channel.basic_consume(f'island-{island_num}', on_message)
    consume()

def consume():
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == '__main__':
    prepare(2)