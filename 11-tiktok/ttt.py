import json
import sys
import urllib.parse as parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer

# constants of known http head elements
CONTENT_LENGTH = "Content-Length"
CONTENT_TYPE = "Content-Type"
MESSAGE = "message"
STATUS = "status"


def getBadResponse(message):
    return {
        STATUS: 'bad',
        MESSAGE: message
    }


def ensureParam(params, key, number):
    result = params.get(key, None)

    if result is None:
        raise Exception("Parameter '{}' is missing.".format(key))
    if number and not result.isnumeric():
        raise Exception("Parameter '{}' should be numeric.".format(key))

    if number:
        return int(result)
    else:
        return result


class Game:
    def __init__(self, name):
        self.id = None
        self.name = name
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.next = None

    def done(self):
        for y in self.board:
            for x in y:
                if x == 0:
                    return False
        return True

    # idk how this works - stack overflow :)
    def isWinner(self, player):
        for x in range(3):
            for y in range(3):
                deltaX = [-1, 1, 0, 0, 1, 1]
                deltaY = [0, 0, 1, -1, 1, -1]

                if self.board[y][x] == player:
                    for i in range(6):
                        x1 = x + deltaX[i]
                        x2 = x - deltaX[i]
                        y1 = y + deltaY[i]
                        y2 = y - deltaY[i]

                        if x1 < 0 or x1 >= 3 or x2 < 0 or x2 >= 3\
                                or y1 < 0 or y1 >= 3 or y2 < 0 or y2 >= 3:
                            continue

                        if self.board[y1][x1] == player and self.board[y2][x2] == player:
                            return True

    def status(self):
        if self.done():
            winner = 0
            if self.isWinner(1):
                winner = 1
            if self.isWinner(2):
                winner = 2
            return {
                'winner': int(winner)
            }

        return {
            'board': self.board,
            'next': self.next
        }

    def move(self, player, x, y):
        if self.done():
            return getBadResponse("Game has been already finished.")
        if player not in [1, 2]:
            return getBadResponse("Player {} does not exists.".format(player))

        if player == 2 and self.next is None:
            return getBadResponse("Player 1 should play first.")

        if player != self.next:
            return getBadResponse("Player {} already played, other player should play now.".format(
                player))

        if x not in [0, 1, 2] or y not in [0, 1, 2]:
            return getBadResponse("Move to x'{}';y'{}' must be between [0, 1, 2].".format(x, y))

        if self.board[y][x] != 0:
            return getBadResponse("Move to x'{}';y'{}' is already marked.".format(x, y))

        if player == 1:
            self.next = 2
        else:
            self.next = 1

        self.board[y][x] = player

        return {
            STATUS: 'ok'
        }


class GameManager:
    def __init__(self):
        self.games = dict()

    def start(self, name):
        board = Game(name)
        id = 1
        while True:
            if self.games[id] is None:
                board.id = id
                self.games[id] = board
                return {
                    "id": id
                }

            id = id + 1

    def move(self, id, player, x, y):
        if self.games[id]:
            return self.games[id].move(player, x, y)

        return getBadResponse("Game with id '{}' does not exists.".format(id))

    def status(self, id):
        if self.games[id]:
            return self.games[id].status()

        return getBadResponse("Game with id '{}' does not exists.".format(id))


def handle():
    manager = GameManager()

    class HTTPHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = parse.urlparse(self.path)

            params = parse.parse_qs(url.query)

            # start
            if url.path == '/start' or url.path == '/start/':
                result = manager.start(params.get("name", ""))
                return self.getRequest(result)

            # status
            if url.path == '/status' or url.path == '/status/':
                try:
                    gameId = ensureParam(params, 'game', True)
                except Exception as ex:
                    return self.getRequest(getBadResponse(str(ex)))

                return self.getRequest(manager.status(int(gameId)))

            # play
            if url.path == '/play' or url.path == '/play/':
                try:
                    gameId = ensureParam(params, 'game', True)
                    x = ensureParam(params, 'x', True)
                    y = ensureParam(params, 'y', True)
                    player = ensureParam(params, 'player', True)
                except Exception as ex:
                    return self.getRequest(getBadResponse(str(ex)))

                manager.move(gameId, player, x, y)

        def getRequest(self, responseContent):
            data = json.dumps(responseContent)

            if responseContent[STATUS] == 'ok':
                self.send_response(HTTPStatus.OK)
            else:
                self.send_response(HTTPStatus.BAD_REQUEST)

            self.send_header(CONTENT_TYPE, "application/json")
            self.send_header(CONTENT_LENGTH, str(len(data)))
            self.end_headers()

            self.wfile.write(bytes(data, 'UTF-8'))

    return HTTPHandler


def main(port):
    # print("starting...")
    server = HTTPServer(('', int(port)), handle())
    # print("everything set!")
    # print("listening...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()


if __name__ == '__main__':
    main(sys.argv[1])
