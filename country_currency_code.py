
#code is refferenced from rabbitMQ tutorial
# example_publisher.py
from locale import currency
import time
import json
import uuid
import pika, os, logging
logging.basicConfig()

class CurrCode(object):

    def __init__(self, country_code):
        url = os.environ.get('CLOUDAMQP_URL', 'amqps://ehysafwd:KO4JhUa3RNZGdStDsrHWEIfhi2Qo4g4F@beaver.rmq.cloudamqp.com/ehysafwd')
        params = pika.URLParameters(url)
        params.socket_timeout = 5

        self.connection = pika.BlockingConnection(params) # Connect to CloudAMQP
        self.channel = self.connection.channel() # start a channel

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.exchangeback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.exchangeback_queue,
            on_message_callback=self.on_response_code,
            auto_ack=True)

        self.response = None
        self.corr_id = None

        self.country_code = country_code

    def getCountryCode(self):
        return self.country_code

    def on_response_code(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def get_code(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='curr_code',
            properties=pika.BasicProperties(
                reply_to=self.exchangeback_queue,
                correlation_id=self.corr_id,
            ), body=self.country_code)
        self.connection.process_data_events(time_limit=None)
        return self.response

