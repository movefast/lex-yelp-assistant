"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages orders for flowers.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'OrderFlowers' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""
import math
import dateutil.parser
import datetime
import time
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


""" --- Helper Functions --- """

""" --- Functions that control the bot's behavior --- """


def search_restaurant(intent_request):
    import requests
    import json

    url = "https://api.yelp.com/v3/businesses/search"

    querystring = {"term": "delis", "latitude": "37.786882", "longitude": "-122.399972"}

    headers = {
        'authorization': "Bearer 1k5o4aibpbMbLcu1zql6affDXcEzvcJ0psekaUJrB2173R6mDEwOfNKd59V8VVZQqy0YcgPTmm8ZUB9gQsTTpxAyl-_X-6I6lPvki0k_HX2iEQyj50SE0llhHsY6WXYx",
        'cache-control': "no-cache",
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    # output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    return json.loads(response.text)['businesses'][:1][0]['name']


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'SearchRestaurant':
        msg = search_restaurant(intent_request)
        return {
            'sessionAttributes': 'session_attributes',
            'dialogAction': {
                'type': 'Close',
                'fulfillmentState': 'Fulfilled',
                'message': msg
            }
        }

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)