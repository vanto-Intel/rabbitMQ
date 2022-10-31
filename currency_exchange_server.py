#code is refferenced from rabbitMQ tutorial
# example_consumer.py
import json
import pika, os, time, sys
import datetime
from forex_python.converter import CurrencyRates # currency api


def currency_converter(from_currency, to_currency, amount):
  cr = CurrencyRates()
  currResult = {'total': None, 'rate': None}
  print("You are converting", amount, from_currency, "to", to_currency,".")
  try:
    output = cr.convert(from_currency, to_currency, amount)
    rates = cr.get_rate(from_currency, to_currency)
    currResult = {'total': output, 'rate': rates}
    jsonString = json.dumps(currResult, indent=3)
    print("The rates is %.2f and the total is: %.2f " %(rates, output))
  except Exception as re:
    print(re)
    jsonString = json.dumps(currResult, indent=3)
  return jsonString
#processing a recieved message

def process_function(msg):
  print(" PDF processing")
  client_request = json.loads(msg.decode('UTF-8')) #decode byte to string and parse it into json object
  total = currency_converter(client_request['from_currency'].upper(), client_request['to_currency'].upper(), client_request['amount'])
  return total;

def main():
  # Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
  url = os.environ.get('CLOUDAMQP_URL', 'amqps://ehysafwd:KO4JhUa3RNZGdStDsrHWEIfhi2Qo4g4F@beaver.rmq.cloudamqp.com/ehysafwd')

  params = pika.URLParameters(url)
  connection = pika.BlockingConnection(params)
  channel = connection.channel() # start a channel
  channel.queue_declare(queue='curr_converter') # Declare a queue

  # create a function which is called on incoming messages
  def callback(ch, method, properties, body):
    exchance_result = process_function(body)
    ch.basic_publish(exchange='',
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id = properties.correlation_id),
                     body=exchance_result)
    ch.basic_ack(delivery_tag=method.delivery_tag)
  # set up subscription on the queue
  channel.basic_qos(prefetch_count=1)
  channel.basic_consume(queue='curr_converter', on_message_callback=callback)
  print(' [*] Waiting for request from remote client. To exit press CTRL+C')
  # start consuming (blocks)
  channel.start_consuming()
  connection.close()
 
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)