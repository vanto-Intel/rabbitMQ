from country_currency_code import CurrCode

curr_code = CurrCode('Japan')
response = curr_code.get_code()
if response == None:
    print("Country is not available!!! Please check again")
else:
    print(response.decode('UTF-8'))