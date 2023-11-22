from http.server import HTTPServer
from request_handler import RequestHandler
port = 8000

# Create HTTP-server with specified address and handler
server_address = ('0.0.0.0', port)
with HTTPServer(server_address, RequestHandler) as server:
    print(f'Starting server on port {port}...')
    server.serve_forever()
