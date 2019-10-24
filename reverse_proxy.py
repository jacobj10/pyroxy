from http.server import HTTPServer, BaseHTTPRequestHandler
from http.client import HTTPConnection

import yaml

# Config values to be overwritten by YAML input.
PORT = 8080
SERVER_ADDRESS = ''
HOSTS = {}

def populate_constants():
    with open('./manifest.yaml') as f:
        yaml_data = yaml.load(f, Loader=yaml.SafeLoader)
        if 'port' in yaml_data:
            PORT = yaml_data['port']
        if 'server' in yaml_data:
            SERVER_ADDRESS = yaml_data['server']
        if 'mapping' in yaml_data:
            for map in yaml_data['mapping']:
                HOSTS[map['host']] = map['target']

# Config values that are invariants
CONTENT_LENGTH = 'Content-Length'
SUPPLANTED_HEADERS = ['Server', 'Date']

class ReverseProxyHandler(BaseHTTPRequestHandler):
    def _get_headers_as_dict(self):
        """
        Convert the library specific HTTP header representation into a
        key-value dictionary.
        """
        to_return = {}
        for key in self.headers.keys():
            to_return[key] = self.headers.get(key)
        return to_return

    def _get_content_length(self, headers):
        content_length = 0
        if CONTENT_LENGTH in headers:
            cl_str = headers[CONTENT_LENGTH]
            if cl_str.isnumeric():
                content_length = int(cl_str)
        return content_length

    def _forward_request(self):
        """
        Forward the current request to the appropriate target, if applicable.
        """
        headers = self._get_headers_as_dict()
        if 'Host' not in headers:
            # This should never happen, but account for it nonetheless.
            self.send_response(500)
            self.end_headers()
            return
        else:
            host = headers['Host'].split(':')[0]
            print("Proxying request for: {}".format(host))

            # Again this should never happen, but redundancy is key.
            if host not in HOSTS:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'Error forwarding request')
                return
            proxied_host = HOSTS[host]

            headers.pop('Host')

            ibody = self.rfile.read(self._get_content_length(headers))
            proxy_connection = HTTPConnection(proxied_host)
            # Force HTTP/1.0 to avoid compatibility issues with handler.
            proxy_connection._http_vsn = 10
            proxy_connection._http_vsn_str = 'HTTP/1.0'

            try:
                proxy_connection.request(self.command, self.path, body=ibody, headers=headers)
            except Exception as e:
                print("Error occured: " + str(e))
                self.send_response(500)
                self.end_headers()
                return
            response = proxy_connection.getresponse()
            body = response.read()
            response.close()
            self.send_response(response.status)
            for header, value in response.getheaders():
                if header not in SUPPLANTED_HEADERS:
                    self.send_header(header, value)
            self.end_headers()
            self.wfile.write(body)

    def do_GET(self):
        self._forward_request()
    def do_PUT(self):
        self._forward_request()
    def do_POST(self):
        self._forward_request()
    def do_OPTIONS(self):
        self._forward_request()
    def do_HEAD(self):
        self._forward_request()


if __name__ == '__main__':
    populate_constants()

    server = HTTPServer((SERVER_ADDRESS, PORT), ReverseProxyHandler)
    try:
        print("Now serving requests!")
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        server.server_close()
