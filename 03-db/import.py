#!/usr/bin/python3
import scorelib
import sys
import sqlite3


SQL_SCHEME_FILE = 'scorelib.sql'


class VoiceDB:
    def __init__(self, voice):
        self.voice = voice

    def process(self, cursor, compositionID):
        return cursor.execute('INSERT INTO voice (number, score, range, name) VALUES (?, ?, ?, ?)',
                              (self.voice.number,
                               compositionID,
                               self.voice.range,
                               self.voice.name)).lastrowid


class EditionDB:
    def __init__(self, edition):
        self.edition = edition

    def process(self, existingEdition, cursor, compositionID):
        if existingEdition is None:
            return cursor.execute('INSERT INTO edition (score, name, year) VALUES (?, ?, ?)',
                                  (compositionID, self.edition.name, None)).lastrowid
        else:
            return existingEdition[0]


class AuthorDB:
    def __init__(self, author):
        self.author = author

    def process(self, cursor, existingAuthor, compositionID):
        if existingAuthor is None:
            authorID = cursor.execute('INSERT INTO person (name, born, died) VALUES (?, ?, ?)',
                                      (self.author.name, self.author.born, self.author.died)).lastrowid

        if self.author.born is not None:
            cursor.execute('UPDATE person SET born=? WHERE id=?',
                           (self.author.born, existingAuthor[0]))
        if self.author.died is not None:
            cursor.execute('UPDATE person SET died=? WHERE id=?',
                           (self.author.died, existingAuthor[0]))

        authorID = existingAuthor[0]
        cursor.execute('INSERT INTO score_author (score, composer) VALUES (?, ?)',
                       (compositionID, authorID))


class CompositionDB:
    def __init__(self, composition):
        self.composition = composition

    def generateSQLInsert(self):
        result = 'SELECT id FROM score WHERE name=?'
        if self.composition.genre is not None:
            result += ' AND genre=?'
        else:
            result += ' AND genre is null'
        if self.composition.key is not None:
            result += ' AND key=?'
        else:
            result += ' AND key is null'
        if self.composition.incipit is not None:
            result += ' AND incipit=?'
        else:
            result += ' AND incipit is null'
        if self.composition.year is not None:
            result += ' AND year=?'
        else:
            result += ' AND year is null'

        return result

    def generateSQLParams(self):
        params = []
        params.append(self.composition.name)
        if self.composition.genre is not None:
            params.append(self.composition.genre)

        if self.composition.key is not None:
            params.append(self.composition.key)

        if self.composition.incipit is not None:
            params.append(self.composition.incipit)

        if self.composition.year is not None:
            params.append(self.composition.year)

        return params


class EditorDB:
    def __init__(self, editor):
        self.editor = editor

    def process(self, existingEditor, editionID, cursor):
        if existingEditor is None:
            editorID = cursor.execute('INSERT INTO person (name, born, died) VALUES (?, ?, ?)',
                                      (self.editor.name,
                                       self.editor.born,
                                       self.editor.died)).lastrowid
        else:
            if self.editor.born is not None:
                cursor.execute('UPDATE person SET born=? WHERE id=?',
                               (self.editor.born, existingEditor[0]))
            if self.editor.died is not None:
                cursor.execute('UPDATE person SET died=? WHERE id=?',
                               (self.editor.died, existingEditor[0]))
            editorID = existingEditor[0]

        cursor.execute('INSERT INTO edition_author (edition, editor) VALUES (?, ?)',
                       (editionID, editorID))


def processPrint(print, cursor):
    compositiondb = CompositionDB(print.edition.composition)
    compositionQuery = compositiondb.generateSQLInsert()
    compositionParam = compositiondb.generateSQLParams()
    composition = cursor.execute(
        compositionQuery,
        compositionParam).fetchone()
    if composition is not None:
        compositionID = composition[0]
    else:
        compositionID = cursor.execute('INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)',
                                       (composition.name, composition.genre, composition.key, composition.incipit,
                                        composition.year)).lastrowid

    for author in print.edition.composition.authors:
        authorDB = authorDB(author)
        existingAuthor = cursor.execute(
            'SELECT id FROM person WHERE name=?', (author.name,)).fetchone()
        authorDB.process(cursor, existingAuthor, compositionID)

    for voice in print.edition.composition.voices:
        voiceDB = VoiceDB(voice)
        voiceDB.process(cursor, compositionID)

    edition = print.edition
    existingEdition = cursor.execute(
        'SELECT id FROM edition WHERE name=? AND score=?', (edition.name, compositionID, )).fetchone()
    editionDB = EditionDB(edition)
    editionID = editionDB.process(existingEdition, cursor, compositionID)

    for editor in print.edition.authors:
        editorDB = EditorDB(editor)
        existingEditor = cursor.execute(
            'SELECT id FROM person WHERE name=?', (editor.name,)).fetchone()

        editorDB.process(existingEditor, editionID, cursor)

    if print.partiture:
        partiture = 'Y'
    else:
        partiture = 'N'

    cursor.execute('INSERT INTO print (id, partiture, edition) VALUES (?, ?, ?)',
                   (print.print_id, partiture, editionID)).lastrowid


def processData(sourceFile, cursor, connection):
    prints = scorelib.load(sourceFile)
    for print in prints:
        processPrint(print, cursor)
        connection.commit()


def main(source, connectionString):
    conn = sqlite3.connect(connectionString)
    cursor = conn.cursor()

    with open(SQL_SCHEME_FILE, 'r', encoding="UTF-8") as file:
        script = file.read()
        cursor.executescript(script)
        conn.commit()

    processData(source, cursor, conn)
    conn.close()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
