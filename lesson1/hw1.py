import requests
import json
from pprint import pprint

url = "https://api.github.com"
user = "ddekun"

responce = requests.get(f'{url}/users/{user}/repos')

#print(responce.text)
j_data = responce.json()
#pprint(j_data)
with open('data.json', 'w') as f:
   json.dump(j_data, f)
for i in responce.json():
    print(i['name'])