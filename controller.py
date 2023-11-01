from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs, unquote
from model import DbModel


class RequestHandler(BaseHTTPRequestHandler):
    model = DbModel()

    def do_GET(self):
        http_code, message, data = None, None, None

        if self.path == '/currencies':
            data, error = self.model.get_data('currencies')
            if data:
                http_code, message, data = 200, "OK", data
            else:
                http_code, message, data = 500, 'Internal Server Error', error

        elif self.path.startswith('/currency/'):
            cur_code = str(self.path.split('/')[-1])
            if not cur_code:
                http_code, message, data = 400, "Bad Request", "The currency code is missing in the address"
            else:
                data, error = self.model.get_data('currency', cur_code)
                if error:
                    http_code, message, data = 500, 'Internal Server Error', error
                elif data:
                    http_code, message, data = 200, "OK", data[0]
                else:
                    http_code, message, data = 404, "Not Found", "Currency not found"

        elif self.path == '/exchangeRates':
            data, error = self.model.get_data('exchange_rates')
            if data:
                http_code, message = 200, "OK"
            else:
                http_code, message, data = 500, 'Internal Server Error', error


        elif self.path.startswith('/exchangeRate/'):
            currencies = str(self.path.split('/')[-1])
            base_currency = currencies[0:3]
            target_currency = currencies[3:]
            if not (base_currency and target_currency):
                http_code, message, data = 400, "Bad Request", "Currency codes pair are missing in the address"
            else:
                data, error = self.model.get_data('exchange_rate', base_currency, target_currency)
                if data:
                    http_code, message, data = 200, "OK", data[0]
                elif error:
                    http_code, message, data = 500, 'Internal Server Error', error
                else:
                    http_code, message, data = 404, "Not Found", "The exchange rate for the pair was not found"

        self.do_response(http_code, message, data)

    def do_POST(self):
        http_code, message, data = None, None, None
        # self.path: /currencies?id=0&name=Euro&code=EUR&sign=%E2%82%AC
        parsed_url = urlparse(self.path)
        # ParseResult(scheme='', netloc='', path='/currencies', params='', query='name=Euro&code=EUR&sign=%E2%82%AC', fragment='')
        query_parameters = parse_qs(parsed_url.query)
        # {'name': ['Euro'], 'code': ['EUR'], 'sign': ['€']}

        if self.path.startswith('/currencies'):
            code = query_parameters['code']
            fullname = query_parameters['name']
            sign = query_parameters['sign']
            if code and fullname and sign:
                code = code[0]
                fullname = fullname[0]
                sign = sign[0]
                data, error = self.model.post_data('currencies', code, fullname, sign)
            else:
                data, error = None, "The required form field is missing"


        elif self.path.startswith('/exchangeRates'):
            base_currency_code = query_parameters['baseCurrencyCode']
            target_currency_code = query_parameters['targetCurrencyCode']
            rate = query_parameters['rate']
            if base_currency_code and target_currency_code and rate:
                base_currency_code = base_currency_code[0]
                target_currency_code = target_currency_code[0]
                rate = rate[0]
                data, error = self.model.post_data('exchange_rates', base_currency_code, target_currency_code, rate)
            else:
                data, error = None, "The required form field is missing"

        if error and 'already exists' in error:
            http_code, message, data = 409, 'Conflict', data
        elif error == "The required form field is missing":
            http_code, message, data = 400, 'Bad Request', error
        elif data:
            http_code, message, data = 200, "OK", data[0]
        else:
            http_code, message, data = 500, 'Internal Server Error', error

        self.do_response(http_code, message, data)

    def do_PATCH(self):
        if self.path.startswith('/exchangeRate/'):
            query = str(self.path.split('/')[-1])
            base_currency = query[0:3]
            target_currency = query[3:6]
            rate = query.split('=')[-1]

            if not base_currency \
                    or not target_currency\
                    or not rate:
                http_code, message, data = 400, "Bad Request", "The currency code is missing in the address"

            else:
                data, error = self.model.patch_rate(base_currency, target_currency, rate)
                if error:
                    http_code, message, data = 500, 'Internal Server Error', error
                elif data:
                    http_code, message, data = 200, "OK", data[0]
                else:
                    http_code, message, data = 404, "Not Found", "Currency not found"

            self.do_response(http_code, message, data)

    def do_response(self, code, message, data):
        # Sent response's header
        self.send_response(code, message)
        self.send_header("Content-type", 'text/html')
        self.end_headers()
        # Sent response's body
        response_content = json.dumps(data)
        self.wfile.write(response_content.encode())
