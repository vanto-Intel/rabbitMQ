from currency_exchange_client import CurrConverter
import json

curr = CurrConverter('USD', 'JPY', 9)
print(" [x] Requesting currency exchange from %s to %s with an amount %f" %(curr.getRequestStr()['from_currency'], curr.getRequestStr()['to_currency'], curr.getRequestStr()['amount']))
response = json.loads(curr.exchange())
if response['rate'] and response['total']:
    print("Rates is %.2f and total is %.2f" %(response['rate'], response['total']))
else:
    print("Currency Rates Source Not Ready yet!!! sorry for inconvenience")