#!/usr/bin/python3
import json
import time
import re
import requests

secrets_file = 'slack_secret.json'
f = open(secrets_file, 'r') 
content = f.read()
auth_info = json.loads(content)
token = auth_info["access_token"]
f.close()


from slackclient import SlackClient
sc = SlackClient(token)

def Message_Match(user_ID, message_text):
    regex_expression = '.*@' + user_id +'.*bot.*'
    regex = re.compile(regex_expression)
    match = regex.match(message_text)
    return match != None

def Extract_CityName(message_text):
    regex_expression = '[H,h]ow\'s the weather in ([A-z, ]+)\?'
    regex = re.compile(regex_expression)
    matches = regex.finditer(message_text)
    for match in matches:
        return match.group(1)
    
    return None

key = '097217bc8c67dcadb7f7f7b295429be1'
def Get_WeatherData(key, city):
    import requests
    return requests.get('http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}'.format(city=city,key=key)).json()


def Kelvin_to_Farenheit(temp_kelvin):
    return (temp_kelvin - 273) * (9/5) + 32


def Return_WeatherResults(city, user):
    key = '097217bc8c67dcadb7f7f7b295429be1'
    data = Get_WeatherData(key, city)
    
    if city == None:
        return "I'm sorry @{user}, I'm not sure I understand. Try rephrasing in this form: \n \'Hey @maxdavish bot, how's the weather in London?\'".format(user=user)
    
    if 'message' in data.keys():
        return "I'm sorry @{user}, I'm not familiar with that place. Please try again.".format(user=user)

    else: 
        city = city
        temperature = round(Kelvin_to_Farenheit(data['main']['temp']), 1)
        hightemp = round(Kelvin_to_Farenheit(data['main']['temp_max']), 1)
        lowtemp = round(Kelvin_to_Farenheit(data['main']['temp_min']), 1)
        description = data['weather'][0]['description']
        result = "@{user}, currently in {city} it's {temperature} degrees farenheit with {description}, with a high of {hightemp} and a low of {lowtemp}.".format(user=user, city=city,temperature=temperature,description=description,hightemp=hightemp,lowtemp=lowtemp)
        return result

def message_matches(user_id, message_text):
    regex_expression = '.*@' + user_id + '.*bot.*'
    regex = re.compile(regex_expression)
    match = regex.match(message_text)
    return match != None 

if sc.rtm_connect():
    while True:
        time.sleep(1)
        response = sc.rtm_read()
        for item in response:
            if item.get("type") != 'message':
                continue
                
            if item.get("user") == None:
                continue
            
            user_id = auth_info["user_id"]
            message_text = item.get('text')
            if not message_matches(user_id, message_text):
                continue
                
            response = sc.api_call("users.info", user=item["user"])
            username = response['user'].get('name')
        
            city_name = Extract_CityName(message_text)

            message = Return_WeatherResults(city_name, username)

            sc.api_call("chat.postMessage", channel="#assignment2_bots", text=message)

