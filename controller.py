from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs, unquote
from model import DbModel


class RequestHandler(BaseHTTPRequestHandler):
    model = DbModel()

    def do_GET(self):
        code, message, data = None, None, None

        if self.path == '/currencies':
            data, error = self.model.get_data('currencies')
            if data:
                code, message, data = 200, "OK", data
            else:
                code, message, data = 500, 'Internal Server Error', error

        elif self.path.startswith('/currency/'):
            code = str(self.path.split('/')[-1])
            if not code:
                code, message, data = 400, "Bad Request", "The currency code is missing in the address"
            else:
                data, error = self.model.get_data('currency', code)
                if error:
                    code, message, data = 500, 'Internal Server Error', error
                elif data:
                    code, message, data = 200, "OK", data[0]
                else:
                    code, message, data = 404, "Not Found", "Currency not found"

        elif self.path == '/exchangeRates':
            data, error = self.model.get_data('exchange_rates')
            if data:
                code, message, data = 200, "OK", data
            else:
                code, message, data = 500, 'Internal Server Error', error


        elif self.path.startswith('/exchangeRate/'):
            currencies = str(self.path.split('/')[-1])
            base_currency = currencies[0:3]
            target_currency = currencies[3:]
            if not (base_currency and target_currency):
                code, message, data = 400, "Bad Request", "Currency codes pair are missing in the address"
            else:
                data, error = self.model.get_data('exchange_rate', base_currency, target_currency)
                if data:
                    code, message, data = 200, "OK", data[0]
                elif error:
                    code, message, data = 500, 'Internal Server Error', error
                else:
                    code, message, data = 404, "Not Found", "The exchange rate for the pair was not found"

        self.do_response(code, message, data)

    def do_POST(self):
        # self.path: /currencies?id=0&name=Euro&code=EUR&sign=%E2%82%AC
        parsed_url = urlparse(self.path)
        # ParseResult(scheme='', netloc='', path='/currencies', params='', query='id=0&name=Euro&code=EUR&sign=%E2%82%AC', fragment='')
        query_parameters = parse_qs(parsed_url.query)
        # {'id': ['0'], 'name': ['Euro'], 'code': ['EUR'], 'sign': ['€']}
        print(query_parameters)

        if self.path.startswith('/currencies'):
            result = self.model.post_data('currencies', query_parameters)

            if result == 200:
                self.do_response(200, 'OK', {"message": 'POST request received'})
            elif result == 400:
                self.do_response(400, 'Bad Request', {"message": "The required form field is missing"})
            elif result == 409:
                self.do_response(409, 'Conflict', {"message": 'A currency with this code already exists'})
            elif result == 500:
                self.do_response(500, 'Internal Server Error', {"message": 'Server error'})

    def do_response(self, code, message, data):
        # Sent response's header
        self.send_response(code, message)
        self.send_header("Content-type", 'text/html')
        self.end_headers()
        # Sent response's body
        response_content = json.dumps(data)
        self.wfile.write(response_content.encode())
