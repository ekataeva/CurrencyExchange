import re
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
from controllers import Controller


class RequestHandler(BaseHTTPRequestHandler):
    http_code, message = 500, {'message': 'The server is in its initial state'}
    controller = Controller()

    def do_GET(self):
        get_controllers = {'/currencies': self.controller.get_currencies,
                           '/currency/': lambda: self.controller.get_currency(self.path),
                           '/exchangeRates': self.controller.get_exchange_rates,
                           '/exchangeRate/': lambda: self.controller.get_exchange_rate(self.path),
                           '/exchange': lambda: self.controller.get_exchange(self.get_query())
                           }

        self.call_controller(get_controllers)
        self.do_response()

    def do_POST(self):
        query = self.get_query()
        post_controllers = {'/currencies': lambda: self.controller.post_currencies(query),
                            '/exchangeRates': lambda: self.controller.post_exchange_rates(query)
                            }
        self.call_controller(post_controllers)
        self.do_response()

    def do_PATCH(self):
        query = self.get_query()
        controllers = {'/exchangeRate/': lambda: self.controller.patch_exchange_rate(self.path, query)}
        self.call_controller(controllers)
        self.do_response()

    def call_controller(self, controllers):
        for request, controller in controllers.items():
            pattern = re.compile(f'^{request}.*$')
            if pattern.match(self.path):
                self.http_code, self.message = controller()
                break

    def do_response(self):
        # Sent response's header
        self.send_response(self.http_code)
        self.send_header("Content-type", 'text/json')
        self.end_headers()
        # Sent response's body
        response_content = json.dumps(self.message)
        self.wfile.write(response_content.encode())

    def get_query(self):
        parsed_url = urlparse(self.path)
        return parse_qs(parsed_url.query)
