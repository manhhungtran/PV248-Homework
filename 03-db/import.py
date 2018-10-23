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
                              (self.voice.order,
                               compositionID,
                               self.voice.range,
                               self.voice.name)).lastrowid


class EditionDB:
    def __init__(self, edition):
        self.edition = edition

    def process(self, existingEdition, cursor, compositionID):
        if existingEdition is None:
            return cursor.execute('INSERT INTO edition (score, name, year) VALUES (?, ?, ?)',
                                  (compositionID, self.edition.name, self.edition.year)).lastrowid
        else:
            return existingEdition[0]


class AuthorDB:
    def __init__(self, author):
        self.author = author

    def process(self, cursor, existingAuthor, compositionID):
        if existingAuthor is None:
            authorID = cursor.execute('INSERT INTO person (name, born, died) VALUES (?, ?, ?)',
                                      (self.author.name, self.author.born, self.author.died)).lastrowid
        else:
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

    def generateSQLQuery(self):
        result = 'SELECT id FROM score WHERE'
        if self.composition.name is not None:
            result += ' name=?'
        else:
            result += ' name is null'
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
        if self.composition.name is not None:
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

    def process(self, cursor, existingComposition, print):
        if existingComposition is not None:
            existingComposers = cursor.execute('SELECT composer FROM score_author WHERE score=?',
                                               (existingComposition[0], )).fetchall()
            existingComposersIDs = map(lambda x: x[0], existingComposers)

            for author in print.composition().authors:
                if author.name is not None:
                    existingAuthor = cursor.execute(
                        'SELECT id FROM person WHERE name=?', (author.name, )).fetchone()
                else:
                    existingAuthor = cursor.execute(
                        'SELECT id FROM person WHERE name is null').fetchone()

                if existingAuthor is not None and existingAuthor[0] in existingComposersIDs:
                    continue
                else:
                    return cursor.execute('INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)',
                                          (self.composition.name,
                                           self.composition.genre,
                                           self.composition.key,
                                           self.composition.incipit,
                                           self.composition.year)).lastrowid

            existingVoices = cursor.execute(
                'SELECT number, name, range FROM voice WHERE score=?', (existingComposition[0], )).fetchall()

            if not print.composition().voices and existingVoices is None:
                return existingComposition[0]

            numbers = map(lambda x: x[0], existingVoices)
            names = map(lambda x: x[1], existingVoices)
            ranges = map(lambda x: x[2], existingVoices)

            for voice in print.composition().voices:
                if(voice.name in names and voice.range in ranges and voice.order in numbers):
                    continue
                else:
                    return cursor.execute('INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)',
                                          (self.composition.name,
                                           self.composition.genre,
                                           self.composition.key,
                                           self.composition.incipit,
                                           self.composition.year)).lastrowid

            return existingComposition[0]
        else:
            return cursor.execute('INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)',
                                  (self.composition.name,
                                   self.composition.genre,
                                   self.composition.key,
                                   self.composition.incipit,
                                   self.composition.year)).lastrowid


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
    # Composition
    compositiondb = CompositionDB(print.edition.composition)
    compositionQuery = compositiondb.generateSQLQuery()
    compositionParam = compositiondb.generateSQLParams()
    existingComposition = cursor.execute(
        compositionQuery,
        compositionParam).fetchone()
    compositionID = compositiondb.process(cursor, existingComposition, print)

    # Authors
    for author in print.composition().authors:
        authorDB = AuthorDB(author)
        if(author.name is not None):
            existingAuthor = cursor.execute(
                'SELECT id FROM person WHERE name=?', (author.name, )).fetchone()
        else:
            existingAuthor = cursor.execute(
                'SELECT id FROM person WHERE name is null').fetchone()
        authorDB.process(cursor, existingAuthor, compositionID)

    # Voices
    for voice in print.composition().voices:
        voiceDB = VoiceDB(voice)
        voiceDB.process(cursor, compositionID)

    # Edition
    edition = print.edition
    if(edition is not None):
        existingEdition = cursor.execute(
            'SELECT id FROM edition WHERE name=? AND score=?', (edition.name, compositionID)).fetchone()
    else:
        existingEdition = cursor.execute(
            'SELECT id FROM edition WHERE name is null AND score=?', (compositionID, )).fetchone()
    editionDB = EditionDB(edition)
    editionID = editionDB.process(existingEdition, cursor, compositionID)

    # Editors
    for editor in print.edition.authors:
        editorDB = EditorDB(editor)
        if(editor is not None):
            existingEditor = cursor.execute(
                'SELECT id FROM person WHERE name=?', (editor.name, )).fetchone()
        else:
            existingEditor = cursor.execute(
                'SELECT id FROM person WHERE name is null').fetchone()
        editorDB.process(existingEditor, editionID, cursor)

    # Partiture
    if print.partiture:
        partiture = 'Y'
    else:
        partiture = 'N'

    cursor.execute('INSERT INTO print (id, partiture, edition) VALUES (?, ?, ?)',
                   (print.print_id, partiture, editionID))


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
