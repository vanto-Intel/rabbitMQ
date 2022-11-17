from send_zip import SendZipClient

rpc = SendZipClient('97225')
response = rpc.call()
city = response['name']
temperature = response['main']['temp']
print ('city name: %s and temperature: %s' %(city, temperature))