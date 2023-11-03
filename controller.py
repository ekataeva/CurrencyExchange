from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs, unquote
from model import DbModel


class RequestHandler(BaseHTTPRequestHandler):
    model = DbModel()

    def do_GET(self):
        http_code, message = None, None

        if self.path == '/currencies':
            data, error = self.model.get_data('currencies')
            if data:
                http_code, message = 200, data
            else:
                http_code, message = 500, {'message': error}

        elif self.path.startswith('/currency/'):
            print(self.path)
            cur_code = str(self.path.split('/')[-1])
            if not cur_code:
                http_code, message = 400, {'message': "The currency code is missing in the address"}
            else:
                data, error = self.model.get_data('currency', cur_code)
                if error:
                    http_code, message = 500, {'message': error}
                elif data:
                    http_code, message = 200, data[0]
                else:
                    http_code, message = 404, {'message': "Currency not found"}

        elif self.path == '/exchangeRates':
            data, error = self.model.get_data('exchange_rates')
            if data:
                http_code = 200
            else:
                http_code, message = 500, {'message': error}


        elif self.path.startswith('/exchangeRate/'):
            currencies = str(self.path.split('/')[-1])
            base_currency = currencies[0:3]
            target_currency = currencies[3:]
            if not (base_currency and target_currency):
                http_code, message = 400, {'message': "Currency codes pair are missing in the address"}
            else:
                data, error = self.model.get_data('exchange_rate', base_currency, target_currency)
                if data:
                    http_code, message = 200, data[0]
                elif error:
                    http_code, message = 500, {'message': error}
                else:
                    http_code, message = 404, {'message': "The exchange rate for the pair was not found"}

        elif self.path.startswith('/exchange'):
            query = self.get_query()
            if not (query.get('from') and query.get('to') and query.get('amount')):
                http_code, message = 400, {'message': "Currency codes pair or amount are missing in the address"}
            else:
                base_currency = query['from'][0]
                target_currency = query['to'][0]
                amount = float(query['amount'][0])
                data, error = self.model.get_data('exchange_rate', base_currency, target_currency)
                if data:
                    data = data[0]
                    converted_amount = amount * data['rate']
                else:
                    invert_data, error = self.model.get_data('exchange_rate', target_currency, base_currency)
                    if invert_data:
                        data = invert_data[0]
                        converted_amount = amount / invert_data['rate']
                    else:
                        bc_data, error = self.model.get_data('exchange_rate', 'USD', base_currency)
                        print(bc_data)
                        tc_data = self.model.get_data('exchange_rate', 'USD', target_currency)
                        if bc_data and tc_data:
                            data = bc_data[0]
                            converted_amount = amount * bc_data[0]['rate'] / tc_data[0]['rate']
                data['amount'] = amount
                data['convertedAmount'] = converted_amount
                if data:
                    http_code, message = 200, data
                elif error:
                    http_code, message = 500, {'message': error}
                else:
                    http_code, message = 404, {'message': "The exchange rate for the pair was not found"}

        self.do_response(http_code, message)

    def do_POST(self):
        http_code, data, error = None, None, None
        query = self.get_query()

        if self.path.startswith('/currencies'):
            code = query['code']
            fullname = query['name']
            sign = query['sign']
            if code and fullname and sign:
                code = code[0]
                fullname = fullname[0]
                sign = sign[0]
                data, error = self.model.post_data('currencies', code, fullname, sign)
            else:
                data, error = None, "The required form field is missing"


        elif self.path.startswith('/exchangeRates'):
            base_currency_code = query['baseCurrencyCode']
            target_currency_code = query['targetCurrencyCode']
            rate = query['rate']
            if base_currency_code and target_currency_code and rate:
                base_currency_code = base_currency_code[0]
                target_currency_code = target_currency_code[0]
                rate = rate[0]
                data, error = self.model.post_data('exchange_rates', base_currency_code, target_currency_code, rate)
            else:
                data, error = None, {'message': "The required form field is missing"}

        if error and 'already exists' in error:
            http_code, message = 409, data
        elif error == "The required form field is missing":
            http_code, message = 400, {'message': error}
        elif data:
            http_code, message = 200, data[0]
        else:
            http_code, message = 500, {'message': error}

        self.do_response(http_code, message)

    def do_PATCH(self):
        query = self.get_query()

        if self.path.startswith('/exchangeRate/'):
            currencies = str(self.path.split('/')[-1])
            base_currency = currencies[0:3]
            target_currency = currencies[3:6]
            rate = query['rate']

            if (len(currencies) < 7
                    or not base_currency \
                    or not target_currency \
                    or not rate):
                http_code, message = 400, {'message': "The currency code or rate are missing in the address"}

            else:
                data, error = self.model.patch_rate(base_currency, target_currency, rate[0])
                if error == "The currency pair is missing in the database":
                    http_code, message = 404, {'message': error}
                elif data:
                    http_code, message = 200, data[0]
                else:
                    http_code, message = 500, {'message': error}

            self.do_response(http_code, message)

    def do_response(self, code, message):
        # Sent response's header
        self.send_response(code)
        self.send_header("Content-type", 'text/json')
        self.end_headers()
        # Sent response's body
        response_content = json.dumps(message)
        self.wfile.write(response_content.encode())

    def get_query(self):
        parsed_url = urlparse(self.path)
        return parse_qs(parsed_url.query)
