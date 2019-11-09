
from requests_html import HTMLSession
from datetime import datetime, timedelta
from slugify import slugify
import argparse
import json
import sys
import os

from redis import StrictRedis
redis = StrictRedis(socket_connect_timeout=3, **{'host': os.environ['HOST'],'port': os.environ['PORT']})

parser = argparse.ArgumentParser()
parser.add_argument("--source")
parser.add_argument("--destination")
parser.add_argument("--departure_date")
args = parser.parse_args()


def get_city_id(name):
    
    id = redis.get('bcn_orhan:location:{}'.format(slugify(name, separator='_')))

    if id is not None:
        print('LOCATION CACHE HIT!')
        return int(id)
    
    session = HTMLSession()
    cities_response = session.get('https://d11mb9zho2u7hy.cloudfront.net/api/v1/cities?locale=en')
    cities = json.loads(cities_response.content)['cities']

    for id in cities:
        city = cities[id]

        if slugify(city['name'], separator='_') == slugify(name, separator='_'):
            redis.set('bcn_orhan:location:{}'.format(slugify(name, separator='_')), city['id'])
            return city['id']
        
        if slugify(city['aliases'], separator='_') == slugify(name, separator='_'):
            redis.set('bcn_orhan:location:{}'.format(slugify(name, separator='_')), city['id'])
            return city['id']
    
    return None

source_id = get_city_id(args.source)
destination_id = get_city_id(args.destination)

departure_datetime = datetime.strptime(args.departure_date, "%Y-%m-%d")

connections = redis.get('bcn_orhan:journey:{}_{}_{}'.format(slugify(args.source), slugify(args.destination), args.departure_date))

if connections is not None:
    print("JOURNEY CACHE HIT!")
    print(json.loads(connections))
    exit()

search_url = "https://shop.global.flixbus.com/search?departureCity={}&arrivalCity={}&route={}-{}&rideDate={}"\
    .format(source_id, destination_id, args.source, args.destination, departure_datetime.strftime("%d.%m.%Y"))


session = HTMLSession()    
search_response = session.get(search_url)
results_container = search_response.html.xpath('//div[@id="results-group-container-direct"]')
results = results_container[0].xpath('//div[@data-group="direct"]')

connections = []
for result in results:
    connection = {}
    
    connection['source'] = args.source
    connection['destination'] = args.destination

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
redis.set('bcn_orhan:journey:{}_{}_{}'.format(slugify(args.source), slugify(args.destination), args.departure_date), json.dumps(connections))
