import requests
from utils import query_place_names
from xml.etree import ElementTree as ET


def send_yr_xml(self, sender, xml, area_name):
    root = ET.fromstring(xml)
    print(root)
    next_hour = root.find('forecast').find('tabular')[0]
    weather = next_hour.find('symbol').attrib['name']
    temp = next_hour.find('temperature').attrib['value']
    temp_unit = next_hour.find('temperature').attrib['unit']
    wind_direction = next_hour.find('windDirection').attrib['name']
    wind_speed = next_hour.find('windSpeed').attrib['name']
    self.respond(
        sender, "Forecast for the next hour for {}:".format(area_name))
    self.respond(sender,
                 "Weather: {} Temp: {} WindDirection: {} WindSpeed: {}".format(weather, (temp + " " + temp_unit),
                                                                               wind_direction, wind_speed))


def fetch_weather_forecast(self, sender, message):
    if message.startswith('!forecast'):
        self.response("The api is no longer available. If you wish to fix this then feel free to look at the migration guide here: https://developer.yr.no/doc/guides/getting-started-from-forecast-xml/")
        return  # Ignored until it is changed to work with api.met.no
        params = message.rstrip().split(' ')
        if len(params) == 1:
            r = requests.get(
                "http://www.yr.no/place/Norway/Hordaland/Bergen/Bergen/forecast_hour_by_hour.xml")
            send_yr_xml(self, sender, r.content, 'Bergen sentrum')

        elif len(params) == 2:
            places = query_place_names(params[1])[0]

            if len(places) == 1:
                url = places[0][1].replace(
                    'forecast.xml', 'forecast_hour_by_hour.xml')
                name = places[0][0] + ', ' + places[0][2]
                r = requests.get(url)
                send_yr_xml(self, sender, r.content, name)

            elif len(places) > 1:
                response_string = 'Found several places: '
                for place in places:
                    response_string = response_string + \
                        '(' + place[0] + ', ' + place[2] + '), '
                response_string = response_string + 'Pick one using the order they appear(1,2 or 3). Underscores(' \
                                                    '_) are used instead of spaces. '
                self.respond(sender, response_string)
        elif len(params) == 3:
            index = -1
            number_input = params[2]
            if number_input == '1':
                index = 0
            elif number_input == '2':
                index = 1
            elif number_input == '3':
                index = 2
            else:
                self.respond(
                    sender, 'Choose a number between 1 and 3. ' + number_input + ' is not valid.')

            if index != -1:
                places = query_place_names(params[1])[0]
                if len(places) >= 1:
                    url = places[index][1].replace(
                        'forecast.xml', 'forecast_hour_by_hour.xml')
                    name = places[index][0] + ', ' + places[index][2]

                    r = requests.get(url)
                    send_yr_xml(self, sender, r.content, name)
                else:
                    self.respond(
                        sender, 'Could not find the place you were looking for.')

        elif len(params) > 3:
            self.respond(
                sender, 'Too many arguments: Use "!forecast some_place <number>"')
