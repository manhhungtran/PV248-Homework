import json
# import ssl
import sys
import urllib.request as req
import urllib.parse as parse
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
    if TYPE in request:
        return request[TYPE]
    else:
        return "GET"


def ensureRequestData(request):
    if TYPE in request and request[TYPE] == "POST":
        return bytes(request[CONTENT], ENCODING)
    else:
        return None


def ensureRequestTimeout(request):
    if TIMEOUT in request:
        return request[TIMEOUT]
    else:
        return 1


def ensureRequestHeader(request):
    if HEADERS in request:
        return request[HEADERS]
    else:
        return {}


def prepareData(code, headers, jsonContent, content):
    data = dict()
    data[CODE] = code

    if headers:
        data[HEADERS] = dict()
        for hkey, hvalue in headers:
            data[HEADERS][hkey] = hvalue

    if content:
        try:
            data[JSON] = json.loads(content)
        except ValueError:
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

            self.send_header(CONTENT_TYPE, "application/json")
            self.send_header(CONTENT_LENGTH, str(len(data)))
            self.end_headers()

            self.wfile.write(bytes(data, 'UTF-8'))

        def do_GET(self):
            # print("gettings something...")
            requestedUrlParams = parse.urlparse(self.path).query
            requestedUrl = "{}?{}".format(url, requestedUrlParams)

            if HOST in self.headers:
                del self.headers[HOST]

            request = req.Request(requestedUrl, None,
                                  self.headers, method="GET")
            try:
                with req.urlopen(request, timeout=1) as response:
                    content = response.read().decode(ENCODING)
                    headers = response.getheaders()
                    self.getRequest(HTTPStatus.OK, headers,
                                    content, None, None)
            except:
                self.timeOut()

        def do_POST(self):
            # print("posting something...")

            try:
                content = ''
                if CONTENT_LENGTH in self.headers:
                    content = self.rfile.read(
                        int(self.headers.get(CONTENT_LENGTH), 0))

                request = json.loads(content.decode(ENCODING))

                if URL not in request or (TYPE in request and request[TYPE] == "POST" and CONTENT not in request):
                    self.InvalidJson()
                    return
            except:
                self.InvalidJson()
                return

            result = req.Request(
                url=request[URL],
                data=ensureRequestData(request),
                headers=ensureRequestHeader(request),
                method=ensureRequestMethod(request))
            timeout = ensureRequestTimeout(request)

            try:
                with req.urlopen(result, timeout=timeout) as response:
                    content = response.read().decode(ENCODING)
                    headers = response.getheaders()
                    self.getRequest(HTTPStatus.OK, headers,
                                    content, None, None)
            except:
                self.getRequest(TIMEOUT, None, None, None, None)
                return

    return HTTPHandler


def main(port, url):
    # print("starting...")
    server = HTTPServer(('', int(port)), handle(url))
    # print("everything set!")
    # print("listening...")
    server.serve_forever()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
