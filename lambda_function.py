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


def build_response_card(title, subtitle, img_url, link_url, options=None):
    """
    Build a responseCard with a title, subtitle, and an optional set of options which should be displayed as buttons.
    """
    # buttons = None
    # if options is not None:
    #     buttons = []
    #     for i in range(min(5, len(options))):
    #         buttons.append(options[i])

    return {
        'contentType': 'application/vnd.amazonaws.card.generic',
        # 'version': 1,
        'genericAttachments': [{
            'title': title,
            'subTitle': subtitle,
            'imageUrl': img_url,
            'link_url': link_url,
            # 'buttons': buttons,
        }]
    }


def build_response_card_attachment(title, subtitle, img_url, link_url, options=None):
    """
    Build a responseCard with a title, subtitle, and an optional set of options which should be displayed as buttons.
    """
    # buttons = None
    # if options is not None:
    #     buttons = []
    #     for i in range(min(5, len(options))):
    #         buttons.append(options[i])

    return {
            'title': title,
            'subTitle': subtitle,
            'imageUrl': img_url,
            'attachmentLinkUrl': link_url,
            # 'buttons': buttons,
        }


def close(session_attributes, fulfillment_state, message, response_cards):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': {
                'contentType': 'PlainText',
                'content': message,
            },
            'responseCard': response_cards,
        }
    }

    return response

""" --- Helper Functions --- """

""" --- Functions that control the bot's behavior --- """


def search_restaurant(intent_request):
    import requests
    import json

    url = "https://api.yelp.com/v3/businesses/search"

    querystring = {"term": "delis", "latitude": "37.786882", "longitude": "-122.399972"}
    slots_map = intent_request['currentIntent'].get('slots', {})
    city = slots_map.get('city')
    if city is not None:
        if city.lower() in ['ny', 'new york']:
            querystring.update({"latitude": "40.7617022", "longitude": "-73.9821027"})
        elif city.lower() in ['sf', 'san francisco']:
            querystring.update({"latitude": "37.786882", "longitude": "-122.399972"})

    headers = {
        'authorization': "Bearer 1k5o4aibpbMbLcu1zql6affDXcEzvcJ0psekaUJrB2173R6mDEwOfNKd59V8VVZQqy0YcgPTmm8ZUB9gQsTTpxAyl-_X-6I6lPvki0k_HX2iEQyj50SE0llhHsY6WXYx",
        'cache-control': "no-cache",
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    # return ','.join([each['name'] for each in json.loads(response.text)['businesses'][:10]])
    businesses = json.loads(response.text)['businesses']

    # build a mock user ratings matrix
    import random
    user_ratings_matrix = [[random.randint(0, 1) for _ in range(len(businesses))] for _ in range(5)]
    user_ratings_col_matrix = [list(i) for i in zip(*user_ratings_matrix)]
    cooccurance_matrix = [[0] * len(user_ratings_matrix[0]) for _ in range(len(user_ratings_matrix[0]))]
    for i in range(len(user_ratings_col_matrix)):
        for j in range(len(user_ratings_col_matrix)):
            cooccurance_matrix[i][j] = sum([x & y for (x, y) in zip(user_ratings_col_matrix[i], user_ratings_col_matrix[j])])

    for i in range(len(cooccurance_matrix)):
        row_sum = sum(cooccurance_matrix[i])
        if row_sum == 0:
            continue
        for j in range(len(cooccurance_matrix[0])):
            cooccurance_matrix[i][j] /= float(row_sum)
    # print cooccurance_matrix

    # randomly select a user
    user_id = random.randint(0, len(user_ratings_matrix) - 1)
    # import numpy as np
    # result = np.matmul(cooccurance_matrix, user_ratings_matrix[user_id])
    # result_index = result.argsort()[-5:]
    result = [sum(each[0] * each[1] for each in zip(user_ratings_matrix[user_id], row)) for row in cooccurance_matrix]
    result_index = sorted(range(len(result)), key=result.__getitem__)[-5:]
    # print(result)
    # print(len(businesses))
    selected_businesses = [businesses[i] for i in result_index]

    response_cards = {
        'contentType': 'application/vnd.amazonaws.card.generic',
        # 'version': 1,
        'genericAttachments': [build_response_card_attachment(each['name'], 'TBD', each['image_url'], each['url']) for each in selected_businesses]
    }
    return close({}, 'Fulfilled', 'Here\'re the choices you may consider:', response_cards)

""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'SearchRestaurant':
        return search_restaurant(intent_request)
        # msg = search_restaurant(intent_request)
        # return {
        #     'sessionAttributes': {},
        #     'dialogAction': {
        #         'type': 'Close',
        #         'fulfillmentState': 'Fulfilled',
        #         'message': {
        #             'contentType': 'PlainText',
        #             'content': msg,
        #         },
        #         'responseCard': {
        #             "version": 1,
        #             "contentType": "application/vnd.amazonaws.card.generic",
        #             "genericAttachments": [
        #                 {
        #                     "title": "What Flavor?",
        #                     "subTitle": "What flavor do you want?",
        #                     "imageUrl": "https://s3-media1.fl.yelpcdn.com/bphoto/H_vQ3ElMoQ8j1bKidrv_1w/o.jpg",
        #                     "attachmentLinkUrl": "https://www.yelp.com/biz/molinari-delicatessen-san-francisco?adjust_creative=jwMDC4ZCoiDXl9qZtNl05w&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=jwMDC4ZCoiDXl9qZtNl05w",
        #                     # "buttons": [
        #                     #     {
        #                     #         "text": "Lemon",
        #                     #         "value": "lemon"
        #                     #     },
        #                     #     {
        #                     #         "text": "Raspberry",
        #                     #         "value": "raspberry"
        #                     #     },
        #                     #     {
        #                     #         "text": "Plain",
        #                     #         "value": "plain"
        #                     #     }
        #                     # ]
        #                 }
        #             ]
        #         }
        #     }
        # }

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