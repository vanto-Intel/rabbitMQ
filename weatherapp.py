#This code has been adapted from RabbitMQ Remote Procedure Calls tutorials https://www.rabbitmq.com/tutorials/tutorial-six-python.html

import pika
import requests
import os

#(Use this if you would prefer to host microservice on local host)
#-----------------------------------------------
#connection = pika.BlockingConnection(
#    pika.ConnectionParameters(host='localhost'))
#-----------------------------------------------


#This CLOUDAMQP_URL is my personal server, you may change the URL if you wish to host it on your own server
#-----------------------------------------------
url = os.environ.get('CLOUDAMQP_URL', 'amqps://cgbguoip:VoHZcopUZ_IiWlb1CmcQ1Ip4JBbD830F@beaver.rmq.cloudamqp.com/cgbguoip')
params = pika.URLParameters(url)
params.socket_timeout = 5
connection = pika.BlockingConnection(params)
#-----------------------------------------------

channel = connection.channel()

channel.queue_declare(queue='weather')
#message durability: saves message to disk.
#We have learned how to make sure that even if the consumer dies, the task isn't lost. But our tasks will still be lost if RabbitMQ server stops.
#When RabbitMQ quits or crashes it will forget the queues and messages unless you tell it not to. Two things are required to make sure that messages aren't lost: we need to mark both the queue and messages as durable.
def weather_api(zip):
    params = {
        'access_key': 'c9f0f6db8b3dc27b6516bc7587ebf93f',
        'zip': zip
        }

    #geocoding API to get city name from zip code, latitude, and longitude
    api_result1 = requests.get("http://api.openweathermap.org/geo/1.0/zip?zip=" + params['zip']+"&appid="+params['access_key'])
    if api_result1.status_code== 200:
        api_response1 = api_result1.json()

        lat = api_response1['lat']
        lon = api_response1['lon']

            #weather API to get weather information from latitude and longitude
        api_result2 = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=imperial" %(lat, lon, params['access_key']))
            
        if api_result2.status_code==200:
            api_response2 = api_result2.json()
            return str(api_response2)
        else:
            print(api_result2.status_code)
            return("Error in Geocoding API. \n"+api_result2)
    else:
          print(api_result1.status_code)
          return("Error in Geocoding API. \n"+api_result1)

def on_request(ch, method, props, body):
    zip_code = str(body.decode())   #body.decode() gets rid of binary encoding
    print("Received request for the zip code %s" % zip_code)

    response = weather_api(zip_code)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='weather', on_message_callback=on_request)

print("Weather Microservice is currently listening for zip code requests...")
channel.start_consuming()