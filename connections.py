
from requests_html import HTMLSession
from slugify import slugify
import argparse
from datetime import datetime, timedelta
import json
import sys

source = sys.argv[1]
destination = sys.argv[2]
departure_date = sys.argv[3]

def find_city_with_name(name):
    
    for id in cities:
        city = cities[id]
        if slugify(city['name'], separator='_') == slugify(name, separator='_'):
            return city
    
    return None

with open('cities.json') as json_file:
    cities = json.load(json_file)

city1 = find_city_with_name(source)
city2 = find_city_with_name(destination)

if city1 is None or city2 is None:
    exit()

departure_datetime = datetime.strptime(departure_date, "%Y-%m-%d")

search_url = "https://shop.global.flixbus.com/search?departureCity={}&arrivalCity={}&route={}-{}&rideDate={}"\
    .format(city1['id'], city2['id'], city1['name'], city2['name'], departure_datetime.strftime("%d.%m.%Y"))

session = HTMLSession()    
search_response = session.get(search_url)
results_container = search_response.html.xpath('//div[@id="results-group-container-direct"]')
results = results_container[0].xpath('//div[@data-group="direct"]')

connections = []
for result in results:
    connection = {}
    
    connection['departure_station'] = result.xpath('//div[@class="station-name departure-station-name"]/text()')[0]
    connection['arrival_station'] = result.xpath('//div[@class="station-name arrival-station-name"]/text()')[0]

    departure_time = result.xpath('//div[@class="departure"]/text()')[0]
    departure_datetime = departure_datetime.replace(hour=int(departure_time.split(':')[0]), minute=int(departure_time.split(':')[1]))
    connection['departure_datetime'] = departure_datetime.strftime("%Y-%m-%d %H:%M")

    duration = result.xpath('//div[@class="col-xs-12 duration ride__duration ride__duration-messages"]/text()')[0].strip()
    arrival_datetime = departure_datetime + timedelta(hours=int(duration.split(':')[0]),minutes=int(duration.split(':')[1]))
    connection['arrival_datetime'] = arrival_datetime.strftime("%Y-%m-%d %H:%M")
    # connection['arrival_time'] = result.xpath('//div[@class="arrival"]/text()')[0]

    euros = result.xpath('//span[@class="num currency-small-cents"]/text()')[0]    
    cents = result.xpath('//span[@class="num currency-small-cents"]/sup/text()')[0]
    connection['price'] = euros + cents
    
    connections.append(connection)

print(connections)
