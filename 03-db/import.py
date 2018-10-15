import scorelib as s
import sys
import sqlite3


def main(source, connectionString):
    conn = sqlite3.connect(connectionString)
    cur = conn.cursor()

    # cur.execute("... values (?, ?)", (foo, bar))

    conn.commit()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
