#!/usr/bin/python3
import json
import sqlite3
import sys


CONNECTION_STRING = 'scorelib.dat'


def main(searchText):
    searchText = "%{}%".format(searchText)
    result = dict()

    conn = sqlite3.connect(CONNECTION_STRING)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    foundComposersWithPrint = c.execute(
        "SELECT person.name, print.id FROM person JOIN score_author ON score_author.composer = person.id JOIN edition ON edition.score = score_author.score JOIN print ON  print.edition = edition.id WHERE person.name LIKE ?",
        (searchText, )).fetchall()

    for composerName, printID in foundComposersWithPrint:
        rPrint = c.execute(
            "SELECT id, partiture, edition FROM print WHERE id=?", (printID, )).fetchone()
        rEdition = c.execute(
            "SELECT score, name, year FROM edition WHERE id=?", (rPrint["edition"],)).fetchone()
        rComposition = c.execute(
            "SELECT name, genre, key, incipit, year FROM score WHERE id=?", (rEdition["score"], )).fetchone()
        rEditors = c.execute("SELECT name, born, died FROM edition_author ea JOIN person p ON p.id = ea.editor WHERE ea.edition = ?",
                             (rPrint["edition"],)).fetchall()
        rComposers = c.execute(
            "SELECT name, born, died FROM score_author sa JOIN person p ON p.id = sa.composer WHERE sa.score = ?",
            (rEdition["score"],)).fetchall()
        rVoices = c.execute(
            "SELECT number, name, range FROM voice v WHERE v.score = ? ORDER BY number",
            (rEdition["score"],)).fetchall()

        rePrint = dict()
        rePrint["Print Number"] = rPrint["id"]
        rePrint["Partiture"] = True if (rPrint["partiture"] == 'Y') else False
        rePrint["Edition"] = rEdition["name"]
        rePrint["Title"] = rComposition["name"]
        rePrint["Composition Year"] = rComposition["year"]
        rePrint["Genre"] = rComposition["genre"]

        for editor in rEditors:
            editors = list()
            if(editor["born"] is not None or editor["died"] is not None):
                editors.append("{} ({}--{})".format(editor["name"] or "",
                                                    editor["born"] or "",
                                                    editor["died"] or ""))
            else:
                editors.append(editor["name"] or "")

        rePrint["Editor"] = editors

        for composer in rComposers:
            composers = list()
            if(composer["born"] is not None or composer["died"] is not None):
                composers.append("{} ({}--{})".format(composer["name"] or "",
                                                      composer["born"] or "",
                                                      composer["died"] or ""))
            else:
                composers.append(editor["name"] or "")

        rePrint["Composer"] = composers

        voices = dict()
        for voice in rVoices:
            oneVoice = dict()
            oneVoice["range"] = voice["range"]
            oneVoice["name"] = voice["name"]
            voices[voice["number"]] = oneVoice

        rePrint["Voices"] = voices

        if composerName in result:
            result[composerName].append(rePrint)
        else:
            result[composerName] = [rePrint]

    conn.commit()
    conn.close()

    print(json.dumps(result, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    main(sys.argv[1])
