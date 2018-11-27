import json
import socket
# import ssl
import sys
import urllib.request as req
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer

# default encoding
ENCODING = "UTF-8"

# constants of known http head elements
TIMEOUT = "timeout"
CONTENT_LENGTH = "Content-Length"
CONTENT_TYPE = "Content-Type"
CONTENT = "content"
HOST = "Host"
TYPE = "type"
URL = "url"
JSON = "json"
HEADERS = "headers"
CODE = "code"


def ensureRequestMethod(request):
    if request[TYPE]:
        type = "GET"
    else:
        type = request[TYPE]

    return type


def ensureRequestTimeout(request):
    if request[TIMEOUT]:
        timeout = [TIMEOUT]
    else:
        timeout = 1

    return timeout


def prepareData(code, headers, jsonContent, content):
    data = dict()
    data[CODE] = code
    data[HEADERS] = dict(headers or {})
    data[JSON] = jsonContent
    data[CONTENT] = content

    return json.dumps(data, indent=2)


def handle(url):
    class HTTPHandler(BaseHTTPRequestHandler):
        def InvalidJson(self):
            self.getRequest('invalid json', None, None, None, None)

        def timeOut(self):
            self.getRequest(TIMEOUT, None, None, None, None)

        def getRequest(self, code, headers, responseContent, jsonContent, content):
            try:
                jsonContent = json.loads(responseContent)
            except:
                content = responseContent

            headers = headers or {}
            data = prepareData(code, headers, jsonContent, content)

            self.send_response(HTTPStatus.OK)

            for key, value in headers:
                self.send_header(key, value)

            self.send_header(CONTENT_TYPE, "application/json")
            self.send_header(CONTENT_LENGTH, str(len(data)))
            self.end_headers()

        def do_GET(self):
            # print("gettings something...")
            if HOST in self.headers:
                del self.headers[HOST]

            request = req.Request(url, None, self.headers, method="GET")
            try:
                with req.urlopen(request, timeout=1) as response:
                    content = response.read().decode(ENCODING)
                    headers = response.getheaders()
                    self.getRequest(HTTPStatus.OK, headers,
                                    content, None, None)
            except socket.timeout:
                self.timeOut()

        def do_POST(self):
            # print("posting something...")

            content = ''
            if CONTENT_LENGTH in self.headers:
                content = self.rfile.read(
                    int(self.headers.get(CONTENT_LENGTH)))

            try:
                request = json.loads(content.decode(ENCODING))
            except:
                self.InvalidJson()
                return

            url = req.Request(
                url=request[URL],
                data=request[CONTENT],
                headers=request[HEADERS],
                method=ensureRequestMethod(request))
            timeout = ensureRequestTimeout(request)

            try:
                with req.urlopen(url, timeout=timeout) as response:
                    content = response.read().decode(ENCODING)
                    headers = response.getheaders()
                    self.getRequest(HTTPStatus.OK, headers,
                                    content, None, None)
            except socket.timeout:
                self.getRequest(TIMEOUT, None, None, None, None)
                return

            if request[URL] is None or (request[TYPE] == "POST" and request[CONTENT] is None):
                self.InvalidJson()

    return HTTPHandler


def main(port, url):
    # print("starting...")
    server = HTTPServer(('', int(port)), handle(url))
    # print("everything set!")
    # print("listening...")
    server.serve_forever()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
