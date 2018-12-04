import os
import sys
import urllib.parse as parse
from http.server import (CGIHTTPRequestHandler, HTTPServer,
                         SimpleHTTPRequestHandler)
from socketserver import ThreadingMixIn


class Server(ThreadingMixIn, HTTPServer):
    pass


def handle():
    class RequestHandler(CGIHTTPRequestHandler):
        def getRequest(self):
            currentDictionaryName = os.path.dirname(self.path)

            if currentDictionaryName not in self.cgi_directories:
                self.cgi_directories.append(currentDictionaryName)

            url = parse.urlparse(self.path).path[1:]
            if url.endswith(".cgi") and self.is_cgi():
                self.run_cgi()
            else:
                with SimpleHTTPRequestHandler.send_head(self) as fileName:
                    if fileName:
                        self.copyfile(fileName, self.wfile)

        def do_HEAD(self):
            self.getRequest()

        def do_POST(self):
            self.getRequest()

        def do_GET(self):
            self.getRequest()

    return RequestHandler


def main(port, directo):
    # ensure dir
    os.chdir(os.path.realpath(directo))

    serverAddress = ('', int(port))
    handler = handle()
    http = Server(server_address=serverAddress,
                  RequestHandlerClass=handler)
    http.serve_forever()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
