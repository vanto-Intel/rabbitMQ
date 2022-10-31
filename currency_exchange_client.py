#code is refferenced from rabbitMQ tutorial
# example_publisher.py
from locale import currency
import time
import json
import uuid
import pika, os, logging
logging.basicConfig()

class CurrConverter(object):

    def __init__(self, from_curr, to_curr, amount):
        url = os.environ.get('CLOUDAMQP_URL', 'amqps://ehysafwd:KO4JhUa3RNZGdStDsrHWEIfhi2Qo4g4F@beaver.rmq.cloudamqp.com/ehysafwd')
        params = pika.URLParameters(url)
        params.socket_timeout = 5

        self.connection = pika.BlockingConnection(params) # Connect to CloudAMQP
        self.channel = self.connection.channel() # start a channel

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.exchangeback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.exchangeback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None
        # #create json object from a dictionary
        self.curr_converter = {'from_currency': from_curr, 'to_currency': to_curr, 'amount': amount}
        self.jsonString = json.dumps(self.curr_converter, indent=4)

    def getRequestStr(self):
        return self.curr_converter

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def exchange(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='curr_converter',
            properties=pika.BasicProperties(
                reply_to=self.exchangeback_queue,
                correlation_id=self.corr_id,
            ), body=self.jsonString)
        self.connection.process_data_events(time_limit=None)
        return self.response


curr_converter = CurrConverter('USD', 'AUD', 10)

print(" [x] Requesting currency exchange from %s to %s with an amount %f" %(curr_converter.getRequestStr()['from_currency'], curr_converter.getRequestStr()['to_currency'], curr_converter.getRequestStr()['amount']))
response = json.loads(curr_converter.exchange())
if response['rate'] and response['total']:
    print("Rates is %.2f and total is %.2f" %(response['rate'], response['total']))
else:
    print("Currency Rates Source Not Ready yet!!! sorry for inconvenience")
