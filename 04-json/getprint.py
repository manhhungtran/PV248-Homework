#!/usr/bin/python3
import json
import sqlite3
import sys


CONNECTION_STRING = 'scorelib.dat'


def main(searchText):
    result = list()

    conn = sqlite3.connect(CONNECTION_STRING)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    rPrint = c.execute(
        "SELECT id, partiture, edition FROM print WHERE id=?", (searchText, )).fetchone()
    rEdition = c.execute(
        "SELECT score, name, year FROM edition WHERE id=?", (rPrint["edition"],)).fetchone()
    rComposers = c.execute(
        "SELECT name, born, died FROM score_author sa JOIN person p ON p.id = sa.composer WHERE sa.score = ?",
        (rEdition["score"],)).fetchall()

    for composer in rComposers:
        rComposer = dict()
        rComposer["name"] = composer["name"]
        rComposer["born"] = composer["born"]
        rComposer["died"] = composer["died"]
        result.append(rComposer)

    conn.commit()
    conn.close()

    print(json.dumps(result, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    main(sys.argv[1])
