'''
    Middleman API for the Robinhood API.
    This API attempts to normalize and sanitize values
    returned by the Robinhood API as well as enable
    CORS for client applications.
'''
import re
from flask import Flask
from flask_restful import Resource, Api, reqparse, request
import requests

# Configure Flask(-RESTful)
APP = Flask(__name__)
LOG = APP.logger
API = Api(APP)
# Set your own unique key here
APP.secret_key = '12345678-xxxx-yyyy-zzzz-1234567890AB'


@APP.after_request
def after_request(response):
    '''Post-processing, CORS'''
    response.headers.add('Access-Control-Allow-Origin',
                         '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,RH-AUTH-TOKEN')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE')
    return response


def parse_result(result, recipe):
    '''Convert from RH format to our format'''
    if not isinstance(recipe, dict):
        return result
    blacklist = recipe.get('blacklist', list())
    mangles = recipe.get('mangles', dict())
    floats = recipe.get('floats', list())
    ints = recipe.get('ints', list())
    # Blacklist
    for key in blacklist:
        if key in result:
            del result[key]
    # Mangles
    for key, val in mangles.iteritems():
        match = re.search(val, result.get(key, ''))
        if match:
            result[key] = match.group(1)
    # Floats
    for key in floats:
        if key in result and result[key] is not None:
            result[key] = float(result[key])
    # Ints
    for key in ints:
        if key in result and result[key] is not None:
            result[key] = int(result[key])
    return result


def parse_results(results, recipe):
    '''Convert from RH format to our format'''
    if not isinstance(recipe, dict):
        return results
    for idx, _ in enumerate(results):
        results[idx] = parse_result(results[idx], recipe)
    return results


def handle_bad_response(res):
    '''Handle bad responses from RH API'''
    if res.status_code is 401:
        return handle_bad_auth()
    return {
        'error': 'Error querying Robinhood API'
    }, 500


def handle_bad_auth():
    '''Handle bad authentication'''
    return {
        'error': 'Unauthorized'
    }, 401


def parse_token(headers):
    '''Gets a token from headers'''
    if 'RH-AUTH-TOKEN' in headers:
        return headers['RH-AUTH-TOKEN']
    return None


class Authenticate(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str,
                            help='Robinhood Username')
        parser.add_argument('password', type=str,
                            help='Robinhood Password')
        args = parser.parse_args()
        res = requests.post(
            url='https://api.robinhood.com/api-token-auth/',
            data={
                'username': args.username,
                'password': args.password
            })
        # Handle errors
        if res.status_code is not 200:
            if res.status_code is 400:
                return handle_bad_auth()
            return handle_bad_response(res)
        return {'results': res.json()}


class User(Resource):
    def get(self):
        token = parse_token(request.headers)
        if not token:
            return handle_bad_auth()
        res = requests.get(
            url='https://api.robinhood.com/user/',
            headers={'Authorization': 'Token ' + token})
        # Handle errors
        if not res or res.status_code is not 200:
            return handle_bad_response(res)
        # Parse data
        return {
            'results': parse_result(
                res.json(),
                {
                    'blacklist': [
                        'user', 'tax_id_ssn', 'additional_info',
                        'basic_info', 'employment', 'id_info',
                        'international_info', 'investment_profile',
                        'url'
                    ],
                })
        }, 200


class Positions(Resource):
    def get(self):
        token = parse_token(request.headers)
        if not token:
            return handle_bad_auth()
        parser = reqparse.RequestParser()
        parser.add_argument('hasquantity', type=bool,
                            help='Filter results that have a quantity of zero')
        args = parser.parse_args()
        res = requests.get(
            url='https://api.robinhood.com/positions/',
            headers={'Authorization': 'Token ' + token})
        # Handle errors
        if not res or res.status_code is not 200:
            return handle_bad_response(res)
        # Parse data
        results = parse_results(
            res.json().get('results', list()),
            {
                'blacklist': ['url', 'account'],
                'mangles': {
                    'instrument':
                        'http[s+]://api.robinhood.com/instruments/(.*)[/+]'
                },
                'floats': [
                    'quantity', 'average_buy_price',
                    'intraday_average_buy_price', 'intraday_quantity',
                    'shares_held_for_buys', 'shares_held_for_sells'
                ]
            })
        # Filter
        if args.hasquantity:
            results = [x for x in results if x['quantity'] > 0]
        # Calculate position totals
        for idx, _ in enumerate(results):
            if results[idx].get('quantity') and \
               results[idx].get('average_buy_price'):
                results[idx]['total_cost'] = \
                    results[idx]['quantity'] * results[idx]['average_buy_price']
        return {'results': results}, 200


class Instruments(Resource):
    def get(self, item_id):
        token = parse_token(request.headers)
        if not token:
            return handle_bad_auth()
        res = requests.get(
            url='https://api.robinhood.com/instruments/%s/' % item_id,
            headers={'Authorization': 'Token ' + token})
        # Handle errors
        if not res or res.status_code is not 200:
            return handle_bad_response(res)
        # Parse data
        return {
            'results': parse_result(
                res.json(),
                {
                    'blacklist': [
                        'url', 'min_tick_size', 'bloomberg_unique',
                        'splits', 'quote', 'fundamentals', 'tradeable'
                    ],
                    'mangles': {
                        'market':
                            'http[s+]://api.robinhood.com/markets/(.*)[/+]'
                    },
                    'floats': [
                        'maintenance_ratio', 'day_trade_ratio',
                        'margin_initial_ratio'
                    ]
                })
        }, 200


class Fundamentals(Resource):
    def get(self, item_id):
        token = parse_token(request.headers)
        if not token:
            return handle_bad_auth()
        res = requests.get(
            url='https://api.robinhood.com/fundamentals/%s/' % item_id,
            headers={'Authorization': 'Token ' + token})
        # Handle errors
        if not res or res.status_code is not 200:
            return handle_bad_response(res)
        # Parse data
        return {
            'results': parse_result(
                res.json(),
                {
                    'blacklist': [
                        'url'
                    ],
                    'mangles': {
                        'instrument':
                            'http[s+]://api.robinhood.com/instruments/(.*)[/+]'
                    },
                    'floats': [
                        'average_volume', 'dividend_yield',
                        'high', 'high_52_weeks',
                        'low', 'low_52_weeks',
                        'market_cap', 'open', 'pe_ratio', 'volume'
                    ]
                })
        }, 200


class Quotes(Resource):
    def get(self, item_id):
        token = parse_token(request.headers)
        if not token:
            return handle_bad_auth()
        res = requests.get(
            url='https://api.robinhood.com/quotes/%s/' % item_id,
            headers={'Authorization': 'Token ' + token})
        # Handle errors
        if not res or res.status_code is not 200:
            return handle_bad_response(res)
        # Parse data
        return {
            'results': parse_result(
                res.json(),
                {
                    'mangles': {
                        'instrument':
                            'http[s+]://api.robinhood.com/instruments/(.*)[/+]'
                    },
                    'floats': [
                        'adjusted_previous_close', 'ask_price', 'ask_size',
                        'bid_price', 'bid_size',
                        'last_extended_hours_trade_price',
                        'last_trade_price', 'previous_close'
                    ]
                })
        }, 200


API.add_resource(Authenticate, '/authenticate')
API.add_resource(User, '/user')
API.add_resource(Positions, '/positions')
API.add_resource(Instruments, '/instruments/<string:item_id>')
API.add_resource(Fundamentals, '/fundamentals/<string:item_id>')
API.add_resource(Quotes, '/quotes/<string:item_id>')

if __name__ == '__main__':
    APP.run(debug=True)
