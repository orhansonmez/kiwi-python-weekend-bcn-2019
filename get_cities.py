from requests_html import HTMLSession
import json

session = HTMLSession()
    
cities_response = session.get('https://d11mb9zho2u7hy.cloudfront.net/api/v1/cities?locale=en')

cities_json = json.loads(cities_response.content)['cities']

with open('cities.json', 'w') as f:
    json.dump(cities_json, f)