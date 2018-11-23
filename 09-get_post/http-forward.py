import sys
import socket


def main(port, url):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((url, port))
    serversocket.listen(5)  # become a server socket, maximum 5 connections

    while True:
        connection, address = serversocket.accept()
        buf = connection.recv(64)
        if len(buf) > 0:
            print(buf)
            break

    print("")


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
