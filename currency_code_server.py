#code is refferenced from rabbitMQ tutorial
# example_consumer.py
import json
import pika, os, time, sys
import datetime
from forex_python.converter import CurrencyRates # currency api
from countryinfo import CountryInfo

#processing a recieved message

def process_function(msg):
  curr_code = None
  try:  
    curr_code = CountryInfo(msg.decode("UTF-8")).currencies()
    print("The currency of %s is %s" %(msg.decode("UTF-8"), str(curr_code[0])))
    return str(curr_code[0]);
  except Exception as ex:
    print(ex)
    return str(curr_code);

def main():
  # Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
  url = os.environ.get('CLOUDAMQP_URL', 'amqps://ehysafwd:KO4JhUa3RNZGdStDsrHWEIfhi2Qo4g4F@beaver.rmq.cloudamqp.com/ehysafwd')

  params = pika.URLParameters(url)
  connection = pika.BlockingConnection(params)
  channel = connection.channel() # start a channel
  channel.queue_declare(queue='curr_code') # Declare a queue

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
  channel.basic_consume(queue='curr_code', on_message_callback = callback)
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