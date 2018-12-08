import re
import json
import sys
import urllib.parse as parse
import urllib.request as req
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import ssl
from urllib.error import HTTPError
import socket

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

# SSL
SSL_VALID = "certificate valid"
SSL_FOR = "certificate for"


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


def ensureRequestUrl(request):
    if re.match('http://.*|https://.*', request[URL]):
        return request[URL]
    else:
        return 'http:*//' + request[URL]


def checkSSL(response, url):
    result = dict()
    result[SSL_VALID] = None
    result[SSL_FOR] = None

    if url.startswith('https'):
        port = 443
        serverHostName = parse.urlparse(response.geturl()).netloc
        sslCtx = ssl.create_default_context()
        wrappedSocket = sslCtx.wrap_socket(
            socket.socket(), server_hostname=serverHostName)

        try:
            wrappedSocket.connect((serverHostName, port))
        except:
            result[SSL_VALID] = False
            return result

        cert = wrappedSocket.getpeercert()
        result[SSL_VALID] = True
        result[SSL_VALID] = [x[1] for x in cert['subjectAltName']]

    return result


def prepareData(code, headers, jsonContent, content, sslRequest):
    data = dict()
    data[CODE] = code

    if headers:
        data[HEADERS] = dict()
        for key, value in headers:
            data[HEADERS][key] = value

    if jsonContent:
        data[JSON] = jsonContent

    if content:
        data[CONTENT] = content

    if sslRequest:
        if sslRequest[SSL_VALID] is not None:
            data[SSL_VALID] = sslRequest[SSL_VALID]
        if sslRequest[SSL_FOR] is not None:
            data[SSL_FOR] = sslRequest[SSL_VALID]

    return json.dumps(data, indent=2)


def handle(url):
    class HTTPHandler(BaseHTTPRequestHandler):
        def InvalidJson(self):
            self.getRequest('invalid json', None, None, None)

        def timeOut(self):
            self.getRequest(TIMEOUT, None, None, None)

        def getRequest(self, code, headers, responseContent, sslRequest):
            jsonContent = None
            content = None

            try:
                jsonContent = json.loads(responseContent)
            except:
                content = responseContent

            data = prepareData(code, headers, jsonContent, content, sslRequest)

            self.send_response(HTTPStatus.OK)
            self.send_header(CONTENT_TYPE, "application/json")
            self.send_header(CONTENT_LENGTH, str(len(data)))
            self.end_headers()

            self.wfile.write(bytes(data, 'UTF-8'))

        def do_GET(self):
            if HOST in self.headers:
                del self.headers[HOST]

            requestedUrlParams = parse.urlparse(self.path).query
            requestedUrl = "{}?{}".format(url, requestedUrlParams)

            request = req.Request(url=requestedUrl, data=None,
                                  headers=self.headers, method="GET")
            try:
                with req.urlopen(request, timeout=1) as response:
                    content = response.read().decode(ENCODING)
                    headers = response.getheaders()
                    sslRequest = checkSSL(response, requestedUrl)
                    self.getRequest(response.status, headers,
                                    content, sslRequest)
            except HTTPError as error:
                return self.getRequest(error.code, None, None, None)
            except:
                self.timeOut()

        def do_POST(self):
            leng = int(self.headers.get(CONTENT_LENGTH), 0)
            content = self.rfile.read(leng)
            decoded = content.decode(ENCODING)
            try:
                request = json.loads(decoded, encoding=ENCODING)
            except:
                self.InvalidJson()
                return

            if URL not in request or (TYPE in request and request[TYPE] == "POST" and CONTENT not in request):
                self.InvalidJson()
                return

            try:
                result = req.Request(
                    url=ensureRequestUrl(request),
                    data=ensureRequestData(request),
                    headers=ensureRequestHeader(request),
                    method=ensureRequestMethod(request))
                timeout = ensureRequestTimeout(request)

                with req.urlopen(result, timeout=timeout) as response:
                    content = response.read().decode(ENCODING)
                    headers = response.getheaders()
                    sslRequest = checkSSL(response, ensureRequestUrl(request))
                    self.getRequest(response.status, headers,
                                    content, sslRequest)
            except HTTPError as error:
                return self.getRequest(error.code, None, None, None)
            except:
                self.timeOut()
                return

    return HTTPHandler


def main(port, url):
    # print("starting...")
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http//' + url

    server = HTTPServer(('', int(port)), handle(url))
    # print("everything set!")
    # print("listening...")
    try:

        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
