
from requests_html import HTMLSession
import argparse
import datetime
import json
import sys

source = sys.argv[1]
destination = sys.argv[2]
departure_date = sys.argv[3]

def find_city_with_name(name):
    
    for id in cities:
        city = cities[id]
        if(city['name'] == name):
            return city
    
    return None


with open('cities.json') as json_file:
    cities = json.load(json_file)

city1 = find_city_with_name(source)
city2 = find_city_with_name(destination)

if city1 is None or city2 is None:
    exit()

departure_datetime = datetime.datetime.strptime(departure_date, "%Y-%m-%d")

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
    connection['departure_time'] = result.xpath('//div[@class="departure"]/text()')[0]

    connection['arrival_station'] = result.xpath('//div[@class="station-name arrival-station-name"]/text()')[0]
    connection['arrival_time'] = result.xpath('//div[@class="arrival"]/text()')[0]

    euros = result.xpath('//span[@class="num currency-small-cents"]/text()')[0]    
    cents = result.xpath('//span[@class="num currency-small-cents"]/sup/text()')[0]
    connection['price'] = euros + cents
    
    connections.append(connection)

print(connections)
